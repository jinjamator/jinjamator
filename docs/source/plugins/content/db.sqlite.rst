db.sqlite
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: db.sqlite.create_table_from_data(table_name, data, db_path=':memory:'):

    Create a sqlite3 table from a python datastructure

    :param table_name: Name of the created table/
    :type table_name: ``str``
    :param data: Python list of dictionaries
    :type data: ``list of dict``
    :param db_path: Path to the sqlite database file, defaults to ':memory:'
    :type db_path: str, optional
    :return: sqlite connection handle
    :rtype: ``sqlite3.Connection``
    


