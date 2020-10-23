conn = db.sqlite.create_table_from_data("test_01", self.configuration["data"])
cur = conn.cursor()
cur.execute("SELECT * FROM test_01")
data_from_db = []
for row in cur.fetchall():
    data_from_db.append(dict(row))
pprint(data_from_db)
pprint(self.configuration["data"])
if data_from_db == self.configuration["data"]:
    return "OK"
