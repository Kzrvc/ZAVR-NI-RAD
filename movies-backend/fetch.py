import requests
from database import add_movie, init_db

TMDB_API_KEY = "5b2dbc4f45bbeea713df897589ff260c"  # zamijeni sa svojim ključem

def fetch_genre_map():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    resp = requests.get(url)
    data = resp.json()
    return {g['id']: g['name'] for g in data['genres']}

def fetch_movies_from_tmdb(pages=5):
    genre_map = fetch_genre_map()
    all_movies = []
    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        response = requests.get(url)
        data = response.json()
        for movie in data['results']:
            genres = [genre_map[gid] for gid in movie.get('genre_ids', []) if gid in genre_map]
            genre_str = ', '.join(genres)
            all_movies.append({
                'title': movie['title'],
                'omdb_id': str(movie['id']),
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None,
                'description': movie['overview'],
                'genre': genre_str
            })
    return all_movies

if __name__ == "__main__":
    init_db()
    movies = fetch_movies_from_tmdb(pages=5)  # 5 stranica x 20 = 100 filmova
    count = 0
    for m in movies:
        # Dodano: spremi i žanr!
        success = add_movie(m['title'], m['omdb_id'], m['poster_url'], m['description'], m['genre'])
        if success:
            count += 1
    print(f"Uspješno spremljeno filmova: {count}")