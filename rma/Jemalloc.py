# Small: All 2^n-aligned allocations of size 2^n will incur no additional overhead, due to how small allocations are aligned and packed.
# Small: [8], [16, 32, 48, ..., 128], [192, 256, 320, ..., 512], [768, 1024, 1280, ..., 3840]

# Large: The worst case size is half the chunk size, in which case only one allocation per chunk can be allocated.
# If the remaining (nearly) half of the chunk isn't otherwise useful for smaller allocations, the overhead will essentially be 50%.
# However, assuming you use a diverse mixture of size classes, the actual overhead shouldn't be a significant issue in practice.
# Large: [4 KiB, 8 KiB, 12 KiB, ..., 4072 KiB]

# Huge: Extra virtual memory is mapped, then the excess is trimmed and unmapped.  This can leave virtual memory holes,
# but it incurs no physical memory overhead.  Earlier versions of jemalloc heuristically attempted to optimistically map
# chunks without excess that would need to be trimmed, but it didn't save much system call overhead in practice, and I
# ripped the code out during a simplification pass.
# Huge: [4 MiB, 8 MiB, 12 MiB, ...


def next_power_of_2(n):
    """
    Return next power of 2 greater than or equal to n
    """
    return 2**(n-1).bit_length()


def is_power2(num):
    """
    states if a number is a power of two
    """
    return num != 0 and ((num & (num - 1)) == 0)

small_range = list(range(16, 128, 16)) + list(range(192, 512, 64)) + list(range(768, 3840, 256))
large_range = list(range(4096, 4194304, 4096))
huge_range = list(range(4194304, 536870912, 4194304))


def lower(search_list, size):
    return min(search_list, key=lambda x: abs(x - size))


class Jemalloc:
    @staticmethod
    def align(size):
        if size < 3840:
            if is_power2(size):
                return size

            return lower(small_range, size)
        elif size < 4194304:
            return lower(large_range, size)
        else:
            return lower(huge_range, size)

