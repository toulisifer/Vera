/* Ví dụ hàm C tự viết cho demo trực tiếp (chế độ 3).
 * Sửa tùy ý, nhưng giữ dòng #include và chữ ký VERA_FN(fn_99).
 * Hàm này: băm kiểu "nhân-cộng" với hằng tự chọn — không phải thuật toán có tên.
 */
#include "vera.h"

VERA_FN(fn_99)
{
    uint32_t h = 0x2F6A1C3Bu;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++)
        h = (h ^ in[i]) * 0x01000197u;
    return h;
}
