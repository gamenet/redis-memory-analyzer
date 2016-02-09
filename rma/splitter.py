def has_numbers(value):
    return any(char.isdigit() for char in value)


def dict_build(indict, pre=None):
    pre = pre[:] if pre else []
    if len(indict):
        for key, value in indict.items():
            if len(value):
                for d in dict_build(value, pre=pre+[key]):
                    yield d
            else:
                yield pre + [key]
    else:
        yield pre


def map_part_to_glob(index, part):
    if index == 0:
        return part

    if not part or has_numbers(part):
        return '*'

    return part


class SimpleSplitter:
    def split(self, data, separator=":"):
        pass1 = map(lambda x: list(map_part_to_glob(i, y) for i, y in enumerate(x.split(separator))), data)
        pass2 = self.fold_to_tree(pass1)
        return self.unfold_to_list(pass2, separator)

    def fold_to_tree(self, pass1):
        tree = {}
        for item in pass1:
            t_len = len(item)
            if t_len not in tree:
                tree[t_len] = {}

            subtree = tree[t_len]
            deep = 0
            for part in item:
                deep += 1
                if '*' in subtree:
                    subtree = subtree['*']
                    continue

                if part in subtree:
                    subtree = subtree[part]
                    continue

                subtree[part] = {}
                if part != '*':
                    subtree = subtree[part]
                    continue

                if len(subtree) == 1:
                    continue

                if deep > 1:
                    self.merge_subtree(subtree)

                subtree = subtree[part]
        return tree

    @staticmethod
    def merge_subtree(subtree):
        all_keys = []
        for sub_part in subtree.keys():
            if sub_part != '*':
                all_keys.append(sub_part)
                subtree['*'].update(subtree[sub_part])
        for sub_part in all_keys:
            del subtree[sub_part]

    @staticmethod
    def unfold_to_list(tree, separator):
        res = set()

        for i, sub_tree in tree.items():
            for compound_key in dict_build(sub_tree):
                res.add(separator.join(compound_key))
        return res
