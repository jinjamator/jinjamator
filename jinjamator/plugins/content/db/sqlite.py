import sqlite3


def create_table_from_data(table_name, data, db_path=":memory:"):
    """Create a sqlite3 table from a python datastructure

    :param table_name: Name of the created table/
    :type table_name: ``str``
    :param data: Python list of dictionaries
    :type data: ``list of dict``
    :param db_path: Path to the sqlite database file, defaults to ':memory:'
    :type db_path: str, optional
    :return: sqlite connection handle
    :rtype: ``sqlite3.Connection``
    """
    try:
        conn = sqlite3.connect(db_path)

    except Exception as e:
        log.error(e)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    cols = ",".join(["'{0}' TEXT".format(i) for i in list(data[0].keys())])
    c.execute("create table if not exists {0}({1})".format(table_name, cols))

    for row in data:
        keys = []
        values = []
        for k, v in row.items():
            keys.append("'{0}'".format(k))
            values.append("'{0}'".format(v.replace("'", "''")))

        c.execute("insert into {0} values({1})".format(table_name, ",".join(values)))
    conn.commit()
    return conn
