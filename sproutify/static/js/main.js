// ===========================
//  Carousel Functionality
// ===========================
const next = document.getElementById("next");
const prev = document.getElementById("prev");
const carousel = document.querySelector(".carousel");
const items = document.querySelectorAll(".carousel .item");
const countItem = items.length;
let active = 1;
let other_1 = null;
let other_2 = null;

const changeSlider = () => {
  const itemOldActive = document.querySelector(".carousel .item.active");
  const itemOldOther1 = document.querySelector(".carousel .item.other_1");
  const itemOldOther2 = document.querySelector(".carousel .item.other_2");

  itemOldActive?.classList.remove("active");
  itemOldOther1?.classList.remove("other_1");
  itemOldOther2?.classList.remove("other_2");

  items.forEach(item => {
    const img = item.querySelector(".image img");
    const caption = item.querySelector(".image figcaption");
    img.style.animation = "none";
    caption.style.animation = "none";
    void item.offsetWidth; // trigger reflow
    img.style.animation = "";
    caption.style.animation = "";
  });

  items[active].classList.add("active");
  items[other_1].classList.add("other_1");
  items[other_2].classList.add("other_2");

  clearInterval(autoPlay);
  autoPlay = setInterval(() => next.click(), 5000);
};

next.onclick = () => {
  carousel.classList.remove("prev");
  carousel.classList.add("next");
  active = (active + 1) % countItem;
  other_1 = (active - 1 + countItem) % countItem;
  other_2 = (active + 1) % countItem;
  changeSlider();
};

prev.onclick = () => {
  carousel.classList.remove("next");
  carousel.classList.add("prev");
  active = (active - 1 + countItem) % countItem;
  other_1 = (active + 1) % countItem;
  other_2 = (other_1 + 1) % countItem;
  changeSlider();
};

let autoPlay = setInterval(() => next.click(), 5000);

// ===========================
//  Sticky Header on Scroll
// ===========================
window.addEventListener("scroll", () => {
  const header = document.querySelector("header");
  header.classList.toggle("scrolled", window.scrollY > 200);
});

// ===========================
//  Footer Accordion Toggle
// ===========================
const footerToggles = document.querySelectorAll(".footer-toggle");

if (window.innerWidth <= 768) {
  footerToggles.forEach(toggle => {
    toggle.addEventListener("click", () => {
      toggle.parentElement.classList.toggle("active");
    });
  });
}

// ===========================
//  Fade-In on Scroll
// ===========================
const faders = document.querySelectorAll(".fade-in-section");

const appearOnScroll = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add("is-visible");
    observer.unobserve(entry.target);
  });
}, {
  threshold: 0.1,
  rootMargin: "0px 0px -20px 0px"
});

faders.forEach(fader => appearOnScroll.observe(fader));

// ===========================
//  Preloader Logic
// ===========================
window.addEventListener("load", () => {
  const preloader = document.getElementById("preloader");
  preloader.style.opacity = "0";
  setTimeout(() => {
    preloader.style.display = "none";
  }, 500);
});


// ===========================
//  Login Popup Shows
// ===========================
document.addEventListener("DOMContentLoaded", function () {
  const loginPopup = document.getElementById("loginPopup");
  const registerPopup = document.getElementById("registerPopup");

  const loginBtn = document.getElementById("loginBtn");
  const loginCloseBtn = document.getElementById("loginCloseBtn");

  const registerCloseBtn = document.getElementById("registerCloseBtn");
  const showRegisterBtn = document.getElementById("showRegisterBtn");
  const showLoginBtn = document.getElementById("showLoginBtn");

  // Show Login
  loginBtn?.addEventListener("click", () => {
    loginPopup.classList.remove("hidden");
  });

  // Close Login
  loginCloseBtn?.addEventListener("click", () => {
    loginPopup.classList.add("hidden");
  });

  // Show Register from Login
  showRegisterBtn?.addEventListener("click", () => {
    loginPopup.classList.add("hidden");
    registerPopup.classList.remove("hidden");
  });

  // Show Login from Register
  showLoginBtn?.addEventListener("click", () => {
    registerPopup.classList.add("hidden");
    loginPopup.classList.remove("hidden");
  });

  // Close Register
  registerCloseBtn?.addEventListener("click", () => {
    registerPopup.classList.add("hidden");
  });
});
