from flask import Flask, request, jsonify
from flask_cors import CORS
from database import (
    init_db,
    add_user,
    check_user,
    add_movie,
    get_all_movies,
    add_rating,
    get_movie_ratings,
    delete_movie,
    edit_movie,
    get_all_movies_with_avg,
    get_user_by_id,
    save_preferences,
    get_user_preferences,
    get_user_rated_movies,
    get_all_ratings,
    remove_rating,
    get_user_favourites
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import sqlite3

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/')
def home():
    return "Radi! Ovo je backend za filmove."

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Sva polja su obavezna.'}), 400
    success = add_user(username, email, password)
    if success:
        return jsonify({'success': True, 'message': 'Registracija uspješna!'})
    else:
        return jsonify({'success': False, 'message': 'Korisničko ime ili email već postoji.'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'message': 'Oba polja su obavezna.'}), 400
    if check_user(username, password):
        return jsonify({'success': True, 'message': 'Prijava uspješna!'})
    else:
        return jsonify({'success': False, 'message': 'Neispravno korisničko ime ili lozinka.'}), 401

@app.route('/add_movie', methods=['POST'])
def add_movie_route():
    data = request.get_json()
    title = data.get('title')
    omdb_id = data.get('omdb_id')
    poster_url = data.get('poster_url')
    description = data.get('description')
    genre = data.get('genre')  # Dodano: žanr mora biti u requestu!
    if not title:
        return jsonify({'success': False, 'message': 'Naslov je obavezan.'}), 400
    success = add_movie(title, omdb_id, poster_url, description, genre)
    if success:
        return jsonify({'success': True, 'message': 'Film uspješno dodan!'})
    else:
        return jsonify({'success': False, 'message': 'Film s tim OMDB ID-em već postoji.'}), 409

@app.route('/movies', methods=['GET'])
def movies():
    return jsonify(get_all_movies())

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    data = request.get_json()
    username = data.get('username')
    movie_id = data.get('movie_id')
    rating = data.get('rating')
    if not username or not movie_id or not rating:
        return jsonify({'success': False, 'message': 'Sva polja su obavezna.'}), 400

    try:
        movie_id = int(movie_id)
        rating = int(rating)
    except ValueError:
        return jsonify({'success': False, 'message': 'movie_id i rating moraju biti brojevi.'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'success': False, 'message': 'Ocjena mora biti između 1 i 5.'}), 400

    success, message = add_rating(username, movie_id, rating)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 409

@app.route('/movie_ratings/<int:movie_id>', methods=['GET'])
def movie_ratings(movie_id):
    return jsonify(get_movie_ratings(movie_id))

@app.route('/delete_movie/<int:movie_id>', methods=['DELETE'])
def delete_movie_route(movie_id):
    if delete_movie(movie_id):
        return jsonify({'success': True, 'message': 'Film obrisan.'})
    else:
        return jsonify({'success': False, 'message': 'Film nije pronađen.'}), 404

@app.route('/edit_movie/<int:movie_id>', methods=['PUT'])
def edit_movie_route(movie_id):
    data = request.get_json()
    title = data.get('title')
    omdb_id = data.get('omdb_id')
    poster_url = data.get('poster_url')
    description = data.get('description')
    genre = data.get('genre')  # Dodano: žanr može se mijenjati!
    if not any([title, omdb_id, poster_url, description, genre]):
        return jsonify({'success': False, 'message': 'Nema podataka za izmjenu.'}), 400
    if edit_movie(movie_id, title, omdb_id, poster_url, description, genre):
        return jsonify({'success': True, 'message': 'Film izmijenjen.'})
    else:
        return jsonify({'success': False, 'message': 'Film nije pronađen ili nema izmjena.'}), 404

@app.route('/movies_with_avg', methods=['GET'])
def movies_with_avg():
    return jsonify(get_all_movies_with_avg())

@app.route('/preferences', methods=['POST'])
def preferences():
    data = request.get_json()
    username = data.get('username')
    preferences = data.get('preferences')
    if not username or not preferences:
        return jsonify({'success': False, 'message': 'Nedostaju podaci.'}), 400
    success = save_preferences(username, preferences)
    if success:
        return jsonify({'success': True, 'message': 'Preference spremljene.'})
    else:
        return jsonify({'success': False, 'message': 'Greška pri spremanju preferenci.'}), 500

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def recommendations_by_id(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Korisnik nije pronađen.'}), 404
    username = user['username']
    films = get_recommendations_for_user(username)
    return jsonify(films)

@app.route('/recommendations/<username>', methods=['GET'])
def recommendations(username):
    films = get_recommendations_for_user(username)
    return jsonify(films)

# Helper function for content-based recommendations (logic only)
def get_content_recommendations(username, n=12):
    all_movies = get_all_movies_with_avg()
    if not all_movies:
        return []

    user_rated_ids = get_user_rated_movies(username)
    if not user_rated_ids:
        sorted_by_rating = sorted(all_movies, key=lambda x: x['average_rating'] or 0, reverse=True)
        return sorted_by_rating[:n]

    def movie_text(movie):
        return movie.get('description', '') or ''

    movie_ids = [movie['id'] for movie in all_movies]
    movie_texts = [movie_text(movie) for movie in all_movies]

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(movie_texts)

    user_indices = [i for i, mid in enumerate(movie_ids) if mid in user_rated_ids]
    if not user_indices:
        return []

    user_profile = np.asarray(np.mean(tfidf_matrix[user_indices], axis=0))

    similarities = cosine_similarity(user_profile, tfidf_matrix).flatten()

    recommended = []
    for idx in np.argsort(similarities)[::-1]:
        movie = all_movies[idx]
        if movie['id'] not in user_rated_ids:
            recommended.append(movie)
        if len(recommended) >= n:
            break

    return recommended

@app.route('/content_recommendations/<username>', methods=['GET'])
def content_recommendations(username):
    recs = get_content_recommendations(username)
    return jsonify(recs)

# Helper function for ML recommendations (logic only)
def get_ml_recommendations(username, n=12):
    try:
        from surprise import SVD, Dataset, Reader
        all_ratings = get_all_ratings()
        if not all_ratings:
            return []
        all_movies = get_all_movies_with_avg()
        if not all_movies:
            return []

        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            pd.DataFrame(all_ratings, columns=['user', 'item', 'rating']),
            reader
        )

        trainset = data.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)

        user_rated_ids = get_user_rated_movies(username)
        movie_ids = [movie['id'] for movie in all_movies]
        rec_candidates = [mid for mid in movie_ids if mid not in user_rated_ids]
        if not rec_candidates:
            return []

        preds = []
        for mid in rec_candidates:
            try:
                pred = algo.predict(username, mid)
                preds.append((mid, pred.est))
            except Exception:
                continue

        preds.sort(key=lambda x: x[1], reverse=True)
        best_ids = [mid for mid, _ in preds[:n]]
        recommended = [movie for movie in all_movies if movie['id'] in best_ids]
        return recommended
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        return []

@app.route('/ml_recommendations/<username>', methods=['GET'])
def ml_recommendations(username):
    recs = get_ml_recommendations(username)
    return jsonify(recs)

@app.route('/my_movies/<username>', methods=['GET'])
def my_movies(username):
    rated_ids = get_user_rated_movies(username)
    if not rated_ids:
        return jsonify([])
    all_movies = get_all_movies_with_avg()
    liked_movies = [m for m in all_movies if m['id'] in rated_ids]
    return jsonify(liked_movies)

@app.route('/search_movies', methods=['GET'])
def search_movies():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    all_movies = get_all_movies_with_avg()
    found = [m for m in all_movies if query.lower() in (m['title'] or '').lower()]
    return jsonify(found)

@app.route('/stats', methods=['GET'])
def stats():
    all_movies = get_all_movies_with_avg()
    movie_count = len(all_movies)
    username = request.args.get('user', None)
    user_fav_count = 0
    if username:
        try:
            user_fav_count = len(get_user_favourites(username))
        except Exception:
            user_fav_count = 0
    return jsonify({
        "movies": movie_count,
        "user_fav_count": user_fav_count
    })

@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    try:
        data = request.get_json()
        username = data['username']
        movie_id = data['movie_id']
        try:
            movie_id = int(movie_id)
        except Exception:
            return jsonify({'success': False, 'message': 'movie_id mora biti broj.'}), 400
        success = remove_rating(username, movie_id)
        if success:
            return jsonify({'success': True, 'message': 'Film uklonjen iz omiljenih.'})
        else:
            return jsonify({'success': False, 'message': 'Film nije pronađen ili greška.'}), 404
    except Exception as e:
        import traceback
        print('Greška u /remove_favorite:', str(e))
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'Greška na serveru: ' + str(e)}), 500

@app.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": "Korisnik nije pronađen"}), 404

@app.route('/recommendation_stats/<username>', methods=['GET'])
def recommendation_stats(username):
    collab_recs = [m['id'] for m in get_recommendations_for_user(username)]
    content_recs = [m['id'] for m in get_content_recommendations(username)]
    ml_recs = [m['id'] for m in get_ml_recommendations(username)]

    liked_ids = set(get_user_favourites(username))

    def count_liked(recommended, liked):
        return len([rid for rid in recommended if rid in liked])

    stats = {
        "collab": {
            "recommended": len(collab_recs),
            "liked": count_liked(collab_recs, liked_ids)
        },
        "content": {
            "recommended": len(content_recs),
            "liked": count_liked(content_recs, liked_ids)
        },
        "ml": {
            "recommended": len(ml_recs),
            "liked": count_liked(ml_recs, liked_ids)
        }
    }
    return jsonify(stats)

@app.route('/genre_hit_stats/<username>', methods=['GET'])
def genre_hit_stats(username):
    liked_ids = get_user_favourites(username)
    if not liked_ids:
        return jsonify({"message": "Korisnik nema lajkanih filmova."})

    all_movies = get_all_movies_with_avg()
    id_to_genre = {movie['id']: (movie.get('genre') or '').strip() for movie in all_movies}

    # Helper za parsiranje žanrova
    def parse_genres(genre_str):
        return [g.strip() for g in genre_str.split(",") if g.strip()]

    # Skupi sve pojedinačne žanrove iz lajkane liste
    liked_genres_set = set()
    for mid in liked_ids:
        genre_str = id_to_genre.get(mid, '')
        liked_genres_set.update(parse_genres(genre_str))

    def count_genre_hits(recommended_ids):
        hits = 0
        for rid in recommended_ids:
            rec_genres = parse_genres(id_to_genre.get(rid, ''))
            if liked_genres_set.intersection(rec_genres):
                hits += 1
        return hits

    collab_recs = [m['id'] for m in get_recommendations_for_user(username)]
    content_recs = [m['id'] for m in get_content_recommendations(username)]
    ml_recs = [m['id'] for m in get_ml_recommendations(username)]

    stats = {
        "collab": {
            "recommended": len(collab_recs),
            "genre_hits": count_genre_hits(collab_recs)
        },
        "content": {
            "recommended": len(content_recs),
            "genre_hits": count_genre_hits(content_recs)
        },
        "ml": {
            "recommended": len(ml_recs),
            "genre_hits": count_genre_hits(ml_recs)
        },
        "liked_genres": sorted(liked_genres_set)
    }
    return jsonify(stats)

# --- ISPRAVLJENA KOLABORATIVNA PREPORUKA ---
def get_recommendations_for_user(username, top_n=12):
    conn = sqlite3.connect('filmovi.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return []
    user_id = user[0]
    c.execute('SELECT movie_id FROM ratings WHERE user_id = ?', (user_id,))
    liked_movies = set(row[0] for row in c.fetchall())
    if not liked_movies:
        conn.close()
        return []
    qmarks = ','.join(['?']*len(liked_movies))
    c.execute(f'SELECT DISTINCT user_id FROM ratings WHERE movie_id IN ({qmarks}) AND user_id != ?', tuple(liked_movies)+(user_id,))
    similar_users = set(row[0] for row in c.fetchall())
    if not similar_users:
        c.execute(f'SELECT movie_id, COUNT(*) as cnt FROM ratings WHERE movie_id NOT IN ({qmarks}) GROUP BY movie_id ORDER BY cnt DESC LIMIT ?', tuple(liked_movies)+(top_n,))
        rec_movies = [row[0] for row in c.fetchall()]
    else:
        qmarks_similar = ','.join(['?']*len(similar_users))
        c.execute(f'''
            SELECT movie_id, COUNT(*) as cnt FROM ratings
            WHERE user_id IN ({qmarks_similar}) AND movie_id NOT IN ({qmarks})
            GROUP BY movie_id ORDER BY cnt DESC LIMIT ?
        ''', tuple(similar_users)+tuple(liked_movies)+(top_n,))
        rec_movies = [row[0] for row in c.fetchall()]
    if not rec_movies:
        conn.close()
        return []
    qmarks_movies = ','.join(['?']*len(rec_movies))
    c.execute(f"SELECT id, title, omdb_id, poster_url, description, genre FROM movies WHERE id IN ({qmarks_movies})", tuple(rec_movies))
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

import json
from app import get_ml_recommendations

username = "tvoje_korisnicko_ime"  # zamijeni s korisničkim imenom
results = get_ml_recommendations(username)

# Spremi u JSON datoteku
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Rezultati ML preporuka su spremljeni u results.json.")

if __name__ == '__main__':
    app.run(debug=True)