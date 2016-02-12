#!/usr/bin/env python
import time
import logging
from optparse import OptionParser
from rma.application import RmaApplication

logging.basicConfig(level=logging.INFO)

VALID_TYPES = ("string", "hash", "list", "set", "zset")
VALID_MODES = ('all', 'scanner', 'ram', 'global')


def main():
    usage = """usage: %prog [options]

Example : %prog -m * --type hash"""

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
    parser.add_option("-l", "--limit", dest="limit", default="0", type="int",
                      help="Get max key matched by pattern")
    parser.add_option("-b", "--behaviour", dest="behaviour", default="all",
                      help="Specify application working mode")
    parser.add_option("-t", "--type", dest="types", action="append",
                      help="""Data types to include. Possible values are string, hash, list, set. Multiple types can be provided.
                    If not specified, all data types will be returned""")

    (options, args) = parser.parse_args()

    filters = {}
    if options.match:
        filters['match'] = options.match

    if options.behaviour:
        if options.behaviour not in VALID_MODES:
            raise Exception(
                'Invalid behaviour provided - %s. Expected one of %s' % (options.behaviour, (", ".join(VALID_TYPES))))
        else:
            filters['behaviour'] = options.behaviour

    if options.types:
        filters['types'] = []
        for x in options.types:
            if x not in VALID_TYPES:
                raise Exception('Invalid type provided - %s. Expected one of %s' % (x, (", ".join(VALID_TYPES))))
            else:
                filters['types'].append(x)

    app = RmaApplication(host=options.host, port=options.port, db=options.db,
                         password=options.password, match=options.match, limit=options.limit, filters=filters)

    start_time = time.clock()
    app.run()
    print("Done in %s seconds" % (time.clock() - start_time))

if __name__ == '__main__':
    main()
