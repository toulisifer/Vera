/*
 * vera.h — chữ ký chung và macro obfuscation cho corpus VeRA.
 *
 * Mọi hàm trong corpus có đúng một chữ ký:
 *
 *   uint64_t fn_XX(const uint8_t *in, size_t len, uint64_t arg,
 *                  uint8_t *out, size_t out_cap);
 *
 * Quy ước (xem docs/conventions.md):
 *   - Hàm trả về một giá trị (checksum, hash, số byte đã ghi, mã trạng thái).
 *   - Hàm có ghi `out` thì KHÔNG ghi byte nào nếu out_cap không đủ, và trả VERA_ERR.
 *   - Không gọi hàm thư viện, không malloc, không I/O, không biến toàn cục có trạng thái.
 *   - Không có hàm phụ: toàn bộ logic nằm trong fn_XX (macro thì được).
 *   - Tên biến trung tính (h, acc, s, i, j, k...) — không đặt tên lộ thuật toán.
 *
 * Cấu hình obf được biên dịch với -DVERA_OBF. Ở plain/opt mọi macro OBF_* rỗng,
 * nên cả ba cấu hình có cùng ngữ nghĩa (build.py kiểm tra điều này trên 50 vector).
 */
#ifndef VERA_H
#define VERA_H

#include <stddef.h>
#include <stdint.h>

#define VERA_ERR ((uint64_t)0xFFFFFFFFFFFFFFFFull)

#define VERA_FN(name) \
    uint64_t name(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap)

/* Đọc/ghi 32-bit little-endian (macro, không phải hàm phụ). */
#define VERA_LD32(p) \
    ((uint32_t)(p)[0] | ((uint32_t)(p)[1] << 8) | ((uint32_t)(p)[2] << 16) | ((uint32_t)(p)[3] << 24))
#define VERA_ST32(p, v)                          \
    do {                                         \
        (p)[0] = (uint8_t)(v);                   \
        (p)[1] = (uint8_t)((v) >> 8);            \
        (p)[2] = (uint8_t)((v) >> 16);           \
        (p)[3] = (uint8_t)((v) >> 24);           \
    } while (0)

#ifdef VERA_OBF

/*
 * Opaque predicate phải sống sót qua -O2, nên dựa vào hai nguồn mà compiler
 * không chứng minh được giá trị:
 *   (1) biến volatile — mỗi lần đọc là một lần load thật từ bộ nhớ;
 *   (2) tính chất số học phụ thuộc đầu vào (bình phương số lẻ ≡ 1 mod 8,
 *       x*(x+1) luôn chẵn).
 * Hằng rác được chọn ngẫu nhiên, KHÔNG trùng hằng của thuật toán nổi tiếng nào.
 */
static volatile uint32_t vera_ok = 0x3C71u;   /* luôn bằng 0x3C71 lúc chạy */
static volatile uint32_t vera_nz = 0u;        /* luôn bằng 0 lúc chạy      */

/* Luôn đúng. */
#define OPQ_T(x) \
    (((((uint64_t)(x) | 1u) * ((uint64_t)(x) | 1u)) & 7u) == 1u && vera_ok == 0x3C71u)

/* Luôn sai. */
#define OPQ_F(x) \
    ((((uint64_t)(x) * ((uint64_t)(x) + 1u)) & 1u) != 0u || vera_nz != 0u)

/* Junk code: nhánh chết thay đổi v theo cách không bao giờ xảy ra. */
#define OBF_JUNK(v, x)                                                   \
    do {                                                                 \
        if (OPQ_F(x)) {                                                  \
            (v) = ((v) ^ ((uint64_t)(x) << 7)) * 0x2D6Bu + vera_ok;      \
            (v) ^= (v) >> 11;                                            \
        }                                                                \
    } while (0)

/* Bogus control flow: stmt thật chạy ở nhánh đúng, nhánh giả làm hỏng v. */
#define OBF_GUARD(v, x, ...)                                             \
    do {                                                                 \
        if (OPQ_T(x)) {                                                  \
            __VA_ARGS__;                                                      \
        } else {                                                         \
            (v) = ((v) + 0x51E3u) ^ ((uint64_t)(x) * 0x1F9u);            \
        }                                                                \
    } while (0)

/* Vòng lặp giả: chạy vera_nz (=0) lần. */
#define OBF_SPIN(v)                                                      \
    do {                                                                 \
        for (uint32_t vera_i = 0; vera_i < vera_nz; vera_i++)            \
            (v) = ((v) << 3) ^ ((v) >> 5) ^ vera_i;                      \
    } while (0)

#else /* plain, opt */

#define OBF_JUNK(v, x) do { } while (0)
#define OBF_GUARD(v, x, ...) do { __VA_ARGS__; } while (0)
#define OBF_SPIN(v) do { } while (0)

#endif /* VERA_OBF */

#endif /* VERA_H */
