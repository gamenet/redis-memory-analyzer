import sys
import statistics

from rma.Redis import *
from rma.Scanner import Scanner

from tabulate import tabulate
from tqdm import tqdm
from redis.exceptions import ConnectionError, ResponseError


def prepare_data_set(entries):
    useful_bytes = 0
    total_bytes = 0
    total_bytes_aligned = 0
    nums = []

    for item in entries:
        useful_bytes += item.usedBytes
        total_bytes += item.total
        total_bytes_aligned += item.aligned
        nums.append(item.usedBytes)

    return [useful_bytes, total_bytes, total_bytes_aligned, float(total_bytes_aligned) / useful_bytes]


def prepare_len_data_set(entries):
    nums = list(map(lambda x: x.usedBytes, entries))
    if len(nums) == 1:
        return [nums[0], nums[0], nums[0], 0]

    return [min(nums), max(nums), statistics.mean(nums), statistics.stdev(nums)]


def print_stat(match, data, patterns):
    tables = dict(ram=[], lens=[])
    for pattern in patterns:
        data_keys = []
        data_values = []
        pattern_count = 0
        for item in data:
            if not item['key'].value.startswith(pattern):
                continue
            pattern_count += 1
            data_keys.append(item['key'])
            data_values.append(item['value'])

        tables["ram"].append([pattern + '*', pattern_count] + prepare_data_set(data_keys) + prepare_data_set(data_values))
        tables["lens"].append(
            [pattern + '*', pattern_count] + prepare_len_data_set(data_keys) + prepare_len_data_set(data_values))

    tables["ram"].sort(key=lambda x: x[1], reverse=True)
    tables["lens"].sort(key=lambda x: x[1], reverse=True)

    print("\r\nUsing match: " + match)
    print("\r\nMemory data")
    print(tabulate(tables["ram"],
                   headers=["Pattern", "Count", "Key Useful", "Key Total", "Key Aligned", "Key Ratio", "Value Useful",
                            "Value Total", "Value Aligned", "Value Ratio"], floatfmt=".2f", tablefmt="pipe"))

    print("\r\nPer key data")
    print(tabulate(tables["lens"], headers=["Pattern", "Count", "Key min", "Key max", "Key avg", "Key stdev",
                                        "Value min", "Value max", "Value avg", "Value stdev"],
                   floatfmt=".2f", tablefmt="pipe"))


def connect_to_redis(host, port, db=0, password=None):
    try:
        redis = RmaRedis(host=host, port=port, db=db, password=password)
        if not check_redis_version(redis):
            sys.stderr.write('This script only works with Redis Server version 2.6.x or higher\n')
            sys.exit(-1)
    except ConnectionError as e:
        sys.stderr.write('Could not connect to Redis Server : %s\n' % e)
        sys.exit(-1)
    except ResponseError as e:
        sys.stderr.write('Could not connect to Redis Server : %s\n' % e)
        sys.exit(-1)
    return redis


def check_redis_version(redis):
    server_info = redis.info()
    version_str = server_info['redis_version']
    version = tuple(map(int, version_str.split('.')))

    if version[0] > 2 or (version[0] == 2 and version[1] >= 6):
        return True
    else:
        return False


class RmaApplication:
    def run(self, options):
        r = connect_to_redis(host=options['host'], port=options['port'])
        progress = tqdm(total=r.total_keys())

        scanner = Scanner(r=r, match=options['match'])
        res = scanner.scan(callback=lambda x: progress.update())

        print_stat(options['match'], res["strings"]['stat'], res["strings"]['patterns'])
