/* Field Atlas project showcase interactions.
 * No model calls or backend writes are made here. Upload previews are local-only.
 */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const state = { lang: 'en', technical: false, motionPaused: false, cropImageUrl: '', lab: '' };

  const translations = {
    en: {
      'nav.story':'The story','nav.approach':'Our approach','nav.models':'Models','nav.architecture':'Architecture','nav.roadmap':'Roadmap',
      'header.technical':'Technical view','hero.eyebrow':'A FARMER DECISION-SUPPORT PROJECT',
      'hero.title':'Rooted in the field.<br><em>Designed for clearer</em><br>decisions.',
      'hero.intro':'Rythu Mitra brings crop planning, crop-health exploration and farm decision support into one thoughtful experience—built around the realities of small and marginal farmers in Telangana.',
      'hero.explore':'Explore the project','hero.models':'Meet the models','hero.noteTitle':'One connected idea.',
      'hero.noteBody':'Multiple tools. Clearer context. Human decisions.','hero.place':'TELANGANA, INDIA',
      'story.need':'THE NEED','story.intro':'Useful agricultural information can be scattered across weather, soil, crop-health, market and scheme sources. <em>Rythu Mitra explores how those pieces could become easier to understand in one place.</em>',
      'story.kicker':'01 / THE PROJECT STORY','story.title':'Not another information pile.<br><em>A clearer way through.</em>',
      'story.p1':'For a farmer, information matters most when it helps answer a practical question: what should I check, what do I know, and what should I verify before acting?',
      'story.p2':'Our project brings those questions into one proposed decision-support experience—designed to be understandable, transparent and extensible.',
      'features.kicker':'02 / WHAT THE PLATFORM EXPLORES','features.title':'A connected view<br><em>of the farm.</em>',
      'features.intro':'Explore the capability areas. Each can grow into its own module as the project develops.',
      'models.kicker':'03 / THE MODEL SHOWCASE','models.title':'Show the thinking.<br><em>Be honest about the output.</em>',
      'models.intro':'A model deserves more than a badge. Its inputs, pipeline, status, evaluation evidence and limitations should be inspectable.',
      'arch.kicker':'04 / SYSTEM DESIGN','arch.title':'One experience.<br><em>Clear boundaries.</em>',
      'arch.intro':'The interface, application logic, models and external data providers should remain distinct. That makes future improvements safer and easier to explain.',
      'status.kicker':'05 / BUILD TRANSPARENCY','status.title':'Show what exists.<br><em>Make the next step visible.</em>',
      'roadmap.kicker':'06 / GROW WITH THE PROJECT','roadmap.title':'Designed to grow.<br><em>Not locked to today.</em>',
      'collab.kicker':'07 / BUILD IT THOUGHTFULLY','collab.title':'A promising idea grows<br><em>with the right people.</em>',
      'collab.button':'Discuss collaboration','footer.note':'A farmer decision-support project concept.<br>Built with care; transparent about what remains to be verified.'
    },
    te: {
      'nav.story':'ప్రాజెక్ట్ కథ','nav.approach':'మా విధానం','nav.models':'మోడళ్లు','nav.architecture':'సాంకేతిక నిర్మాణం','nav.roadmap':'భవిష్యత్ ప్రణాళిక',
      'header.technical':'సాంకేతిక వివరాలు','hero.eyebrow':'రైతు నిర్ణయ సహాయక ప్రాజెక్ట్',
      'hero.title':'పొలంలో పుట్టిన ఆలోచన.<br><em>మరింత స్పష్టమైన</em><br>నిర్ణయాల కోసం.',
      'hero.intro':'రైతు మిత్ర పంట ప్రణాళిక, పంట ఆరోగ్య పరిశీలన, వ్యవసాయ నిర్ణయ సహాయాన్ని ఒకే అనుభవంగా తీసుకురావాలని లక్ష్యంగా పెట్టుకుంది—తెలంగాణలోని చిన్న మరియు సన్నకారు రైతుల అవసరాలను దృష్టిలో ఉంచుకుని.',
      'hero.explore':'ప్రాజెక్ట్‌ను చూడండి','hero.models':'మోడళ్లను చూడండి','hero.noteTitle':'ఒక సమగ్ర ఆలోచన.',
      'hero.noteBody':'అనేక సాధనాలు. స్పష్టమైన సమాచారం. మనుషుల నిర్ణయాలు.','hero.place':'తెలంగాణ, భారత్',
      'story.need':'అవసరం','story.intro':'వాతావరణం, నేల, పంట ఆరోగ్యం, మార్కెట్ ధరలు మరియు ప్రభుత్వ పథకాల సమాచారం వేర్వేరు చోట్ల ఉండవచ్చు. <em>ఈ సమాచారాన్ని ఒకే చోట సులభంగా అర్థం చేసుకునే విధానాన్ని రైతు మిత్ర పరిశీలిస్తోంది.</em>',
      'story.kicker':'01 / ప్రాజెక్ట్ కథ','story.title':'సమాచార గందరగోళం కాదు.<br><em>స్పష్టమైన దారి.</em>',
      'story.p1':'రైతుకు సమాచారం అంటే ఆచరణలో ఉపయోగపడే ప్రశ్నలకు సమాధానం: ఏం పరిశీలించాలి, ఏం తెలుసు, చర్యకు ముందు ఏది ధృవీకరించాలి?',
      'story.p2':'ఈ ప్రశ్నలను అర్థమయ్యేలా, పారదర్శకంగా, భవిష్యత్తులో విస్తరించగల నిర్ణయ సహాయక అనుభవంగా రూపొందించడమే మా లక్ష్యం.',
      'features.kicker':'02 / వేదికలోని విభాగాలు','features.title':'వ్యవసాయానికి<br><em>ఒక సమగ్ర దృక్కోణం.</em>',
      'features.intro':'ప్రతి సామర్థ్యం ప్రాజెక్ట్ అభివృద్ధి చెందుతున్న కొద్దీ స్వతంత్ర విభాగంగా విస్తరించవచ్చు.',
      'models.kicker':'03 / మోడళ్ల పరిచయం','models.title':'విధానాన్ని చూపండి.<br><em>ఫలితాలపై నిజాయితీగా ఉండండి.</em>',
      'models.intro':'మోడల్‌కు ఒక బ్యాడ్జ్ మాత్రమే సరిపోదు. దాని ఇన్‌పుట్లు, ప్రక్రియ, స్థితి, మూల్యాంకన ఆధారాలు, పరిమితులు పరిశీలించగలిగేలా ఉండాలి.',
      'arch.kicker':'04 / సిస్టమ్ రూపకల్పన','arch.title':'ఒక అనుభవం.<br><em>స్పష్టమైన విభజన.</em>',
      'arch.intro':'ఇంటర్‌ఫేస్, అప్లికేషన్ లాజిక్, మోడళ్లు మరియు బాహ్య డేటా సేవలను వేర్వేరుగా ఉంచితే భవిష్యత్ మెరుగుదలలు సురక్షితంగా, స్పష్టంగా ఉంటాయి.',
      'status.kicker':'05 / అమలు పారదర్శకత','status.title':'ఉన్నదాన్ని చూపండి.<br><em>తదుపరి అడుగును స్పష్టం చేయండి.</em>',
      'roadmap.kicker':'06 / ప్రాజెక్ట్‌తో పాటు ఎదగడం','roadmap.title':'విస్తరణకు సిద్ధంగా.<br><em>ఈ రోజుకే పరిమితం కాదు.</em>',
      'collab.kicker':'07 / ఆలోచనతో నిర్మిద్దాం','collab.title':'మంచి ఆలోచన ఎదుగుతుంది<br><em>సరైన వ్యక్తులతో.</em>',
      'collab.button':'సహకారం గురించి చర్చించండి','footer.note':'రైతు నిర్ణయ సహాయక ప్రాజెక్ట్ కాన్సెప్ట్.<br>ధృవీకరించాల్సిన విషయాలపై పారదర్శకతతో రూపొందించబడింది.'
    }
  };
  const mapped = [
    ['.desktop-nav a:nth-child(1)','nav.story'],['.desktop-nav a:nth-child(2)','nav.approach'],['.desktop-nav a:nth-child(3)','nav.models'],['.desktop-nav a:nth-child(4)','nav.architecture'],['.desktop-nav a:nth-child(5)','nav.roadmap'],
    ['#technicalToggle','header.technical'],['.hero-copy .eyebrow','hero.eyebrow'],['.hero-copy h1','hero.title'],['.hero-intro','hero.intro'],
    ['.hero-buttons .button-dark','hero.explore'],['.hero-buttons .text-link','hero.models'],['.hero-note strong','hero.noteTitle'],['.hero-note span:last-child','hero.noteBody'],
    ['.landscape-caption span:last-child','hero.place'],['.strip-label','story.need'],['.intro-strip p','story.intro'],
    ['.story-section .section-kicker','story.kicker'],['.two-col-heading h2','story.title'],['.two-col-heading div p:first-child','story.p1'],['.two-col-heading div p:last-child','story.p2'],
    ['.feature-section .section-kicker','features.kicker'],['.feature-section .section-heading-row h2','features.title'],['.feature-section .section-heading-row p','features.intro'],
    ['.model-section .section-kicker','models.kicker'],['.model-section .section-heading-row h2','models.title'],['.model-section .section-heading-row p','models.intro'],
    ['.architecture-section .section-kicker','arch.kicker'],['.architecture-section .section-heading-row h2','arch.title'],['.architecture-section .section-heading-row p','arch.intro'],
    ['.status-section .section-kicker','status.kicker'],['.status-section .section-heading-row h2','status.title'],
    ['.roadmap-section .section-kicker','roadmap.kicker'],['.roadmap-section .section-heading-row h2','roadmap.title'],
    ['.collab-copy .section-kicker','collab.kicker'],['.collab-copy h2','collab.title'],['#collabButton','collab.button'],['.site-footer>p','footer.note']
  ];
  const englishSnapshots = new Map();
  function setLanguage(lang) {
    state.lang = lang;
    document.documentElement.lang = lang === 'te' ? 'te' : 'en';
    const dict = translations[lang];
    mapped.forEach(([selector, key]) => {
      const el = $(selector);
      if (!el) return;
      if (!englishSnapshots.has(selector)) englishSnapshots.set(selector, el.innerHTML);
      el.innerHTML = dict[key] || englishSnapshots.get(selector);
    });
    $('#languageToggle').textContent = lang === 'en' ? 'తెలుగు ↗' : 'English ↗';
    $('#languageToggle').setAttribute('aria-label',lang==='en'?'Switch to Telugu':'Switch to English');
    const tech = $('#technicalToggle');
    tech.setAttribute('aria-pressed',String(state.technical));
    document.body.dataset.language = lang;
  }
  $('#languageToggle')?.addEventListener('click', () => setLanguage(state.lang === 'en' ? 'te' : 'en'));

  $('#menuToggle')?.addEventListener('click', () => {
    const menu = $('.desktop-nav');
    const open = menu.classList.toggle('open');
    $('#menuToggle').setAttribute('aria-expanded',String(open));
    $('#menuToggle').textContent = open ? '×' : '☰';
  });
  $$('.desktop-nav a').forEach(link => link.addEventListener('click', () => {
    $('.desktop-nav').classList.remove('open');
    $('#menuToggle')?.setAttribute('aria-expanded','false');
    if ($('#menuToggle')) $('#menuToggle').textContent = '☰';
  }));

  $('#technicalToggle')?.addEventListener('click', () => {
    state.technical = !state.technical;
    document.body.classList.toggle('technical-mode',state.technical);
    $('#technicalToggle').setAttribute('aria-pressed',String(state.technical));
    $('#technicalToggle').innerHTML = state.lang === 'te' ? (state.technical ? 'సాధారణ వీక్షణ <span>↗</span>' : 'సాంకేతిక వివరాలు <span>↗</span>') : (state.technical ? 'Overview view <span>↗</span>' : 'Technical view <span>↗</span>');
    const details = $('#technicalDetails');
    if(details) details.hidden = !state.technical;
    $('.accordion-panel').forEach(panel => { panel.hidden = !state.technical; });
    $('.accordion-trigger').forEach(btn => { btn.setAttribute('aria-expanded',String(state.technical)); btn.querySelector('span').textContent = state.technical ? '−' : '＋'; });
  });

  $$('.accordion-trigger').forEach(btn => btn.addEventListener('click', () => {
    const panel = $('#'+btn.dataset.accordion);
    const open = btn.getAttribute('aria-expanded') !== 'true';
    btn.setAttribute('aria-expanded',String(open));
    panel.hidden = !open;
    btn.querySelector('span').textContent = open ? '−' : '＋';
  }));

  const dialog = $('#infoDialog');
  function showInfo(title, body, kicker='PROJECT NOTE') {
    $('#dialogKicker').textContent = kicker;
    $('#dialogTitle').textContent = title;
    $('#dialogBody').textContent = body;
    if (!dialog.open) dialog.showModal();
  }
  $('#statusDetails')?.addEventListener('click', () => showInfo(
    'How we label status',
    'BUILT means the visible interface or behavior exists in this branch. DEMO means the content is illustrative or runs locally for demonstration. UNAVAILABLE means an integration is not connected or has not been verified. REAL OUTPUT should appear only after the actual model/provider has run successfully and its response has been validated. A failed request must never silently turn into a real-looking demo result.'
  ));
  $('#collabButton')?.addEventListener('click', () => showInfo(
    'Let’s shape the next iteration',
    'This prototype does not have a partnership form or contact address connected yet. Useful next steps for a collaboration discussion: define the target users, identify the model artifacts and evidence that can be demonstrated, choose one end-to-end feature to validate, and agree how user feedback and limitations will be documented.',
    'COLLABORATION'
  ));
  $('.dialog-close')?.addEventListener('click', () => dialog?.close());

  const lab = $('#demoLab');
  const labBody = $('#demoLabBody');
  function openLab(kind) {
    state.lab = kind;
    lab.hidden = false;
    if(kind === 'crop') {
      $('#demoLabTitle').textContent = 'Crop recommendation — input walkthrough';
      labBody.innerHTML = '<p class="muted-copy">Enter illustrative inputs to see how a future request might be organised. This does not call the model or produce a crop recommendation.</p><form id="cropDemoForm" class="demo-form"><label>Soil type<select name="soil" required><option value="">Choose a soil type</option><option>Red soil</option><option>Black soil</option><option>Loamy soil</option><option>Sandy soil</option></select></label><label>Season<select name="season" required><option value="">Choose a season</option><option>Kharif</option><option>Rabi</option><option>Summer</option></select></label><label>Rainfall input (mm)<input name="rainfall" type="number" min="0" max="3000" value="780" required></label><label>Soil pH<input name="ph" type="number" min="0" max="14" step=".1" value="6.5" required></label><label>District (optional)<input name="district" placeholder="Enter a district"></label><label>Mode<select name="mode"><option>Walkthrough only</option></select></label><button class="button button-dark" type="submit">Validate walkthrough ↗</button></form><div id="demoOutput" class="demo-message" role="status">No output yet. Model inference is unavailable in this showcase interaction.</div>';
      $('#cropDemoForm').addEventListener('submit', e => {
        e.preventDefault();
        if(!e.currentTarget.reportValidity()) return;
        const data = Object.fromEntries(new FormData(e.currentTarget));
        $('#demoOutput').textContent = 'DEMO WALKTHROUGH ONLY — browser input validation passed for '+data.soil+', '+data.season+', '+data.rainfall+' mm rainfall and pH '+data.ph+'. No API call was made and no crop was predicted. A real result needs a verified model response.';
      });
    } else {
      $('#demoLabTitle').textContent = 'Plant-health image — local preview';
      labBody.innerHTML = '<p class="muted-copy">Select a plant image to preview the upload flow. The image stays in this browser page; it is not uploaded and is not diagnosed.</p><div class="demo-image-row"><div id="imagePreviewPlaceholder" class="demo-image-preview" aria-label="Image preview placeholder"></div><label>Choose crop image<input id="showcaseImageInput" type="file" accept="image/*"></label></div><div id="imageStatus" class="demo-message" role="status">No image selected. Disease classification is unavailable.</div>';
      $('#showcaseImageInput').addEventListener('change', e => {
        const file = e.target.files?.[0];
        if(!file) return;
        if(!file.type.startsWith('image/')) { $('#imageStatus').textContent='Please choose an image file.'; return; }
        if(state.cropImageUrl) URL.revokeObjectURL(state.cropImageUrl);
        state.cropImageUrl = URL.createObjectURL(file);
        const img = document.createElement('img');
        img.src=state.cropImageUrl;img.alt='Selected plant image preview';img.className='demo-image-preview';
        $('#imagePreviewPlaceholder').replaceWith(img);
        $('#imageStatus').textContent='LOCAL IMAGE PREVIEW — '+file.name+'. Nothing was uploaded; no disease class or confidence score was generated because the model was not called.';
      });
    }
    lab.scrollIntoView({behavior:state.motionPaused?'auto':'smooth',block:'center'});
  }
  $$('[data-demo]').forEach(btn => btn.addEventListener('click', () => openLab(btn.dataset.demo)));
  $('#closeLab')?.addEventListener('click', () => {
    lab.hidden=true;
    if(state.cropImageUrl){URL.revokeObjectURL(state.cropImageUrl);state.cropImageUrl='';}
    state.lab='';
  });

  $('#motionToggle')?.addEventListener('click', () => {
    state.motionPaused = !state.motionPaused;
    document.body.classList.toggle('motion-paused',state.motionPaused);
    $('#motionToggle').textContent = state.motionPaused ? '▶' : 'Ⅱ';
    $('#motionToggle').setAttribute('aria-pressed',String(state.motionPaused));
    $('#motionToggle').setAttribute('aria-label',state.motionPaused?'Resume decorative motion':'Pause decorative motion');
  });

  const sections = $$('main section[id]');
  const navLinks = $$('[data-nav]');
  if('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if(entry.isIntersecting) {
          navLinks.forEach(link => link.classList.toggle('is-current',link.dataset.nav === entry.target.id));
          entry.target.classList.add('is-visible');
        }
      });
    },{rootMargin:'-22% 0px -62% 0px',threshold:0});
    sections.forEach(section => observer.observe(section));
    $$('.story-card,.feature-tile,.model-card,.status-grid article').forEach(el => {
      el.classList.add('scroll-reveal');
      const itemObserver = new IntersectionObserver(entries => entries.forEach(entry => {
        if(entry.isIntersecting){entry.target.classList.add('is-visible');itemObserver.unobserve(entry.target);}
      }),{threshold:.14});
      itemObserver.observe(el);
    });
  } else {
    $$('.scroll-reveal').forEach(el=>el.classList.add('is-visible'));
  }

  // Keep the demo lab state visibly separate from real outputs.
  window.RythuMitraShowcase = Object.freeze({
    version:'field-atlas-1',
    capabilities:['project-story','model-showcase','technical-architecture','roadmap','local-only-demos'],
    integrations:{cropRecommendation:'unavailable in this showcase',plantHealth:'unavailable in this showcase',weather:'not connected here',markets:'not connected here',authentication:'not used by this showcase'},
    statusVocabulary:['BUILT','DEMO','UNAVAILABLE','REAL OUTPUT']
  });
  setLanguage('en');
})();