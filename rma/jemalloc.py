from rma.helpers import *


class Jemalloc:
    """
    Small: All 2^n-aligned allocations of size 2^n will incur no additional overhead, due to how small allocations are
    aligned and packed.

    Small: [8], [16, 32, 48, ..., 128], [192, 256, 320, ..., 512], [768, 1024, 1280, ..., 3840]

    Large: The worst case size is half the chunk size, in which case only one allocation per chunk can be allocated.
    If the remaining (nearly) half of the chunk isn't otherwise useful for smaller allocations, the overhead will
    essentially be 50%. However, assuming you use a diverse mixture of size classes, the actual overhead shouldn't be a
    significant issue in practice.

    Large: [4 KiB, 8 KiB, 12 KiB, ..., 4072 KiB]

    Huge: Extra virtual memory is mapped, then the excess is trimmed and unmapped.  This can leave virtual memory holes,
    but it incurs no physical memory overhead.  Earlier versions of jemalloc heuristically attempted to optimistically
    map chunks without excess that would need to be trimmed, but it didn't save much system call overhead in practice.

    Huge: [4 MiB, 8 MiB, 12 MiB, ..., 512 MiB]
    """
    @staticmethod
    def align(size):
        if size <= 4096:
            # Small
            if is_power2(size):
                return size
            elif size < 128:
                return min_ge(range(16, 128 + 1, 16), size)
            elif size < 512:
                return min_ge(range(192, 512 + 1, 64), size)
            else:
                return min_ge(range(768, 4096 + 1, 256), size)
        elif size < 4194304:
            # Large
            return min_ge(range(4096, 4194304 + 1, 4096), size)
        else:
            # Huge
            return min_ge(range(4194304, 536870912 + 1, 4194304), size)
