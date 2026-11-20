/*
 * runner — gọi một hàm VeRA trong shared object trên từng vector I/O.
 *
 *   runner <file.so> <symbol> [timeout_giây]
 *
 * stdin, mỗi dòng một vector:   <len> <arg_hex> <out_cap> <in_hex | ->
 * stdout, mỗi dòng một kết quả:
 *   OK <ret_hex16> <out_hex | -> <in_changed 0|1> <overflow 0|1>
 *   TIMEOUT
 *   CRASH <signal>
 *   BADLINE
 *
 * Mỗi vector chạy trong một tiến trình con riêng (fork) với giới hạn bộ nhớ, CPU
 * và timeout, nên mã do LLM sinh ra có treo hay crash cũng chỉ hỏng vector đó.
 * Bộ đệm out được tô 0xCC trước khi gọi; sau out_cap có 16 byte canh để phát hiện ghi tràn.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

typedef uint64_t (*vera_fn)(const uint8_t *, size_t, uint64_t, uint8_t *, size_t);

#define GUARD 16
#define MAX_LINE (1 << 22)

static int hexval(int c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static void put_hex(FILE *f, const uint8_t *p, size_t n)
{
    static const char hx[] = "0123456789abcdef";
    if (n == 0) { fputc('-', f); return; }
    for (size_t i = 0; i < n; i++) {
        fputc(hx[p[i] >> 4], f);
        fputc(hx[p[i] & 15], f);
    }
}

static void run_child(vera_fn fn, const uint8_t *in, size_t len, uint64_t arg,
                      size_t out_cap, int fd, unsigned timeout)
{
    struct rlimit rl;
    rl.rlim_cur = rl.rlim_max = 512ul << 20;
    setrlimit(RLIMIT_AS, &rl);
    rl.rlim_cur = rl.rlim_max = timeout + 1;
    setrlimit(RLIMIT_CPU, &rl);
    alarm(timeout);

    uint8_t *ib = malloc(len ? len : 1);
    uint8_t *ic = malloc(len ? len : 1);
    uint8_t *ob = malloc(out_cap + GUARD);
    if (!ib || !ic || !ob) _exit(3);
    memcpy(ib, in, len);
    memcpy(ic, in, len);
    memset(ob, 0xCC, out_cap + GUARD);

    uint64_t ret = fn(ib, len, arg, ob, out_cap);

    int in_changed = memcmp(ib, ic, len) != 0;
    int overflow = 0;
    for (size_t i = 0; i < GUARD; i++)
        if (ob[out_cap + i] != 0xCC) overflow = 1;

    FILE *f = fdopen(fd, "w");
    fprintf(f, "OK %016llx ", (unsigned long long)ret);
    put_hex(f, ob, out_cap);
    fprintf(f, " %d %d\n", in_changed, overflow);
    fclose(f);
    _exit(0);
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: %s <file.so> <symbol> [timeout_s]\n", argv[0]);
        return 2;
    }
    unsigned timeout = argc > 3 ? (unsigned)atoi(argv[3]) : 2;
    void *h = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!h) { fprintf(stderr, "dlopen: %s\n", dlerror()); return 2; }
    vera_fn fn = (vera_fn)dlsym(h, argv[2]);
    if (!fn) { fprintf(stderr, "dlsym: %s\n", dlerror()); return 2; }

    char *line = malloc(MAX_LINE);
    uint8_t *in = malloc(MAX_LINE / 2);
    char *res = malloc(MAX_LINE * 2 + 64);
    if (!line || !in || !res) return 2;

    while (fgets(line, MAX_LINE, stdin)) {
        size_t len, out_cap;
        unsigned long long arg;
        char *hex = malloc(strlen(line) + 1);
        if (sscanf(line, "%zu %llx %zu %s", &len, &arg, &out_cap, hex) != 4 ||
            len > MAX_LINE / 2 || out_cap > (64u << 20)) {
            puts("BADLINE"); free(hex); continue;
        }
        if (strcmp(hex, "-") == 0) {
            if (len != 0) { puts("BADLINE"); free(hex); continue; }
        } else {
            if (strlen(hex) != 2 * len) { puts("BADLINE"); free(hex); continue; }
            for (size_t i = 0; i < len; i++)
                in[i] = (uint8_t)(hexval(hex[2 * i]) << 4 | hexval(hex[2 * i + 1]));
        }
        free(hex);

        int pfd[2];
        if (pipe(pfd) != 0) return 2;
        fflush(stdout);
        pid_t pid = fork();
        if (pid == 0) {
            close(pfd[0]);
            run_child(fn, in, len, (uint64_t)arg, out_cap, pfd[1], timeout);
        }
        close(pfd[1]);
        size_t got = 0;
        ssize_t r;
        while ((r = read(pfd[0], res + got, MAX_LINE * 2 + 63 - got)) > 0)
            got += (size_t)r;
        close(pfd[0]);
        res[got] = 0;
        int st;
        waitpid(pid, &st, 0);
        if (WIFEXITED(st) && WEXITSTATUS(st) == 0 && got > 0)
            fputs(res, stdout);
        else if (WIFSIGNALED(st) && (WTERMSIG(st) == SIGALRM || WTERMSIG(st) == SIGXCPU))
            puts("TIMEOUT");
        else if (WIFSIGNALED(st))
            printf("CRASH %d\n", WTERMSIG(st));
        else
            printf("CRASH exit%d\n", WEXITSTATUS(st));
    }
    return 0;
}
