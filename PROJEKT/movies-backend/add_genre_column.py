import sqlite3

conn = sqlite3.connect('filmovi.db')
c = conn.cursor()
try:
    c.execute('ALTER TABLE movies ADD COLUMN genre TEXT')
    print("Polje 'genre' dodano!")
except Exception as e:
    print(f"Greška ili polje već postoji: {e}")
conn.commit()
conn.close()