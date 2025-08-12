from database import (
    get_user_rated_movies,
    get_all_ratings,
    get_recommendations_for_user
)
from app import content_recommendations, ml_recommendations

username = "tvoj_username"  # zamijeni svojim usernameom

# 1. Dohvati preporučene filmove po svakom modelu
collab_movies = [m['id'] for m in get_recommendations_for_user(username)]
content_movies = [m['id'] for m in content_recommendations(username).json]
ml_movies = [m['id'] for m in ml_recommendations(username).json]

# 2. Dohvati sve pozitivno ocijenjene filmove korisnika
# Pretpostavljamo da je "pozitivna ocjena" >= 4
all_ratings = get_all_ratings()
positive_rated_ids = set(
    r[1] for r in all_ratings if r[0] == username and r[2] >= 4
)

# 3. Prebroji za svaki model koliko preporučenih filmova je pozitivno ocijenjeno
def count_positive(recommended_ids, positive_ids):
    return len([rid for rid in recommended_ids if rid in positive_ids])

collab_positive = count_positive(collab_movies, positive_rated_ids)
content_positive = count_positive(content_movies, positive_rated_ids)
ml_positive = count_positive(ml_movies, positive_rated_ids)

print(f"Kolaborativni: {collab_positive} od {len(collab_movies)}")
print(f"Content-based: {content_positive} od {len(content_movies)}")
print(f"ML/SVD: {ml_positive} od {len(ml_movies)}")