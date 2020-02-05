#!/usr/bin/env python
import time
import logging
import sys
from argparse import ArgumentParser, HelpFormatter
from rma.application import RmaApplication

logging.basicConfig(level=logging.INFO)

VALID_TYPES = ("string", "hash", "list", "set", "zset")
VALID_MODES = ('all', 'scanner', 'ram', 'global')


class CustomHelpFormatter(HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string


def parser_formatter(prog):
    return CustomHelpFormatter(prog)


def main():
    description = """RMA is used to scan Redis key space in and aggregate memory usage statistic by key patterns."""

    parser = ArgumentParser(prog='rma', description=description, formatter_class=parser_formatter)
    parser.add_argument("-s", "--server",
                        dest="host",
                        default="127.0.0.1",
                        help="Redis Server hostname. Defaults to 127.0.0.1")
    parser.add_argument("-p", "--port",
                        dest="port",
                        default=6379,
                        type=int,
                        help="Redis Server port. Defaults to 6379")
    parser.add_argument("-a", "--password",
                        dest="password",
                        help="Password to use when connecting to the server")
    parser.add_argument("-d", "--db",
                        dest="db",
                        default=0,
                        help="Database number, defaults to 0")
    parser.add_argument("--ssl",
                        dest="ssl",
                        action="store_true",
                        help="If argument is specified, SSL will be used for making connection")
    parser.add_argument("-m", "--match",
                        dest="match",
                        default="*",
                        help="Keys pattern to match")
    parser.add_argument("-l", "--limit",
                        dest="limit",
                        default="0",
                        type=int,
                        help="Get max key matched by pattern")
    parser.add_argument("-b", "--behaviour",
                        dest="behaviour",
                        default="all",
                        help="Specify application working mode. Allowed values are " + ', '.join(VALID_MODES))
    parser.add_argument("-t", "--type",
                        dest="types",
                        action="append",
                        help="""Data types to include. Possible values are string, hash, list, set.
                              Multiple types can be provided. If not specified, all data types will be returned.
                              Allowed values are """ + ', '.join(VALID_TYPES))
    parser.add_argument("-f", "--format",
                        dest="format",
                        default="text",
                        help="Output type format: json or text (by default)")
    parser.add_argument("-x", "--separator",
                        dest="separator",
                        default=":",
                        help="Specify namespace separator. Default is ':'")

    options = parser.parse_args()

    filters = {}
    if options.behaviour:
        if options.behaviour not in VALID_MODES:
            raise Exception(
                    'Invalid behaviour provided - %s. Expected one of %s' % (
                        options.behaviour, (", ".join(VALID_TYPES))))
        else:
            filters['behaviour'] = options.behaviour

    if options.types:
        filters['types'] = []
        for x in options.types:
            if x not in VALID_TYPES:
                raise Exception('Invalid type provided - %s. Expected one of %s' % (x, (", ".join(VALID_TYPES))))
            else:
                filters['types'].append(x)

    app = RmaApplication(host=options.host, port=options.port, db=options.db, password=options.password,
                         ssl=options.ssl, match=options.match, limit=options.limit, filters=filters, format=options.format,
                         separator=options.separator)

    start_time = time.clock()
    app.run()

    sys.stderr.write("\r\nDone in %s seconds" % (time.clock() - start_time))

if __name__ == '__main__':
    main()
