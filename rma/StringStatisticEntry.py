from rma.Redis import REDIS_ENCODING_RAW


class StringStatisticEntry:
    def __init__(self, used_bytes=0, free_bytes=0, r_obj=0, aligned=0, encoding=REDIS_ENCODING_RAW, value=""):
        self.usedBytes = used_bytes
        self.freeBytes = free_bytes
        self.rObj = r_obj
        self.aligned = aligned
        self.encoding = encoding
        self.value = value

    @property
    def total(self):
        return self.usedBytes + self.freeBytes


def get_redis_object_overhead():
    """
     typedef struct redisObject {
         unsigned type:4;
         unsigned encoding:4;
         unsigned lru:REDIS_LRU_BITS; /* lru time (relative to server.lruclock) */
         int refcount;
         void *ptr;
     } robj;

    :return:
    """
    return 4 + 4 + 8 + 8 + 8
