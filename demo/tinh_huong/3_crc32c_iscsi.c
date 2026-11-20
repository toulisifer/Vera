/* Tình huống 3 — CRC-32C (Castagnoli), dùng thật trong iSCSI, ext4, Btrfs, SSE4.2.
 * Thực tế: một thuật toán CÓ TÊN, rất giống CRC-32, chỉ khác đa thức (0x82F63B78 thay cho 0xEDB88320).
 * Đáp án: CRC-32C. Nếu AI gọi nhầm là "CRC-32", VeRA chạy oracle CRC-32 ra số khác → bắt được.
 * Nếu AI gọi đúng "CRC-32C", oracle CRC-32C khớp 50/50 → verified.
 */
#include "vera.h"

VERA_FN(fn_99)
{
    (void)arg; (void)out; (void)out_cap;
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= in[i];
        for (int k = 0; k < 8; k++)
            crc = (crc >> 1) ^ (0x82F63B78u & (0u - (crc & 1u)));
    }
    return crc ^ 0xFFFFFFFFu;
}
