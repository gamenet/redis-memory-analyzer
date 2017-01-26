from tabulate import tabulate


class TextReporter:
    def print(self, data):

        for report in data:
            if "nodes" in report:
                self.print_nodes(report['nodes'])
            elif "keys" in report:
                self.print_keys(report['keys'])
            elif "stat" in report:
                self.print_keys_stat(report['stat'])
            else:
                self.print_unsupported(report)


    def print_nodes(self, nodes):
        values = []
        print("\r\nNodes\r\n")

        for node in nodes:
            for key, value in node.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        values.append(["{0} {1}".format(key, sub_key), sub_value])

            for key, value in node.items():
                if not isinstance(value, dict):
                    values.append([key, value])

            print(tabulate(values, ["Stat", "Value"], floatfmt=".2f", tablefmt="pipe"))


    def print_keys(self, keys):
        print("\r\nKeys by types\r\n")
        print(tabulate(keys['data'], keys['headers'], floatfmt=".2f", tablefmt="pipe"))


    def print_keys_stat(self, keys):
        print("\r\nKeys statistic")

        for type, prop in keys.items():
            print("\r\nStat by <{0}>\r\n".format(type))
            print(tabulate(prop['data'], prop['headers'], floatfmt=".2f", tablefmt="pipe"))


    def print_unsupported(self, data):
        print("\r\nUnsupported block")
        print(data)
