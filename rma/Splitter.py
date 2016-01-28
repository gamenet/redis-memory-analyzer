class SplitNode:
    def __init__(self, count, name, parent, nodes):
        self.count = count
        self.name = name
        self.parent = parent
        self.nodes = nodes


# Кейс, когда в ветке дерева вариантивная часть листа в единственном экземпляре не должна вырезаться - это не маска.

class Splitter:
    def split(self, data):
        acc = {}
        for item in data:
            self.split_by_parts(acc, item)

        return self.extract_patterns(acc)

    def split_by_parts(self, result, data, parent=None):
        if not data:
            return result

        entry = data.pop(0)
        if not entry:
            return result

        if entry not in result:
            result[entry] = SplitNode(count=1, name=entry, parent=parent, nodes={})
        else:
            result[entry].count += 1

        return self.split_by_parts(result[entry].nodes, data, result[entry])

    def extract_patterns(self, data):
        result = {}
        self._extract_patterns(result, data)
        return result.keys()

    def _extract_patterns(self, acc, data):
        for key, item in data.items():
            if len(item.nodes) == 0:
                if item.parent is None:
                    acc[key] = 1
                else:
                    rec_key = key if item.count > 1 else ""
                    rec_parent = item.parent

                    while rec_parent is not None:
                        rec_key = rec_parent.name + ":" + rec_key
                        rec_parent = rec_parent.parent

                    acc[rec_key] = 1
            else:
                self._extract_patterns(acc, item.nodes)