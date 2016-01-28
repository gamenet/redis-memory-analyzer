Redis Memory Analyzer
===

Cтроковые ключи:
- количество таких ключей
- выделение маски ключа
- средняя /минимальеная/средняя/медиана по ключу или типу
- затраты на строку ключа
- затраты на значение
- данные о типах кодировки в котором лежит значение ключа

### Installing rma

Pre-Requisites :

1. python >= 3.4 and pip.
2. redis-py.

To install from PyPI (recommended) :

    pip install rma

To install from source :

    git clone https://github.com/gamenet/redis-memory-analyzer
    cd redis-memory-analyzer
    sudo python setup.py install


### Why doesn't reported memory match actual memory used?

The memory reported by this tool is approximate. In general, the reported memory should be within 10% of what is reported by [info](http://redis.io/commands/info).

Also note that the tool does not (and cannot) account for the following -
* Memory used by allocator metadata
* Memory used for pub/sub
* Redis process internals (like shared objects)

## License

rma is licensed under the MIT License. See [LICENSE](https://github.com/gamenet/redis-memory-analyzer/blob/master/LICENSE)

