import sqlite3

conn = sqlite3.connect('filmovi.db')
c = conn.cursor()
c.execute('DELETE FROM ratings')  # obriši sve ocjene
c.execute('DELETE FROM movies')   # obriši sve filmove
conn.commit()
conn.close()
print("Svi filmovi i ocjene su obrisani!")