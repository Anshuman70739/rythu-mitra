(() => {
  "use strict";
  const root = document.querySelector(".app-shell") || document.body;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (!reduced.matches && "IntersectionObserver" in window) {
    const candidates = document.querySelectorAll(".main-content .panel,.main-content .hero-panel,.main-content .stat-card,.main-content .tool-card");
    const observer = new IntersectionObserver((entries, io) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("atlas-in-view");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    candidates.forEach((node, i) => {
      node.style.setProperty("--atlas-entry-delay", (i % 5) * 35 + "ms");
      observer.observe(node);
    });
  }
  root.classList.add("monsoon-atlas-experience");
  const setMotion = () => {
    if (reduced.matches) root.classList.add("atlas-reduced-motion");
  };
  setMotion();
  reduced.addEventListener?.("change", setMotion);
})();