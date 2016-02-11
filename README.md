Redis Memory Analyzer
===

RMA is a console tool to scan Redis key space in real time and aggregate memory usage statistic by key patterns. You may
use this tools without maintenance on production servers. You can scanning by all or selected Redis types such as "string",
"hash", "list", "set", "zset" and use matching pattern as you like. RMA try to discern key names by patterns, for example
if you have keys like 'user:100' and 'user:101' application would pick out common pattern 'user:*' in output so you can
analyze most memory distressed data in your instance.

### Installing rma

Pre-Requisites :

1. python >= 3.4 and pip.
2. redis-py.

To install from PyPI (recommended) :

    pip install rma

To install from source :

    git clone https://github.com/gamenet/redis-memory-analyzer
    cd redis-memory-analyzer
    sudo python setup.py install

## Running

After install used it from console:

```
>rma --help
Usage: rma-script.py [options]

Example : rma-script.py -m * --type hash

Options:
  -h, --help                            Show this help message and exit
  -s HOST, --server=HOST                Redis Server hostname. Defaults to 127.0.0.1
  -p PORT, --port=PORT                  Redis Server port. Defaults to 6379
  -a PASSWORD, --password=PASSWORD      Password to use when connecting to the server
  -d DB, --db=DB                        Database number, defaults to 0
  -m MATCH, --match=MATCH               Keys pattern to match
  -l LIMIT, --limit=LIMIT               Get max key matched by pattern
  -b BEHAVIOUR, --behaviour=BEHAVIOUR   Specify application working mode
  -t TYPES, --type=TYPES                Data types to include. Possible values are string,
                                        hash, list, set. Multiple types can be provided.
                                        If not specified, all data types will be returned
```

If you have large database try running first with `--limit` option to run first limited amount of keys. Also run with `--types`
 to limit only specified Redis types in large database. Not this tool has performance issues - call encoding for individual
 keys instead if batch queue with LUA (like in scanner does). So this option may be very useful.

## Internals

RMA shows statistics separated by types. You can choose what kind of data would be aggregated from Redis node using
`-b (--behaviour)` option as console argument.

### Global output

The global data is some Redis server statistics which helps you to understand other data from this tools:

```
| Stat                             | Value          |
|:---------------------------------|:---------------|
| Total keys in db                 | 28979          |
| RedisDB key space overhead       | 790528         |
| Used `set-max-intset-entries`    | 512            |
| ....                             | ...            |
| Info `total_system_memory`       | 3190095872     |
| ....                             | ...            |
```

The one of interesting things here is "RedisDB key space overhead". The amount of memory used Redis to store key space
data. If you have lots of keys in your Redis instance this actually shows your overhead for this.

### Key types

This table helps then you do not know actually that kind of keys stored in your Redis database. For example then DevOps or
system administrator want to understand what kind of keys stored in Redis instance. Which data structure is most used in
system. This also helps if you are new to some big project - this kind of `SHOW ALL TABLES` request :)

```
| Match                 |   Count | Type   | %      |
|:----------------------|--------:|:-------|:-------|
| job:*                 |    5254 | hash   | 18.13% |
| game:privacy:*        |    2675 | hash   | 9.23%  |
| user:*                |    1890 | hash   | 6.52%  |
| group:*               |    1885 | set    | 6.50%  |

```

### Data related output

All output separated by keys and values statistics. This division is used because:
1. Keys of any type in Redis actually stored in RedisDB internal data structure based on dict (more about this on [RedisPlanet](http://redisplanet.com/)).
2. This type of data specially important in Redis instances with lots of keys.

```
| Match                         | Count | Useful |   Real | Ratio | Encoding                     | Min | Max |   Avg |
|:------------------------------|------:|-------:|-------:|------:|:-----------------------------|----:|----:|------:|
| event:data:*                  |  1198 |  17970 |  76672 |  4.27 | embstr [50.0%] / raw [50.0%] |  15 |  71 | 41.20 |
| mm:urllist:*                  |   524 |   7648 |  33536 |  4.38 | embstr [100.0%]              |  12 |  15 | 14.60 |
| Provider:ParallelForm:*:*:*:* |   459 |  43051 |  66096 |  1.54 | raw [100.0%]                 |  92 |  94 | 93.79 |
| user:spamblocked:dialy:post:* |    48 |   2208 |   4608 |  2.09 | raw [100.0%]                 |  46 |  46 | 46.00 |
| ...                           |   ... |    ... |    ... |   ... |                          ... | ... | ... |   ... |
| Total:                        |  2432 |  80493 | 200528 |  0.00 |                              |   0 |   0 |  0.00 |
```

So you can see count of keys matching given pattern, expected (by developer) and real memory with taking into account the
Redis data structures and allocator overhead. Ratio and encoding distribution min/max/avg len of key. For example in sample
above keys some keys encoded as `raw` (sds string). Each sds encoded string:

1. Has useful payload
2. Has sds string header overhead
3. Has `redis object` overhead
4. The Redis implementation during memory allocation would be align(redis object) + align(sds header + useful payload)

In x64 instance of Redis key `event:data:f1wFFqgqqwgeg` (24 byte len) actually would use 24 bytes payload bytes, 9 bytes sds header
and 32 bytes in r_obj (`redis object`). So we may think this would use 65 bytes. But after jemalloc allocator align it
this 24 byte (65 byte data with Redis internals) would use 80 bytes - in ~3,3 more times as you expect (`Ratio`` value
in table).

Not we can look at values. All values output individual by Redis type. Each type has they own limitations so here is
some common data for each type and some unique. The `strings` data type value same as keys output above. The only one
 difference is `Free` field which shows unused but allocated memory by SDS strings in `raw` encoding.

So for example look at output for `HASH` values:

```
| Match                 | Count | Avg field count | Key mem |   Real | Ratio | Value mem |   Real |    Ratio |   System | Encoding         | Total mem |  Total aligned |
|:----------------------|------:|----------------:|--------:|-------:|------:|----------:|-------:|---------:|---------:|:-----------------|----------:|---------------:|
| job:*                 |  5254 |            9.00 |  299485 | 619988 |  2.07 |    685451 | 942984 |     1.38 |  1345024 | ziplist [100.0%] |    984936 |        2907996 |
| LIKE:*                |  1890 |            1.02 |    5744 |  30262 |  5.27 |      1932 |  15432 |     7.99 |    91344 | ziplist [100.0%] |      7676 |         137038 |
| game:*:count:*        |  1231 |            1.00 |    7386 |  19696 |  2.67 |      1234 |   9848 |     7.98 |    59088 | ziplist [100.0%] |      8620 |          88632 |
| LIKE:game:like:*      |  1207 |            1.00 |    3621 |  19312 |  5.33 |      1210 |   9656 |     7.98 |    57936 | ziplist [100.0%] |      4831 |          86904 |
| integration:privacy:* |   530 |            3.00 |   20140 |  33920 |  1.68 |         0 |  25440 | 25440.00 |    42400 | ziplist [100.0%] |     20140 |         101760 |
```

Look at `job:*` hashes. This instance contains 5254 such keys with 9 fields each. Looks like this data has regular structure
like python tuple. This means you can change data structure of this data from Redis `hash` to `list` and use 2 times less
memory then now. Why do this? Now you `job:*` hash uses ~3,2 times more memory as you developers expect.

### Why doesn't reported memory match actual memory used?

The memory reported by this tool is approximate. In general, the reported memory should be within 10% of what is reported by [info](http://redis.io/commands/info).

Also note that the tool does not (and cannot) account for the following -
* Memory used by allocator metadata (it is actually not possible without `c`)
* Memory used for pub/sub (no any commands in Redis for that)
* Redis process internals (like shared objects)


### Known issues

1. `Skiplist` (`zset` actually) encoding actually not realized.
2. `Quicklist` now calculated as `ziplist`.
3. SDS strings from redis 3.2 (optimized headers) not implemented. Now used fixed 9 bytes header.


### Whats next?

Now we use this tools as awesome helper. We most used data structures in our Redis instances is `hash` and `list`. After
upgradings our servers to Redis 3.2.x planning to fix known issues. Be glad to know that are you think about this tool.
In my dreams this tools should used as `redis-lint` tools which can say you `Hey, change this from this to this and save
30% of RAM`, `Hey, you are using PHP serializer for strings - change to msgpack and save 15% of RAM` and so on.

## License

This application was developed for using in [GameNet](https://gamenet.ru/) project as part of Redis memory optimizations
 and analise. RMA is licensed under the MIT License. See [LICENSE](https://github.com/gamenet/redis-memory-analyzer/blob/master/LICENSE)
