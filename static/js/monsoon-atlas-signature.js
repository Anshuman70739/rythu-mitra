/* Monsoon Atlas signature interactions. No dependencies; respects reduced motion and touch devices. */
(() => {
  "use strict";
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const lowPower = window.matchMedia("(max-width: 760px), (pointer: coarse)");
  const body = document.body;

  // A cinematic, one-shot curtain for navigation between public showcase pages.
  if (body.classList.contains("showcase-page")) {
    if (!reduceMotion.matches && !lowPower.matches && window.performance?.getEntriesByType("navigation")?.[0]?.type === "navigate") {
      body.classList.add("route-arrived");
      window.setTimeout(() => body.classList.remove("route-arrived"), 900);
    }
    if (!reduceMotion.matches && !lowPower.matches) {
      const curtain = document.createElement("div");
      curtain.className = "atlas-route-curtain";
      curtain.setAttribute("aria-hidden", "true");
      body.appendChild(curtain);
      let navigating = false;
      document.addEventListener("click", (event) => {
        const link = event.target.closest("a[href]");
        if (!link || navigating || event.defaultPrevented || event.button !== 0 ||
            event.metaKey || event.ctrlKey || event.shiftKey || event.altKey ||
            link.target || link.hasAttribute("download")) return;
        let destination;
        try { destination = new URL(link.href, window.location.href); } catch { return; }
        if (destination.origin !== window.location.origin ||
            destination.pathname === window.location.pathname ||
            destination.protocol !== "http:" && destination.protocol !== "https:") return;
        const rect = link.getBoundingClientRect();
        curtain.style.setProperty("--atlas-origin-x", Math.round(rect.left + rect.width / 2) + "px");
        curtain.style.setProperty("--atlas-origin-y", Math.round(rect.top + rect.height / 2) + "px");
        navigating = true;
        event.preventDefault();
        curtain.classList.add("is-active");
        window.setTimeout(() => { window.location.href = destination.href; }, 430);
      });
      window.addEventListener("pageshow", () => { navigating = false; curtain.classList.remove("is-active"); });
    }
  }

  // Async Flask views are inserted after the initial page load. Observe each render
  // so the visual entrance also works after navigating between workspace routes.
  const view = document.getElementById("view");
  if (!view || reduceMotion.matches || !("IntersectionObserver" in window)) return;
  let revealObserver;
  const revealTargets = [
    ".atlas-dashboard-hero", ".atlas-stat-card", ".atlas-action-card",
    ".atlas-quick-tools", ".atlas-finance-card", ".atlas-honesty-note",
    ".main-content .panel", ".main-content .hero-panel", ".main-content .stat-card",
    ".main-content .tool-card", ".main-content .module-card", ".main-content .feature-tile",
    ".main-content .empty-state", ".main-content .data-card"
  ].join(",");
  const attach = (root) => {
    if (!(root instanceof Element)) return;
    const nodes = [];
    if (root.matches(revealTargets)) nodes.push(root);
    nodes.push(...root.querySelectorAll(revealTargets));
    nodes.forEach((node, index) => {
      if (node.dataset.atlasRevealReady === "true") return;
      node.dataset.atlasRevealReady = "true";
      node.classList.add("atlas-motion-item");
      node.style.setProperty("--atlas-motion-delay", Math.min(index % 5, 4) * 48 + "ms");
      revealObserver.observe(node);
    });
  };
  revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-atlas-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.04, rootMargin: "0px 0px -24px 0px" });
  attach(view);
  const mutationObserver = new MutationObserver((records) => {
    records.forEach((record) => record.addedNodes.forEach((node) => {
      if (node instanceof Element) attach(node);
    }));
  });
  mutationObserver.observe(view, { childList: true, subtree: true });
  window.addEventListener("pagehide", () => {
    mutationObserver.disconnect();
    revealObserver.disconnect();
  }, { once: true });
})();
