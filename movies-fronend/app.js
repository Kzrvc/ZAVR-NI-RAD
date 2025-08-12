// ========== LOGIN/REGISTER LOGIKA ==========

function showAuthForms() {
  if (!document.querySelector('.auth-forms-wrapper')) {
    injectAuthForms();
  }
  const authWrapper = document.querySelector('.auth-forms-wrapper');
  if (authWrapper) {
    authWrapper.style.display = 'flex';
    document.getElementById('login-form').style.display = 'flex';
    document.getElementById('register-form').style.display = 'flex';
  }
  document.getElementById('user-info')?.style?.setProperty('display', 'none');
  document.querySelector('.content-container').style.display = 'none';
}

function showAppContent() {
  const authWrapper = document.querySelector('.auth-forms-wrapper');
  if (authWrapper) {
    authWrapper.parentNode.removeChild(authWrapper);
  }
  renderUserInfo();
  document.getElementById('user-info')?.style?.setProperty('display', 'flex');
  document.querySelector('.content-container').style.display = '';
  prikaziSveFilmove();
  prikaziPreporuke('collab');
}

function isLoggedIn() {
  return !!localStorage.getItem('username');
}

function register() {
  fetch('http://127.0.0.1:5000/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: document.getElementById('reg-username').value,
      email: document.getElementById('reg-email').value,
      password: document.getElementById('reg-password').value
    })
  })
  .then(resp => resp.json())
  .then(data => {
    const msgDiv = document.getElementById('register-msg');
    msgDiv.innerText = data.message;
    if (data.success) {
      msgDiv.style.color = 'green'; // Zeleno za uspjeh
      msgDiv.innerText = "Registracija uspješna! Prijavi se.";
    } else {
      msgDiv.style.color = 'red'; // Crno za grešku
    }
  })
  .catch(() => {
    const msgDiv = document.getElementById('register-msg');
    msgDiv.innerText = "Greška pri registraciji.";
    msgDiv.style.color = 'black';
  });
}

function login() {
  fetch('http://127.0.0.1:5000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: document.getElementById('login-username').value,
      password: document.getElementById('login-password').value
    })
  })
  .then(resp => resp.json())
  .then(data => {
    document.getElementById('login-msg').innerText = data.message;
    if (data.success) {
      localStorage.setItem('username', document.getElementById('login-username').value);
      showAppContent();
    }
  });
}

function logout() {
  localStorage.removeItem('username');
  renderUserInfo();
  showAuthForms();
}

// ========== DODAJ LOGIN/REGISTER FORME U HTML DINAMIČKI ==========

function injectAuthForms() {
  if (document.querySelector('.auth-forms-wrapper')) return;
  const container = document.querySelector('.container');
  const authHtml = `
    <div class="auth-forms-wrapper">
      <form id="register-form" autocomplete="off">
        <h2>Registracija</h2>
        <input type="text" id="reg-username" placeholder="Korisničko ime" autocomplete="username" required />
        <input type="email" id="reg-email" placeholder="Email" autocomplete="email" required />
        <input type="password" id="reg-password" placeholder="Lozinka" autocomplete="new-password" required />
        <button type="button" onclick="register()">Registriraj se</button>
        <div id="register-msg"></div>
      </form>
      <form id="login-form" autocomplete="off">
        <h2>Prijava</h2>
        <input type="text" id="login-username" placeholder="Korisničko ime" autocomplete="username" required />
        <input type="password" id="login-password" placeholder="Lozinka" autocomplete="current-password" required />
        <button type="button" onclick="login()">Prijavi se</button>
        <div id="login-msg"></div>
      </form>
    </div>
  `;
  container.insertAdjacentHTML('afterbegin', authHtml);
}

// ========== PRIKAZ KORISNIČKOG IMENA GORE DESNO ==========
function renderUserInfo() {
  const userInfo = document.getElementById('user-info');
  const userWelcome = document.getElementById('user-welcome');
  const username = localStorage.getItem('username');
  if (userInfo && userWelcome) {
    if (username) {
      userWelcome.textContent = username;
      userInfo.style.display = 'flex';
    } else {
      userWelcome.textContent = '';
      userInfo.style.display = 'none';
    }
  }
}

// ========== DINAMIČKI PRIKAZ SVIH FILMOVA S OCJENOM ==========
// MODERN MOVIE ITEM LAYOUT WITH OVERLAY ON HOVER
function prikaziSveFilmove() {
  const loader = document.getElementById('all-loader');
  const listDiv = document.getElementById('movie-list');
  loader.style.display = 'block';
  listDiv.innerHTML = '';

  fetch('http://127.0.0.1:5000/movies_with_avg')
    .then(res => res.json())
    .then(films => {
      loader.style.display = 'none';
      listDiv.innerHTML = '';
      if (!films || films.length === 0) {
        listDiv.innerHTML = `<div class="empty-list-msg">Nema dostupnih filmova u bazi.</div>`;
        return;
      }
      films.forEach(film => {
        listDiv.innerHTML += `
          <div class="movie-list-item">
            <img class="movie-list-item-img" src="${film.poster_url || 'img/placeholder.jpg'}" alt="${film.title}">
            <div class="movie-info-overlay">
              <div class="movie-title">${film.title}</div>
              <div class="movie-rating">★ ${film.average_rating !== null && film.average_rating !== undefined ? film.average_rating.toFixed(2) : 'N/A'}</div>
              <div class="movie-desc">${film.description || 'Nema opisa.'}</div>
              <button class="movie-list-item-button" onclick="lajkajFilm('${film.id}')">Like 👍</button>
            </div>
          </div>
        `;
      });
    })
    .catch(error => {
      loader.style.display = 'none';
      listDiv.innerHTML = `<div class="empty-list-msg">Greška pri dohvaćanju filmova.</div>`;
      console.error("Greška pri dohvaćanju filmova s backend-a:", error);
    });
}

// ========== LAJKANJE FILMA ==========
function lajkajFilm(movieId) {
  const username = localStorage.getItem('username');
  if (!username) {
    alert('Moraš biti prijavljen!');
    return;
  }
  fetch('http://127.0.0.1:5000/rate_movie', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: username,
      movie_id: movieId,
      rating: 1
    })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
    prikaziSveFilmove();
    prikaziPreporuke(getActiveTab());
    osvjeziStatistiku();
  });
}

// ========== TABOVI I PRIKAZ PREPORUKA ==========
function getActiveTab() {
  if (document.getElementById('tab-collab')?.classList.contains('active')) return 'collab';
  if (document.getElementById('tab-content')?.classList.contains('active')) return 'content';
  if (document.getElementById('tab-ml')?.classList.contains('active')) return 'ml';
  return 'collab';
}

function prikaziPreporuke(tip) {
  ['collab','content','ml'].forEach(t => {
    const el = document.getElementById('tab-' + t);
    if (el) el.classList.remove('active');
  });
  const tabEl = document.getElementById('tab-' + tip);
  if (tabEl) tabEl.classList.add('active');

  const loader = document.getElementById('rec-loader');
  const listDiv = document.getElementById('recommended-list');
  loader.style.display = 'block';
  listDiv.innerHTML = '';

  const username = localStorage.getItem('username');
  let endpoint = '';
  if (tip === 'collab') endpoint = `/recommendations/${username}`;
  else if (tip === 'content') endpoint = `/content_recommendations/${username}`;
  else if (tip === 'ml') endpoint = `/ml_recommendations/${username}`;

  fetch(`http://127.0.0.1:5000${endpoint}`)
    .then(res => res.json())
    .then(films => {
      loader.style.display = 'none';
      listDiv.innerHTML = '';
      if (!films || films.length === 0) {
        listDiv.innerHTML = `<div class="empty-list-msg">Trenutno nema preporuka za ovaj način.</div>`;
        return;
      }
      films.forEach(film => {
        listDiv.innerHTML += `
          <div class="movie-list-item">
            <img class="movie-list-item-img" src="${film.poster_url || 'img/placeholder.jpg'}" alt="${film.title}">
            <div class="movie-info-overlay">
              <div class="movie-title">${film.title}</div>
              <div class="movie-rating">★ ${film.average_rating !== null && film.average_rating !== undefined ? film.average_rating.toFixed(2) : 'N/A'}</div>
              <div class="movie-desc">${film.description || 'Nema opisa.'}</div>
              <button class="movie-list-item-button" onclick="lajkajFilm('${film.id}')">Like 👍</button>
            </div>
          </div>
        `;
      });
    })
    .catch(error => {
      loader.style.display = 'none';
      listDiv.innerHTML = `<div class="empty-list-msg">Greška pri dohvaćanju preporuka.</div>`;
      console.error("Greška pri dohvaćanju preporuka s backend-a:", error);
    });
}

// ========== Prikaz statistike na About stranici ==========
function osvjeziStatistiku() {
  const username = localStorage.getItem('username');
  fetch("http://127.0.0.1:5000/stats" + (username ? "?user=" + encodeURIComponent(username) : ""))
    .then(res => res.json())
    .then(data => {
        const movieCount = document.getElementById("movie-count");
        const userFavCount = document.getElementById("user-fav-count");
        if (movieCount) movieCount.textContent = data.movies ?? "–";
        if (userFavCount) userFavCount.textContent = username ? (data.user_fav_count ?? "0") : "Prijavi se";
    })
    .catch(() => {
        const movieCount = document.getElementById("movie-count");
        const userFavCount = document.getElementById("user-fav-count");
        if (movieCount) movieCount.textContent = "–";
        if (userFavCount) userFavCount.textContent = username ? "0" : "Prijavi se";
    });
}

// ========== INIT ==========
window.addEventListener('DOMContentLoaded', () => {
  injectAuthForms();
  renderUserInfo();

  if (isLoggedIn()) {
    showAppContent();
    prikaziPreporuke('collab');
  } else {
    showAuthForms();
  }

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.onclick = () => {
    logout();
    renderUserInfo();
  };

  osvjeziStatistiku();
});

// === 1. Prikaz "Moji filmovi" (filmovi koje je korisnik lajkao/ocijenio) ===

function prikaziMojeFilmove() {
  const username = localStorage.getItem('username');
  if (!username) {
    alert('Moraš biti prijavljen!');
    return;
  }
  document.querySelector('.content-container').innerHTML = `
    <div class="movie-list-container">
      <h1 class="movie-list-title">🎬 Moji lajkani/ocijenjeni filmovi</h1>
      <div class="movie-list-wrapper">
        <div id="mymovies-loader" class="spinner"></div>
        <div class="movie-list" id="my-movie-list"></div>
      </div>
      <button onclick="location.reload()">Natrag</button>
    </div>
  `;
  const loader = document.getElementById('mymovies-loader');
  const listDiv = document.getElementById('my-movie-list');
  loader.style.display = 'block';
  listDiv.innerHTML = '';

  fetch(`http://127.0.0.1:5000/my_movies/${username}`)
    .then(res => res.json())
    .then(films => {
      loader.style.display = 'none';
      if (!films || films.length === 0) {
        listDiv.innerHTML = `<div class="empty-list-msg">Nema tvojih filmova.</div>`;
        return;
      }
      films.forEach(film => {
        listDiv.innerHTML += `
          <div class="movie-list-item">
            <img class="movie-list-item-img" src="${film.poster_url || 'img/placeholder.jpg'}" alt="${film.title}">
            <div class="movie-info-overlay">
              <div class="movie-title">${film.title}</div>
              <div class="movie-rating">★ ${film.average_rating !== null && film.average_rating !== undefined ? film.average_rating.toFixed(2) : 'N/A'}</div>
              <div class="movie-desc">${film.description || 'Nema opisa.'}</div>
            </div>
          </div>
        `;
      });
    })
    .catch(error => {
      loader.style.display = 'none';
      listDiv.innerHTML = `<div class="empty-list-msg">Greška pri dohvaćanju filmova.</div>`;
      console.error("Greška pri dohvaćanju mojih filmova:", error);
    });
}

// === 2. Pretraga filmova po naslovu ===

function pretraziFilmove() {
  const q = document.getElementById('search-input').value.trim();
  if (!q) {
    prikaziSveFilmove();
    return;
  }
  const loader = document.getElementById('all-loader');
  const listDiv = document.getElementById('movie-list');
  loader.style.display = 'block';
  listDiv.innerHTML = '';

  fetch(`http://127.0.0.1:5000/search_movies?q=${encodeURIComponent(q)}`)
    .then(res => res.json())
    .then(films => {
      loader.style.display = 'none';
      listDiv.innerHTML = '';
      if (!films || films.length === 0) {
        listDiv.innerHTML = `<div class="empty-list-msg">Nema rezultata za "${q}".</div>`;
        return;
      }
      films.forEach(film => {
        listDiv.innerHTML += `
          <div class="movie-list-item">
            <img class="movie-list-item-img" src="${film.poster_url || 'img/placeholder.jpg'}" alt="${film.title}">
            <div class="movie-info-overlay">
              <div class="movie-title">${film.title}</div>
              <div class="movie-rating">★ ${film.average_rating !== null && film.average_rating !== undefined ? film.average_rating.toFixed(2) : 'N/A'}</div>
              <div class="movie-desc">${film.description || 'Nema opisa.'}</div>
              <button class="movie-list-item-button" onclick="lajkajFilm('${film.id}')">Like 👍</button>
            </div>
          </div>
        `;
      });
    })
    .catch(error => {
      loader.style.display = 'none';
      listDiv.innerHTML = `<div class="empty-list-msg">Greška pri pretrazi filmova.</div>`;
      console.error("Greška pri pretrazi filmova:", error);
    });
}

function ukloniFilm(movieId) {
    const username = localStorage.getItem('username');
    if (!username) {
        alert('Moraš biti prijavljen!');
        return;
    }
    fetch('http://127.0.0.1:5000/remove_favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, movie_id: movieId })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || 'Film uklonjen.');
        location.reload(); // ili ponovo pozovi funkciju za prikaz liste
    })
    .catch(() => alert('Greška pri uklanjanju filma.'));
}