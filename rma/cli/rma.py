#!/usr/bin/env python

import os
import sys

from optparse import OptionParser
from rma.RmaApplication import RmaApplication

VALID_TYPES = ("hash", "set", "string", "list", "sortedset")

def main():
    usage = """usage: %prog [options] /path/to/dump.rdb

Example : %prog --command json -k "user.*" /var/redis/6379/dump.rdb"""

    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--server", dest="host", default="127.0.0.1",
                      help="Redis Server hostname. Defaults to 127.0.0.1")
    parser.add_option("-p", "--port", dest="port", default=6379, type="int",
                      help="Redis Server port. Defaults to 6379")
    parser.add_option("-a", "--password", dest="password",
                      help="Password to use when connecting to the server")
    parser.add_option("-d", "--db", dest="db", default=0,
                      help="Database number, defaults to 0")
    parser.add_option("-m", "--match", dest="match", default="*",
                      help="Keys pattern to match")
    parser.add_option("-l", "--limit", dest="limit", default="0",
                      help="Get max key matched by pattern")
    parser.add_option("-t", "--type", dest="types", action="append",
                      help="""Data types to include. Possible values are string, hash, list. Multiple typees can be provided.
                    If not specified, all data types will be returned""")

    (options, args) = parser.parse_args()

    # if len(args) == 0:
    #     parser.error("Redis RDB file not specified")
    #     return

    filters = {}
    if options.match:
        filters['match'] = options.match

    if options.types:
        filters['types'] = []
        for x in options.types:
            if not x in VALID_TYPES:
                raise Exception('Invalid type provided - %s. Expected one of %s' % (x, (", ".join(VALID_TYPES))))
            else:
                filters['types'].append(x)

    app = RmaApplication({'host': options.host, 'port': options.port, 'match': options.match, 'limit': options.limit})
    app.run()


if __name__ == '__main__':
    main()
