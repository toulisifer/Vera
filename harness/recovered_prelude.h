/*
 * Prelude chèn trước recovered_c khi biên dịch (E0 compile rate và V1).
 * Chỉ định nghĩa những gì prompt đã hứa với model (VERA_ERR, stdint/stddef) và các kiểu
 * dữ liệu Ghidra hay bị chép sang mã khôi phục. Không định nghĩa DAT_xxx hay hàm nào.
 * <sys/types.h> cho các kiểu POSIX (ssize_t...) mà mã C trên Linux hay dùng — thêm sau E1
 * (LLM4Decompile dùng ssize_t); V1 của MỌI lượt chạy đã được tính lại với prelude này.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>

#define VERA_ERR ((uint64_t)0xFFFFFFFFFFFFFFFFull)

typedef unsigned char byte, uchar, undefined, undefined1;
typedef unsigned short ushort, undefined2;
typedef unsigned int uint, undefined4;
typedef unsigned long ulong, undefined8;
typedef long long longlong;
typedef unsigned long long ulonglong;
