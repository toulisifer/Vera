/* Tình huống 2 — CRC-32 viết kiểu thư viện zlib (dùng bảng tra 256 phần tử).
 * Thực tế: đây là cách CRC-32 được cài trong zlib, libpng, 7-Zip... — khác bản trong corpus (fn_01 tính
 * từng bit), nên hằng 0xEDB88320 không còn nằm trong lệnh máy mà nằm rải trong một bảng.
 * Đáp án: CRC-32 chuẩn (IEEE 802.3). AI nói "CRC-32" là ĐÚNG — VeRA phải xác nhận, không bắt oan.
 */
#include "vera.h"

static uint32_t table[256];

VERA_FN(fn_99)
{
    (void)arg; (void)out; (void)out_cap;
    if (!table[1])
        for (uint32_t n = 0; n < 256; n++) {
            uint32_t c = n;
            for (int k = 0; k < 8; k++)
                c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
            table[n] = c;
        }
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; i++)
        crc = table[(crc ^ in[i]) & 0xFF] ^ (crc >> 8);
    return crc ^ 0xFFFFFFFFu;
}
