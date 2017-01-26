import json
import sys


class JsonReporter:
    def print(self, data):
        output = {}

        for index, report in enumerate(data):
            if "nodes" in report:
                output['nodes'] = report['nodes']
            elif "keys" in report:
                output['keys'] = self.prepare_keys(report['keys'])
            elif "stat" in report:
                output['stat'] = self.prepare_stat(report['stat'])
            else:
                output["unsupported{0}".format(index)] = report

        print(json.dumps(output, indent=4, sort_keys=True))


    def prepare_keys(self, keys):
        data = []

        for values in keys['data']:
            entry = {}
            for index, value in enumerate(values):
                entry[keys['headers'][index]] = value

            data.append(entry)

        return data


    def prepare_stat(self, params):
        stat = {}

        for type, prop in params.items():
            data = []
            for row in prop['data']:
                entry = {}
                for index, value in enumerate(row):
                    entry[prop['headers'][index]] = value

                data.append(entry)
            stat[type] = data

        return stat
