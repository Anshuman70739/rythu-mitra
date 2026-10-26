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
      'story.card1':'Information lives in different places.','story.card1p':'Finding, comparing and interpreting useful context can take time—especially when connectivity, language and access vary.',
      'story.card2':'Bring the context together.','story.card2p':'A single workspace can connect farm inputs, guidance and reference information while showing where each result comes from.',
      'story.card3':'Support decisions, not replace people.','story.card3p':'Models and data should assist a farmer and local experts—not hide uncertainty or pretend a prediction is a guarantee.',
      'tile.crop':'Crop recommendation','tile.cropp':'Explore how soil and environmental inputs could be organised for a model-assisted crop recommendation.',
      'tile.health':'Plant-health exploration','tile.healthp':'A careful image workflow with a place for real model status, uncertainty and expert follow-up.',
      'tile.weather':'Weather & advisories','tile.weatherp':'Make forecast source, freshness and local relevance visible instead of presenting unsupported certainty.',
      'tile.market':'Markets & farm economics','tile.marketp':'Compare source-labelled market information and transparent assumptions for income calculations.',
      'feature.more':'ALSO IN THE ROADMAP','feature.morep':'Crop calendar · Farm records · Government scheme references · Yield and storage calculations · Equipment and services · English and Telugu · Offline-aware access',
      'model.crop':'Crop recommendation','model.cropp':'Explore a future workflow from farm and soil inputs to a ranked recommendation with explanation and uncertainty.',
      'model.health':'Plant-health image analysis','model.healthp':'A transparent image-to-model pathway designed to keep a real result distinct from an upload preview or demonstration.',
      'integrity.title':'Evidence before claims.','integrity.p':'This showcase intentionally does not claim live inference, validated model accuracy, real-time market prices or current weather. Those states should change only after the relevant integration and checks are confirmed.',
      'arch.map.title':'Proposed integration view','arch.map.p':'Conceptual diagram based on the project\'s intended components; not a claim that every connection is currently working.',
      'status.card1':'Project story & visual prototype','status.card1p':'Collaborator-facing introduction, modular sections and interactive technical views.',
      'status.card2':'Model and provider verification','status.card2p':'Inspect current model artifacts, API responses, evaluation evidence and external data sources before claiming readiness.',
      'status.card3':'Real model demonstrations','status.card3p':'Connect validated inference, traceable source labels, loading and error states, and model limitations.',
      'roadmap.card1':'Establish the evidence','roadmap.card1p':'Confirm current routes, models, data sources, evaluation and what works end-to-end.',
      'roadmap.card2':'Connect real capabilities','roadmap.card2p':'Wire one feature at a time, with validated responses, loading/error states and source labels.',
      'roadmap.card3':'Add what farmers and collaborators need','roadmap.card3p':'Potential additions include offline-friendly workflows, local-language guidance, expert connections and additional verified services.',
      'future.title':'Room for the next good idea.','future.p':'These are possible directions—not promised or completed features.',
      'collab.kicker':'07 / BUILD IT THOUGHTFULLY','collab.title':'A promising idea grows<br><em>with the right people.</em>',
      'collab.intro':'Rythu Mitra is an academic project in development. Feedback from collaborators, domain experts and potential users can help prioritise what to validate and build next.',
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
      'story.card1':'సమాచారం వేర్వేరు చోట్ల ఉంది.','story.card1p':'సమాచారాన్ని కనుగొనడం, పోల్చడం, అర్థం చేసుకోవడం సమయం తీసుకోవచ్చు—ముఖ్యంగా నెట్‌వర్క్, భాష, అందుబాటు పరిమితంగా ఉన్నప్పుడు.',
      'story.card2':'సమాచారాన్ని ఒకచోట కలపండి.','story.card2p':'ఒకే వేదిక వ్యవసాయ ఇన్‌పుట్లు, మార్గదర్శకం, సూచన సమాచారాన్ని కలిపి ప్రతి ఫలితం ఎక్కడి నుంచి వచ్చిందో చూపగలదు.',
      'story.card3':'నిర్ణయాలకు తోడ్పడాలి, మనుషుల స్థానంలో కాదు.','story.card3p':'మోడళ్లు, డేటా రైతులు మరియు స్థానిక నిపుణులకు సహాయం చేయాలి—అనిశ్చితిని దాచకూడదు, అంచనాను హామీగా చూపకూడదు.',
      'tile.crop':'పంట సిఫార్సు','tile.cropp':'నేల మరియు పర్యావరణ ఇన్‌పుట్లను మోడల్ ఆధారిత పంట సిఫార్సు కోసం ఎలా ఏర్పాటు చేయవచ్చో చూడండి.',
      'tile.health':'పంట ఆరోగ్య పరిశీలన','tile.healthp':'నిజమైన మోడల్ స్థితి, అనిశ్చితి, నిపుణుల సలహాకు చోటు కలిగిన చిత్ర ప్రక్రియ.',
      'tile.weather':'వాతావరణం & సూచనలు','tile.weatherp':'ధృవీకరించని నిశ్చయంగా చూపకుండా వాతావరణ మూలం, తాజాదనం, స్థానిక ప్రాసంగికతను చూపండి.',
      'tile.market':'మార్కెట్లు & వ్యవసాయ ఆర్థికం','tile.marketp':'మూలం చూపిన మార్కెట్ సమాచారాన్ని, ఆదాయ లెక్కల స్పష్టమైన ఊహాగానాలను పోల్చండి.',
      'feature.more':'భవిష్యత్ ప్రణాళికలో మరిన్ని','feature.morep':'పంట క్యాలెండర్ · వ్యవసాయ రికార్డులు · ప్రభుత్వ పథకాల సూచనలు · దిగుబడి మరియు నిల్వ లెక్కలు · పరికరాలు, సేవలు · తెలుగు మరియు ఇంగ్లీష్ · ఆఫ్‌లైన్ వినియోగం',
      'model.crop':'పంట సిఫార్సు','model.cropp':'వ్యవసాయ మరియు నేల ఇన్‌పుట్ల నుంచి వివరణ, అనిశ్చితితో కూడిన సిఫార్సు వరకు భవిష్యత్ ప్రక్రియను చూడండి.',
      'model.health':'పంట ఆరోగ్య చిత్ర విశ్లేషణ','model.healthp':'నిజమైన ఫలితాన్ని చిత్ర ప్రివ్యూ లేదా డెమో నుంచి వేరు చూపించే పారదర్శక చిత్ర-మోడల్ ప్రక్రియ.',
      'integrity.title':'వాదనలకు ముందు ఆధారాలు.','integrity.p':'ఈ ప్రదర్శన ప్రత్యక్ష ఇన్‌ఫరెన్స్, ధృవీకరించిన మోడల్ ఖచ్చితత్వం, తాజా మార్కెట్ ధరలు లేదా ప్రస్తుత వాతావరణం ఉన్నాయని చెప్పదు. సంబంధిత ఇంటిగ్రేషన్ మరియు తనిఖీలు పూర్తైన తర్వాతే స్థితిని మార్చాలి.',
      'arch.map.title':'ప్రతిపాదిత అనుసంధాన దృశ్యం','arch.map.p':'ప్రాజెక్ట్‌లో ఉద్దేశించిన భాగాల ఆధారంగా రూపొందించిన భావనాత్మక చిత్రం; ప్రతి అనుసంధానం ప్రస్తుతం పనిచేస్తుందని ఇది నిర్ధారించదు.',
      'status.card1':'ప్రాజెక్ట్ కథ & దృశ్య నమూనా','status.card1p':'సహకారుల కోసం పరిచయం, విభాగాల రూపకల్పన, ఇంటరాక్టివ్ సాంకేతిక వీక్షణలు.',
      'status.card2':'మోడల్ మరియు సేవల ధృవీకరణ','status.card2p':'సిద్ధంగా ఉందని చెప్పే ముందు మోడల్ ఫైళ్లు, API ప్రతిస్పందనలు, మూల్యాంకన ఆధారాలు, బాహ్య డేటా మూలాలను పరిశీలించాలి.',
      'status.card3':'నిజమైన మోడల్ ప్రదర్శనలు','status.card3p':'ధృవీకరించిన ఇన్‌ఫరెన్స్, మూలం లేబుళ్లు, లోడింగ్/లోప స్థితులు, మోడల్ పరిమితులను అనుసంధానించాలి.',
      'roadmap.card1':'ఆధారాలను నిర్ధారించండి','roadmap.card1p':'ప్రస్తుత రూట్లు, మోడళ్లు, డేటా మూలాలు, మూల్యాంకనం, మొదటి నుంచి చివరి వరకు ఏది పనిచేస్తుందో నిర్ధారించండి.',
      'roadmap.card2':'నిజమైన సామర్థ్యాలను అనుసంధానించండి','roadmap.card2p':'ధృవీకరించిన ప్రతిస్పందనలు, లోడింగ్/లోప స్థితులు, మూల లేబుళ్లతో ఒక్కో విభాగాన్ని అనుసంధానించండి.',
      'roadmap.card3':'రైతులు, సహకారులు కోరేది చేర్చండి','roadmap.card3p':'ఆఫ్‌లైన్ పనితీరు, స్థానిక భాష మార్గదర్శనం, నిపుణుల అనుసంధానం, ధృవీకరించిన సేవలు భవిష్యత్ అవకాశాలు.',
      'future.title':'తదుపరి మంచి ఆలోచనకు స్థలం.','future.p':'ఇవి సాధ్యమైన దిశలు మాత్రమే—పూర్తయిన లేదా హామీ ఇచ్చిన ఫీచర్లు కావు.',
      'collab.kicker':'07 / ఆలోచనతో నిర్మిద్దాం','collab.title':'మంచి ఆలోచన ఎదుగుతుంది<br><em>సరైన వ్యక్తులతో.</em>',
      'collab.intro':'రైతు మిత్ర అభివృద్ధిలో ఉన్న విద్యా ప్రాజెక్ట్. సహకారులు, రంగ నిపుణులు, భావితర వినియోగదారుల అభిప్రాయాలు తదుపరి ధృవీకరణ, నిర్మాణ పనులకు ప్రాధాన్యం నిర్ణయించడంలో సహాయపడతాయి.',
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
    ['.story-card:nth-child(1) h3','story.card1'],['.story-card:nth-child(1) p','story.card1p'],['.story-card:nth-child(2) h3','story.card2'],['.story-card:nth-child(2) p','story.card2p'],['.story-card:nth-child(3) h3','story.card3'],['.story-card:nth-child(3) p','story.card3p'],
    ['.tile-crop h3','tile.crop'],['.tile-crop p','tile.cropp'],['.tile-health h3','tile.health'],['.tile-health p','tile.healthp'],['.tile-weather h3','tile.weather'],['.tile-weather p','tile.weatherp'],['.tile-market h3','tile.market'],['.tile-market p','tile.marketp'],
    ['.feature-more span','feature.more'],['.feature-more p','feature.morep'],['.model-card-crop h3','model.crop'],['.model-card-crop>p','model.cropp'],['.model-card-health h3','model.health'],['.model-card-health>p','model.healthp'],
    ['.integrity-note strong','integrity.title'],['.integrity-note p','integrity.p'],['.architecture-intro p','arch.map.title'],['.architecture-intro small','arch.map.p'],
    ['.status-grid article:nth-child(1) h3','status.card1'],['.status-grid article:nth-child(1) p','status.card1p'],['.status-grid article:nth-child(2) h3','status.card2'],['.status-grid article:nth-child(2) p','status.card2p'],['.status-grid article:nth-child(3) h3','status.card3'],['.status-grid article:nth-child(3) p','status.card3p'],
    ['.roadmap-line article:nth-child(1) h3','roadmap.card1'],['.roadmap-line article:nth-child(1) p','roadmap.card1p'],['.roadmap-line article:nth-child(2) h3','roadmap.card2'],['.roadmap-line article:nth-child(2) p','roadmap.card2p'],['.roadmap-line article:nth-child(3) h3','roadmap.card3'],['.roadmap-line article:nth-child(3) p','roadmap.card3p'],
    ['.future-catalogue h3','future.title'],['.future-catalogue p','future.p'],['.collab-copy .section-kicker','collab.kicker'],['.collab-copy h2','collab.title'],['.collab-copy>p:not(.fineprint)','collab.intro'],['#collabButton','collab.button'],['.site-footer>p','footer.note']
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