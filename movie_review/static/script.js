const mobileNavLinks = document.getElementById("links");
const toggleMobileNav = document.getElementById("toggle-mobile-nav");

toggleMobileNav.addEventListener("click", () => {
  mobileNavLinks.classList.toggle("hidden");
});

const toggleProfilePopUp = () => {
  const profilePopUp = document.getElementById("profile-popup");
  profilePopUp.classList.toggle("hidden");
};

document.addEventListener('DOMContentLoaded', () => {
  const elements = document.querySelectorAll('.on-scroll');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15,
  });

  elements.forEach(el => observer.observe(el));
});
