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