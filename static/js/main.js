/* Kessler & Hyde — Global JS Foundation
   Phase 1 only handles the mobile navigation toggle.
   Scroll animation logic will be added in a later phase. */

document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.querySelector("[data-hamburger]");
  const mobileNav = document.querySelector("[data-mobile-nav]");

  if (hamburger && mobileNav) {
    hamburger.addEventListener("click", function () {
      const isOpen = mobileNav.classList.toggle("is-open");
      hamburger.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }
});
/* Product gallery — clicking a thumbnail swaps the main image */
document.addEventListener("DOMContentLoaded", function () {
  const mainImageContainer = document.querySelector("[data-main-image]");
  const thumbs = document.querySelectorAll("[data-thumb]");

  thumbs.forEach(function (thumb) {
    thumb.addEventListener("click", function () {
      const fullImageUrl = thumb.getAttribute("data-full");
      const mainImg = mainImageContainer.querySelector("img");
      if (mainImg && fullImageUrl) {
        mainImg.src = fullImageUrl;
      }
      thumbs.forEach(function (t) { t.classList.remove("is-active"); });
      thumb.classList.add("is-active");
    });
  });
});
/* Scroll showcase — fades/slides items in as they enter the viewport */
document.addEventListener("DOMContentLoaded", function () {
  const showcaseItems = document.querySelectorAll(".showcase-item");

  if (showcaseItems.length === 0) return;

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target); // animate once, not every scroll
        }
      });
    },
    { threshold: 0.2 }
  );

  showcaseItems.forEach(function (item) {
    observer.observe(item);
  });
});