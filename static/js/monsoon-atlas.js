(() => {
  "use strict";
  const html = document.documentElement;
  html.classList.add("has-js");
  const copy = {
    en:{
      skip:"Skip to main content",tagline:"A farmer’s friend for a better tomorrow",openNav:"Open navigation",
      home:"Home",toolsNav:"Farm tools",journeyNav:"How it works",trustNav:"Our approach",signIn:"Sign in",openWorkspace:"Open workspace",
      heroEyebrow:"WEATHER · CROPS · MARKETS · SUPPORT",headlineA:"Empowering Farmers,",headlineB:"Naturally.",
      heroIntro:"Rythu Mitra brings weather updates, crop insights, market information and government scheme guidance into one calm, practical place.",
      heroPrimary:"Explore your farm workspace",heroSecondary:"Explore farm tools",heroTrust:"Clear source labels. Practical guidance. No made-up live readings.",
      weather:"Weather",weatherNote:"Check your forecast",crop:"Crop insights",cropNote:"Review a plant photo",market:"Market prices",marketNote:"Compare dated reports",
      weatherCardTitle:"Weather for your field",weatherCardDesc:"Select a district to see available information",cropCardTitle:"Crop insights",cropCardDesc:"Model screening is not a confirmed diagnosis",sourceAware:"SOURCE-AWARE",modelOutput:"MODEL OUTPUT",caption:"A field companion for every season",heroFooter:"LOCAL KNOWLEDGE · CLEARER SIGNALS · BETTER-INFORMED DECISIONS",scroll:"Scroll to explore",
      toolsEyebrow:"MADE FOR REAL FARM QUESTIONS",toolsTitleA:"Small decisions.",toolsTitleB:"Clearer next steps.",toolsIntro:"Start with the question in front of you. Explore useful guidance without losing track of where information came from.",
      toolWeather:"Weather & forecasts",toolWeatherDesc:"Choose your district to review forecasts, sources and timestamps.",toolWeatherLink:"Open weather",
      toolCrop:"Crop insights",toolCropDesc:"Request preliminary image screening with limitations clearly explained.",toolCropLink:"Explore crop health",
      toolMarket:"Market information",toolMarketDesc:"Compare reported prices by crop, market and observation date.",toolMarketLink:"Review prices",
      toolSchemes:"Schemes & support",toolSchemesDesc:"Find official starting points and verify eligibility with the relevant authority.",toolSchemesLink:"Explore support",
      toolsNote:"Availability depends on configured sources and services. Missing information stays clearly marked.",
      journeyEyebrow:"A CALMER WAY TO GET STARTED",journeyTitleA:"From farm context",journeyTitleB:"to the next decision.",journeyIntro:"The aim is not to replace farmer experience. It is to bring useful information together so the next step is easier to assess.",journeyLink:"Enter the farm workspace",
      stepOne:"Add your farm context",stepOneDesc:"Select your area and add crop or field details when you are ready.",stepTwo:"Review the signals",stepTwoDesc:"Check forecasts, crop screening, dated price reports and scheme information.",stepThree:"Choose your next step",stepThreeDesc:"Use information alongside local knowledge and qualified agricultural advice.",
      trustEyebrow:"TRUST IS PART OF THE INTERFACE",trustTitle:"Know what you are looking at.",trustIntro:"Forecasts, model estimates, market reports and curated resources are different things. Their status should always be visible.",trustCta:"Open the workspace",curated:"CURATED",unavailable:"UNAVAILABLE / DEMO",trustSource:"The source and time matter.",trustModel:"Predictions are estimates, not guarantees.",trustCurated:"Check official information at its source.",trustUnavailable:"Unavailable information must not look live.",
      closingEyebrow:"YOUR FARM. YOUR DECISIONS.",closingA:"A little more clarity",closingB:"for every season.",closingIntro:"Start with the information you need today. Explore the rest when it helps.",closingCta:"Enter Rythu Mitra",
      footerNote:"An academic farmer-support project. Information supports, but does not replace, local knowledge and qualified advice.",privacy:"Privacy",terms:"Terms",workspace:"Workspace",pauseMotion:"Pause motion",resumeMotion:"Resume motion",reducedMotion:"Reduced motion enabled"
    },
    te:{
      skip:"ప్రధాన విషయానికి వెళ్లండి",tagline:"మెరుగైన రేపటి కోసం రైతు మిత్రుడు",openNav:"నావిగేషన్ తెరవండి",
      home:"హోమ్",toolsNav:"వ్యవసాయ సాధనాలు",journeyNav:"ఇది ఎలా పనిచేస్తుంది",trustNav:"మా విధానం",signIn:"సైన్ ఇన్",openWorkspace:"వర్క్‌స్పేస్ తెరవండి",
      heroEyebrow:"వాతావరణం · పంటలు · మార్కెట్లు · సహాయం",headlineA:"రైతులకు సాధికారత,",headlineB:"సహజమైన తోడుతో.",
      heroIntro:"వాతావరణ సమాచారం, పంట వివరాలు, మార్కెట్ సమాచారం, ప్రభుత్వ పథకాల మార్గదర్శకం రైతు మిత్రలో ఒకే చోట లభిస్తాయి.",
      heroPrimary:"మీ వ్యవసాయ వర్క్‌స్పేస్ చూడండి",heroSecondary:"వ్యవసాయ సాధనాలు చూడండి",heroTrust:"మూల సమాచారం స్పష్టంగా చూపిస్తాం. కల్పిత ప్రత్యక్ష వివరాలు ఉండవు.",
      weather:"వాతావరణం",weatherNote:"వాతావరణ సూచన చూడండి",crop:"పంట వివరాలు",cropNote:"మొక్క ఫోటోను పరిశీలించండి",market:"మార్కెట్ ధరలు",marketNote:"తేదీతో ఉన్న నివేదికలు",
      weatherCardTitle:"మీ పొలానికి వాతావరణం",weatherCardDesc:"లభించే సమాచారానికి మీ జిల్లాను ఎంచుకోండి",cropCardTitle:"పంట వివరాలు",cropCardDesc:"మోడల్ పరిశీలన తుది నిర్ధారణ కాదు",sourceAware:"మూల సమాచారం",modelOutput:"మోడల్ ఫలితం",caption:"ప్రతి సీజన్‌కు రైతు మిత్రుడు",heroFooter:"స్థానిక అనుభవం · స్పష్టమైన సమాచారం · మెరుగైన నిర్ణయాలు",scroll:"మరింత చూడండి",
      toolsEyebrow:"నిజమైన వ్యవసాయ ప్రశ్నల కోసం",toolsTitleA:"చిన్న నిర్ణయాలు.",toolsTitleB:"స్పష్టమైన తదుపరి అడుగులు.",toolsIntro:"మీకు ఇప్పుడున్న ప్రశ్నతో ప్రారంభించండి. సమాచారం ఎక్కడి నుంచి వచ్చిందో తెలుసుకుంటూ ఉపయోగకరమైన మార్గదర్శకాన్ని చూడండి.",
      toolWeather:"వాతావరణం మరియు సూచనలు",toolWeatherDesc:"సూచనలు, మూలం, సమయ వివరాల కోసం మీ జిల్లాను ఎంచుకోండి.",toolWeatherLink:"వాతావరణం చూడండి",
      toolCrop:"పంట వివరాలు",toolCropDesc:"పరిమితులను స్పష్టంగా చూపించే ప్రాథమిక పరిశీలన కోసం మొక్క ఫోటోను సమర్పించండి.",toolCropLink:"పంట ఆరోగ్యం చూడండి",
      toolMarket:"మార్కెట్ సమాచారం",toolMarketDesc:"పంట, మార్కెట్, నివేదిక తేదీ ఆధారంగా ధరలను పోల్చండి.",toolMarketLink:"ధరలను పరిశీలించండి",
      toolSchemes:"పథకాలు మరియు సహాయం",toolSchemesDesc:"అధికారిక లింకులు చూడండి; అర్హతను సంబంధిత అధికారితో నిర్ధారించండి.",toolSchemesLink:"సహాయ పథకాలు చూడండి",
      toolsNote:"లభించే సమాచారం ఎంచుకున్న మూలం మరియు సేవలపై ఆధారపడుతుంది. లేని వివరాలు స్పష్టంగా చూపిస్తాం.",
      journeyEyebrow:"సులభంగా ప్రారంభించండి",journeyTitleA:"మీ పొలం వివరాల నుంచి",journeyTitleB:"తదుపరి నిర్ణయం వరకు.",journeyIntro:"రైతు అనుభవాన్ని భర్తీ చేయడం మా లక్ష్యం కాదు. ఉపయోగకరమైన సమాచారాన్ని ఒకచోట చేర్చి తదుపరి అడుగును అంచనా వేయడంలో సహాయపడటమే లక్ష్యం.",journeyLink:"వ్యవసాయ వర్క్‌స్పేస్‌లోకి వెళ్లండి",
      stepOne:"మీ పొలం వివరాలు నమోదు చేయండి",stepOneDesc:"మీ ప్రాంతాన్ని ఎంచుకుని, అవసరమైనప్పుడు పంట లేదా పొలం వివరాలు నమోదు చేయండి.",stepTwo:"సమాచారాన్ని పరిశీలించండి",stepTwoDesc:"వాతావరణం, పంట ప్రాథమిక పరిశీలన, తేదీతో ఉన్న ధరల నివేదికలు, పథకాల సమాచారాన్ని చూడండి.",stepThree:"తదుపరి అడుగును ఎంచుకోండి",stepThreeDesc:"స్థానిక అనుభవం మరియు అర్హులైన వ్యవసాయ నిపుణుల సలహాతో సమాచారాన్ని ఉపయోగించండి.",
      trustEyebrow:"నమ్మకం కూడా రూపకల్పనలో భాగమే",trustTitle:"మీరు చూస్తున్న సమాచారం ఏమిటో తెలుసుకోండి.",trustIntro:"వాతావరణ సూచనలు, మోడల్ అంచనాలు, మార్కెట్ నివేదికలు, సంకలనం చేసిన వనరులు వేర్వేరు. వాటి స్థితి స్పష్టంగా ఉండాలి.",trustCta:"వర్క్‌స్పేస్ తెరవండి",curated:"సంకలనం చేసినది",unavailable:"లభ్యం కాదు / డెమో",trustSource:"మూలం మరియు సమయం ముఖ్యమైనవి.",trustModel:"అంచనాలు హామీలు కావు.",trustCurated:"అధికారిక సమాచారాన్ని మూల వెబ్‌సైట్‌లో నిర్ధారించండి.",trustUnavailable:"లభ్యం కాని సమాచారం ప్రత్యక్షంగా ఉన్నట్లు చూపకూడదు.",
      closingEyebrow:"మీ పొలం. మీ నిర్ణయాలు.",closingA:"ప్రతి సీజన్‌లో",closingB:"మరింత స్పష్టత.",closingIntro:"ఈరోజు అవసరమైన సమాచారంతో ప్రారంభించండి. ఉపయోగపడినప్పుడు మిగతా వివరాలు చూడండి.",closingCta:"రైతు మిత్రలోకి వెళ్లండి",
      footerNote:"ఇది విద్యా ప్రాజెక్ట్. సమాచారం స్థానిక అనుభవం లేదా అర్హులైన నిపుణుల సలహాకు ప్రత్యామ్నాయం కాదు.",privacy:"గోప్యత",terms:"నిబంధనలు",workspace:"వర్క్‌స్పేస్",pauseMotion:"చలనాన్ని ఆపండి",resumeMotion:"చలనాన్ని మళ్లీ ప్రారంభించండి",reducedMotion:"తక్కువ చలనం ప్రారంభించబడింది"
    }
  };
  const langButtons = Array.from(document.querySelectorAll("[data-language]"));
  const motionButton = document.getElementById("motionToggle");
  const menuButton = document.getElementById("menuToggle");
  const nav = document.getElementById("primaryNav");
  const reduced = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  let lang = "en";
  let pausedByUser = false;
  const safeGet = key => { try { return localStorage.getItem(key); } catch (_) { return null; } };
  const safeSet = (key, value) => { try { localStorage.setItem(key, value); } catch (_) {} };

  function updateMotionLabel() {
    if (!motionButton) return;
    const paused = reduced || pausedByUser;
    motionButton.setAttribute("aria-pressed", String(paused));
    const label = motionButton.querySelector("[data-i18n]");
    if (label) label.textContent = reduced ? copy[lang].reducedMotion : (pausedByUser ? copy[lang].resumeMotion : copy[lang].pauseMotion);
  }
  function setLanguage(next) {
    lang = next === "te" ? "te" : "en";
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach(node => {
      const key = node.getAttribute("data-i18n");
      if (Object.prototype.hasOwnProperty.call(copy[lang], key)) node.textContent = copy[lang][key];
    });
    langButtons.forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.language === lang));
      button.setAttribute("aria-label", lang === "te"
        ? (button.dataset.language === "te" ? "తెలుగు భాష ఎంచుకోబడింది" : "Switch to English")
        : (button.dataset.language === "en" ? "English selected" : "తెలుగుకు మారండి"));
    });
    safeSet("rythu-mitra-landing-language", lang);
    updateMotionLabel();
  }
  langButtons.forEach(button => button.addEventListener("click", () => setLanguage(button.dataset.language)));
  if (motionButton) motionButton.addEventListener("click", () => {
    if (reduced) { pausedByUser = true; document.documentElement.classList.add("motion-paused"); }
    else { pausedByUser = !pausedByUser; document.documentElement.classList.toggle("motion-paused", pausedByUser); }
    updateMotionLabel();
  });
  if (menuButton && nav) {
    menuButton.addEventListener("click", () => {
      const open = menuButton.getAttribute("aria-expanded") !== "true";
      menuButton.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
      const label = menuButton.querySelector(".sr-only");
      if (label) label.textContent = lang === "te" ? (open ? "నావిగేషన్ మూసివేయండి" : "నావిగేషన్ తెరవండి") : (open ? "Close navigation" : "Open navigation");
    });
    nav.addEventListener("click", event => {
      if (!event.target.closest("a")) return;
      nav.classList.remove("is-open");
      menuButton.setAttribute("aria-expanded", "false");
    });
    document.addEventListener("click", event => {
      if (!nav.contains(event.target) && !menuButton.contains(event.target)) {
        nav.classList.remove("is-open");
        menuButton.setAttribute("aria-expanded", "false");
      }
    });
  }
  const reveals = Array.from(document.querySelectorAll(".reveal"));
  if (reduced || !("IntersectionObserver" in window)) reveals.forEach(node => node.classList.add("is-visible"));
  else {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        obs.unobserve(entry.target);
      });
    }, {threshold:.12, rootMargin:"0px 0px -28px 0px"});
    reveals.forEach(node => observer.observe(node));
  }
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) document.documentElement.classList.add("motion-paused");
    else if (!pausedByUser && !reduced) document.documentElement.classList.remove("motion-paused");
  });
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
  setLanguage(safeGet("rythu-mitra-landing-language") === "te" ? "te" : "en");
  if (reduced) document.documentElement.classList.add("motion-paused");
  updateMotionLabel();
})();