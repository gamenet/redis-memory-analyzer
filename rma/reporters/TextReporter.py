from tabulate import tabulate


class TextReporter:
    def print(self, data):
        for out in data:
            print("\r\n")
            if isinstance(out, str):
                print(out)
            else:
                print(tabulate(out["data"], headers=out["headers"], floatfmt=".2f", tablefmt="pipe"))
