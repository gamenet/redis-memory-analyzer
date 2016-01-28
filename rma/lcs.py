from collections import defaultdict
import sys


def ptable(m, n, table):
   for i in range(m):
       line = ""
       for j in range(n):
           line += str(table[i, j]) + " "
       print(line)


def lcs(x, y):
    table = defaultdict(int)
    n = len(x)
    m = len(y)

    for i in range(n):
        for j in range(m):
            if x[i] == y[j]:
                table[i, j] = table[i-1, j-1]+1
            else:
                table[i, j] = max(table[i-1, j], table[i, j-1])

    return table


def mlcs(strings):
    strings = list(set(strings))
    tables = dict()
    for i in range(1, len(strings)):
        x = strings[i]
        for y in strings[:i]:
            lcsxy = lcs(x, y)
            tables[x,y] = lcsxy

    def rec(indexes):
        for v in indexes.values():
            if v < 0:
                return ""
        same = True
        for i in range(len(strings)-1):
            x = strings[i]
            y = strings[i+1]
            same &= x[indexes[x]] == y[indexes[y]]
        if same:
            x = strings[0]
            c = x[indexes[x]]
            for x in strings:
                indexes[x] -= 1
            return rec(indexes) + c
        else:
            v = -1
            ind = None
            for x in strings:
                indcopy = indexes.copy()
                indcopy[x] -= 1
                icv = valueat(indcopy)
                if icv > v:
                    ind = indcopy
                    v = icv
            indexes = ind
            return rec(indexes)

    def valueat(indexes):
        m = 12777216
        for i in range(1, len(strings)):
            x = strings[i]
            for y in strings[:i]:
                lcsxy = tables[x,y]
                p = lcsxy[indexes[x],indexes[y]]
                m = min(m, p)
        return m

    indexes = dict()
    for x in strings:
        indexes[x] = len(x) - 1
    return rec(indexes)


def check(string, seq):
    i = 0
    j = 0
    while i < len(string) and j < len(seq):
        if string[i] == seq[j]:
            j += 1
        i += 1
    return len(seq) - j


def checkall(strings, seq):
    for x in strings:
        a = check(x, seq)
        if not a == 0:
            print(x, seq, a)
            return False
    return True