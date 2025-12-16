import sqlite3

conn = sqlite3.connect('mishnayot.db')
cursor = conn.cursor()

creat_mishnayot_table="""CREATE TABLE IF NOT EXISTS mishnayot (
  id INT NOT NULL,
  masechet CHAR(15) NOT NULL,
  daf CHAR(10) NOT NULL,
  mishna TEXT NOT NULL
);"""

creat_citations_table="""CREATE TABLE IF NOT EXISTS citations (
  id INT NOT NULL,
  masechet CHAR(15) NOT NULL,
  daf CHAR(10) NOT NULL,
  citation TEXT NOT NULL
);"""

creat_matched_table="""CREATE TABLE IF NOT EXISTS matched(
   id INT NOT NULL,
   masechet CHAR(15) NOT NULL,
   mishna_daf CHAR(10) NOT NULL,
   citation_id INT NOT NULL,
   citation_daf CHAR(10) NOT NULL
);"""

cursor.execute(creat_mishnayot_table)
cursor.execute(creat_citations_table)
cursor.execute(creat_matched_table)
conn.commit()

def insert(masechet,table, id, daf, text):
    query = f"INSERT INTO {table} (id,masechet,daf, {'mishna' if table == 'mishnayot' else 'citation'}) VALUES (?, ?, ?, ?)"
    cursor.execute(query, (id,masechet,daf, text))
    conn.commit()

def insert_match(id,masechet,daf_m,c_id,daf_c):
    query = f"INSERT INTO matched (id,masechet,mishna_daf,citation_id,citation_daf) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(query, (id,masechet,daf_m,c_id,daf_c))
    conn.commit()