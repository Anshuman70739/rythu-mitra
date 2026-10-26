(() => {
  "use strict";
  const root = document.documentElement;
  const body = document.body;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const lowPower = window.matchMedia("(max-width: 760px), (pointer: coarse)");
  const nav = document.getElementById("siteNav");
  const menu = document.getElementById("menuToggle");
  const progress = document.getElementById("scrollProgress");
  const motionToggle = document.getElementById("motionToggle");
  const soundToggle = document.getElementById("soundToggle");
  const status = document.getElementById("motionStatus");
  const masthead = document.getElementById("masthead");
  let language = "en";
  let userPausedMotion = false;
  let audioContext = null;
  let audioNodes = null;
  let lastParticleAt = 0;
  const setLanguage = (next) => {
    language = next;
    root.lang = next === "te" ? "te" : "en";
    document.querySelectorAll("[data-en][data-te]").forEach((el) => {
      el.textContent = next === "te" ? el.getAttribute("data-te") : el.getAttribute("data-en");
    });
    document.querySelectorAll("[data-language]").forEach((button) => button.setAttribute("aria-pressed", String(button.getAttribute("data-language") === next)));
    if (status) status.textContent = next === "te" ? "భాష తెలుగుకు మార్చబడింది" : "Language set to English";
  };
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => setLanguage(button.getAttribute("data-language"))));
  if (menu && nav) menu.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    menu.setAttribute("aria-expanded", String(open));
    menu.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  });
  if (nav) nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
    nav.classList.remove("is-open");
    if (menu) menu.setAttribute("aria-expanded", "false");
  }));
  const updateScroll = () => {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const ratio = Math.min(1, Math.max(0, window.scrollY / max));
    if (progress) progress.style.width = (ratio * 100).toFixed(2) + "%";
    if (masthead) masthead.classList.toggle("is-scrolled", window.scrollY > 28);
  };
  window.addEventListener("scroll", updateScroll, { passive: true });
  window.addEventListener("resize", updateScroll, { passive: true });
  updateScroll();
  const revealNodes = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion.matches && !userPausedMotion) {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); observer.unobserve(entry.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -30px 0px" });
    revealNodes.forEach((node, i) => { node.style.transitionDelay = (i % 4) * 65 + "ms"; revealObserver.observe(node); });
  } else revealNodes.forEach((node) => node.classList.add("is-visible"));
  const chapters = Array.from(document.querySelectorAll("[data-chapter]"));
  const stage = document.getElementById("chapterStage");
  const stageStamp = document.getElementById("stageStamp");
  const stageCaption = document.getElementById("stageCaption");
  const chapterNames = ["Read the conditions", "Look closer at the crop", "Connect information to action"];
  const setChapter = (index) => {
    chapters.forEach((card, i) => card.classList.toggle("is-active", i === index));
    if (stage) stage.setAttribute("data-active", String(index));
    if (stageStamp) stageStamp.textContent = "0" + (index + 1);
    if (stageCaption) stageCaption.textContent = chapterNames[index] || chapterNames[0];
  };
  if ("IntersectionObserver" in window && chapters.length && !reduceMotion.matches) {
    const chapterObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => { if (entry.isIntersecting) setChapter(Number(entry.target.getAttribute("data-chapter"))); });
    }, { threshold: 0.55 });
    chapters.forEach((card) => chapterObserver.observe(card));
  }
  if (stage) stage.setAttribute("data-active", "0");
  if (motionToggle) motionToggle.addEventListener("click", () => {
    userPausedMotion = !userPausedMotion;
    body.classList.toggle("motion-paused", userPausedMotion || reduceMotion.matches);
    motionToggle.setAttribute("aria-pressed", String(userPausedMotion));
    const label = motionToggle.querySelector("[data-en]");
    if (label) { label.setAttribute("data-en", userPausedMotion ? "Motion paused" : "Motion on"); label.setAttribute("data-te", userPausedMotion ? "చలనం నిలిపివేసింది" : "చలనం ఆన్"); label.textContent = language === "te" ? label.getAttribute("data-te") : label.getAttribute("data-en"); }
    if (userPausedMotion) revealNodes.forEach((node) => node.classList.add("is-visible"));
    if (status) status.textContent = userPausedMotion ? "Decorative motion paused" : "Decorative motion resumed";
  });
  const stopAudio = () => { if (audioContext && audioContext.state === "running") audioContext.suspend().catch(() => {}); };
  if (soundToggle) soundToggle.addEventListener("click", async () => {
    const enabled = soundToggle.getAttribute("aria-pressed") !== "true";
    if (enabled) {
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) throw new Error("not supported");
        if (!audioContext) {
          audioContext = new AudioCtx();
          const master = audioContext.createGain(); master.gain.value = 0.012; master.connect(audioContext.destination);
          const one = audioContext.createOscillator(); one.type = "sine"; one.frequency.value = 110; one.connect(master); one.start();
          const two = audioContext.createOscillator(); two.type = "sine"; two.frequency.value = 164.81; const gainTwo = audioContext.createGain(); gainTwo.gain.value = 0.35; two.connect(gainTwo); gainTwo.connect(master); two.start();
          audioNodes = [master, one, two];
        }
        await audioContext.resume();
        soundToggle.setAttribute("aria-pressed", "true");
        const label = soundToggle.querySelector("[data-en]");
        if (label) { label.setAttribute("data-en", "Sound on"); label.setAttribute("data-te", "శబ్దం ఆన్"); label.textContent = language === "te" ? label.getAttribute("data-te") : label.getAttribute("data-en"); }
        if (status) status.textContent = "Optional ambient tone enabled";
      } catch (_) { if (status) status.textContent = "Ambient sound is not available in this browser"; }
    } else {
      stopAudio();
      soundToggle.setAttribute("aria-pressed", "false");
      const label = soundToggle.querySelector("[data-en]");
      if (label) { label.setAttribute("data-en", "Sound off"); label.setAttribute("data-te", "శబ్దం ఆఫ్"); label.textContent = language === "te" ? label.getAttribute("data-te") : label.getAttribute("data-en"); }
      if (status) status.textContent = "Optional ambient tone disabled";
    }
  });
  const heroScene = document.getElementById("heroScene");
  if (heroScene && !lowPower.matches && !reduceMotion.matches) {
    window.addEventListener("pointermove", (event) => {
      const rect = heroScene.getBoundingClientRect();
      if (event.clientX < rect.left - 60 || event.clientX > rect.right + 60 || event.clientY < rect.top - 60 || event.clientY > rect.bottom + 60) return;
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      heroScene.style.transform = "rotateY(" + (x * 3.2).toFixed(2) + "deg) rotateX(" + (-y * 2.5).toFixed(2) + "deg)";
      heroScene.querySelectorAll("[data-depth]").forEach((layer) => {
        const depth = Number(layer.getAttribute("data-depth")) || 0.1;
        layer.style.translate = (x * depth * 15).toFixed(1) + "px " + (y * depth * 10).toFixed(1) + "px";
      });
    }, { passive: true });
    heroScene.addEventListener("pointerleave", () => { heroScene.style.transform = ""; heroScene.querySelectorAll("[data-depth]").forEach((layer) => layer.style.translate = ""); });
  }
  if (!lowPower.matches && !reduceMotion.matches) {
    document.querySelectorAll(".magnetic-button,.nav-cta").forEach((button) => {
      button.addEventListener("pointermove", (event) => {
        const rect = button.getBoundingClientRect();
        const x = (event.clientX - rect.left - rect.width / 2) / rect.width;
        const y = (event.clientY - rect.top - rect.height / 2) / rect.height;
        button.style.transform = "translate(" + (x * 7).toFixed(1) + "px," + (y * 5).toFixed(1) + "px)";
      });
      button.addEventListener("pointerleave", () => button.style.transform = "");
    });
  }
  if (!lowPower.matches && !reduceMotion.matches) {
    window.addEventListener("pointermove", (event) => {
      const now = performance.now();
      if (now - lastParticleAt < 75) return;
      lastParticleAt = now;
      if (document.querySelectorAll(".cursor-seed").length > 8) return;
      const particle = document.createElement("span");
      particle.className = "cursor-seed";
      particle.style.left = event.clientX + "px";
      particle.style.top = event.clientY + "px";
      document.body.appendChild(particle);
      particle.addEventListener("animationend", () => particle.remove(), { once: true });
    }, { passive: true });
  }
  if (reduceMotion.matches) body.classList.add("motion-paused");
  reduceMotion.addEventListener?.("change", () => {
    if (reduceMotion.matches) { body.classList.add("motion-paused"); revealNodes.forEach((node) => node.classList.add("is-visible")); }
    else if (!userPausedMotion) body.classList.remove("motion-paused");
  });
})();