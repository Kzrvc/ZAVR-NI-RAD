import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    # Tablica za korisnike
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Tablica za filmove (DODANO: genre)
    c.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            omdb_id TEXT UNIQUE,
            poster_url TEXT,
            description TEXT,
            genre TEXT
        )
    ''')
    # Tablica za ocjene
    c.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            movie_id INTEGER,
            rating INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
    ''')
    # Tablica za preference
    c.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            preferences TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, email, password):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    if result and check_password_hash(result[0], password):
        return True
    return False

def add_movie(title, omdb_id=None, poster_url=None, description=None, genre=None):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO movies (title, omdb_id, poster_url, description, genre) VALUES (?, ?, ?, ?, ?)',
                  (title, omdb_id, poster_url, description, genre))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_movies():
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    c.execute('SELECT id, title, omdb_id, poster_url, description, genre FROM movies')
    movies = [
        {
            'id': row[0],
            'title': row[1],
            'omdb_id': row[2],
            'poster_url': row[3],
            'description': row[4],
            'genre': row[5]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return movies

def add_rating(username, movie_id, rating):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    # Pronađi user_id prema usernameu
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return False, "Korisnik ne postoji."
    user_id = user[0]

    # Provjeri je li već ocijenio taj film
    c.execute('SELECT id FROM ratings WHERE user_id = ? AND movie_id = ?', (user_id, movie_id))
    if c.fetchone():
        conn.close()
        return False, "Već si ocijenio ovaj film."

    # Dodaj ocjenu
    try:
        c.execute('INSERT INTO ratings (user_id, movie_id, rating) VALUES (?, ?, ?)', (user_id, movie_id, rating))
        conn.commit()
        return True, "Ocjena spremljena!"
    except sqlite3.IntegrityError:
        return False, "Neuspješno spremanje ocjene."
    finally:
        conn.close()

def get_movie_ratings(movie_id):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    # Sve ocjene za film
    c.execute('''
        SELECT u.username, r.rating
        FROM ratings r
        JOIN users u ON r.user_id = u.id
        WHERE r.movie_id = ?
    ''', (movie_id,))
    ratings = [{"username": row[0], "rating": row[1]} for row in c.fetchall()]
    # Prosjek
    c.execute('SELECT AVG(rating) FROM ratings WHERE movie_id = ?', (movie_id,))
    avg = c.fetchone()[0]
    conn.close()
    return {
        "average": round(avg, 2) if avg is not None else None,
        "ratings": ratings
    }

def delete_movie(movie_id):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    # Prvo brišemo ocjene za taj film zbog foreign key constraints
    c.execute('DELETE FROM ratings WHERE movie_id = ?', (movie_id,))
    # Zatim brišemo film
    c.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

def edit_movie(movie_id, title=None, omdb_id=None, poster_url=None, description=None, genre=None):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    # Gradimo dinamički upit ovisno o poslanim podacima
    fields = []
    values = []
    if title is not None:
        fields.append("title = ?")
        values.append(title)
    if omdb_id is not None:
        fields.append("omdb_id = ?")
        values.append(omdb_id)
    if poster_url is not None:
        fields.append("poster_url = ?")
        values.append(poster_url)
    if description is not None:
        fields.append("description = ?")
        values.append(description)
    if genre is not None:
        fields.append("genre = ?")
        values.append(genre)
    if not fields:
        conn.close()
        return False  # Nema ništa za izmijeniti
    values.append(movie_id)
    sql = f"UPDATE movies SET {', '.join(fields)} WHERE id = ?"
    c.execute(sql, values)
    conn.commit()
    updated = c.rowcount
    conn.close()
    return updated > 0

def get_all_movies_with_avg():
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    c.execute('''
        SELECT m.id, m.title, m.omdb_id, m.poster_url, m.description, m.genre,
               AVG(r.rating) as avg_rating
        FROM movies m
        LEFT JOIN ratings r ON m.id = r.movie_id
        GROUP BY m.id
    ''')
    movies = []
    for row in c.fetchall():
        movies.append({
            'id': row[0],
            'title': row[1],
            'omdb_id': row[2],
            'poster_url': row[3],
            'description': row[4],
            'genre': row[5],
            'average_rating': round(row[6], 2) if row[6] is not None else None
        })
    conn.close()
    return movies

def get_recommendations_for_user(username, top_n=10):
    # collaborative filtering na osnovi zajedničkih lajkova
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()

    # 1. Tko je korisnik?
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return []
    user_id = user[0]

    # 2. Filmovi koje je korisnik već lajkao
    c.execute('SELECT movie_id FROM ratings WHERE user_id = ?', (user_id,))
    liked_movies = set(row[0] for row in c.fetchall())
    if not liked_movies:
        conn.close()
        return []

    # 3. Svi drugi korisnici koji su lajkali iste filmove
    c.execute('SELECT user_id FROM ratings WHERE movie_id IN ({seq}) AND user_id != ?'.format(
        seq=','.join(['?']*len(liked_movies))), tuple(liked_movies) + (user_id,))
    similar_users = set(row[0] for row in c.fetchall())
    if not similar_users:
        conn.close()
        return []

    # 4. Filmovi koje su lajkali ti korisnici, a ovaj korisnik nije
    c.execute('SELECT movie_id, COUNT(*) as cnt FROM ratings WHERE user_id IN ({seq}) AND movie_id NOT IN ({seq2}) GROUP BY movie_id ORDER BY cnt DESC LIMIT ?'.format(
        seq=','.join(['?']*len(similar_users)),
        seq2=','.join(['?']*len(liked_movies))
    ), tuple(similar_users)+tuple(liked_movies)+(top_n,))
    rec_movies = [row[0] for row in c.fetchall()]
    if not rec_movies:
        conn.close()
        return []

    # 5. Dohvati podatke o filmovima
    qmarks = ','.join(['?']*len(rec_movies))
    c.execute(f"SELECT id, title, omdb_id, poster_url, description, genre FROM movies WHERE id IN ({qmarks})", tuple(rec_movies))
    films = [
        {
            'id': row[0],
            'title': row[1],
            'omdb_id': row[2],
            'poster_url': row[3],
            'description': row[4],
            'genre': row[5]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return films

def get_user_rated_movies(username):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username=?', (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return []
    user_id = user[0]
    c.execute('SELECT movie_id FROM ratings WHERE user_id=?', (user_id,))
    rated = [row[0] for row in c.fetchall()]
    conn.close()
    return rated

def get_all_ratings():
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    c.execute('''
        SELECT u.username, r.movie_id, r.rating
        FROM ratings r
        JOIN users u ON r.user_id = u.id
    ''')
    ratings = [(row[0], row[1], row[2]) for row in c.fetchall()]
    conn.close()
    return ratings

def get_user_favourites(username):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    # Prvo dohvati user_id
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return []
    user_id = user[0]
    # Zatim dohvati sve lajkane filmove (rating = 1)
    c.execute("SELECT movie_id FROM ratings WHERE user_id = ? AND rating = 1", (user_id,))
    results = c.fetchall()
    conn.close()
    return [row[0] for row in results]

def remove_rating(username, movie_id):
    conn = sqlite3.connect('filmovi.db')
    cur = conn.cursor()
    # Dohvati user_id
    cur.execute('SELECT id FROM users WHERE username=?', (username,))
    user = cur.fetchone()
    if not user:
        conn.close()
        return False
    user_id = user[0]
    # Obriši rating
    cur.execute('DELETE FROM ratings WHERE user_id=? AND movie_id=?', (user_id, movie_id))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0

def get_user_by_id(user_id):
    conn = sqlite3.connect('filmovi.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    else:
        return None

# ========== Preference korisnika ==========
def save_preferences(username, preferences):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    # Dohvati user_id
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return False
    user_id = user[0]
    # Provjeri postoji li vec preference
    c.execute('SELECT id FROM preferences WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    try:
        if row:
            # update
            c.execute('UPDATE preferences SET preferences = ? WHERE user_id = ?', (preferences, user_id))
        else:
            # insert
            c.execute('INSERT INTO preferences (user_id, preferences) VALUES (?, ?)', (user_id, preferences))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_preferences(username):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return None
    user_id = user[0]
    c.execute('SELECT preferences FROM preferences WHERE user_id = ?', (user_id,))
    pref = c.fetchone()
    conn.close()
    if pref:
        return pref[0]
    else:
        return None