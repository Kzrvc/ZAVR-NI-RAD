const movieLists = document.querySelectorAll(".movie-list");

const ball = document.querySelector(".toggle-ball");
const items = document.querySelectorAll(
  ".container,.movie-list-title,.navbar-container,.sidebar,.left-menu-icon,.toggle"
);

ball.addEventListener("click", () => {
  items.forEach((item) => {
    item.classList.toggle("active");
  });
  ball.classList.toggle("active");
});


const buttons = document.querySelectorAll(".movie-list-item-button");
buttons.forEach((button) => {
  button.addEventListener("click", () => {
    const url = button.getAttribute("data-url");
    if (url) {
      window.open(url, "_blank");
    } else {
      console.error("URL nije postavljen za ovaj gumb.");
    }
  });
});

const featuredButtons = document.querySelectorAll(".featured-button");
featuredButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const url = button.getAttribute("data-url"); 
    if (url) {
      window.open(url, "_blank"); 
    } else {
      console.error("URL nije postavljen za Featured gumb.");
    }
  });
});

const featuredButtonss = document.querySelectorAll(".profile-text-container");
featuredButtonss.forEach((button) => {
  button.addEventListener("click", () => {
    const url = button.getAttribute("data-url"); 
    if (url) {
      window.open(url, "_blank");
    } else {
      console.error("URL nije postavljen za Featured gumb.");
    }
  });
});



const API_KEY = "cf13e496";
const movies = [
  { id: "tt1798709", elementId: "movie-desc-her" }, // "Her"
  { id: "tt1375666", elementId: "movie-desc-inception" }, // "Inception"
  { id: "tt3568804", elementId: "movie-desc-storm" }, // "Strom"
  { id: "tt8579674", elementId: "movie-desc-1917" }, // "1917"
  { id: "tt4154756", elementId: "movie-desc-avengers" }, // "Avengers"
  { id: "tt2488496", elementId: "movie-desc-starWars" }, // "Star Wars"
  { id: "tt2231461", elementId: "movie-desc-rampage" }, // "Rampage"
  { id: "tt1483013", elementId: "movie-desc-oblivion" }, // "Oblivion"
  { id: "tt5753856", elementId: "movie-desc-dark" }, // "Dark"
  { id: "tt1853728", elementId: "movie-desc-django" }, // "Django"
  { id: "tt1301698", elementId: "movie-desc-1920" }, // "1920"
  { id: "tt0050825", elementId: "movie-desc-paths" }, // "Paths of glory"
  { id: "tt4116284", elementId: "movie-desc-legobatman" }, // "Lego Batmn"
  { id: "tt5638500", elementId: "movie-desc-1920l" }, // "1920 london"
  { id: "tt6548966", elementId: "movie-desc-fairy" }, // "Fairy"
  { id: "tt10872600", elementId: "movie-desc-spiderman" }, // "Spiderman"
  { id: "tt0903624", elementId: "movie-desc-hobbit" }, // "Hobbit"
  { id: "tt1231583", elementId: "movie-desc-duedate" }, // "due date"
  { id: "tt1650554", elementId: "movie-desc-kickass" }, // "kick ass 2"
  { id: "tt4877122", elementId: "movie-desc-emoji" }, // "emoji movie"
  { id: "tt1477834", elementId: "movie-desc-aquaman" }, // "aquaman"
];

movies.forEach((movie) => {
  const apiUrl = `https://www.omdbapi.com/?i=${movie.id}&apikey=${API_KEY}`;
  
  fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
      const descriptionElement = document.getElementById(movie.elementId);
      if (data.Plot) {
        descriptionElement.textContent = data.Plot;
      } else {
        descriptionElement.textContent = "Description not available.";
      }
    })
    .catch((error) => {
      console.error("Error fetching movie description:", error);
      document.getElementById(movie.elementId).textContent =
        "Failed to load description.";
    });
});
