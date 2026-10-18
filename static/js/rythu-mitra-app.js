/* Rythu Mitra frontend v2: plain JavaScript and same-origin Flask API. */
(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const localeRoot = document.documentElement.dataset.locales || '/static/locales/';
  const resourceConfigUrl = document.documentElement.dataset.resourceConfig || '/static/data/resource-config.json';
  const USER_ROLES = ['farmer', 'expert', 'admin', 'buyer', 'provider'];
  const OFFLINE_RESOURCES = new Set(['farm-diary', 'expenses', 'income', 'crop-tasks', 'farm-observations', 'soil-records', 'irrigation-records', 'inventory-items', 'seed-test-results', 'seed-complaints']);
  const PRIVATE_RESOURCES = new Set(['farms','farm-plots','crop-plans','crop-tasks','farm-diary','soil-records','input-purchases','seed-lots','seed-scans','seed-test-results','seed-complaints','expenses','income','loans','water-sources','irrigation-records','irrigation-plans','rainwater-plans','inventory-items','labour-plans','crop-rotation-plans','intercropping-plans','livestock','livestock-health','dairy-records','fish-ponds','harvest-records','produce-quality','drying-records','storage-bookings','equipment-bookings','expert-questions','expert-votes','crop-damage-reports','complaints','insurance-records','insurance-claims','fpo-groups','family-helpers','livestock-fish-records','harvest-plans','farm-observations','benefit-tracking','offline-drafts']);

  const NAV = [
    { route: 'home', key: 'nav.home', icon: 'i-home' },
    { route: 'farms', key: 'nav.farms', icon: 'i-farm' },
    { route: 'crop-planning', key: 'nav.cropPlanning', icon: 'i-plan' },
    { route: 'crop-health', key: 'nav.cropHealth', icon: 'i-leaf' },
    { route: 'seed-safety', key: 'nav.seedSafety', icon: 'i-shield' },
    { route: 'weather', key: 'nav.weather', icon: 'i-weather' },
    { route: 'markets', key: 'nav.markets', icon: 'i-market' },
    { route: 'more', key: 'nav.more', icon: 'i-grid' }
  ];

  const MORE_GROUPS = [
    { key: 'more.group.field', items: [
      ['soil-inputs','nav.soilInputs','Soil tests, water sources, inventory and input purchases.'],
      ['diary','nav.diary','Dated field notes and crop observations.'],
      ['calendar','nav.calendar','Upcoming, due, overdue, completed and skipped tasks.'],
      ['harvest','nav.harvest','Harvest, produce quality, drying and storage.'],
      ['livestock','nav.livestock','Animal health reminders, dairy and fish-pond records.']
    ]},
    { key: 'more.group.money', items: [
      ['finance','nav.finance','Recorded costs, income, loans and break-even scenarios.'],
      ['schemes','nav.schemes','Published schemes and your follow-up tracker.'],
      ['damage','nav.damage','In-app damage evidence, claims and grievance records.'],
      ['markets','nav.markets','Dated market observations and cost comparisons.'],
      ['equipment','nav.equipment','Equipment and agricultural-service listings.']
    ]},
    { key: 'more.group.help', items: [
      ['marketplace','nav.marketplace','Farmer listings, buyer requests and FPO information.'],
      ['expert','nav.expert','Expert questions, answers, reports and community posts.'],
      ['notifications','nav.notifications','In-app notifications and published notices.'],
      ['help','nav.help','Agricultural directories and official escalation options.']
    ]},
    { key: 'more.group.records', items: [
      ['evidence','nav.evidence','Private uploads made in this session.'],
      ['family','nav.family','Limited helper access and consent status.'],
      ['offline','nav.offline','Device-local drafts and server-confirmed sync.'],
      ['settings','nav.settings','Language, profile and privacy controls.']
    ]}
  ];

  const PAGE_META = {
    'home': ['page.home', 'home.desc'],
    'farms': ['page.farms', 'page.farmsDesc'],
    'crop-planning': ['page.cropPlanning', 'page.cropPlanningDesc'],
    'crop-health': ['page.cropHealth', 'page.cropHealthDesc'],
    'seed-safety': ['page.seedSafety', 'page.seedSafetyDesc'],
    'weather': ['page.weather', 'page.weatherDesc'],
    'markets': ['page.markets', 'page.marketsDesc'],
    'more': ['page.more', 'page.moreDesc'],
    'soil-inputs': ['page.soilInputs', 'page.soilInputsDesc'],
    'diary': ['page.diary', 'page.diaryDesc'],
    'calendar': ['page.calendar', 'page.calendarDesc'],
    'finance': ['page.finance', 'page.financeDesc'],
    'schemes': ['page.schemes', 'page.schemesDesc'],
    'damage': ['page.damage', 'page.damageDesc'],
    'livestock': ['page.livestock', 'page.livestockDesc'],
    'harvest': ['page.harvest', 'page.harvestDesc'],
    'equipment': ['page.equipment', 'page.equipmentDesc'],
    'marketplace': ['page.marketplace', 'page.marketplaceDesc'],
    'expert': ['page.expert', 'page.expertDesc'],
    'evidence': ['page.evidence', 'page.evidenceDesc'],
    'notifications': ['page.notifications', 'page.notificationsDesc'],
    'family': ['page.family', 'page.familyDesc'],
    'family-dashboard': ['family.dashboard', 'family.dashboardNote'],
    'settings': ['page.settings', 'page.settingsDesc'],
    'help': ['page.help', 'page.helpDesc'],
    'offline': ['page.offline', 'page.offlineDesc'],
    'admin': ['page.admin', 'page.adminDesc']
  };

  const MODULE_RESOURCES = {
    farms: ['farms','farm-plots'],
    'soil-inputs': ['soil-records','input-purchases','inventory-items','input-products','water-sources','irrigation-records','irrigation-plans','rainwater-plans'],
    diary: ['farm-diary','farm-observations'],
    calendar: ['crop-tasks','crop-plans','crop-rotation-plans','intercropping-plans','harvest-plans'],
    finance: ['expenses','income','loans','labour-plans'],
    schemes: ['schemes','scheme-tracking','scheme-documents','benefit-tracking'],
    damage: ['crop-damage-reports','insurance-records','insurance-claims','complaints','seed-complaint-events'],
    livestock: ['livestock','livestock-health','dairy-records','fish-ponds','livestock-fish-records'],
    harvest: ['harvest-records','produce-quality','drying-records','storage-facilities','storage-bookings','harvest-plans'],
    equipment: ['equipment-listings','equipment-bookings','service-directory'],
    marketplace: ['farmer-listings','buyer-requests','fpo-directory','fpo-groups','market-feedback','community-posts','pest-reports','notices','local-alerts'],
    expert: ['expert-questions','expert-answers','expert-votes','disease-knowledge','disease-reviews'],
    family: ['family-helpers'],
    help: ['service-directory','fpo-directory','storage-facilities','equipment-listings','notices','local-alerts','schemes'],
    'seed-safety': ['seed-lots','seed-scans','seed-test-results','seed-complaints'],
    'crop-health': ['expert-questions','disease-knowledge'],
    'crop-planning': ['crop-plans','crop-tasks','crop-rotation-plans','intercropping-plans','harvest-plans'],
    'evidence': [],
    admin: ['market-prices','schemes','notices','service-directory','source-records']
  };

  function readLocalText(key) {
    try { return window.localStorage.getItem(key); } catch { return null; }
  }
  function writeLocalText(key, value) {
    try { window.localStorage.setItem(key, String(value)); return true; } catch { return false; }
  }

  const MODULE_ICONS = {
    'soil-inputs':'i-soil','diary':'i-clipboard','calendar':'i-calendar','finance':'i-wallet','schemes':'i-shield',
    'damage':'i-alert','livestock':'i-livestock','harvest':'i-harvest','equipment':'i-tools','marketplace':'i-users',
    'expert':'i-help','evidence':'i-archive','notifications':'i-bell','family':'i-users','settings':'i-settings',
    'help':'i-help','offline':'i-cloud','admin':'i-settings','farms':'i-farm','crop-planning':'i-plan',
    'crop-health':'i-leaf','seed-safety':'i-shield','weather':'i-weather','markets':'i-market'
  };

  const state = {
    lang: readLocalText('rm-language') === 'te' ? 'te' : 'en',
    locales: { en: {}, te: {} },
    resources: {},
    session: null,
    user: null,
    csrf: null,
    route: 'home',
    lastScan: null,
    lastSeedScan: null,
    lastUpload: null,
    seedConfirmedFields: null,
    voiceTranscript: '',
    voiceIntent: null,
    marketRecords: [],
    schemesMatches: [],
    knownLocalOnlyMessage: false,
    routeRenderId: 0,
    lastRenderedRoute: null,
    routeController: null,
    sessionController: null,
    loginController: null,
    logoutController: null,
    diseaseController: null,
    qualityController: null,
    qualityRunId: 0,
    diseaseRunId: 0,
    photoPreviewUrl: null,
    dialogReturnFocus: new WeakMap(),
    signaturePlayed: false,
    sessionStatus: 'unknown'
  };

  class ApiError extends Error {
    constructor(message, status = 0, body = null) { super(message); this.name = 'ApiError'; this.status = status; this.body = body; }
  }

  function t(key, fallback = '') {
    const preferred = state.locales[state.lang]?.[key];
    if (typeof preferred === 'string' && preferred.trim()) return preferred;
    const english = state.locales.en?.[key];
    if (typeof english === 'string' && english.trim()) return english;
    return fallback || humanize(key);
  }
  function isAbortError(error) { return error?.name === 'AbortError' || error?.code === 'ABORT_ERR'; }
  function safeApiMessage(status, data = {}) {
    const code = String(data.error_code || data.code || '').toLowerCase();
    if (code === 'csrf_invalid') return t('errors.requestSecurity','This request could not be verified. Refresh the page and try again.');
    if (status === 401) return t('errors.signInRequired','Please sign in to continue.');
    if (status === 403) return t('errors.notAllowed','You are not allowed to complete this action.');
    if (status === 404) return t('errors.notAvailable','This information or action is not available yet.');
    if (status === 413) return t('errors.fileTooLarge','The selected file is too large. Choose a smaller file.');
    if (status === 422 || status === 400) return t('errors.checkInput','Please check the information and try again.');
    if (status === 429) return t('errors.tooManyRequests','Too many attempts. Please wait a little and try again.');
    if (status >= 500) return t('errors.serviceUnavailable','The service could not complete this request. Please try again later.');
    return t('errors.requestFailed','The request could not be completed. Please try again.');
  }
  async function fetchJsonAsset(url, fallbackObject = {}) {
    const response = await fetch(url, { cache: 'no-cache', credentials: 'same-origin' });
    if (!response.ok) throw new Error(`Asset request failed (${response.status})`);
    const data = await response.json();
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Expected a JSON object');
    return data;
  }
  function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function humanize(value) {
    return String(value || '').replace(/[-_]/g, ' ').replace(/\b\w/g, ch => ch.toUpperCase());
  }
  function localizeRole(role) { return t(`role.${role || 'guest'}`, humanize(role || 'guest')); }
  function statusBadge(value) {
    if (!value) return `<span class="status-badge status-badge--unavailable">${esc(t('status.NOT_STATED','STATUS NOT STATED'))}</span>`;
    const raw = String(value).toUpperCase();
    const cls = raw.toLowerCase().replace(/[^a-z0-9_-]/g, '_');
    return `<span class="status-badge status-badge--${esc(cls)}">${esc(t(`status.${raw}`, humanize(raw).toUpperCase()))}</span>`;
  }
  function sourceLine(data = {}) {
    const fields = [];
    if (data.source_name) fields.push(`<dt>${esc(t('common.source','Source'))}</dt><dd>${esc(data.source_name)}</dd>`);
    if (data.data_type || data.status || data.record_status) fields.push(`<dt>${esc(t('common.dataStatus','Data status'))}</dt><dd>${statusBadge(data.data_type || data.status || data.record_status)}</dd>`);
    if (data.last_updated || data.server_fetched_at || data.provider_observed_at) fields.push(`<dt>${esc(t('common.updated','Last updated'))}</dt><dd>${esc(formatDate(data.provider_observed_at || data.last_updated || data.server_fetched_at))}</dd>`);
    if (data.last_verified) fields.push(`<dt>${esc(t('common.verified','Last verified'))}</dt><dd>${esc(formatDate(data.last_verified))}</dd>`);
    if (data.source_url && /^https:\/\//i.test(data.source_url)) fields.push(`<dt>${esc(t('common.sourceLink','Source link'))}</dt><dd><a rel="noopener noreferrer" target="_blank" href="${esc(data.source_url)}">${esc(data.source_name || t('common.openSource','Open source'))}</a></dd>`);
    return fields.length ? `<dl class="metadata-list">${fields.join('')}</dl>` : `<p class="field-help">${esc(t('common.noSourceMetadata','No source or freshness metadata was returned for this record.'))}</p>`;
  }
  function formatDate(value) {
    if (!value) return 'Not available';
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return new Intl.DateTimeFormat(state.lang === 'te' ? 'te-IN' : 'en-IN', { dateStyle: 'medium', timeStyle: String(value).includes('T') ? 'short' : undefined }).format(d);
  }
  function money(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return 'Not available';
    return new Intl.NumberFormat(state.lang === 'te' ? 'te-IN' : 'en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(n);
  }
  function num(value, digits = 1) {
    const n = Number(value);
    return Number.isFinite(n) ? new Intl.NumberFormat(state.lang === 'te' ? 'te-IN' : 'en-IN', { maximumFractionDigits: digits }).format(n) : 'Not available';
  }
  function htmlPage(route, content, opts = {}) {
    const meta = PAGE_META[route] || [`resource.${route}`, ''];
    const title = opts.title || t(meta[0], humanize(route));
    const desc = opts.desc || t(meta[1], '');
    const active = route === 'resource' ? '' : route;
    return `<section class="page-heading"><div><span class="kicker">${esc(opts.kicker || 'FIELD NOTES / RYTHU MITRA')}</span><h1 tabindex="-1">${esc(title)}</h1>${desc ? `<p>${esc(desc)}</p>` : ''}</div>${opts.actions ? `<div class="button-row">${opts.actions}</div>` : ''}</section><div class="state-stack">${content}</div>`;
  }
  function panel(title, body, subtitle = '', actions = '') {
    return `<section class="panel"><div class="panel-head"><div><h2>${esc(title)}</h2>${subtitle ? `<p>${esc(subtitle)}</p>` : ''}</div>${actions}</div><div class="panel-body">${body}</div></section>`;
  }
  function emptyState(title, body, action = '') {
    return `<div class="empty-state"><strong>${esc(title)}</strong><p>${esc(body)}</p>${action}</div>`;
  }
  function errorBox(message, retryRoute = state.route) {
    return `<div class="inline-error" role="alert">${esc(message)}<div class="button-row" style="margin-top:8px"><button class="button button--quiet button--small" data-action="navigate" data-route="${esc(retryRoute)}">${esc(t('common.retry','Try again'))}</button></div></div>`;
  }
  function loading() { return `<div class="loading-state" role="status">${esc(t('common.loading','Loading…'))}</div>`; }
  function button(label, action, attrs = '', cls = 'button button--secondary') {
    return `<button type="button" class="${cls}" data-action="${esc(action)}" ${attrs}>${esc(label)}</button>`;
  }
  function icon(symbol = 'i-grid') { return `<svg class="icon" aria-hidden="true"><use href="#${esc(symbol)}"/></svg>`; }
  function cardLink(route, title, desc, symbol = 'i-calendar') {
    return `<a class="module-card" href="#/${esc(route)}"><span class="module-icon" aria-hidden="true">${icon(symbol)}</span><span><h3>${esc(title)}</h3><p>${esc(desc)}</p></span></a>`;
  }
  function resourceLink(resource, label = '') {
    const config = state.resources[resource];
    const title = label || t(`resource.${resource}`, humanize(resource));
    const allowed = config && state.user && config.create_roles?.includes(state.user.role);
    return `<a class="module-card" href="#/resource/${esc(resource)}"><span class="module-icon" aria-hidden="true">${icon('i-clipboard')}</span><span><h3>${esc(title)}</h3><p>${esc(allowed ? t('common.recordManagement','Saved records and supported changes.') : t('common.browseRecords','Browse records and available details.'))}</p></span></a>`;
  }

  async function api(path, options = {}) {
    const { signal: suppliedSignal, timeoutMs = 20000, ...requestOptions } = options;
    const method = (requestOptions.method || 'GET').toUpperCase();
    const headers = new Headers(requestOptions.headers || {});
    headers.set('Accept', 'application/json');
    if (requestOptions.body && !(requestOptions.body instanceof FormData) && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
    if (!['GET','HEAD','OPTIONS'].includes(method) && state.csrf) headers.set('X-CSRF-Token', state.csrf);

    // Route GETs inherit the active route signal. Mutations only use an explicit operation signal.
    const externalSignal = suppliedSignal || (method === 'GET' ? state.routeController?.signal : undefined);
    const controller = new AbortController();
    let timedOut = false;
    const abortFromExternal = () => controller.abort();
    if (externalSignal) {
      if (externalSignal.aborted) controller.abort();
      else externalSignal.addEventListener('abort', abortFromExternal, { once: true });
    }
    const timer = Number.isFinite(timeoutMs) && timeoutMs > 0
      ? window.setTimeout(() => { timedOut = true; controller.abort(); }, timeoutMs)
      : null;
    let response;
    try {
      response = await fetch(path, { ...requestOptions, method, headers, credentials: 'same-origin', cache: 'no-store', signal: controller.signal });
    } catch (err) {
      if (externalSignal?.aborted || (!timedOut && controller.signal.aborted)) {
        const abort = new DOMException('Request cancelled', 'AbortError');
        throw abort;
      }
      if (timedOut) throw new ApiError(t('errors.timeout','The request took too long. Check your connection and try again.'), 0, null);
      throw new ApiError(t('errors.network','Cannot reach the service. Check your connection and try again.'), 0, null);
    } finally {
      if (timer !== null) window.clearTimeout(timer);
      if (externalSignal) externalSignal.removeEventListener('abort', abortFromExternal);
    }

    let data = {};
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      try { data = await response.json(); } catch { data = {}; }
    }
    if (data.csrf_token) state.csrf = data.csrf_token;
    if (!response.ok || data.success === false) {
      // Keep server diagnostics in memory for development/debugging, but never print raw details to farmers.
      if (document.documentElement.dataset.appEnv === 'development') console.warn('Rythu Mitra API request failed', { path, status: response.status, error_code: data.error_code || data.code || null });
      throw new ApiError(safeApiMessage(response.status, data), response.status, data);
    }
    return data;
  }

  // Backend contract adapters: keep response-shape assumptions here rather than inside UI templates.
  // Missing fields remain empty/unavailable; no demo values are synthesized.
  function isRecord(value) { return Boolean(value) && typeof value === 'object' && !Array.isArray(value); }
  function responsePayload(value) {
    if (!isRecord(value)) return {};
    if (isRecord(value.data)) return { ...value, ...value.data };
    return value;
  }
  function firstArray(...values) { return values.find(Array.isArray) || []; }
  function mapWeatherResponse(raw) {
    const item = responsePayload(raw);
    return {
      ...item,
      temperature: item.temperature ?? item.temp_c ?? item.temperature_c ?? null,
      humidity: item.humidity ?? item.relative_humidity ?? null,
      rainfall: item.rainfall ?? item.precipitation_mm ?? null,
      rain_probability: item.rain_probability ?? item.precipitation_probability ?? null,
      wind: item.wind ?? item.wind_speed_kmh ?? item.wind_speed ?? null,
      source_name: item.source_name ?? item.source ?? null,
      last_updated: item.last_updated ?? item.observed_at ?? item.timestamp ?? null
    };
  }
  function mapDashboardResponse(raw) {
    const data = responsePayload(raw);
    const records = isRecord(data.records) ? data.records : {};
    const profile = isRecord(data.profile) ? data.profile : (isRecord(data.farmer_profile) ? data.farmer_profile : {});
    const weatherRaw = data.weather ?? data.current_weather ?? data.weather_summary;
    return {
      ...data,
      profile,
      weather: weatherRaw == null ? {} : mapWeatherResponse(weatherRaw),
      crop_calendar: firstArray(data.crop_calendar, data.cropCalendar, data.tasks, data.upcoming_tasks, records.crop_tasks),
      actions: firstArray(data.actions, data.today_actions, data.recommendation_notes),
      market: firstArray(data.market, data.market_prices, data.markets, records.market_prices),
      notifications: firstArray(data.notifications, data.notices, records.notifications),
      finance_summary: isRecord(data.finance_summary) ? data.finance_summary : (isRecord(data.financial_summary) ? data.financial_summary : {})
    };
  }
  function mapDiseaseResponse(raw) {
    const data = responsePayload(raw);
    // Preserve original status fields and expose only documented candidate fields to the renderer.
    const nested = isRecord(data.result) ? data.result : (isRecord(data.prediction_result) ? data.prediction_result : null);
    return nested ? { ...data, ...nested, data_type: data.data_type ?? nested.data_type } : data;
  }
  function mapRecordsResponse(raw) {
    const data = responsePayload(raw);
    const rows = firstArray(data.records, data.items, data.results, data.rows, Array.isArray(data.data) ? data.data : null);
    return { ...data, records: rows };
  }

  function authOrExplain() {
    if (state.user) return '';
    return `<div class="inline-warning">${esc(t('common.signInNeeded','Sign in to view or save private farm records.'))} ${button(t('auth.signin','Sign in'), 'open-auth', 'data-auth-mode="login"', 'button button--primary button--small')}</div>`;
  }
  function requireFarmer() {
    if (state.user?.role === 'farmer') return '';
    if (!state.user) return authOrExplain();
    return `<div class="inline-warning">${esc(t('errors.farmerOnly','This workflow is available to farmer accounts. Current role:'))} ${esc(localizeRole(state.user.role))}.</div>`;
  }
  function setToast(message, kind = '') {
    const region = $('#toastRegion'); if (!region) return;
    const toast = document.createElement('p'); toast.className = `toast${kind ? ` toast--${kind}` : ''}`; toast.textContent = String(message || ''); region.append(toast);
    window.setTimeout(() => toast.remove(), 5200);
  }
  function setInline(id, message, kind = 'error') {
    const node = document.getElementById(id); if (!node) return;
    node.textContent = message || ''; node.className = kind === 'success' ? 'inline-success' : kind === 'warning' ? 'inline-warning' : 'inline-error'; node.hidden = !message;
  }
  function currentPath() {
    const path = (location.hash.replace(/^#\/?/, '') || 'home').split('/').filter(Boolean);
    if (path[0] === 'resource' && path[1]) return { route: `resource/${path[1]}`, resource: path[1] };
    return { route: path[0] || 'home', extra: path[1] || null };
  }
  function goto(route) {
    location.hash = `#/${String(route).replace(/^\/+/, '')}`;
  }

  function renderNavigation() {
    const role = state.user?.role;
    const items = NAV.filter(item => item.route !== 'admin');
    const side = $('#sideNav');
    side.innerHTML = items.map((item, i) => {
      const route = item.route;
      const current = state.route === route || (route === 'more' && (['soil-inputs','diary','calendar','finance','schemes','damage','livestock','harvest','equipment','marketplace','expert','evidence','notifications','family','settings','help','offline','admin','family-dashboard'].includes(state.route) || state.route.startsWith('resource/')));
      const divider = i === 6 ? '<hr class="nav-divider">' : '';
      return `${divider}<a class="nav-item" href="#/${route}" ${current ? 'aria-current="page"' : ''}>${icon(item.icon)}<span>${esc(t(item.key))}</span></a>`;
    }).join('');
    // Four high-frequency destinations keep labels readable on narrow Telugu layouts.
    // Seed Safety remains available through the sidebar and More section.
    const bottomItems = [NAV[0],NAV[2],NAV[3],NAV[7]];
    $('#bottomNav').innerHTML = bottomItems.map(item => {
      const current = state.route === item.route || (item.route === 'more' && !NAV.some(n => n.route === state.route));
      return `<a href="#/${item.route}" ${current ? 'aria-current="page"' : ''}>${icon(item.icon)}<span>${esc(t(item.key))}</span></a>`;
    }).join('');
    const menu = $('#profileMenu');
    menu.innerHTML = state.user
      ? `<p><strong>${esc(state.user.name || t('profile.title'))}</strong><br><small>${esc(localizeRole(role))}</small></p><button type="button" data-action="open-profile">${esc(t('nav.settings'))}</button><button type="button" data-action="logout">${esc(t('auth.logout','Sign out'))}</button>`
      : `${state.sessionStatus === 'unavailable' ? `<p role="status">${esc(t('status.sessionUnavailable','Could not verify your sign-in status.'))}</p><button type="button" data-action="retry-session">${esc(t('status.retrySession','Retry connection'))}</button>` : `<p>${esc(t('status.signedOut'))}</p>`}<button type="button" data-action="open-auth" data-auth-mode="login">${esc(t('auth.signin'))}</button><button type="button" data-action="open-auth" data-auth-mode="register">${esc(t('auth.create'))}</button>`;
    if (role === 'admin' && !items.some(x=>x.route==='admin')) {
      side.insertAdjacentHTML('beforeend', `<hr class="nav-divider"><a class="nav-item" href="#/admin" ${state.route==='admin'?'aria-current="page"':''}>${icon('i-grid')}<span>${esc(t('nav.admin'))}</span></a>`);
    }
    $('#profileName').textContent = state.user?.name || t('role.guest','Guest farmer');
    $('#profileRole').textContent = localizeRole(role);
    const first = String(state.user?.name || 'RM').split(/\s+/).slice(0,2).map(s=>s[0]).join('').toUpperCase();
    $('#profileInitial').textContent = first || 'RM';
  }
  function applyTranslations() {
    document.documentElement.lang = state.lang;
    document.documentElement.dir = 'ltr';
    $$('[data-i18n]').forEach(node => {
      const key = node.dataset.i18n;
      const preferred = state.locales[state.lang]?.[key];
      const value = typeof preferred === 'string' && preferred.trim() ? preferred : state.locales.en?.[key];
      if (typeof value === 'string' && value.trim()) node.textContent = value;
    });
    $$('[data-i18n-title]').forEach(node => {
      const key = node.dataset.i18nTitle;
      const translated = state.locales[state.lang]?.[key] || state.locales.en?.[key];
      if (typeof translated === 'string' && translated.trim()) node.title = translated;
    });
    $$('[data-i18n-aria-label]').forEach(node => {
      const existing = node.getAttribute('aria-label') || '';
      const key = node.dataset.i18nAriaLabel;
      const translated = state.locales[state.lang]?.[key] || state.locales.en?.[key];
      if (typeof translated === 'string' && translated.trim()) node.setAttribute('aria-label', translated);
      else if (existing) node.setAttribute('aria-label', existing);
    });
    $$('[data-lang]').forEach(btn => btn.setAttribute('aria-pressed', String(btn.dataset.lang === state.lang)));
    renderNavigation();
  }
  function connectionState() {
    const status = $('#connectionStatus');
    if (navigator.onLine) {
      status.innerHTML = `<i></i><span>${esc(t('status.online','Online'))}</span>`; status.classList.remove('is-offline');
      $('#offlineBanner').hidden = true;
    } else {
      status.innerHTML = `<i></i><span>${esc(t('status.offline','Offline'))}</span>`; status.classList.add('is-offline');
      $('#offlineBanner').hidden = false;
    }
  }

  function renderNotFound(route) {
    const action = `<div class="button-row"><a class="button button--primary" href="#/home">${esc(t('common.goHome','Return home'))}</a><a class="button button--secondary" href="#/more">${esc(t('nav.more','Explore sections'))}</a></div>`;
    return htmlPage('home', emptyState(t('navigation.notFoundTitle','This page is not available'), t('navigation.notFoundBody','The address does not match a page in this version of Rythu Mitra.'), action), { title: t('navigation.notFoundTitle','Page not found'), desc: String(route || '') ? '' : t('navigation.notFoundBody','The address does not match a page in this version of Rythu Mitra.') });
  }

  async function navigateToCurrent() {
    const parsed = currentPath();
    const previousRoute = state.lastRenderedRoute;
    const initialRender = previousRoute === null;
    const routeChanged = previousRoute !== parsed.route;
    const renderId = ++state.routeRenderId;
    if (state.routeController) state.routeController.abort();
    state.routeController = new AbortController();
    if (previousRoute === 'crop-health' && parsed.route !== 'crop-health') {
      cancelDiseaseAnalysis(false);
      clearDiseasePhoto(false);
    }
    $('#profileMenu').hidden = true;
    $('#profileButton').setAttribute('aria-expanded','false');
    state.route = parsed.route;
    renderNavigation();
    const view = $('#view'); view.setAttribute('aria-busy','true'); view.innerHTML = loading();
    try {
      let markup;
      const knownRoute = Boolean(parsed.resource ? state.resources[parsed.resource] : Object.prototype.hasOwnProperty.call(PAGE_META, parsed.route));
      if (!knownRoute) markup = renderNotFound(parsed.route);
      else if (parsed.resource) markup = await renderResourcePage(parsed.resource);
      else if (parsed.route === 'home') markup = await renderHome();
      else if (parsed.route === 'farms') markup = renderResourceChooser('farms');
      else if (parsed.route === 'crop-planning') markup = renderCropPlanning();
      else if (parsed.route === 'crop-health') markup = await renderCropHealth();
      else if (parsed.route === 'seed-safety') markup = await renderSeedSafety();
      else if (parsed.route === 'weather') markup = await renderWeather();
      else if (parsed.route === 'markets') markup = await renderMarkets();
      else if (parsed.route === 'more') markup = renderMore();
      else if (['soil-inputs','diary','calendar','finance','schemes','damage','livestock','harvest','equipment','marketplace','expert','family','help'].includes(parsed.route)) markup = renderResourceChooser(parsed.route);
      else if (parsed.route === 'evidence') markup = renderEvidence();
      else if (parsed.route === 'notifications') markup = await renderNotifications();
      else if (parsed.route === 'settings') markup = renderSettings();
      else if (parsed.route === 'offline') markup = renderOffline();
      else if (parsed.route === 'admin') markup = await renderAdmin();
      else if (parsed.route === 'family-dashboard') markup = await renderFamilyDashboard();
      else markup = renderNotFound(parsed.route);
      if (renderId !== state.routeRenderId || state.routeController.signal.aborted) return;
      view.innerHTML = markup;
      view.setAttribute('aria-busy','false');
      const pageTitle = view.querySelector('.page-heading h1')?.textContent?.trim();
      document.title = pageTitle ? `${pageTitle} · Rythu Mitra` : 'Rythu Mitra';
      renderNavigation();
      applyTranslations();
      if (routeChanged && !initialRender) {
        const heading = view.querySelector('h1[tabindex="-1"]');
        if (heading) heading.focus({ preventScroll: true });
        window.scrollTo({ top: 0, behavior: 'auto' });
      }
      state.lastRenderedRoute = parsed.route;
      playSignatureOnce();
    } catch (error) {
      if (isAbortError(error) || renderId !== state.routeRenderId) return;
      view.innerHTML = htmlPage('home', errorBox(t('errors.serviceUnavailable','The service could not complete this request. Please try again later.'), state.route));
      view.setAttribute('aria-busy','false');
      document.title = `${t('errors.serviceUnavailable','Service unavailable')} · Rythu Mitra`;
      applyTranslations();
      state.lastRenderedRoute = parsed.route;
    }
  }
  function playSignatureOnce() {
    const signature = $('#fieldSignature');
    if (!signature || state.signaturePlayed || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let played = false;
    try { played = sessionStorage.getItem('rm-field-signature-played') === '1'; } catch { /* Storage can be disabled. */ }
    if (played) { state.signaturePlayed = true; return; }
    signature.classList.add('field-signature--draw');
    state.signaturePlayed = true;
    try { sessionStorage.setItem('rm-field-signature-played','1'); } catch { /* Animation remains one-time per render state. */ }
  }

  async function renderHome() {
    const title = t('home.title','Farm tasks and latest updates');
    if (!state.user) {
      return htmlPage('home', `<section class="hero-panel"><svg id="fieldSignature" class="field-signature" viewBox="0 0 260 150" aria-hidden="true" focusable="false"><path pathLength="1" d="M8 28 C56 4 111 8 151 28 S222 55 252 23"/><path pathLength="1" d="M8 57 C52 35 105 37 151 57 S220 83 252 52"/><path pathLength="1" d="M8 86 C54 65 110 66 155 86 S217 110 252 81"/><path pathLength="1" d="M8 115 C54 96 106 96 153 116 S218 140 252 110"/></svg><span class="kicker">${esc(t('top.kicker','FIELD NOTEBOOK / TELANGANA'))}</span><h2>${esc(t('home.guestTitle'))}</h2><p>${esc(t('home.guestBody'))}</p><div class="button-row"><button class="button button--primary" data-action="open-auth" data-auth-mode="login">${esc(t('home.signIn'))}</button><button class="button button--secondary" data-action="open-auth" data-auth-mode="register">${esc(t('home.register'))}</button></div></section><div class="grid grid--2">${panel(t('home.shortTitle'), `<div class="module-grid">${cardLink('crop-health',t('nav.cropHealth'),t('page.cropHealthDesc'),'i-leaf')}${cardLink('seed-safety',t('nav.seedSafety'),t('page.seedSafetyDesc'),'i-shield')}${cardLink('weather',t('nav.weather'),t('page.weatherDesc'),'i-weather')}${cardLink('markets',t('nav.markets'),t('page.marketsDesc'),'i-market')}</div>`)}${panel(t('home.weather'), `<p class="muted-copy">${esc(t('weather.noProvider'))}</p>${statusBadge('UNAVAILABLE')}`, '')}</div>`, { title });
    }
    let data;
    try { data = mapDashboardResponse(await api('/api/dashboard')); }
    catch (error) {
      if (error.status === 401) { state.user = null; renderNavigation(); return htmlPage('home', authOrExplain()); }
      return htmlPage('home', errorBox(error.message, 'home'));
    }
    const profile = data.profile || {};
    const weather = data.weather || {};
    const tasks = Array.isArray(data.crop_calendar) ? data.crop_calendar : [];
    const actions = (Array.isArray(data.actions) ? data.actions : []).map(item => typeof item === 'string' ? item : (item?.title || item?.action || item?.text || item?.label)).filter(item => typeof item === 'string' && item.trim());
    const markets = Array.isArray(data.market) ? data.market : [];
    const notes = Array.isArray(data.notifications) ? data.notifications : [];
    const expenses = data.finance_summary?.expense_total;
    const income = data.finance_summary?.income_total;
    const taskRows = tasks.length ? `<ul class="action-list">${tasks.slice(0,8).map((task,i)=>`<li><span class="action-number">${String(i+1).padStart(2,'0')}</span><div class="action-copy"><strong>${esc(task.task || task.title || t('common.untitled','Untitled task'))}</strong><p>${esc([task.crop,task.stage,task.due_date ? `${t('field.due_date','Due')}: ${task.due_date}` : ''].filter(Boolean).join(' · '))}</p><div class="status-line">${statusBadge(task.status || 'NOT_STATED')}${task.data_type ? statusBadge(task.data_type) : ''}${['OVERDUE','DUE','UPCOMING'].includes(task.status) ? button(t('calendar.markCompleted','Mark completed'),'complete-task',`data-id="${esc(task.id)}"`,'button button--quiet button--small') : ''}</div></div></li>`).join('')}</ul>` : emptyState(t('common.noData'), t('home.noActions'), `<a class="button button--secondary button--small" href="#/calendar">${esc(t('nav.calendar'))}</a>`);
    const weatherBody = weather && weather.success ? `<div class="weather-current"><strong class="weather-temp">${weather.temperature == null ? 'Not available' : `${esc(num(weather.temperature))}°`}</strong><div><strong>${esc(profile.district || t('weather.locationDefault','Selected location'))}</strong><div class="status-line">${statusBadge(weather.status || 'UNAVAILABLE')}${weather.data_type ? statusBadge(weather.data_type) : ''}</div></div></div><div class="weather-metrics">${[[t('weather.humidity','Humidity'),weather.humidity,'%'],[t('weather.rainfall','Rainfall'),weather.rainfall,' mm'],[t('weather.rainChance','Rain chance'),weather.rain_probability,'%'],[t('weather.wind','Wind'),weather.wind,' km/h']].map(([l,v,u])=>`<div class="weather-metric"><span>${esc(l)}</span><strong>${v == null ? 'Not available' : `${esc(num(v))}${u}`}</strong></div>`).join('')}</div><p class="field-help">${esc(weather.reason || weather.source_name || t('common.noSourceMetadata'))}</p>${sourceLine(weather)}` : `<p>${esc(weather.error || t('home.noWeather'))}</p>${statusBadge(weather.status || 'UNAVAILABLE')}`;
    const marketBody = markets.length ? `<div class="resource-list">${markets.slice(0,3).map(m=>`<article class="record-card"><div class="record-card-head"><h4>${esc(m.commodity || 'Not available')} · ${esc(m.market || 'Not available')}</h4>${statusBadge(m.data_type || m.freshness_status || 'UNAVAILABLE')}</div><p>${esc(t('field.price_date','Price date'))}: ${esc(m.price_date || 'Not available')}${m.is_stale ? ` · ${esc(t('markets.stale','Stale price record'))}` : ''}</p><dl class="record-values"><div class="record-value"><dt>${esc(t('field.modal_price','Modal price'))}</dt><dd>${esc(m.modal_price == null ? 'Not available' : `${money(m.modal_price)} / ${m.unit || 'quintal'}`)}</dd></div></dl>${sourceLine(m)}</article>`).join('')}</div>` : `<p>${esc(t('home.noMarket'))}</p>${statusBadge('UNAVAILABLE')}`;
    const noticeBody = notes.length ? `<div class="notice-list">${notes.map(n=>`<article class="notice-item notice-item--${esc(n.severity || 'info')}"><div class="status-line">${statusBadge(n.data_type || 'USER_SUBMITTED')}<small>${esc(formatDate(n.created_at))}</small></div><h3>${esc(n.title || t('common.notice','Notice'))}</h3><p>${esc(n.body || '')}</p></article>`).join('')}</div>` : emptyState(t('notifications.none','No notification records'), t('notifications.noneHelp','Notifications appear here only when returned by the backend.'));
    const actionsMarkup = actions.length ? `<ol class="action-list">${actions.map((text,i)=>`<li><span class="action-number">${String(i+1).padStart(2,'0')}</span><div class="action-copy"><strong>${esc(text)}</strong><p>${esc(t('home.notRecommendation','These dashboard notes are not automatically verified farm-specific recommendations.'))}</p></div></li>`).join('')}</ol>` : emptyState(t('home.actionTitle'),t('home.noActions'));
    const body = `<section class="hero-panel"><svg id="fieldSignature" class="field-signature" viewBox="0 0 260 150" aria-hidden="true" focusable="false"><path pathLength="1" d="M8 28 C56 4 111 8 151 28 S222 55 252 23"/><path pathLength="1" d="M8 57 C52 35 105 37 151 57 S220 83 252 52"/><path pathLength="1" d="M8 86 C54 65 110 66 155 86 S217 110 252 81"/><path pathLength="1" d="M8 115 C54 96 106 96 153 116 S218 140 252 110"/></svg><span class="kicker">${esc(t('home.actionTitle'))} / ${esc(formatDate(new Date().toISOString().slice(0,10)))}</span><h2>${esc(t('home.hello','Hello'))}, ${esc(profile.name || state.user.name || t('role.farmer','Farmer'))}</h2><p class="home-context">${esc([profile.current_crop,profile.crop_stage,profile.district].filter(Boolean).join(' · ') || t('home.profile'))}</p><p class="home-supporting-copy">${esc(title)}</p><div class="status-line">${statusBadge(data.status || 'PARTIAL_DASHBOARD')}${statusBadge(data.data_type || 'MIXED')}<span class="field-help">${esc(t('home.notRecommendation'))}</span></div><div class="button-row"><a class="button button--primary" href="#/calendar">${esc(t('nav.calendar'))}</a><a class="button button--secondary" href="#/crop-health">${esc(t('nav.cropHealth'))}</a><a class="button button--quiet" href="#/seed-safety">${esc(t('nav.seedSafety'))}</a></div></section><div class="grid grid--2">${panel(t('home.actionTitle'),actionsMarkup)}${panel(t('home.taskTitle'),taskRows,'',`<a class="text-button" href="#/calendar">${esc(t('common.viewAll','View tasks'))} →</a>`)}</div><div class="grid grid--2">${panel(t('home.weather'),weatherBody,'')}${panel(t('home.market'),marketBody,'')}</div>${panel(t('notifications.title','Notifications & seed alerts'),noticeBody)}${(expenses != null || income != null) ? `<section class="home-finance-line" aria-label="${esc(t('home.financeSnapshot','Recorded farm finances'))}"><strong>${esc(t('home.financeSnapshot','Recorded farm finances'))}</strong><span>${esc(t('finance.expenses','Recorded expenses'))}: <b>${expenses == null ? esc(t('common.unavailable','Unavailable')) : esc(money(expenses))}</b></span><span>${esc(t('finance.income','Recorded income'))}: <b>${income == null ? esc(t('common.unavailable','Unavailable')) : esc(money(income))}</b></span><small>${esc(t('finance.recordedOnly','User-entered records only'))}</small></section>` : ''}<div class="quick-link-grid">${cardLink('crop-planning',t('nav.cropPlanning'),t('page.cropPlanningDesc'),'i-calendar')}${cardLink('weather',t('nav.weather'),t('page.weatherDesc'),'i-weather')}${cardLink('markets',t('nav.markets'),t('page.marketsDesc'),'i-market')}${cardLink('soil-inputs',t('nav.soilInputs'),t('page.soilInputsDesc'),'i-soil')}</div>`;
    return htmlPage('home', body, { title });
  }

  function renderMore() {
    const groups = MORE_GROUPS.map(group => `<section><div class="group-heading"><h2>${esc(t(group.key,humanize(group.key)))}</h2></div><div class="module-grid">${group.items.map(([route,key,desc])=>cardLink(route,t(key),desc,MODULE_ICONS[route] || 'i-calendar')).join('')}</div></section>`).join('');
    const adminLink = state.user?.role === 'admin' ? `<section><div class="group-heading"><h2>${esc(t('nav.admin'))}</h2></div><div class="module-grid">${cardLink('admin',t('page.admin'),t('page.adminDesc'),MODULE_ICONS.admin)}</div></section>` : '';
    return htmlPage('more', `${groups}${adminLink}`);
  }

  function renderResourceChooser(route) {
    const list = MODULE_RESOURCES[route] || [];
    let cards = list.map(slug => resourceLink(slug)).join('');
    if (route === 'farms') cards += `<a class="module-card" href="#/resource/farm-plots"><span class="module-icon">${icon('i-farm')}</span><span><h3>${esc(t('resource.farm-plots','Farm plots'))}</h3><p>${esc(t('farms.plotNote','Track each plot under a saved farm.'))}</p></span></a>`;
    const special = route === 'schemes' ? `<div class="panel"><div class="panel-head"><div><h2>${esc(t('schemes.matchTitle','Possible scheme matches'))}</h2><p>${esc(t('schemes.matchNote','Requires a signed-in account. Matches are not official eligibility decisions.'))}</p></div></div><div class="panel-body"><button class="button button--primary" data-action="load-scheme-matches">${esc(t('schemes.loadMatches','Check possible matches'))}</button><div id="schemeMatches" class="state-stack" style="margin-top:14px"></div></div></div>` : (route === 'family' ? `<div class="panel"><div class="panel-head"><div><h2>${esc(t('family.dashboard','Shared family dashboard'))}</h2><p>${esc(t('family.dashboardNote','Only fields shared with this helper account are returned.'))}</p></div><button class="button button--primary button--small" data-action="family-dashboard">${esc(t('family.loadDashboard','Load shared dashboard'))}</button></div><div class="panel-body"><div id="familyDashboardResult"></div></div></div>` : '');
    const routeLinks = route === 'farms' ? `<div class="button-row"><a class="button button--primary" href="#/resource/farms">${esc(t('farms.manage','Manage farms'))}</a><a class="button button--secondary" href="#/resource/farm-plots">${esc(t('farms.plots','Farm plots'))}</a></div>` : '';
    if (route === 'family') cards += cardLink('family-dashboard',t('family.dashboard','Family dashboard'),t('family.dashboardNote','Only records shared with this helper account are returned.'),'i-users');
    if (route === 'help') cards += cardLink('notifications',t('nav.notifications'),t('page.notificationsDesc'),'i-bell');
    return htmlPage(route, `${routeLinks}${special}<section class="module-grid">${cards || emptyState(t('common.noModules','No resource module configured'),t('common.noModulesNote','This workspace has no linked generic resources yet.'))}</section>`);
  }

  function renderCropPlanning() {
    const form = `<form id="recommendationForm" class="form-grid" novalidate><label><span>N (nitrogen)</span><input name="N" type="number" min="0" max="300" step="any" required></label><label><span>P (phosphorus)</span><input name="P" type="number" min="0" max="300" step="any" required></label><label><span>K (potassium)</span><input name="K" type="number" min="0" max="300" step="any" required></label><label><span>Temperature (°C)</span><input name="temperature" type="number" min="-5" max="60" step="any" required></label><label><span>Humidity (%)</span><input name="humidity" type="number" min="0" max="100" step="any" required></label><label><span>Soil pH</span><input name="ph" type="number" min="0" max="14" step="any" required></label><label><span>Rainfall (mm)</span><input name="rainfall" type="number" min="0" max="1000" step="any" required></label><div class="form-submit-row"><button class="button button--primary" type="submit">${esc(t('crop.getRecommendation','Get model recommendation'))}</button><p class="field-help">${esc(t('crop.recNote'))}</p></div></form><div id="recommendationResult" class="state-stack" aria-live="polite" style="margin-top:14px"></div>`;
    const tools = `<div class="grid grid--2">${panel(t('crop.recTitle'),form,t('crop.recNote'))}${panel(t('crop.riskTitle'),`<form id="riskForm" class="form-stack"><label><span>${esc(t('field.crop','Crop'))}</span><input name="crop" required></label><label><span>${esc(t('field.stage','Growth stage'))}</span><input name="crop_stage"></label><label><span>Humidity (%)</span><input name="humidity" type="number" min="0" max="100" step="any"></label><label><span>Rain probability (%)</span><input name="rain_probability" type="number" min="0" max="100" step="any"></label><label><span>Wind (km/h)</span><input name="wind_kmh" type="number" min="0" max="300" step="any"></label><label><span>Nearby pest reports (count; optional)</span><input name="nearby_pest_reports" type="number" min="0" max="10000" step="1"></label><button class="button button--primary" type="submit">${esc(t('crop.checkRisk','Check risk factors'))}</button></form><div id="riskResult" class="state-stack" style="margin-top:12px"></div>`,t('crop.riskNote'))}</div><div class="grid grid--2">${panel(t('crop.irrigationTitle'),`<form id="irrigationForm" class="form-stack"><label><span>${esc(t('field.crop'))}</span><input name="crop" required></label><label><span>${esc(t('field.crop_stage'))}</span><input name="crop_stage"></label><label><span>Recent rainfall (mm)</span><input name="recent_rainfall_mm" type="number" min="0" max="1000" step="any"></label><label><span>Soil moisture observation</span><select name="soil_moisture_observation"><option value="">Not selected</option><option value="dry">Dry</option><option value="moist">Moist</option><option value="wet">Wet</option><option value="unknown">Unknown</option></select></label><label><span>Irrigation method</span><select name="irrigation_method"><option value="">Not selected</option>${['borewell','well','canal','tank','drip','sprinkler','rainfed','other'].map(s=>`<option value="${s}">${humanize(s)}</option>`).join('')}</select></label><button class="button button--primary" type="submit">${esc(t('crop.getGuidance','Get irrigation guidance'))}</button></form><div id="irrigationResult" class="state-stack" style="margin-top:12px"></div>`,t('crop.irrigationNote'))}${panel(t('crop.yieldTitle'),`<form id="yieldForm" class="form-stack"><label><span>${esc(t('field.ph'))}</span><input name="ph" type="number" min="0" max="14" step="any" required></label><label><span>Temperature (°C)</span><input name="temperature" type="number" min="-5" max="60" step="any" required></label><label><span>Rainfall (mm)</span><input name="rainfall" type="number" min="0" max="1000" step="any" required></label><button class="button button--primary" type="submit">${esc(t('crop.getYieldReference','Get reference check'))}</button></form><div id="yieldResult" class="state-stack" style="margin-top:12px"></div>`,t('crop.yieldNote'))}</div><div class="inline-warning">${esc(t('crop.modelSafety','Crop prediction, rule-based risk and reference calculators are not guarantees of suitability, yield or profit. Use measured data and validate locally.'))}</div>`;
    const resources = (MODULE_RESOURCES['crop-planning'] || []).map(s => resourceLink(s)).join('');
    return htmlPage('crop-planning', `${tools}<section><div class="group-heading"><h2>${esc(t('crop.recordsTitle','Crop plans and calendar records'))}</h2></div><div class="module-grid">${resources}</div></section>`);
  }

  async function renderCropHealth() {
    const current = state.lastScan ? renderScanResult(state.lastScan) : '';
    let history = '';
    if (state.user) {
      try {
        const data = mapRecordsResponse(await api('/api/scan-history?limit=30'));
        const rows = data.records;
        history = rows.length ? `<div class="resource-list">${rows.map(renderScanHistory).join('')}</div>` : emptyState(t('health.noHistory','No saved scan history'),t('health.noHistoryNote','A scan will appear after the backend completes and saves it.'));
      } catch (error) { history = errorBox(error.message,'crop-health'); }
    } else history = authOrExplain();
    const body = `<div class="grid grid--2"><section class="panel"><div class="panel-head"><div><h2>${esc(t('health.uploadTitle','Upload a crop photo'))}</h2><p>${esc(t('health.uploadNote','Use a clear photo of the affected plant or leaf. Do not include people or private documents.'))}</p></div></div><div class="panel-body"><ol class="steps-strip" aria-label="Crop photo workflow" data-i18n-aria-label="health.photoWorkflow"><li class="is-active" data-photo-step="capture"><span class="step-dot">1</span><span>${esc(t('health.stepCapture','Capture'))}</span></li><li data-photo-step="check"><span class="step-dot">2</span><span>${esc(t('health.stepCheck','Check photo'))}</span></li><li data-photo-step="understand"><span class="step-dot">3</span><span>${esc(t('health.stepUnderstand','Understand result'))}</span></li></ol><form id="diseaseForm" class="form-stack" enctype="multipart/form-data"><label class="photo-upload" for="diseaseImage"><span>${esc(t('health.chooseImage','Choose plant image'))}</span><input id="diseaseImage" name="image" type="file" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp" required><span class="field-help">${esc(t('health.fileNote','JPEG, PNG or WebP. Up to 5 MB. The server validates the image again.'))}</span></label><div id="diseasePreview" class="photo-preview-grid" aria-live="polite"></div><p id="diseaseQuality" class="field-help" role="status" aria-live="polite">${esc(t('health.photoPrompt','Choose a clear leaf photo in natural light. Photo checks are advisory only.'))}</p><div class="button-row disease-actions"><button class="button button--primary" type="submit">${esc(t('health.scanButton','Request preliminary analysis'))}</button><button id="replaceDiseasePhoto" class="button button--secondary" type="button" data-action="replace-disease-photo" disabled>${esc(t('health.replacePhoto','Choose another photo'))}</button><button id="removeDiseasePhoto" class="button button--quiet" type="button" data-action="remove-disease-photo" disabled>${esc(t('health.removePhoto','Remove photo'))}</button><button id="cancelDiseaseAnalysis" class="button button--quiet" type="button" data-action="cancel-disease-analysis" hidden>${esc(t('health.cancelAnalysis','Cancel analysis'))}</button></div><div id="diseaseProgress" class="field-help" role="status" aria-live="polite" aria-atomic="true"></div><p id="diseaseError" class="inline-error" role="alert" hidden></p></form><div id="scanResult">${current}</div></div></section><section class="panel"><div class="panel-head"><div><h2>${esc(t('health.safetyTitle','Before acting on a result'))}</h2><p>${esc(t('health.safetyNote','A model response is a screening aid, not a confirmed diagnosis.'))}</p></div></div><div class="panel-body"><ul class="result-list"><li>${esc(t('health.safe1','Check symptoms across more than one plant and note the crop stage.'))}</li><li>${esc(t('health.safe2','Retake a clear photo in natural light if the model returns low confidence.'))}</li><li>${esc(t('health.safe3','Consult an agriculture officer or qualified expert before applying a treatment.'))}</li><li>${esc(t('health.safe4','This interface will not invent missing model labels or unsupported chemical doses.'))}</li></ul></div></section></div>${panel(t('health.historyTitle','Saved scan history'),history)}<div class="module-grid">${resourceLink('expert-questions')}${resourceLink('disease-knowledge')}</div>`;
    return htmlPage('crop-health', body);
  }
  // Contract assumption for this frontend/backend candidate: confidence is a percentage from 0 to 100.
  // Values below 1 are ambiguous with fractional probabilities, so they are withheld rather than guessed.
  // If the backend contract changes to 0..1, update this adapter explicitly and test it.
  function normalizeConfidence(value) {
    if (typeof value === 'string' && !/^\s*(?:\d+(?:\.\d*)?|\.\d+)\s*$/.test(value)) return null;
    if (value === null || value === undefined || value === '') return null;
    const n = Number(value);
    if (!Number.isFinite(n) || n < 1 || n > 100) return null;
    return n / 100;
  }
  function renderScanResult(result) {
    const responseStatus = String(result?.status || result?.data_type || '').toUpperCase();
    const unavailable = ['UNAVAILABLE','ERROR','FAILED','NOT_CONNECTED'].includes(responseStatus) || result?.success === false;
    if (!result || typeof result !== 'object' || unavailable) {
      return `<div class="result-box result-reveal" role="status" style="margin-top:14px"><h3 tabindex="-1">${esc(t('health.resultUnable','Unable to assess'))}</h3><p>${esc(t('health.resultUnavailable','The backend did not return a usable analysis result. No diagnosis is shown. Try again later or ask a qualified local agriculture professional.'))}</p>${statusBadge(responseStatus || 'UNAVAILABLE')}</div>`;
    }
    const low = result.low_confidence === true || responseStatus === 'LOW_CONFIDENCE';
    const rawLabel = (low && result.candidate_label) || result.label || result.prediction || result.crop || result.candidate_label || result.result;
    const label = rawLabel && typeof rawLabel === 'string' ? rawLabel : t('health.unknownLabel','No verified label was returned');
    const confidence = normalizeConfidence(result.confidence);
    const verified = result.label_verified === true;
    const metadata = `<details class="technical-details"><summary>${esc(t('health.technicalDetails','Technical details'))}</summary><div class="technical-details__body">${sourceLine(result)}${result.model_version ? `<p>${esc(t('common.modelVersion','Model version'))}: ${esc(result.model_version)}</p>` : ''}${result.image_id ? `<p>${esc(t('health.imageReference','Image reference'))}: ${esc(result.image_id)} · ${esc(t('health.imageRetentionNote','The backend determines whether a photo is retained; see the response status above.'))}</p>` : ''}</div></details>`;
    const guidance = typeof result.guidance === 'string' ? result.guidance : (typeof result.note === 'string' ? result.note : t('health.noGuidance','No verified guidance text was returned.'));
    return `<div class="result-box result-reveal" style="margin-top:14px"><div class="status-line">${statusBadge(result.data_type || 'MODEL_OUTPUT')}${statusBadge(low ? 'LOW_CONFIDENCE' : (verified ? 'LABEL_VERIFIED' : 'UNVERIFIED'))}</div><h3 tabindex="-1">${esc(t('health.resultReady','Result received'))}</h3><div class="result-number">${esc(label)}</div>${confidence !== null ? `<p>${esc(t('health.confidence','Model-reported confidence'))}: ${esc(num(confidence*100))}%</p><div class="confidence-track" role="img" aria-label="${esc(t('health.confidenceTrack','Model-reported confidence indicator'))}"><span style="width:${confidence*100}%"></span></div>` : `<p>${esc(t('health.noConfidence','The backend did not provide a supported confidence value.'))}</p>`}<p class="inline-warning">${esc(t('health.notDiagnosis','This is a preliminary model output, not a confirmed diagnosis. Confirm the crop and result label with a qualified local agriculture professional before treatment.'))}</p><p>${esc(guidance)}</p>${result.history_save_available ? `<div class="button-row"><button class="button button--primary" data-action="save-scan">${esc(t('health.saveScan','Save this scan to my account'))}</button>` : ''}${result.history_save_available && !state.user ? `<button class="button button--quiet" data-action="open-auth" data-auth-mode="login">${esc(t('auth.signin'))}</button>` : ''}${result.history_save_available ? `</div>` : ''}${metadata}</div>`;
  }

  function renderScanHistory(record) {
    return `<article class="record-card"><div class="record-card-head"><h4>${esc(record.result || t('health.unknownLabel'))}</h4>${statusBadge(record.low_confidence ? 'LOW_CONFIDENCE' : (record.label_verified ? 'LABEL_VERIFIED' : 'UNVERIFIED'))}</div><p>${esc(formatDate(record.created_at))}</p>${normalizeConfidence(record.confidence) === null ? '' : `<p>${esc(t('health.confidence','Model-reported confidence'))}: ${esc(num(normalizeConfidence(record.confidence)*100))}%</p>`}<p>${esc(record.guidance || '')}</p><details class="technical-details"><summary>${esc(t('health.technicalDetails','Technical details'))}</summary><p>${esc(record.model_version || t('common.modelVersionUnknown','Model version not supplied'))}</p></details>${Array.isArray(record.expert_reviews) && record.expert_reviews.length ? `<div class="timeline">${record.expert_reviews.map(r=>`<li><strong>${esc(r.reviewer_name || t('role.expert'))} · ${esc(r.assessment || '')}</strong><p>${esc(r.review_notes || '')}</p><p>${esc(r.recommended_next_step || '')}</p>${sourceLine(r)}</li>`).join('')}</div>` : ''}<div class="record-actions"><button class="button button--danger button--small" data-action="delete-scan" data-id="${esc(record.scan_id)}">${esc(t('common.delete','Delete saved history'))}</button></div></article>`;
  }

  async function renderSeedSafety() {
    const seedRecords = (MODULE_RESOURCES['seed-safety'] || []).map(s => resourceLink(s)).join('');
    let escalation = '';
    try { const d = await api('/api/seed/escalation'); escalation = renderDataCards(d.contacts || d.options || d.links || [], t('seed.official','Official escalation links')); }
    catch (e) { escalation = `<p class="field-help">${esc(t('seed.escalationUnavailable','Escalation directory unavailable from backend. Do not guess an office phone number.'))}</p>`; }
    const body = `<div class="inline-warning">${esc(t('seed.notProof'))}</div><div class="grid grid--2"><section class="panel"><div class="panel-head"><div><h2>${esc(t('seed.scanTitle'))}</h2><p>${esc(t('seed.scanNote'))}</p></div></div><div class="panel-body">${requireFarmer()}<form id="seedScanForm" class="form-stack" enctype="multipart/form-data"><div class="form-grid">${[['front_packet','seed.front','Front of packet'],['back_packet','seed.back','Back of packet'],['certification_tag','seed.tag','Certification tag'],['qr_label','seed.qrImage','QR/barcode label'],['receipt','seed.receipt','Receipt or bill']].map(([name,key,fallback])=>`<label><span>${esc(t(key,fallback))}</span><input type="file" name="${name}" accept="image/jpeg,image/png,image/webp"></label>`).join('')}</div><div class="form-grid">${[['crop','field.crop','text'],['variety','field.variety','text'],['brand','field.brand','text'],['lot_number','field.lot_number','text'],['batch_number','field.batch_number','text'],['packing_date','field.packing_date','date'],['validity_date','field.validity_date','date'],['germination_label_pct','field.germination_label_pct','number'],['purity_pct','field.purity_pct','number'],['net_weight','field.net_weight','text'],['mrp','field.mrp','number'],['dealer','field.dealer','text'],['certification_number','field.certification_number','text'],['qr_content','field.qr_content','text'],['farm_id','field.farm_id','text']].map(([name,key,type])=>`<label><span>${esc(t(key,humanize(name)))}</span><input name="${name}" type="${type}" ${type==='number'?'min="0" step="any"':''}></label>`).join('')}</div><div id="seedScanError" class="inline-error" role="alert" hidden></div><button class="button button--primary" type="submit">${esc(t('seed.scanButton','Save evidence and inspect OCR candidates'))}</button></form><div id="seedScanResult">${state.lastSeedScan ? renderSeedScanResult(state.lastSeedScan) : ''}</div></div></section><section class="panel"><div class="panel-head"><div><h2>${esc(t('seed.packetCheck'))}</h2><p>${esc(t('seed.checkOnlyNote','Checks label completeness only, not authenticity or safety.'))}</p></div></div><div class="panel-body"><form id="packetCheckForm" class="form-stack"><label><span>${esc(t('field.crop'))}</span><input name="crop"></label><label><span>${esc(t('field.variety'))}</span><input name="variety"></label><label><span>${esc(t('field.brand'))}</span><input name="brand"></label><label><span>${esc(t('field.lot_number'))}</span><input name="lot_number"></label><label><span>${esc(t('field.packing_date'))}</span><input name="packing_date" type="date"></label><label><span>${esc(t('field.validity_date'))}</span><input name="validity_date" type="date"></label><label><span>${esc(t('field.germination_label_pct'))}</span><input name="germination_label_pct" type="number" min="0" max="100" step="any"></label><label><span>${esc(t('field.mrp'))}</span><input name="mrp" type="number" min="0" step="any"></label><button class="button button--secondary" type="submit">${esc(t('seed.packetCheck'))}</button></form><div id="packetCheckResult" style="margin-top:12px"></div><hr><h3>${esc(t('seed.qrManual'))}</h3><form id="qrCheckForm" class="form-stack"><label><span>${esc(t('field.qr_content'))}</span><textarea name="qr_content" required maxlength="2000"></textarea></label><label><span>${esc(t('field.lot_number'))}</span><input name="lot_number"></label><label><span>${esc(t('field.brand'))}</span><input name="brand"></label><button class="button button--secondary" type="submit">${esc(t('seed.qrCheck','Compare entered details'))}</button></form><div id="qrCheckResult" style="margin-top:12px"></div><hr><h3>${esc(t('seed.qrDecode'))}</h3><form id="qrDecodeForm" class="form-stack" enctype="multipart/form-data"><label><span>${esc(t('seed.qrImage','QR/barcode label photo'))}</span><input type="file" name="image" accept="image/jpeg,image/png,image/webp" required></label><button class="button button--quiet" type="submit">${esc(t('seed.decodeButton','Decode QR / barcode'))}</button></form><div id="qrDecodeResult" style="margin-top:12px"></div></div></section></div><div class="grid grid--2">${panel(t('seed.germination'),`<form id="germinationForm" class="form-stack"><label><span>${esc(t('field.tested_count'))}</span><input name="tested_count" type="number" min="1" step="1" required></label><label><span>${esc(t('field.germinated_count'))}</span><input name="germinated_count" type="number" min="0" step="1" required></label><label><span>${esc(t('field.test_date'))}</span><input name="test_date" type="date" required></label><label><span>${esc(t('field.test_method'))}</span><select name="test_method"><option value="home_paper">Paper / plate method</option><option value="soil_tray">Soil tray</option><option value="other">Other</option></select></label><label><span>${esc(t('field.seed_lot_id'))}</span><input name="seed_lot_id"></label><label><span>${esc(t('field.label_germination_pct'))}</span><input name="label_germination_pct" type="number" min="0" max="100" step="any"></label><label><span>${esc(t('field.notes'))}</span><textarea name="notes"></textarea></label><button class="button button--primary" type="submit">${esc(t('seed.calculateGermination','Calculate and save informal test'))}</button></form><div id="germinationResult" style="margin-top:12px"></div><p class="inline-warning">${esc(t('seed.germinationNote'))}</p>`)}${panel(t('seed.complaint'),`<form id="seedComplaintForm" class="form-stack"><label><span>${esc(t('field.complaint_type'))}</span><select name="complaint_type" required>${['poor_germination','suspected_counterfeit','misleading_claims','missing_label','qr_mismatch','wrong_variety','crop_failure','dealer_refused_bill','other'].map(v=>`<option value="${v}">${esc(humanize(v))}</option>`).join('')}</select></label><label><span>${esc(t('field.crop'))}</span><input name="crop"></label><label><span>${esc(t('field.variety'))}</span><input name="variety"></label><label><span>${esc(t('field.brand'))}</span><input name="brand"></label><label><span>${esc(t('field.lot_number'))}</span><input name="lot_number"></label><label><span>${esc(t('field.dealer'))}</span><input name="dealer"></label><label><span>${esc(t('field.purchase_date'))}</span><input name="purchase_date" type="date"></label><label><span>${esc(t('field.sowing_date'))}</span><input name="sowing_date" type="date"></label><label><span>${esc(t('field.district'))}</span><input name="district"></label><label><span>${esc(t('field.mandal'))}</span><input name="mandal"></label><label><span>${esc(t('field.village'))}</span><input name="village"></label><label><span>${esc(t('field.affected_area_acres'))}</span><input name="affected_area_acres" type="number" min="0" step="any"></label><label><span>${esc(t('field.description'))}</span><textarea name="description" required maxlength="3000"></textarea></label><label><span>${esc(t('field.attachment_ids'))}</span><textarea name="attachment_ids" placeholder='["upload-id"]'></textarea><small class="field-help">Upload evidence in the Evidence Locker first; attach only IDs returned for your own account.</small></label><button class="button button--primary" type="submit">${esc(t('seed.submitComplaint','Save seed complaint record'))}</button></form><div id="seedComplaintResult" style="margin-top:12px"></div><p class="inline-warning">${esc(t('seed.notFiled'))}</p>`)}</div>${panel(t('seed.official'),escalation)}<section><div class="group-heading"><h2>${esc(t('seed.register','Seed records'))}</h2></div><div class="module-grid">${seedRecords}</div></section>`;
    return htmlPage('seed-safety', body);
  }

  function renderSeedScanResult(data) {
    const record = data.record || data.scan || data;
    const payload = record.payload || record;
    const candidates = Array.isArray(payload.ocr_candidates) ? payload.ocr_candidates : [];
    const editable = ['crop','variety','brand','lot_number','batch_number','packing_date','validity_date','germination_label_pct','purity_pct','net_weight','mrp','dealer','certification_number','qr_content','farm_id'];
    const vals = {};
    editable.forEach(k => { vals[k] = payload[k] ?? ''; });
    candidates.forEach(c => { if (editable.includes(c.field) && !vals[c.field] && c.candidate != null) vals[c.field] = c.candidate; });
    const confirmationForm = `<h3>${esc(t('seed.confirmTitle'))}</h3><p class="muted-copy">${esc(t('seed.confirmNote'))}</p><div class="status-line">${statusBadge(payload.ocr_status || 'OCR_UNAVAILABLE')}${statusBadge('UNVERIFIED')}</div>${candidates.length ? `<div class="notice-list">${candidates.map(c=>`<article class="notice-item"><h3>${esc(t(`field.${c.field}`,humanize(c.field)))}</h3><p>${esc(c.candidate || '')}</p><small>${esc(t('seed.ocrConfidence','OCR confidence: not scored. Compare the printed packet manually.'))}</small></article>`).join('')}</div>` : `<p class="field-help">${esc(t('seed.noOcr','No OCR candidates were returned. Enter the visible label values yourself.'))}</p>`}<form id="confirmSeedFieldsForm" class="form-grid" data-scan-id="${esc(record.id || '')}">${editable.map(k=>`<label><span>${esc(t(`field.${k}`,humanize(k)))}</span><input name="${k}" value="${esc(vals[k])}" ${['germination_label_pct','purity_pct','mrp'].includes(k)?'type="number" min="0" step="any"':(['packing_date','validity_date'].includes(k)?'type="date"':'type="text')}></label>`).join('')}<label class="checkbox-row span-all"><input name="confirmation" type="checkbox" required><span>${esc(t('seed.confirmCheckbox','I checked each field above against the physical packet.'))}</span></label><div class="form-submit-row"><button class="button button--primary" type="submit">${esc(t('seed.confirmButton'))}</button></div></form><div id="seedConfirmResult"></div>`;
    return `<div class="result-box" style="margin-top:14px"><div class="status-line">${statusBadge(record.status || 'USER_SUBMITTED')}${statusBadge(payload.ocr_status || 'UNVERIFIED')}</div><p>${esc(data.note || t('seed.notProof'))}</p>${sourceLine(record)}${confirmationForm}</div>`;
  }

  async function renderWeather() {
    const profileCity = state.user?.district || state.user?.mandal || state.user?.village || '';
    const selectedCity = String(state.weatherCity || profileCity).trim();
    let current = null; let error = '';
    if (selectedCity) {
      try { current = await api(`/api/weather?city=${encodeURIComponent(selectedCity)}${state.forceWeatherRefresh ? '&refresh=1' : ''}`); }
      catch (e) { error = e.message || t('errors.serviceUnavailable','The service could not complete this request. Please try again later.'); }
    } else {
      error = t('weather.enterLocationFirst','Enter your district or city to request weather information.');
    }
    state.forceWeatherRefresh = false;
    const data = current ? mapWeatherResponse(current) : {status:'UNAVAILABLE',error};
    const weatherBody = data.success ? `<section class="weather-hero" data-weather-motion="${Boolean(data.success && (data.status === 'LIVE' || data.status === 'CACHED' || data.status === 'DEMO'))}"><div class="weather-current"><strong class="weather-temp">${data.temperature == null ? 'Not available' : `${esc(num(data.temperature))}°C`}</strong><div><h2>${esc(selectedCity)}</h2><div class="status-line">${statusBadge(data.status)}${statusBadge(data.data_type)}</div></div></div><div class="weather-metrics">${[[t('weather.humidity','Humidity'),data.humidity,'%'],[t('weather.rainfall','Rainfall'),data.rainfall,' mm'],[t('weather.rainChance','Rain chance'),data.rain_probability,'%'],[t('weather.wind','Wind'),data.wind,' km/h']].map(([label,v,u])=>`<div class="weather-metric"><span>${esc(label)}</span><strong>${v == null ? 'Not available' : `${esc(num(v))}${u}`}</strong></div>`).join('')}</div>${data.status === 'CACHED' ? `<p class="inline-warning">${esc(t('weather.cached'))} ${esc(data.cache_age_seconds == null ? '' : `Cache age: ${num(data.cache_age_seconds)} seconds.`)}</p>` : ''}${data.status === 'DEMO' ? `<p class="inline-warning">${esc(t('weather.demoWarning','Fictional demonstration values. Never use them to make a farm decision.'))}</p>` : ''}${sourceLine(data)}</section>${Array.isArray(data.advisories) && data.advisories.length ? panel(t('weather.advisories','Weather notes'),`<ul class="result-list">${data.advisories.map(a=>`<li>${esc(a)}</li>`).join('')}</ul>`) : ''}${Array.isArray(data.forecast) && data.forecast.length ? panel(t('weather.forecast'),`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>${esc(t('weather.tableTime','Time'))}</th><th>${esc(t('weather.tableTemperature','Temperature'))}</th><th>${esc(t('weather.tableRainChance','Rain chance'))}</th><th>${esc(t('weather.tableRain','Rain'))}</th></tr></thead><tbody>${data.forecast.map(x=>`<tr><td>${esc(x.time || 'Not available')}</td><td>${x.temperature == null?'Not available':`${esc(num(x.temperature))}°C`}</td><td>${x.rain_probability == null?'Not available':`${esc(num(x.rain_probability))}%`}</td><td>${x.rainfall == null?'Not available':`${esc(num(x.rainfall))} mm`}</td></tr>`).join('')}</tbody></table></div>`) : ''}` : `<div class="result-box"><div class="status-line">${statusBadge(data.status || 'UNAVAILABLE')}</div><h2>${esc(t(selectedCity ? 'weather.noProvider' : 'weather.locationRequiredTitle', selectedCity ? 'Weather service unavailable' : 'Choose a location'))}</h2><p>${esc(data.error || error || t('common.unavailable'))}</p>${sourceLine(data)}</div>`;
    const body = `<div class="grid grid--2"><section class="panel"><div class="panel-head"><div><h2>${esc(t('weather.currentTitle','Weather reading'))}</h2><p>${esc(t('weather.sourceNote','Source timestamps are shown if the backend returns them.'))}</p></div><button class="button button--quiet button--small" data-action="refresh-weather">${esc(t('weather.refresh'))}</button></div><div class="panel-body">${weatherBody}<form id="weatherForm" class="filter-row" style="margin-top:14px"><label class="field" style="flex:1"><span>${esc(t('weather.city'))}</span><input name="city" value="${esc(selectedCity)}" maxlength="80" required></label><button class="button button--primary" type="submit">${esc(t('weather.load'))}</button></form></div></section><section class="panel"><div class="panel-head"><div><h2>${esc(t('weather.preparation','Weather preparation checklist'))}</h2><p>${esc(t('weather.checklistNote','General preparedness steps, not a claim of an incoming event.'))}</p></div></div><div class="panel-body"><ul class="result-list">${['weather.checkDrainage','weather.checkWater','weather.avoidSpraying','weather.secureMaterials','weather.localGuidance'].map((key,index)=>esc(t(key,['Check field drainage and keep channels clear before heavy rain.','Review irrigation and water storage during dry spells.','Avoid spraying when wind or rainfall may cause drift or wash-off.','Secure light materials before locally confirmed strong winds.','Use local agriculture-office guidance for crop-stage-specific decisions.'][index]))).map(x=>`<li>${x}</li>`).join('')}</ul><p class="field-help">${esc(t('weather.checklistSource','General checklist only; no local warning is inferred by this list.'))}</p></div></section></div><div class="module-grid">${resourceLink('water-sources')}${resourceLink('irrigation-records')}${resourceLink('irrigation-plans')}${resourceLink('rainwater-plans')}</div>`;
    return htmlPage('weather', body);
  }

  async function renderMarkets() {
    let records = []; let responseStatus = 'UNAVAILABLE'; let error = '';
    try { const d = await api('/api/markets'); records = Array.isArray(d.records) ? d.records : []; responseStatus = d.status || d.data_type || 'UNAVAILABLE'; state.marketRecords = records; }
    catch (e) { error = e.message; }
    const recordCards = rows => rows.length ? `<div class="resource-list">${rows.map(r=>`<article class="record-card"><div class="record-card-head"><h4>${esc(r.commodity || 'Not available')} · ${esc(r.market || 'Not available')}</h4>${statusBadge(r.data_type || 'UNAVAILABLE')}</div><p>${esc(r.district || '')}${r.price_date ? ` · ${esc(t('field.price_date'))}: ${esc(r.price_date)}` : ''}</p><div class="record-values"><div class="record-value"><dt>${esc(t('field.minimum_price'))}</dt><dd>${r.minimum_price==null?'Not available':esc(money(r.minimum_price))}</dd></div><div class="record-value"><dt>${esc(t('field.modal_price'))}</dt><dd>${r.modal_price==null?'Not available':esc(money(r.modal_price))}</dd></div><div class="record-value"><dt>${esc(t('field.maximum_price'))}</dt><dd>${r.maximum_price==null?'Not available':esc(money(r.maximum_price))}</dd></div><div class="record-value"><dt>${esc(t('field.arrival_quantity'))}</dt><dd>${r.arrival_quantity==null||r.arrival_quantity===''?'Not available':`${esc(r.arrival_quantity)} ${esc(r.arrival_unit || '')}`}</dd></div></div>${r.is_stale || r.stale ? `<p class="inline-warning">${esc(t('markets.stale','This price record is stale or date-unknown. Do not treat it as current.'))}</p>` : ''}${sourceLine(r)}</article>`).join('')}</div>` : emptyState(t('markets.noData'), error || t('markets.noData'));
    const body = `<div class="panel"><div class="panel-head"><div><h2>${esc(t('markets.priceRecords','Published market records'))}</h2><p>${esc(t('markets.priceNote','Every price is associated with a source and observation date when supplied.'))}</p></div><div class="status-line">${statusBadge(responseStatus)}</div></div><div class="panel-body"><form id="marketSearchForm" class="filter-row"><label class="field"><span>${esc(t('markets.commodity'))}</span><input name="commodity" placeholder="Cotton, paddy…"></label><label class="field"><span>${esc(t('markets.district'))}</span><input name="district"></label><button class="button button--primary" type="submit">${esc(t('markets.load'))}</button><button class="button button--secondary" type="button" data-action="markets-live">${esc(t('markets.live'))}</button></form><div id="marketResults" style="margin-top:15px">${recordCards(records)}</div><p class="field-help">${esc(t('markets.noForecast','No future price rise or profit is predicted. User-entered scenarios are calculations only.'))}</p></div></div><div class="grid grid--2">${panel(t('markets.trendTitle','Historical price trend'),`<form id="marketTrendForm" class="form-stack"><label><span>${esc(t('markets.commodity'))}</span><input name="commodity" required></label><label><span>${esc(t('field.market'))}</span><input name="market" required></label><button class="button button--secondary" type="submit">${esc(t('markets.trend'))}</button></form><div id="marketTrendResult" style="margin-top:12px"></div>`,t('markets.trendNote','Historical observations only; this does not forecast future prices.'))}${panel(t('finance.netTitle'),`<form id="netIncomeForm" class="form-stack"><label><span>${esc(t('finance.quantity','Quantity'))}</span><input name="quantity" type="number" min="0" step="any" required></label><label><span>${esc(t('finance.price','Sale price per unit'))}</span><input name="price" type="number" min="0" step="any" required></label><label><span>${esc(t('finance.transport','Transport cost'))}</span><input name="transport" type="number" min="0" step="any" value="0"></label><label><span>${esc(t('finance.charges','Market charges'))}</span><input name="charges" type="number" min="0" step="any" value="0"></label><label><span>${esc(t('finance.storageCost','Storage costs'))}</span><input name="storage_cost" type="number" min="0" step="any" value="0"></label><label><span>${esc(t('finance.otherCosts','Other costs'))}</span><input name="other_costs" type="number" min="0" step="any" value="0"></label><button class="button button--primary" type="submit">${esc(t('finance.calculate','Calculate scenario'))}</button></form><div id="netIncomeResult" style="margin-top:12px"></div>`,t('finance.disclaimer'))}</div><div class="grid grid--2">${panel(t('finance.breakTitle'),`<form id="breakEvenForm" class="form-stack"><label><span>${esc(t('finance.totalCosts','Total costs (₹)'))}</span><input name="total_costs" type="number" min="0" step="any" required></label><label><span>${esc(t('finance.expectedQuantity','Expected quantity'))}</span><input name="expected_quantity" type="number" min="0.000001" step="any" required></label><label><span>${esc(t('finance.unit','Unit'))}</span><input name="unit" value="quintal" required></label><label><span>${esc(t('finance.expectedPrice','Expected price (optional)'))}</span><input name="expected_price" type="number" min="0" step="any"></label><button class="button button--primary" type="submit">${esc(t('finance.calculate'))}</button></form><div id="breakEvenResult" style="margin-top:12px"></div>`,t('finance.disclaimer'))}${panel(t('finance.storeTitle'),`<form id="storageCalcForm" class="form-stack">${[['quantity','Quantity'],['days','Storage days'],['cost_per_quintal_day','Storage cost / quintal / day'],['sell_now_price','Sell-now price'],['future_price','User-entered future scenario price'],['transport','Transport cost'],['charges','Market charges'],['spoilage_cost','Expected spoilage cost (assumption)']].map(([name,label])=>`<label><span>${esc(label)}</span><input name="${name}" type="number" min="0" step="any" ${['quantity','days','cost_per_quintal_day','sell_now_price','future_price'].includes(name)?'required':''}></label>`).join('')}<button class="button button--primary" type="submit">${esc(t('finance.calculate'))}</button></form><div id="storageCalcResult" style="margin-top:12px"></div>`,t('finance.disclaimer'))}</div><div class="module-grid">${resourceLink('expenses')}${resourceLink('income')}${resourceLink('loans')}${resourceLink('market-prices')}</div>`;
    return htmlPage('markets', body);
  }

  async function renderResourcePage(resource) {
    const config = state.resources[resource];
    if (!config) return htmlPage('more', errorBox(t('errors.unknownResource','Unknown resource.'),'more'));
    const title = t(`resource.${resource}`, humanize(resource));
    const desc = t(`resourceDesc.${resource}`, t('common.genericResourceDesc','This page uses the backend resource allowlist. It is record storage, not a separate prediction or external verification service.'));
    if (!state.user && !config.public_read) return htmlPage('resource', authOrExplain(), {title,desc});
    let data;
    try { data = mapRecordsResponse(await api(`/api/v1/${encodeURIComponent(resource)}?limit=50`)); }
    catch (e) { return htmlPage('resource', errorBox(e.message,`resource/${resource}`), {title,desc}); }
    const records = Array.isArray(data.records) ? data.records : [];
    const canCreate = !!state.user && config.create_roles?.includes(state.user.role);
    const addButton = canCreate ? button(t('common.add','Add record'),'new-record',`data-resource="${esc(resource)}"`,'button button--primary') : '';
    const cards = records.length ? records.map(r=>renderResourceRecord(resource,r,config)).join('') : emptyState(t('common.noData'),t('common.noRecordsStored','No records were returned. This is not evidence that an external service has no records.'), canCreate ? button(t('common.add','Add record'),'new-record',`data-resource="${esc(resource)}"`,'button button--primary button--small') : '');
    const body = `<section class="panel"><div class="panel-head"><div><h2>${esc(title)}</h2><p>${esc(t('resource.count','Server returned'))}: ${esc(records.length)} · ${esc(t('common.dataStatus','Data status'))}: ${esc(data.data_type || 'UNAVAILABLE')}</p></div>${addButton}</div><div class="record-toolbar"><label class="search-control">${icon('i-search')}<input type="search" id="resourceSearch" placeholder="${esc(t('common.search','Search records'))}" data-resource="${esc(resource)}" aria-label="${esc(t('common.search','Search records'))}"></label><button class="button button--quiet button--small" data-action="resource-search" data-resource="${esc(resource)}">${esc(t('common.search','Search records'))}</button></div><div id="resourceList" class="resource-list" data-resource="${esc(resource)}">${cards}</div><div class="resource-foot"><span>${esc(t('resource.footnote','Ownership, status and provenance are controlled by the backend.'))}</span><span>${esc(data.count ?? records.length)} ${esc(t('resource.records','records'))}</span></div></section>${resource === 'seed-complaints' || resource === 'complaints' || resource === 'crop-damage-reports' || resource === 'insurance-claims' ? `<div class="inline-warning">${esc(t('seed.notFiled'))}</div>` : ''}`;
    return htmlPage('resource', body, {title,desc,kicker:`RESOURCE / ${resource.toUpperCase()}`});
  }
  function renderResourceRecord(resource, r, config) {
    const payload = r.payload || r;
    const preferred = ['name','title','task','crop','product_name','item_name','complaint_type','category','service_name','animal_type','commodity','market','question','provider','damage_type','scheme_id','record_date','test_date','entry_date','expense_date','income_date'];
    const key = preferred.find(k=>payload[k] != null && payload[k] !== '') || Object.keys(payload).find(k=>payload[k] != null && payload[k] !== '' && !['attachment_ids','packet_upload_ids','image_ids','draft_payload'].includes(k));
    const title = payload[key] != null ? payload[key] : `${humanize(resource)} #${r.id}`;
    const primary = Object.keys(payload).filter(k => !['attachment_ids','packet_upload_ids','image_ids','draft_payload','ocr_text'].includes(k)).slice(0,8);
    const ownerish = PRIVATE_RESOURCES.has(resource) || (!!state.user && state.user.role === 'admin');
    // A helper may be allowed to read delegated records. The generic list response does not
    // promise ownership metadata, so do not offer writes to delegated records in this generic UI.
    const canEdit = !!state.user && ownerish && resource !== 'family-helpers' && !config.admin_managed && (!config.public_read || (r.data_type === 'USER_SUBMITTED' && PRIVATE_RESOURCES.has(resource)));
    const isPendingHelperInvite = resource === 'family-helpers' && String(r.status || '').toUpperCase() === 'PENDING_CONSENT';
    let actions = '';
    if (isPendingHelperInvite) actions += button(t('family.accept','Accept invitation'),'family-accept',`data-id="${esc(r.id)}"`,'button button--primary button--small');
    if (resource === 'family-helpers' && state.user?.role === 'farmer' && payload.helper_user_id && ['PENDING_CONSENT','ACCEPTED'].includes(String(r.status || '').toUpperCase())) actions += button(t('family.revoke','Revoke access'),'transition-record',`data-resource="family-helpers" data-id="${esc(r.id)}" data-status="REVOKED"`,'button button--danger button--small');
    if (resource === 'storage-bookings' && !['CANCELLED','CLOSED'].includes(String(r.status || '').toUpperCase())) actions += button(t('common.cancel','Cancel request'),'transition-record',`data-resource="storage-bookings" data-id="${esc(r.id)}" data-status="CANCELLED"`,'button button--danger button--small');
    if (resource === 'equipment-bookings' && !['CANCELLED','CLOSED'].includes(String(r.status || '').toUpperCase())) actions += button(t('common.cancel','Cancel request'),'transition-record',`data-resource="equipment-bookings" data-id="${esc(r.id)}" data-status="CANCELLED"`,'button button--danger button--small');
    if (['farmer-listings','buyer-requests'].includes(resource) && !['CLOSED','CANCELLED'].includes(String(r.status || '').toUpperCase())) actions += button(t('common.closeListing','Close listing/request'),'transition-record',`data-resource="${esc(resource)}" data-id="${esc(r.id)}" data-status="CLOSED"`,'button button--quiet button--small');
    if (['seed-complaints','complaints','crop-damage-reports'].includes(resource) && !['CANCELLED','CLOSED'].includes(String(r.status || '').toUpperCase())) actions += button(t('common.addEvidenceStatus','Mark evidence added'),'transition-record',`data-resource="${esc(resource)}" data-id="${esc(r.id)}" data-status="EVIDENCE_ADDED"`,'button button--quiet button--small');
    if (resource === 'scheme-tracking' && !['CANCELLED','EXTERNAL_STATUS_REPORTED'].includes(String(r.status || '').toUpperCase())) actions += `<label class="field-inline"><span>${esc(t('schemes.updateStatus','Update tracking status'))}</span><select aria-label="${esc(t('schemes.updateStatus','Update tracking status'))}" data-scheme-status data-resource="scheme-tracking" data-id="${esc(r.id)}"><option value="">${esc(t('common.choose','Choose…'))}</option>${['DRAFT','SUBMITTED_TO_AUTHORITY','IN_PROGRESS','EXTERNAL_STATUS_REPORTED','NEEDS_ACTION','CANCELLED'].map(v=>`<option value="${v}">${humanize(v)}</option>`).join('')}</select></label>`;
    if (canEdit) {
      actions += button(t('common.edit','Edit'),'edit-record',`data-resource="${esc(resource)}" data-id="${esc(r.id)}"`,'button button--quiet button--small');
      if (resource === 'crop-tasks' && !['COMPLETED','SKIPPED'].includes(String(r.status || '').toUpperCase())) actions += button(t('calendar.markCompleted','Mark completed'),'complete-task',`data-id="${esc(r.id)}"`,'button button--secondary button--small');
      actions += button(t('common.delete','Archive'),'archive-record',`data-resource="${esc(resource)}" data-id="${esc(r.id)}"`,'button button--danger button--small');
    }
    if(state.user?.role==='admin' && config.admin_managed) {
      actions += `<form class="moderation-form" data-moderate-resource="${esc(resource)}" data-id="${esc(r.id)}"><label class="field"><span>${esc(t('admin.status','Moderation status'))}</span><select name="status">${['DRAFT','PENDING_REVIEW','ACTIVE','APPROVED','PUBLISHED','UNDER_REVIEW','SUSPENDED','BLOCKED','CLOSED','REJECTED','EXPIRED'].map(v=>`<option value="${v}" ${String(r.status).toUpperCase()===v?'selected':''}>${v}</option>`).join('')}</select></label><label class="field"><span>${esc(t('admin.sourceName','Source name'))}</span><input name="source_name" value="${esc(r.source_name || '')}" maxlength="160"></label><label class="field"><span>${esc(t('admin.https','Source URL (HTTPS, optional)'))}</span><input name="source_url" type="url" value="${esc(r.source_url || '')}" placeholder="https://…"></label><label class="field"><span>${esc(t('admin.verifiedDate','Verification date (optional)'))}</span><input name="last_verified" type="date" value="${esc(r.last_verified || '')}"></label><button class="button button--quiet button--small" type="submit">${esc(t('admin.moderate','Save moderation decision'))}</button></form>`;
    }
    const dataValues = primary.map(k=>`<div class="record-value"><dt>${esc(t(`field.${k}`,humanize(k)))}</dt><dd>${esc(Array.isArray(payload[k]) ? payload[k].join(', ') : typeof payload[k] === 'object' ? JSON.stringify(payload[k]) : payload[k])}</dd></div>`).join('');
    return `<article class="record-card"><div class="record-card-head"><h4>${esc(title)}</h4>${statusBadge(r.status || r.data_type || 'NOT_STATED')}</div><dl class="record-values">${dataValues}</dl><div class="status-line">${r.data_type ? statusBadge(r.data_type) : ''}${r.last_verified ? `<small>${esc(t('common.verified','Last verified'))}: ${esc(formatDate(r.last_verified))}</small>` : ''}</div>${sourceLine(r)}${actions ? `<div class="record-actions">${actions}</div>` : ''}</article>`;
  }

  function renderEvidence() {
    return htmlPage('evidence', `${authOrExplain()}<div class="grid grid--2"><section class="panel"><div class="panel-head"><div><h2>${esc(t('evidence.uploadTitle','Save private evidence'))}</h2><p>${esc(t('evidence.uploadNote','Only the upload reference returned by the backend can be attached to your private records.'))}</p></div></div><div class="panel-body"><form id="evidenceForm" class="form-stack" enctype="multipart/form-data"><label><span>${esc(t('evidence.file','Evidence image'))}</span><input name="image" type="file" accept="image/jpeg,image/png,image/webp" required></label><label><span>${esc(t('evidence.category','Evidence category'))}</span><select name="category"><option value="general">General</option><option value="receipt">Receipt / bill</option><option value="seed_packet">Seed packet</option><option value="crop_damage">Crop damage</option><option value="soil_card">Soil Health Card</option><option value="crop_observation">Crop observation</option></select></label><button class="button button--primary" type="submit">${esc(t('evidence.upload','Upload privately'))}</button></form><div id="evidenceResult" style="margin-top:12px"></div></div></section><section class="panel"><div class="panel-head"><div><h2>${esc(t('evidence.recent','Uploads returned in this page session'))}</h2><p>${esc(t('evidence.noList','The backend has no account-wide uploads listing endpoint. This view does not pretend to fetch one.'))}</p></div></div><div class="panel-body"><div id="evidenceRecent">${state.lastUpload ? renderUploadResult(state.lastUpload) : emptyState(t('common.noData'),t('evidence.noSessionUploads','No upload has been made from this page in this session.'))}</div></div></section></div>`);
  }
  function renderUploadResult(data) {
    const upload = data.upload || data;
    return `<div class="result-box"><div class="status-line">${statusBadge(upload.status || 'USER_SUBMITTED')}${statusBadge('PRIVATE_UPLOAD')}</div><p>${esc(t('evidence.uploadSuccess','The backend returned a private upload reference.'))}</p><dl class="metadata-list"><dt>${esc(t('evidence.uploadId','Upload ID'))}</dt><dd><code>${esc(upload.id || upload.upload_id || 'Not available')}</code></dd><dt>${esc(t('evidence.category','Category'))}</dt><dd>${esc(upload.category || 'Not available')}</dd><dt>${esc(t('common.created','Created'))}</dt><dd>${esc(formatDate(upload.created_at || upload.last_updated))}</dd></dl><p class="field-help">${esc(t('evidence.privateNote','Keep this ID private. Only your authorized records should reference it.'))}</p></div>`;
  }

  function renderSettings() {
    return htmlPage('settings', `<div class="grid grid--2"><section class="panel"><div class="panel-head"><div><h2>${esc(t('profile.title'))}</h2><p>${esc(t('settings.profileNote','Profile updates are persisted through the backend.'))}</p></div><button class="button button--primary" data-action="open-profile">${esc(t('settings.editProfile','Edit profile'))}</button></div><div class="panel-body">${state.user ? `<dl class="metadata-list">${[['name',state.user.name],['phone',state.user.phone],['role',localizeRole(state.user.role)],['district',state.user.district],['language',state.user.language]].map(([k,v])=>`<dt>${esc(t(`field.${k}`,humanize(k)))}</dt><dd>${esc(v || 'Not available')}</dd>`).join('')}</dl>` : authOrExplain()}</div></section><section class="panel"><div class="panel-head"><div><h2>${esc(t('settings.language','Language'))}</h2><p>${esc(t('settings.languageNote','Language choice is stored on this device and sent to the profile when signed in.'))}</p></div></div><div class="panel-body"><div class="button-row"><button class="button button--secondary" data-action="set-language" data-lang-choice="en">English</button><button class="button button--secondary" data-action="set-language" data-lang-choice="te">తెలుగు</button></div></div></section></div><div class="grid grid--2">${panel(t('settings.privacy','Privacy and data boundaries'),`<div class="privacy-panel"><h3>${esc(t('settings.privateUploads','Private uploads'))}</h3><p>${esc(t('settings.privateUploadsNote','The API authorizes retrieval by owner. Do not share upload IDs or put them in public listings.'))}</p></div><div class="privacy-panel"><h3>${esc(t('settings.external','External actions'))}</h3><p>${esc(t('settings.externalNote','Seed complaints, damage reports and grievance records are not officially filed by this app.'))}</p></div><div class="privacy-panel"><h3>${esc(t('settings.model','Model results'))}</h3><p>${esc(t('settings.modelNote','Crop model and disease model outputs are preliminary and may be unavailable or wrong.'))}</p></div>`) }${panel(t('settings.localData','Local drafts on this device'),`<p>${esc(t('settings.localDataNote','Clear drafts only if you understand that unsynced local content will be removed.'))}</p><button class="button button--danger" data-action="clear-drafts">${esc(t('offline.clear'))}</button><a class="button button--quiet" href="#/offline">${esc(t('nav.offline'))}</a>`)}</div>`);
  }

  async function renderNotifications() {
    const bits = [];
    if (!state.user) bits.push(authOrExplain());
    else {
      try {
        const d = await api('/api/notifications');
        const records = Array.isArray(d.records) ? d.records : Array.isArray(d.notifications) ? d.notifications : [];
        bits.push(records.length ? `<div class="notice-list">${records.map(n=>`<article class="notice-item notice-item--${esc(n.severity || 'info')}"><div class="status-line">${statusBadge(n.data_type || 'SYSTEM')}<small>${esc(formatDate(n.created_at))}</small></div><h3>${esc(n.title || 'Notification')}</h3><p>${esc(n.body || '')}</p>${!n.read_at ? button(t('notifications.markRead','Mark as read'),'notification-read',`data-id="${esc(n.id)}"`,'button button--quiet button--small') : `<small>${esc(t('notifications.read','Read'))}</small>`}</article>`).join('')}</div>` : emptyState(t('notifications.none'),t('notifications.noneHelp')));
      } catch (e) { bits.push(errorBox(e.message,'notifications')); }
    }
    const noticeResources = ['notices','local-alerts','service-directory','pest-reports'].map(s=>resourceLink(s)).join('');
    return htmlPage('notifications', `${panel(t('notifications.title','In-app notifications'),bits.join(''))}<section><div class="group-heading"><h2>${esc(t('notifications.directoryTitle','Notices and local directories'))}</h2></div><div class="module-grid">${noticeResources}</div></section>`);
  }

  function renderOffline() {
    const drafts = getDrafts();
    const html = drafts.length ? `<div class="resource-list">${drafts.map(d=>`<article class="record-card"><div class="record-card-head"><h4>${esc(d.resource)} · ${esc(d.operation_id)}</h4>${statusBadge(d.localStatus || 'LOCAL_ONLY')}</div><p>${esc(formatDate(d.device_saved_at))}</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(JSON.stringify(d.payload,null,2))}</pre><div class="record-actions"><button class="button button--danger button--small" data-action="remove-draft" data-id="${esc(d.operation_id)}">${esc(t('common.delete','Remove local draft'))}</button></div></article>`).join('')}</div>` : emptyState(t('offline.empty'),t('offline.local'));
    return htmlPage('offline', `<div class="inline-warning">${esc(t('offline.local'))}</div>${panel(t('offline.titlePage','Your local queue'),`<div id="offlineDraftList">${html}</div><div class="button-row" style="margin-top:14px"><button class="button button--primary" data-action="sync-drafts" ${drafts.length ? '' : 'disabled'}>${esc(t('offline.sync'))}</button><button class="button button--danger" data-action="clear-drafts" ${drafts.length ? '' : 'disabled'}>${esc(t('offline.clear'))}</button></div><div id="offlineSyncResult" style="margin-top:12px"></div>`)}<p class="field-help">${esc(t('offline.noUploads','File uploads are not queued offline. Drafts are sent only to documented sync-allowed resources, with a stable operation ID.'))}</p>`);
  }

  async function renderAdmin() {
    if (state.user?.role !== 'admin') return htmlPage('admin', `<div class="inline-warning">${esc(t('admin.protected','This section is only shown to an authorized administrator. Your server session is not an admin session.'))}</div>${authOrExplain()}`);
    const sections = [];
    let summary = null;
    try { summary = await api('/api/admin/summary'); sections.push(panel(t('admin.summary','System summary'),`<pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(JSON.stringify(summary,null,2))}</pre>${sourceLine(summary)}`)); }
    catch (e) { sections.push(panel(t('admin.summary','System summary'),errorBox(e.message,'admin'))); }
    let health = null;
    try { health = await api('/api/admin/data-health'); sections.push(panel(t('admin.freshness','Source freshness'),`<pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(JSON.stringify(health,null,2))}</pre><p class="field-help">${esc(health.note || '')}</p>`)); }
    catch (e) { sections.push(panel(t('admin.freshness','Source freshness'),errorBox(e.message,'admin'))); }
    let users = [];
    try { const u = await api('/api/admin/users?limit=100'); users = u.users || u.records || []; }
    catch (e) { sections.push(panel(t('admin.users','User access'),errorBox(e.message,'admin'))); }
    if (users.length) sections.push(panel(t('admin.users','User access'),`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>ID</th><th>Name</th><th>Role</th><th>Status</th><th>Change</th></tr></thead><tbody>${users.map(u=>`<tr><td>${esc(u.id)}</td><td>${esc(u.name)}</td><td>${esc(u.role)}</td><td>${esc(u.is_active ? 'ACTIVE':'SUSPENDED')}</td><td><form data-admin-user="${esc(u.id)}" class="admin-user-form"><select name="role" aria-label="Role">${USER_ROLES.map(r=>`<option value="${r}" ${r===u.role?'selected':''}>${humanize(r)}</option>`).join('')}</select><label class="checkbox-row"><input name="is_active" type="checkbox" ${u.is_active?'checked':''}><span>${esc(t('admin.active'))}</span></label><button class="button button--quiet button--small" type="submit">${esc(t('admin.update'))}</button></form></td></tr>`).join('')}</tbody></table></div>`));
    let audits = null;
    try { audits = await api('/api/admin/audit-logs?limit=40'); sections.push(panel(t('admin.audit','Recent audit log'),`<div class="resource-list">${(audits.records || []).map(a=>`<article class="record-card"><div class="record-card-head"><h4>${esc(a.action || 'Event')}</h4><small>${esc(formatDate(a.created_at))}</small></div><p>${esc(a.target || '')} · user ${esc(a.user_id ?? 'system')}</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(JSON.stringify(a.details || {},null,2))}</pre></article>`).join('')}</div>`)); }
    catch (e) { sections.push(panel(t('admin.audit','Recent audit log'),errorBox(e.message,'admin'))); }
    const body = `${sections.join('')}<div class="grid grid--2">${panel(t('admin.health','Operational health'),`<p><a href="/health" target="_blank" rel="noopener noreferrer">/health</a></p><p><a href="/ready" target="_blank" rel="noopener noreferrer">/ready</a></p>`,t('admin.healthNote','Health reports are diagnostics, not proof of production security.'))}${panel(t('admin.noticeTitle','Create in-app notice'),`<form id="adminNoticeForm" class="form-stack"><label><span>${esc(t('admin.userId','Recipient user ID'))}</span><input name="user_id" type="number" min="1" required></label><label><span>${esc(t('field.title'))}</span><input name="title" required maxlength="160"></label><label><span>${esc(t('field.body'))}</span><textarea name="body" required maxlength="2000"></textarea></label><label><span>${esc(t('field.severity'))}</span><select name="severity"><option value="info">Info</option><option value="warning">Warning</option><option value="urgent">Urgent</option><option value="success">Success</option></select></label><button class="button button--primary" type="submit">${esc(t('admin.sendNotice','Save in-app notification'))}</button></form><div id="adminNoticeResult" style="margin-top:12px"></div><p class="field-help">${esc(t('admin.noSms','No SMS or external message is sent by this action.'))}</p>`)}</div><div class="module-grid">${resourceLink('market-prices')}${resourceLink('schemes')}${resourceLink('notices')}${resourceLink('source-records')}</div>`;
    return htmlPage('admin', body);
  }

  function renderDataCards(rows, title) {
    if (!Array.isArray(rows) || !rows.length) return emptyState(t('common.noData'),t('common.noRecordsStored'));
    return `<h3>${esc(title)}</h3><div class="resource-list">${rows.map(row=>`<article class="record-card"><div class="record-card-head"><h4>${esc(row.title || row.name || row.label || row.service_name || row.scheme_name || 'Record')}</h4>${statusBadge(row.status || row.data_type || 'NOT_STATED')}</div><p>${esc(row.description || row.body || row.note || '')}</p>${sourceLine(row)}${row.url && /^https:\/\//.test(row.url) ? `<a href="${esc(row.url)}" target="_blank" rel="noopener noreferrer">${esc(t('common.openOfficial','Open official page'))}</a>` : ''}</article>`).join('')}</div>`;
  }

  function getDrafts() {
    try { const d = JSON.parse(readLocalText(draftKey()) || '[]'); return Array.isArray(d) ? d : []; } catch { return []; }
  }
  function draftKey() { return `rm-offline-drafts:${state.user?.id || 'guest'}`; }
  function saveDrafts(rows) {
    if (!writeLocalText(draftKey(), JSON.stringify(rows))) throw new Error(t('errors.localStorage','This browser could not save the draft on this device. Check browser storage settings and try again.'));
  }
  function queueDraft(resource, payload) {
    if (!OFFLINE_RESOURCES.has(resource)) throw new Error(t('offline.notQueueable','This resource is not enabled for offline sync.'));
    if (!state.user) throw new Error(t('common.signInNeeded'));
    const rows = getDrafts();
    const op = crypto.randomUUID ? crypto.randomUUID() : `rm-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    rows.push({operation_id:op,resource,payload,device_saved_at:new Date().toISOString(),localStatus:'LOCAL_ONLY'});
    saveDrafts(rows);
    setToast(t('offline.savedLocally','Draft saved on this device. The server has not confirmed it.'),'warning');
  }

  function formValues(form, config = null) {
    const data = {};
    const allowed = config ? new Set(config.fields.map(f=>f.name)) : null;
    for (const [key, raw] of new FormData(form).entries()) {
      if (key === 'confirmation' || key === 'image' || raw instanceof File) continue;
      if (allowed && !allowed.has(key)) continue;
      const schema = config?.fields.find(f=>f.name===key);
      const value = String(raw).trim();
      if (value === '') continue;
      if (schema?.type === 'number') {
        const n = Number(value); if (!Number.isFinite(n)) throw new Error(`${t(`field.${key}`,humanize(key))}: ${t('errors.enterNumber','enter a valid number')}`); data[key]=n;
      } else if (schema?.type === 'array' || schema?.type === 'object') {
        let parsed; try { parsed=JSON.parse(value); } catch { throw new Error(`${t(`field.${key}`,humanize(key))}: ${t('errors.validJson','enter valid JSON')}`); }
        if (schema.type === 'array' && !Array.isArray(parsed)) throw new Error(`${key} ${t('errors.mustArray','must be a JSON array')}`);
        if (schema.type === 'object' && (!parsed || Array.isArray(parsed) || typeof parsed !== 'object')) throw new Error(`${key} ${t('errors.mustObject','must be a JSON object')}`);
        data[key]=parsed;
      } else if (schema?.type === 'boolean') data[key] = raw === 'on' || value === 'true';
      else data[key]=value;
    }
    if (config) {
      // FormData omits unchecked checkboxes; send explicit false for allowlisted boolean fields.
      for (const field of config.fields.filter(f => f.type === 'boolean')) {
        const input = form.elements.namedItem(field.name);
        if (input && input.type === 'checkbox') data[field.name] = input.checked;
      }
      const missing = config.required.filter(k => data[k] === undefined || data[k] === null || data[k] === '');
      if (missing.length) throw new Error(`${t('errors.requiredFields','Required fields')}: ${missing.map(k=>t(`field.${k}`,humanize(k))).join(', ')}`);
    }
    return data;
  }
  function fieldInput(field, value) {
    const key = field.name;
    const val = value == null ? '' : (typeof value === 'object' ? JSON.stringify(value) : String(value));
    const label = t(`field.${key}`,humanize(key));
    const req = field.required ? 'required' : '';
    const hint = (field.type === 'array' || field.type === 'object') ? `<small class="field-help">${esc(field.type==='array' ? t('fields.jsonArray','Enter valid JSON such as ["one", "two"].') : t('fields.jsonObject','Enter a JSON object.'))}</small>` : '';
    if (field.type === 'textarea' || field.type === 'array' || field.type === 'object') return `<label class="${['array','object'].includes(field.type)?'span-all':''}"><span>${esc(label)}</span><textarea name="${esc(key)}" ${req} ${field.type==='array'?'placeholder="[]"':field.type==='object'?'placeholder="{}"':''}>${esc(val)}</textarea>${hint}</label>`;
    if (field.type === 'boolean') return `<label class="checkbox-row"><input name="${esc(key)}" type="checkbox" ${val==='true'?'checked':''}><span>${esc(label)}</span></label>`;
    const type = ['number','date'].includes(field.type) ? field.type : 'text';
    return `<label><span>${esc(label)}${field.required ? ' *' : ''}</span><input name="${esc(key)}" type="${type}" value="${esc(val)}" ${req} ${type==='number'?'step="any"':''}>${hint}</label>`;
  }
  function openRecordDialog(resource, record = null) {
    if (!state.user) { openDialog('authDialog'); return; }
    const config = state.resources[resource]; if (!config) return setToast(t('errors.unknownResource'),'error');
    if (!record && !config.create_roles?.includes(state.user.role)) return setToast(t('errors.roleCannotCreate','Your account role cannot create this record.'),'error');
    state.editingRecord = record;
    state.editingResource = resource;
    const form = $('#recordForm');
    form.dataset.resource = resource;
    form.dataset.id = record?.id || '';
    const current = record?.payload || record || {};
    form.innerHTML = config.fields.map(field=>fieldInput(field,current[field.name])).join('') + `<p id="recordFormError" class="inline-error span-all" role="alert" hidden></p><div class="form-submit-row"><button class="button button--quiet" type="button" data-close-dialog>${esc(t('common.cancel'))}</button><button class="button button--primary" type="submit">${esc(record ? t('common.saveChanges','Save changes') : t('common.save'))}</button></div>`;
    $('#recordDialogTitle').textContent = record ? t('common.editRecord','Edit record') : t('common.addRecord','Add record');
    $('#recordDialogKicker').textContent = resource.toUpperCase();
    $('#recordDialogNote').textContent = t('resource.formNote','Only documented resource fields are sent. Backend-generated ownership/status/source fields are not editable here.');
    openDialog('recordDialog');
  }
  function openDialog(id) {
    const dialog = document.getElementById(id); if (!dialog) return;
    $('#profileMenu').hidden = true; $('#profileButton').setAttribute('aria-expanded','false');
    if (!dialog.open) {
      state.dialogReturnFocus.set(dialog, document.activeElement instanceof HTMLElement ? document.activeElement : null);
      dialog.showModal();
    }
  }
  function closeDialogs() { $$('dialog[open]').forEach(d=>d.close()); }
  $$('dialog').forEach(dialog => {
    dialog.addEventListener('close', () => {
      const returnTo=state.dialogReturnFocus.get(dialog);
      window.requestAnimationFrame(() => {
        if (returnTo?.isConnected && typeof returnTo.focus === 'function') returnTo.focus({preventScroll:true});
        else if ($('#profileButton')?.isConnected) $('#profileButton').focus({preventScroll:true});
      });
    });
  });

  async function refreshSession() {
    if (state.sessionController) state.sessionController.abort();
    const controller = new AbortController(); state.sessionController = controller;
    try {
      const d = await api('/api/session',{signal:controller.signal,timeoutMs:12000});
      if (controller.signal.aborted || state.sessionController !== controller) return;
      state.session=d; state.user=d.user || null; state.csrf=d.csrf_token || state.csrf; state.sessionStatus='available';
    } catch (error) {
      if (isAbortError(error) || state.sessionController !== controller) return;
      state.user = null; state.session = null; state.sessionStatus = error.status === 401 ? 'signed-out' : 'unavailable';
    }
    if (state.sessionController !== controller) return;
    if (state.user?.language && ['en','te'].includes(state.user.language) && !readLocalText('rm-language')) state.lang = state.user.language;
    renderNavigation(); applyTranslations();
  }

  function handleAuthMode(mode) {
    const login = mode !== 'register';
    $('#loginForm').hidden = !login; $('#registerForm').hidden = login;
    $$('[data-auth-mode]').forEach(btn=>btn.classList.toggle('is-active', btn.dataset.authMode === (login?'login':'register')));
    $('#authTitle').textContent = login ? t('auth.loginTitle','Welcome back') : t('auth.create','Create account');
    if (!$('#authDialog').open) openDialog('authDialog');
    window.requestAnimationFrame(() => { const first = $(`${login ? '#loginForm' : '#registerForm'} input:not([type=hidden])`); if (first) first.focus(); });
  }
  async function onLogin(event) {
    event.preventDefault(); setInline('loginError','');
    const form = event.currentTarget;
    if (form.dataset.submitting === 'true') return;
    const submit = $('button[type="submit"]',form); form.dataset.submitting='true'; submit.disabled=true;
    if (state.loginController) state.loginController.abort();
    const controller = new AbortController(); state.loginController=controller;
    try {
      const body = formValues(form); const d = await api('/api/login',{method:'POST',body:JSON.stringify(body),signal:controller.signal,timeoutMs:20000});
      if (controller.signal.aborted || state.loginController !== controller) return;
      state.user=d.user; state.csrf=d.csrf_token || state.csrf; state.session={...state.session,user:state.user}; state.sessionStatus='available';
      form.reset(); closeDialogs(); renderNavigation(); setToast(t('auth.signedIn','You are signed in.'),'success'); await navigateToCurrent();
    } catch (e) { if (!isAbortError(e)) setInline('loginError',e.message || t('errors.requestFailed','The request could not be completed. Please try again.')); }
    finally { if (state.loginController === controller) state.loginController=null; form.dataset.submitting='false'; submit.disabled=false; }
  }
  async function onRegister(event) {
    event.preventDefault(); setInline('registerError','');
    const form=event.currentTarget; if(form.dataset.submitting==='true') return;
    const submit=$('button[type="submit"]',form); form.dataset.submitting='true'; submit.disabled=true;
    try {
      const data=formValues(form); data.language=state.lang;
      const d=await api('/api/register',{method:'POST',body:JSON.stringify(data),timeoutMs:20000});
      state.user=d.user; state.csrf=d.csrf_token || state.csrf; state.sessionStatus='available'; form.reset(); closeDialogs(); renderNavigation(); setToast(t('auth.registered','Account created and signed in.'),'success'); await navigateToCurrent();
    } catch(e) { if(!isAbortError(e)) setInline('registerError',e.message); }
    finally { form.dataset.submitting='false'; submit.disabled=false; }
  }
  async function logout() {
    if (!state.user || state.logoutPending) return;
    if (!confirm(t('auth.confirmLogout','Sign out of Rythu Mitra?'))) return;
    if (state.logoutController) state.logoutController.abort();
    const controller=new AbortController(); state.logoutController=controller; state.logoutPending=true;
    const buttonNode=$('[data-action="logout"]'); if(buttonNode) buttonNode.disabled=true;
    try {
      const d=await api('/api/logout',{method:'POST',body:'{}',signal:controller.signal,timeoutMs:20000});
      if(controller.signal.aborted || state.logoutController!==controller) return;
      state.csrf=d.csrf_token || null; state.user=null; state.session={...state.session,user:null}; state.sessionStatus='signed-out';
      setToast(t('auth.signedOut','Signed out.'),'success'); renderNavigation(); await navigateToCurrent();
    } catch(e) { if(!isAbortError(e)) setToast(e.message || t('errors.requestFailed','The request could not be completed. Please try again.'),'error'); }
    finally { if(state.logoutController===controller) state.logoutController=null; state.logoutPending=false; if(buttonNode?.isConnected) buttonNode.disabled=false; }
  }
  function openProfileDialog() {
    if (!state.user) { handleAuthMode('login'); return; }
    const form=$('#profileForm');
    const keys=['name','district','mandal','village','land_area','soil_type','irrigation','current_crop','crop_stage','previous_crop','season','budget','experience'];
    keys.forEach(k=>{ const input=form.elements.namedItem(k); if(input) input.value=state.user[k] ?? ''; });
    setInline('profileError',''); openDialog('profileDialog');
  }
  async function saveProfile(event) {
    event.preventDefault(); setInline('profileError','');
    try {
      const data=formValues(event.currentTarget);
      data.language=state.lang;
      const d=await api('/api/profile',{method:'POST',body:JSON.stringify(data)});
      state.user=d.user || {...state.user,...data}; closeDialogs(); renderNavigation(); setToast(t('profile.saved'),'success'); await navigateToCurrent();
    } catch(e) { setInline('profileError',e.message); }
  }

  async function onDiseaseSubmit(event) {
    event.preventDefault(); setInline('diseaseError','');
    const form = event.currentTarget; const input = $('#diseaseImage'); const image = input?.files?.[0];
    if (!image) return setInline('diseaseError',t('health.chooseFirst','Choose an image first.'));
    if (image.size <= 0) return setInline('diseaseError',t('health.invalidImage','Choose a valid JPEG, PNG or WebP image.'));
    if (image.size > 5*1024*1024) return setInline('diseaseError',t('errors.fileTooLarge','The selected file is too large. Choose a smaller file.'));
    const extensionOkay = /\.(jpe?g|png|webp)$/i.test(image.name || '');
    const imageMime = (image.type || '').toLowerCase();
    const typeOkay = !imageMime || ['image/jpeg','image/jpg','image/png','image/webp','application/octet-stream'].includes(imageMime);
    if (!extensionOkay || !typeOkay) return setInline('diseaseError',t('health.invalidImage','Choose a JPEG, PNG or WebP image.'));
    cancelDiseaseAnalysis(false);
    const controller = new AbortController(); state.diseaseController = controller;
    const runId = ++state.diseaseRunId;
    const progress=$('#diseaseProgress'); if (progress) progress.textContent=t('health.uploading','Sending the photo for preliminary analysis.');
    const submit=$('button[type="submit"]',form); if (submit) submit.disabled=true;
    const cancel=$('#cancelDiseaseAnalysis'); if (cancel) cancel.hidden=false;
    form.setAttribute('aria-busy','true');
    const steps=$$('[data-photo-step]'); steps.forEach((step,index)=>{step.classList.toggle('is-active',index===2);step.classList.toggle('is-complete',index<2);});
    try {
      const fd=new FormData(); fd.append('image',image);
      const result=mapDiseaseResponse(await api('/api/disease-scan',{method:'POST',body:fd,signal:controller.signal,timeoutMs:60000}));
      if (controller.signal.aborted || runId !== state.diseaseRunId || state.route !== 'crop-health') return;
      state.lastScan=result;
      const resultNode=$('#scanResult'); if(resultNode) resultNode.innerHTML=renderScanResult(result);
      if (progress) progress.textContent=t('health.complete','Backend response received.');
      const cancelNode=$('#cancelDiseaseAnalysis'); if(cancelNode) cancelNode.hidden=true;
      form.removeAttribute('aria-busy');
      const understand=$('[data-photo-step="understand"]'); if(understand){understand.classList.add('is-active','is-complete');}
      const heading=$('#scanResult h3'); if(heading) heading.focus({preventScroll:true});
      if (state.user) await navigateToCurrent();
    } catch(e) {
      if (isAbortError(e) || controller.signal.aborted || runId !== state.diseaseRunId) {
        if (progress) progress.textContent=t('health.analysisCancelled','Analysis was cancelled. No result was received.');
      } else if (e.status === 401) {
        state.user=null; state.sessionStatus='signed-out'; state.lastScan=null; renderNavigation();
        setInline('diseaseError',t('errors.signInRequired','Please sign in to continue.'));
        handleAuthMode('login');
      } else setInline('diseaseError',e.message || t('errors.requestFailed','The request could not be completed. Please try again.'));
    } finally {
      if (runId === state.diseaseRunId) {
        if (submit) submit.disabled=false;
        if (cancel) cancel.hidden=true;
        form.removeAttribute('aria-busy');
        state.diseaseController=null;
      }
    }
  }

  async function saveScan() {
    if (!state.user) { handleAuthMode('login'); return; }
    if (!state.lastScan?.scan_id) return setToast(t('health.noScan','No pending scan to save.'),'warning');
    try { await api('/api/scan-history',{method:'POST',body:JSON.stringify({scan_id:state.lastScan.scan_id})}); state.lastScan.history_save_available=false; setToast(t('health.scanSaved','Scan history linked to your account.'),'success'); await navigateToCurrent(); }
    catch(e) { setToast(e.message,'error'); }
  }
  async function deleteScan(id) {
    if (!confirm(t('health.confirmDelete','Delete this saved scan history entry? Uploaded evidence may be retained privately.'))) return;
    try { await api(`/api/scan-history/${encodeURIComponent(id)}`,{method:'DELETE'}); setToast(t('health.deleted','Scan history entry removed.'),'success'); await navigateToCurrent(); }
    catch(e) { setToast(e.message,'error'); }
  }

  function appendJsonResult(target, data, title = '') {
    const node=document.getElementById(target); if (!node) return;
    const obj=data || {};
    const pairs=Object.entries(obj).filter(([k,v])=>v!==undefined && v!==null && typeof v!=='object' && !['success'].includes(k));
    const bullets=Object.entries(obj).filter(([k,v])=>Array.isArray(v)).map(([k,v])=>`<div><strong>${esc(humanize(k))}</strong><ul class="result-list">${v.map(x=>`<li>${esc(typeof x==='object'?JSON.stringify(x):x)}</li>`).join('')}</ul></div>`).join('');
    node.innerHTML=`<div class="result-box">${title?`<h3>${esc(title)}</h3>`:''}<div class="status-line">${statusBadge(obj.status || obj.data_type || 'USER_ENTERED_CALCULATION')}${obj.data_type?statusBadge(obj.data_type):''}</div><dl class="metadata-list">${pairs.map(([k,v])=>`<dt>${esc(humanize(k))}</dt><dd>${esc(typeof v==='number' && /price|cost|income|profit|amount|value|total/i.test(k)?money(v):v)}</dd>`).join('')}</dl>${bullets}${sourceLine(obj)}${obj.disclaimer?`<p class="field-help">${esc(obj.disclaimer)}</p>`:''}${obj.note?`<p class="field-help">${esc(obj.note)}</p>`:''}</div>`;
  }
  async function submitCalc(event, path, target, options = {}) {
    event.preventDefault(); const form=event.currentTarget; const submit=$('button[type="submit"]',form); submit.disabled=true;
    try { const data=formValues(form); Object.keys(data).forEach(k=>{ if(data[k]==='') delete data[k]; }); const result=await api(path,{method:'POST',body:JSON.stringify(data)}); appendJsonResult(target,result,options.title || ''); }
    catch(e) { const node=document.getElementById(target); if(node) node.innerHTML=errorBox(e.message,state.route); }
    finally { submit.disabled=false; }
  }
  async function submitSeedScan(event) {
    event.preventDefault();
    if (!state.user || state.user.role !== 'farmer') return setInline('seedScanError', t('errors.farmerOnly','Sign in with a farmer account.'));
    setInline('seedScanError',''); const form=event.currentTarget; const fd=new FormData();
    const imageNames=['front_packet','back_packet','certification_tag','qr_label','receipt']; let count=0;
    for (const name of imageNames) { const file=form.elements.namedItem(name)?.files?.[0]; if(file){fd.append(name,file);count++;} }
    const fields=['crop','variety','brand','lot_number','batch_number','packing_date','validity_date','germination_label_pct','purity_pct','net_weight','mrp','dealer','certification_number','qr_content','farm_id'];
    fields.forEach(k=>{const v=form.elements.namedItem(k)?.value?.trim();if(v)fd.append(k,v);});
    if(!count) return setInline('seedScanError',t('seed.attachAtLeastOne','Attach at least one packet, tag, QR label or receipt photo.'));
    const btn=$('button[type="submit"]',form); btn.disabled=true;
    try { const data=await api('/api/seed/scans',{method:'POST',body:fd}); state.lastSeedScan=data; $('#seedScanResult').innerHTML=renderSeedScanResult(data); setToast(t('seed.scanSaved','Evidence uploaded. Review the OCR fields before confirming.'),'success'); }
    catch(e) { setInline('seedScanError',e.message); }
    finally { btn.disabled=false; }
  }
  async function confirmSeed(event) {
    event.preventDefault(); const form=event.currentTarget; const check=form.elements.namedItem('confirmation');
    if(!check?.checked) return setInline('seedConfirmResult',t('seed.confirmRequired','Please confirm only after comparing each field with the physical packet.'),'warning');
    const scanId=form.dataset.scanId; if(!scanId) return setInline('seedConfirmResult',t('seed.noScanId','No scan ID was returned. The scan cannot be confirmed.'),'error');
    const fields=['crop','variety','brand','lot_number','batch_number','packing_date','validity_date','germination_label_pct','purity_pct','net_weight','mrp','dealer','certification_number','qr_content','farm_id']; const confirmed={};
    for(const k of fields){const value=form.elements.namedItem(k)?.value?.trim(); if(value!=='') confirmed[k]=['germination_label_pct','purity_pct','mrp'].includes(k)?Number(value):value;}
    try { const result=await api(`/api/seed/scans/${encodeURIComponent(scanId)}/confirm`,{method:'POST',body:JSON.stringify({confirmation:true,confirmed_fields:confirmed})}); setInline('seedConfirmResult',result.message || t('seed.confirmed','Confirmed fields stored; authenticity remains unverified.'),'success'); setToast(t('seed.confirmed','Fields stored as farmer-confirmed.'),'success'); state.lastSeedScan={...state.lastSeedScan,record:result.scan,seed_lot:result.seed_lot}; }
    catch(e) { setInline('seedConfirmResult',e.message); }
  }
  async function checkPacket(event) {
    event.preventDefault(); const data=formValues(event.currentTarget); ['germination_label_pct','mrp'].forEach(k=>{if(data[k]!==undefined && data[k]!=='') data[k]=Number(data[k]);});
    try { appendJsonResult('packetCheckResult',await api('/api/seed/packet-check',{method:'POST',body:JSON.stringify(data)})); }
    catch(e) { $('#packetCheckResult').innerHTML=errorBox(e.message,'seed-safety'); }
  }
  async function checkQr(event) {
    event.preventDefault(); const data=formValues(event.currentTarget);
    try { appendJsonResult('qrCheckResult',await api('/api/seed/qr-check',{method:'POST',body:JSON.stringify(data)})); }
    catch(e) { $('#qrCheckResult').innerHTML=errorBox(e.message,'seed-safety'); }
  }
  async function decodeQr(event) {
    event.preventDefault(); const file=event.currentTarget.elements.namedItem('image')?.files?.[0]; if(!file) return;
    const fd=new FormData(); fd.append('image',file);
    try { appendJsonResult('qrDecodeResult',await api('/api/seed/qr-decode',{method:'POST',body:fd})); }
    catch(e) { $('#qrDecodeResult').innerHTML=errorBox(e.message,'seed-safety'); }
  }
  async function germination(event) {
    event.preventDefault(); let data;
    try { data=formValues(event.currentTarget); data.tested_count=Number(data.tested_count); data.germinated_count=Number(data.germinated_count); if(data.label_germination_pct!==undefined)data.label_germination_pct=Number(data.label_germination_pct); }
    catch(e) { $('#germinationResult').innerHTML=errorBox(e.message,'seed-safety'); return; }
    if(data.germinated_count>data.tested_count) return $('#germinationResult').innerHTML=errorBox(t('seed.germinationRange','Germinated seeds cannot exceed the tested count.'),'seed-safety');
    try { appendJsonResult('germinationResult',await api('/api/seed/germination',{method:'POST',body:JSON.stringify(data)})); }
    catch(e) { $('#germinationResult').innerHTML=errorBox(e.message,'seed-safety'); }
  }
  async function seedComplaint(event) {
    event.preventDefault(); let data;
    try { data=formValues(event.currentTarget); if(data.affected_area_acres!==undefined)data.affected_area_acres=Number(data.affected_area_acres); if(data.attachment_ids!==undefined)data.attachment_ids=JSON.parse(data.attachment_ids); }
    catch(e) { $('#seedComplaintResult').innerHTML=errorBox(e.message,'seed-safety'); return; }
    try { const result=await api('/api/seed/complaints',{method:'POST',body:JSON.stringify(data)}); appendJsonResult('seedComplaintResult',result); $('#seedComplaintResult').insertAdjacentHTML('afterbegin',`<div class="inline-warning">${esc(t('seed.notFiled'))}</div>`); }
    catch(e) { $('#seedComplaintResult').innerHTML=errorBox(e.message,'seed-safety'); }
  }

  async function searchMarkets(event) {
    event.preventDefault(); const data=formValues(event.currentTarget); const params=new URLSearchParams(); if(data.commodity)params.set('commodity',data.commodity);if(data.district)params.set('district',data.district);
    const target=$('#marketResults');target.innerHTML=loading();
    try { const res=await api(`/api/markets${params.size?'?'+params.toString():''}`); state.marketRecords=res.records||[]; target.innerHTML=state.marketRecords.length ? state.marketRecords.map(r=>`<article class="record-card"><div class="record-card-head"><h4>${esc(r.commodity)} · ${esc(r.market)}</h4>${statusBadge(r.data_type)}</div><p>${esc(r.price_date || 'Not available')} · ${esc(r.district || '')}</p><dl class="record-values"><div class="record-value"><dt>Minimum</dt><dd>${esc(r.minimum_price == null ? 'Not available' : money(r.minimum_price))}</dd></div><div class="record-value"><dt>Modal</dt><dd>${esc(r.modal_price == null ? 'Not available' : money(r.modal_price))}</dd></div><div class="record-value"><dt>Maximum</dt><dd>${esc(r.maximum_price == null ? 'Not available' : money(r.maximum_price))}</dd></div></dl>${r.is_stale ? `<p class="inline-warning">${esc(t('markets.stale','Stale price record'))}</p>`:''}${sourceLine(r)}</article>`).join('') : emptyState(t('markets.noData'),t('markets.noData')); }
    catch(e) { target.innerHTML=errorBox(e.message,'markets'); }
  }
  async function searchLiveMarkets() {
    const form=$('#marketSearchForm');
    const data=formValues(form);
    const params=new URLSearchParams({provider:'live'});
    if(data.commodity)params.set('commodity',data.commodity);
    if(data.district)params.set('district',data.district);
    $('#marketResults').innerHTML=loading();
    try {
      const res=await api(`/api/markets?${params.toString()}`);
      const rows=Array.isArray(res.records) ? res.records : [];
      $('#marketResults').innerHTML=rows.length ? `<div class="resource-list">${rows.map(r=>`<article class="record-card"><div class="record-card-head"><h4>${esc(r.commodity || 'Not available')} · ${esc(r.market || 'Not available')}</h4>${statusBadge(r.data_type || res.data_type || 'UNAVAILABLE')}</div><p>${esc(r.state || '')}${r.district ? ` · ${esc(r.district)}` : ''}${r.price_date ? ` · ${esc(t('field.price_date','Price date'))}: ${esc(r.price_date)}` : ''}</p><div class="record-values"><div class="record-value"><dt>${esc(t('field.minimum_price','Minimum price'))}</dt><dd>${r.minimum_price==null?'Not available':esc(money(r.minimum_price))}</dd></div><div class="record-value"><dt>${esc(t('field.modal_price','Modal price'))}</dt><dd>${r.modal_price==null?'Not available':esc(money(r.modal_price))}</dd></div><div class="record-value"><dt>${esc(t('field.maximum_price','Maximum price'))}</dt><dd>${r.maximum_price==null?'Not available':esc(money(r.maximum_price))}</dd></div></div>${r.is_stale ? `<p class="inline-warning">${esc(t('markets.stale','This price record is stale or date-unknown. Do not treat it as current.'))}</p>` : ''}${sourceLine(r)}</article>`).join('')}</div>` : emptyState(t('markets.noData','No market data'),res.error || t('markets.noData','No usable official market records were returned.'));
      if(res.note)$('#marketResults').insertAdjacentHTML('beforeend',`<p class="field-help">${esc(res.note)}</p>`);
    } catch(e) {
      $('#marketResults').innerHTML=errorBox(e.message,'markets');
    }
  }
  async function loadMarketTrend(event) {
    event.preventDefault();const data=formValues(event.currentTarget);const params=new URLSearchParams(data);
    try { const res=await api(`/api/markets/trend?${params}`);const rows=res.records||[];$('#marketTrendResult').innerHTML=rows.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Date</th><th>Min</th><th>Modal</th><th>Max</th><th>Status</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(r.date || 'Not available')}</td><td>${esc(r.minimum_price==null?'Not available':money(r.minimum_price))}</td><td>${esc(r.modal_price==null?'Not available':money(r.modal_price))}</td><td>${esc(r.maximum_price==null?'Not available':money(r.maximum_price))}</td><td>${statusBadge(r.data_type)} ${r.stale?statusBadge('STALE'):''}</td></tr>`).join('')}</tbody></table></div><p class="field-help">${esc(res.note || '')}</p>`:emptyState(t('common.noData'),t('markets.noData')); }
    catch(e) { $('#marketTrendResult').innerHTML=errorBox(e.message,'markets'); }
  }

  async function loadSchemeMatches() {
    const target=$('#schemeMatches');if(!target)return;target.innerHTML=loading();
    try { const res=await api('/api/schemes/matches');const rows=res.matches||[];target.innerHTML=rows.length?rows.map(r=>`<article class="record-card"><div class="record-card-head"><h4>${esc(r.name || 'Scheme')}</h4>${statusBadge(r.match_status || 'VERIFY_OFFICIALLY')}</div><p>${esc(r.description || '')}</p><p>${esc(r.benefit || '')}</p><p>${esc(r.eligibility_note || '')}</p>${sourceLine(r)}${r.official_url && /^https:\/\//.test(r.official_url)?`<a href="${esc(r.official_url)}" target="_blank" rel="noopener noreferrer">${esc(t('schemes.officialLink','Check official scheme page'))}</a>`:''}</article>`).join(''):emptyState(t('common.noData'),t('schemes.none','No published scheme match records were returned.')); }
    catch(e){target.innerHTML=errorBox(e.message,'schemes');}
  }

  async function submitWeatherForm(event) {
    event.preventDefault(); const data=formValues(event.currentTarget); state.weatherCity=data.city;state.forceWeatherRefresh=true;await navigateToCurrent();
  }

  async function onRecordSubmit(event) {
    event.preventDefault(); const form=event.currentTarget;const resource=form.dataset.resource;const id=form.dataset.id;
    const config=state.resources[resource];let data;
    try { data=formValues(form,config); }
    catch(e) { setInline('recordFormError',e.message); return; }
    const submit=$('button[type="submit"]',form);submit.disabled=true;
    try {
      if (id) { await api(`/api/v1/${encodeURIComponent(resource)}/${encodeURIComponent(id)}`,{method:'PATCH',body:JSON.stringify(data)}); setToast(t('common.saved'),'success'); }
      else { const result=await api(`/api/v1/${encodeURIComponent(resource)}`,{method:'POST',body:JSON.stringify(data)}); setToast(result.message || t('common.saved'),'success'); }
      closeDialogs();await navigateToCurrent();
    } catch(e) {
      if (!navigator.onLine && OFFLINE_RESOURCES.has(resource) && !id) {
        try { queueDraft(resource,data); closeDialogs(); await navigateToCurrent(); }
        catch(qe) { setInline('recordFormError',qe.message); }
      } else setInline('recordFormError',e.message);
    } finally { submit.disabled=false; }
  }
  async function archiveResource(resource,id) {
    if (!confirm(t('resource.confirmArchive','Archive this record? The backend performs a soft-delete where supported.'))) return;
    try { await api(`/api/v1/${encodeURIComponent(resource)}/${encodeURIComponent(id)}`,{method:'DELETE'}); setToast(t('common.archived'),'success'); await navigateToCurrent(); }
    catch(e) { setToast(e.message,'error'); }
  }
  async function completeTask(id) {
    if (!id) return;
    try { await api(`/api/v1/crop-tasks/${encodeURIComponent(id)}`,{method:'PATCH',body:JSON.stringify({status:'COMPLETED'})}); setToast(t('calendar.taskCompleted','Task marked completed by the server.'),'success'); await navigateToCurrent(); }
    catch(e) { setToast(e.message,'error'); }
  }
  async function resourceSearch(resource) {
    const input=$('#resourceSearch');const q=input?.value?.trim() || '';const target=$('#resourceList');if(!target)return;
    target.innerHTML=loading();
    try { const d=mapRecordsResponse(await api(`/api/v1/${encodeURIComponent(resource)}?limit=50&q=${encodeURIComponent(q)}`));const rows=d.records; const config=state.resources[resource];target.innerHTML=rows.length?rows.map(r=>renderResourceRecord(resource,r,config)).join(''):emptyState(t('common.noData'),t('common.noRecordsStored')); }
    catch(e){target.innerHTML=errorBox(e.message,`resource/${resource}`);}
  }
  async function updateNotificationRead(id) {
    try { await api(`/api/notifications/${encodeURIComponent(id)}/read`,{method:'POST',body:'{}'});setToast(t('notifications.markedRead','Notification marked read.'),'success');await navigateToCurrent(); }
    catch(e){setToast(e.message,'error');}
  }

  async function uploadEvidence(event) {
    event.preventDefault(); if(!state.user)return openDialog('authDialog');
    const form=event.currentTarget;const file=form.elements.namedItem('image')?.files?.[0];if(!file)return;
    const fd=new FormData();fd.append('image',file);fd.append('category',form.elements.namedItem('category').value);
    try { const result=await api('/api/v1/uploads',{method:'POST',body:fd});state.lastUpload=result;$('#evidenceResult').innerHTML=renderUploadResult(result);$('#evidenceRecent').innerHTML=renderUploadResult(result);setToast(t('evidence.uploadSuccess','The backend returned a private upload reference.'),'success'); }
    catch(e) { $('#evidenceResult').innerHTML=errorBox(e.message,'evidence'); }
  }

  async function saveLanguage(lang) {
    if(!['en','te'].includes(lang))return;
    $('#profileMenu').hidden=true; $('#profileButton').setAttribute('aria-expanded','false');
    state.lang=lang;
    const savedLocally = writeLocalText('rm-language',lang);
    applyTranslations();
    if (!savedLocally) setToast(t('settings.languageMemoryOnly','Language changed for this session, but browser storage is unavailable.'),'warning');
    if(state.user){try { const d=await api('/api/profile',{method:'POST',body:JSON.stringify({language:lang})});state.user=d.user || {...state.user,language:lang}; }catch(e){setToast(t('settings.languageLocal','Language changed on this device; server profile did not update: ')+e.message,'warning');} }
    await navigateToCurrent();
  }

  function openVoice() {
    state.voiceTranscript=''; state.voiceIntent=null; $('#voiceTranscript').textContent=t('voice.ready'); $('#voiceConfirm').disabled=true;
    const Recognition=window.SpeechRecognition || window.webkitSpeechRecognition;
    const support=$('#voiceSupportNote');
    support.innerHTML=`<label class="field"><span>${esc(t('voice.textLabel','What do you need?'))}</span><input id="voiceFallbackText" maxlength="500" placeholder="${esc(t('voice.fallback'))}"></label><button type="button" class="button button--quiet button--small" data-action="voice-check">${esc(t('voice.check','Check intent'))}</button>`;
    if(!Recognition) { $('#voiceTranscript').textContent=t('voice.unsupported'); openDialog('voiceDialog'); return; }
    openDialog('voiceDialog'); listenAgain();
  }
  function listenAgain() {
    const Recognition=window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!Recognition) { setToast(t('voice.unsupported'),'warning');return; }
    try {
      const rec=new Recognition(); rec.lang=state.lang==='te'?'te-IN':'en-IN'; rec.interimResults=false;rec.maxAlternatives=1;
      $('#voiceTranscript').textContent=t('voice.listening','Listening…');
      rec.onresult=e=>{state.voiceTranscript=e.results?.[0]?.[0]?.transcript || '';$('#voiceTranscript').textContent=`${t('voice.heard','What I heard')}: “${state.voiceTranscript}”`;$('#voiceConfirm').disabled=!state.voiceTranscript;};
      rec.onerror=()=>{$('#voiceTranscript').textContent=t('voice.unsupported');};
      rec.onend=()=>{}; rec.start();
    } catch(e) { $('#voiceTranscript').textContent=t('voice.unsupported'); }
  }
  async function checkVoiceIntent() {
    const fallback=$('#voiceFallbackText');const textValue=state.voiceTranscript || fallback?.value?.trim();
    if(!textValue) return setToast(t('voice.noText','Speak or type a request first.'),'warning');
    state.voiceTranscript=textValue;$('#voiceTranscript').textContent=`${t('voice.heard','What I heard')}: “${textValue}”`;
    try { state.voiceIntent=await api('/api/assistant/intent',{method:'POST',body:JSON.stringify({text:textValue})});$('#voiceConfirm').disabled=false;setToast(t('voice.intentReady','Intent suggested. Confirm before opening the proposed screen.'),'success'); }
    catch(e) { setToast(e.message,'error'); }
  }
  function confirmVoiceIntent() {
    if(!state.voiceTranscript)return;
    const textValue=state.voiceTranscript.toLowerCase();const intent=state.voiceIntent || {};
    const suggested=intent.suggested_route || intent.intent || '';
    const routes=[['weather',['weather','వాతావరణం']],['markets',['market','price','ధర']],['calendar',['task','today','టాస్క్']],['crop-health',['disease','plant','disease scan','రోగం']],['seed-safety',['seed','packet','విత్తనం']],['crop-planning',['crop','recommend','పంట']]];
    let target=routes.find(([route,words])=>words.some(w=>textValue.includes(w)))?.[0];
    if(!target) {
      const intentRoutes={'weather':'weather','market-prices':'markets','crop-tasks':'calendar','seed-scans':'seed-safety','complaints':'damage','help':'more'};
      target=intentRoutes[String(intent.intent || suggested).toLowerCase()] || (/weather|market|calendar|seed|crop|health/.test(String(suggested).toLowerCase()) ? String(suggested).replace(/^#?\/?/, '').replace(/^\//,'').split('/')[0] : null);
    }
    if(!target) { closeDialogs();setToast(t('voice.noRoute','No destination was identified. No action was performed.'),'warning'); return; }
    closeDialogs();goto(target);
  }
  function readAloud() {
    if(!('speechSynthesis' in window) || !window.SpeechSynthesisUtterance) return setToast(t('voice.ttsUnsupported','Read-aloud is not supported by this browser.'),'warning');
    const utterance=new SpeechSynthesisUtterance($('#view')?.innerText || '');utterance.lang=state.lang==='te'?'te-IN':'en-IN';utterance.rate=0.92;window.speechSynthesis.cancel();window.speechSynthesis.speak(utterance);
  }

  async function syncDrafts() {
    if(!state.user)return openDialog('authDialog');
    const drafts=getDrafts();if(!drafts.length)return setToast(t('offline.empty'),'warning');
    if(!navigator.onLine)return setToast(t('offline.noConnection','Connect to the internet before syncing local drafts.'),'warning');
    const allowed=drafts.filter(d=>OFFLINE_RESOURCES.has(d.resource));const target=$('#offlineSyncResult');if(target)target.innerHTML=loading();
    let allSynced=new Set();
    for(let i=0;i<allowed.length;i+=25){
      const batch=allowed.slice(i,i+25).map(d=>({operation_id:d.operation_id,resource:d.resource,payload:d.payload}));
      try { const res=await api('/api/offline/sync',{method:'POST',body:JSON.stringify({operations:batch})});(res.results||[]).forEach(r=>{if(r.status==='SYNCED')allSynced.add(r.operation_id);});if(target)target.insertAdjacentHTML('beforeend',`<p class="field-help">${esc(t('offline.batchResult','Sync batch'))}: ${esc(i+1)} to ${esc(Math.min(i+25,allowed.length))}</p>`); }
      catch(e){if(target)target.innerHTML=errorBox(e.message,'offline');break;}
    }
    const remaining=getDrafts().filter(d=>!allSynced.has(d.operation_id));saveDrafts(remaining);
    if(target)target.innerHTML=`<div class="${remaining.length?'inline-warning':'inline-success'}">${esc(t('offline.syncSummary','Backend-confirmed synced'))}: ${allSynced.size} · ${esc(t('offline.remaining','Still local or rejected'))}: ${remaining.length}. ${esc(t('offline.syncTruth','Only operations returned as SYNCED were removed from the local queue.'))}</div>`;
    await navigateToCurrent();
  }
  function removeDraft(id) { saveDrafts(getDrafts().filter(d=>d.operation_id!==id));setToast(t('offline.removed','Local draft removed.'),'success');navigateToCurrent(); }
  function clearDrafts() { const drafts=getDrafts();if(!drafts.length)return;if(!confirm(t('offline.confirmClear','Permanently remove all local drafts for this account from this device? Unsynced work will be lost.')))return;saveDrafts([]);setToast(t('offline.cleared','Local drafts cleared from this device.'),'success');navigateToCurrent(); }

  async function familyDashboard() {
    try { const d=await api('/api/family-dashboard'); const rows=d.accounts||[];const target=$('#familyDashboardResult'); if(target) target.innerHTML=rows.length?renderDataCards(rows,t('family.dashboard')):emptyState(t('family.noShares','No dashboard shares were returned.'),d.note || t('family.limited')); return d; }
    catch(e) { const target=$('#familyDashboardResult');if(target)target.innerHTML=errorBox(e.message,'family'); throw e; }
  }
  async function renderFamilyDashboard() {
    if(!state.user) return htmlPage('family', authOrExplain(), {title:t('family.dashboard','Family dashboard')});
    try { const d=await api('/api/family-dashboard');const rows=d.accounts||[];return htmlPage('family',`${rows.length?renderDataCards(rows,t('family.dashboard')):emptyState(t('family.noShares','No dashboard shares were returned.'),d.note || t('family.limited'))}<p class="field-help">${esc(d.note || '')}</p>`,{title:t('family.dashboard','Family dashboard')}); }
    catch(e) { return htmlPage('family',errorBox(e.message,'family-dashboard'),{title:t('family.dashboard','Family dashboard')}); }
  }
  async function transitionResource(resource,id,status) {
    if(!confirm(`${t('common.confirmTransition','Update record status to')} ${humanize(status)}?`)) { await navigateToCurrent(); return; }
    try { const r=await api(`/api/v1/${encodeURIComponent(resource)}/${encodeURIComponent(id)}`,{method:'PATCH',body:JSON.stringify({status})});setToast(r.message || t('common.statusUpdated','Status updated by the backend.'),'success');await navigateToCurrent(); }
    catch(e){setToast(e.message,'error');await navigateToCurrent();}
  }

  async function acceptFamilyHelper(id) {
    try { await api(`/api/v1/family-helpers/${encodeURIComponent(id)}/accept`,{method:'POST',body:'{}'});setToast(t('family.accepted','Helper access accepted.'),'success');await navigateToCurrent(); }
    catch(e){setToast(e.message,'error');}
  }

  async function loadAdminUser(event) {
    event.preventDefault();const form=event.currentTarget;const id=form.dataset.adminUser;const data={role:form.elements.namedItem('role').value,is_active:form.elements.namedItem('is_active').checked};
    try { await api(`/api/admin/users/${encodeURIComponent(id)}`,{method:'PATCH',body:JSON.stringify(data)});setToast(t('admin.updated','User permissions updated by the server.'),'success');await navigateToCurrent(); }
    catch(e) { setToast(e.message,'error'); }
  }
  async function submitModeration(event) {
    event.preventDefault();const form=event.currentTarget;const resource=form.dataset.moderateResource;const id=form.dataset.id;const data=formValues(form);
    if(data.source_url && !/^https:\/\//i.test(data.source_url)) return setToast(t('errors.httpsOnly','Source URL must begin with https://.'),'error');
    try { const result=await api(`/api/admin/resources/${encodeURIComponent(resource)}/${encodeURIComponent(id)}/moderate`,{method:'POST',body:JSON.stringify(data)});setToast(t('admin.moderated','Moderation status saved.'),'success');await navigateToCurrent(); }
    catch(e) { setToast(e.message,'error'); }
  }
  async function createAdminNotice(event) {
    event.preventDefault();const target=$('#adminNoticeResult');
    try { const data=formValues(event.currentTarget);data.user_id=Number(data.user_id);const res=await api('/api/admin/notifications',{method:'POST',body:JSON.stringify(data)});appendJsonResult('adminNoticeResult',res);target.insertAdjacentHTML('afterbegin',`<p class="inline-warning">${esc(t('admin.noSms','No SMS or external message is sent by this action.'))}</p>`); }
    catch(e) { target.innerHTML=errorBox(e.message,'admin'); }
  }

  async function adminImportCsv(file) {
    const fd=new FormData();fd.append('file',file);
    try { const r=await api('/api/admin/market-prices/import-csv',{method:'POST',body:fd});setToast(r.message || t('admin.imported','CSV imported.'),'success');await navigateToCurrent(); }
    catch(e){setToast(e.message,'error');}
  }

  function clearDiseasePhoto(updateInput = true) {
    if (state.qualityController) state.qualityController.abort();
    state.qualityController = null;
    state.qualityRunId += 1;
    if (state.photoPreviewUrl) { URL.revokeObjectURL(state.photoPreviewUrl); state.photoPreviewUrl = null; }
    const input = $('#diseaseImage');
    if (updateInput && input) { input.value = ''; state.lastScan = null; $('#scanResult')?.replaceChildren(); }
    const preview = $('#diseasePreview'); if (preview) preview.replaceChildren();
    const quality = $('#diseaseQuality'); if (quality) quality.textContent = t('health.photoPrompt','Choose a clear leaf photo in natural light. Photo checks are advisory only.');
    const remove = $('#removeDiseasePhoto'); if (remove) remove.disabled = true;
    const replace = $('#replaceDiseasePhoto'); if (replace) replace.disabled = true;
    const submit = $('#diseaseForm button[type="submit"]'); if (submit) submit.disabled = Boolean(state.diseaseController && !state.diseaseController.signal.aborted);
    const steps = $$('[data-photo-step]'); steps.forEach((step,index)=>{step.classList.toggle('is-active',index===0);step.classList.remove('is-complete');});
  }
  function cancelDiseaseAnalysis(showMessage = true) {
    if (state.diseaseController && !state.diseaseController.signal.aborted) state.diseaseController.abort();
    state.diseaseController = null;
    state.diseaseRunId += 1;
    const submit = $('#diseaseForm button[type="submit"]'); if (submit) submit.disabled = false;
    const cancel = $('#cancelDiseaseAnalysis'); if (cancel) cancel.hidden = true;
    const progress = $('#diseaseProgress'); if (progress) progress.textContent = showMessage ? t('health.analysisCancelled','Analysis was cancelled. No result was received.') : '';
    const form = $('#diseaseForm'); if (form) form.removeAttribute('aria-busy');
  }
  function inspectDiseasePhoto(file) {
    if (state.qualityController) state.qualityController.abort();
    const controller = new AbortController(); state.qualityController = controller;
    const runId = ++state.qualityRunId;
    const quality = $('#diseaseQuality');
    const preview = $('#diseasePreview');
    const submit = $('#diseaseForm button[type="submit"]');
    const remove = $('#removeDiseasePhoto');
    const replace = $('#replaceDiseasePhoto');
    if (state.diseaseController && !state.diseaseController.signal.aborted) cancelDiseaseAnalysis(false);
    if (!file) { clearDiseasePhoto(false); return; }
    const staleResult=$('#scanResult'); if (staleResult) staleResult.replaceChildren();
    state.lastScan=null;
    const maxBytes = 5 * 1024 * 1024; // Matches this backend's configured default; the server remains authoritative.
    const extensionOkay = /\.(jpe?g|png|webp)$/i.test(file.name || '');
    const mime = (file.type || '').toLowerCase();
    const mimeOkay = !mime || ['image/jpeg','image/jpg','image/png','image/webp','application/octet-stream'].includes(mime);
    if (file.size <= 0 || file.size > maxBytes || (!mimeOkay && !(!file.type && extensionOkay)) || !extensionOkay) {
      state.qualityController = null;
      if (preview) preview.replaceChildren();
      if (state.photoPreviewUrl) URL.revokeObjectURL(state.photoPreviewUrl);
      state.photoPreviewUrl = null;
      if (quality) quality.textContent = file.size > maxBytes ? t('errors.fileTooLarge','The selected file is too large. Choose a smaller file.') : t('health.invalidImage','Choose a JPEG, PNG or WebP image.');
      if (submit) submit.disabled = true;
      if (remove) remove.disabled = false;
      if (replace) replace.disabled = false;
      setInline('diseaseError', file.size > maxBytes ? t('errors.fileTooLarge','The selected file is too large. Choose a smaller file.') : t('health.invalidImage','Choose a JPEG, PNG or WebP image.'));
      return;
    }
    setInline('diseaseError','');
    if (state.photoPreviewUrl) URL.revokeObjectURL(state.photoPreviewUrl);
    const url = URL.createObjectURL(file); state.photoPreviewUrl = url;
    if (preview) {
      preview.replaceChildren();
      const card = document.createElement('div'); card.className = 'photo-preview photo-preview--checking'; card.id = 'diseasePhotoCard';
      card.addEventListener('animationend', event => { if (event.pseudoElement === '::after') card.classList.remove('photo-preview--checking'); });
      const image = document.createElement('img'); image.alt = t('health.previewAlt','Selected crop photo preview'); image.decoding = 'async'; image.src = url;
      const caption = document.createElement('div'); caption.className = 'photo-preview__caption';
      const name = document.createElement('strong'); name.textContent = file.name;
      const size = document.createElement('small'); size.textContent = `${Math.ceil(file.size / 1024)} KB`;
      caption.append(name,size); card.append(image,caption); preview.append(card);
      image.addEventListener('load', () => {
        if (controller.signal.aborted || runId !== state.qualityRunId || state.photoPreviewUrl !== url) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) card.classList.remove('photo-preview--checking');
        const maxSide = 384; const scale = Math.min(1,maxSide / Math.max(image.naturalWidth || 1,image.naturalHeight || 1));
        const width = Math.max(1,Math.round((image.naturalWidth || 1)*scale));
        const height = Math.max(1,Math.round((image.naturalHeight || 1)*scale));
        let note = t('health.photoLooksReady','Photo preview loaded. Image-quality checks are advisory only; the backend will validate the image again.');
        try {
          const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
          const ctx = canvas.getContext('2d',{willReadFrequently:true});
          if (ctx) {
            ctx.drawImage(image,0,0,width,height);
            const data = ctx.getImageData(0,0,width,height).data; let total=0, count=0;
            const gray = new Float32Array(width*height);
            for (let pixel=0, i=0; pixel<gray.length; pixel++, i+=4) {
              const value=.2126*data[i]+.7152*data[i+1]+.0722*data[i+2]; gray[pixel]=value; total+=value; count++;
            }
            const average = count ? total/count : 128;
            let lapSum=0, lapSquareSum=0, lapCount=0;
            for (let y=1; y<height-1; y+=2) for (let x=1; x<width-1; x+=2) {
              const i=y*width+x; const lap=4*gray[i]-gray[i-1]-gray[i+1]-gray[i-width]-gray[i+width];
              lapSum+=lap; lapSquareSum+=lap*lap; lapCount++;
            }
            const lapMean=lapCount?lapSum/lapCount:0;
            const detailVariance=lapCount?Math.max(0,lapSquareSum/lapCount-lapMean*lapMean):null;
            if (average < 42) note = t('health.photoDark','This photo looks quite dark in a quick check. Consider retaking it in even natural light. This check can be wrong.');
            else if (average > 238) note = t('health.photoBright','This photo looks very bright in a quick check. Check that leaf details are visible. This check can be wrong.');
            else if (detailVariance !== null && detailVariance < 28) note = t('health.photoSoftFocus','The quick check found little edge detail. The photo may be out of focus, but smooth leaves or backgrounds can cause this warning too. Inspect the preview; this is not a reliable diagnosis of image quality.');
          }
          canvas.width=1;canvas.height=1;
        } catch { note = t('health.photoQualityUnavailable','The quick photo check was unavailable. You can still request server-side validation.'); }
        if (quality) quality.textContent = note;
        state.qualityController = null;
        const steps = $$('[data-photo-step]'); steps.forEach((step,index)=>{step.classList.toggle('is-active',index===1);step.classList.toggle('is-complete',index===0);});
        if (submit) submit.disabled = false;
        if (remove) remove.disabled = false;
        if (replace) replace.disabled = false;
      },{once:true});
      image.addEventListener('error',()=>{
        if (controller.signal.aborted || runId !== state.qualityRunId) return;
        card.classList.remove('photo-preview--checking');
        if (quality) quality.textContent = t('health.photoPreviewFailed','The browser could not preview this image. Choose another image.');
        if (submit) submit.disabled = true;
        if (remove) remove.disabled = false;
        if (replace) replace.disabled = false;
      },{once:true});
    }
    if (quality) quality.textContent = t('health.photoChecking','Loading the image preview. Photo-quality checks are advisory only.');
    if (submit) submit.disabled = true;
    if (remove) remove.disabled = false;
    if (replace) replace.disabled = false;
  }
  function renderPreview(input, targetId) {
    const target=document.getElementById(targetId);if(!target)return;target.replaceChildren();
    const files=[...(input.files||[])].slice(0,5);
    files.forEach(file=>{
      if(!file.type.startsWith('image/'))return;
      const url=URL.createObjectURL(file);const node=document.createElement('div');node.className='photo-preview';
      const img=document.createElement('img');img.src=url;img.alt=`Preview of ${file.name}`;img.decoding='async';
      const caption=document.createElement('small');caption.textContent=`${file.name} · ${Math.round(file.size/1024)} KB`;node.append(img,caption);target.append(node);
      const revoke=()=>URL.revokeObjectURL(url);img.addEventListener('load',revoke,{once:true});img.addEventListener('error',revoke,{once:true});
    });
  }

  // Delegated interactions keep individual views simple and reviewable.
  document.addEventListener('click', async event => {
    const target=event.target.closest('[data-action],[data-close-dialog],[data-auth-mode],[data-lang],[data-lang-choice]');
    if (!target) return;
    if (target.matches('[data-close-dialog]')) { closeDialogs(); return; }
    if (target.matches('[data-auth-mode]')) { handleAuthMode(target.dataset.authMode); return; }
    if (target.matches('[data-lang]')) { await saveLanguage(target.dataset.lang); return; }
    if (target.matches('[data-lang-choice]')) { await saveLanguage(target.dataset.langChoice); return; }
    const action=target.dataset.action;
    try {
      if(action==='navigate') goto(target.dataset.route || 'home');
      else if(action==='open-auth') handleAuthMode(target.dataset.authMode || 'login');
      else if(action==='open-profile') openProfileDialog();
      else if(action==='logout') await logout();
      else if(action==='retry-session') { await refreshSession(); await navigateToCurrent(); }
      else if(action==='new-record') openRecordDialog(target.dataset.resource);
      else if(action==='edit-record') {
        const resource=target.dataset.resource,id=target.dataset.id;
        const data=await api(`/api/v1/${encodeURIComponent(resource)}/${encodeURIComponent(id)}`);openRecordDialog(resource,data.record);
      }
      else if(action==='archive-record') await archiveResource(target.dataset.resource,target.dataset.id);
      else if(action==='transition-record') await transitionResource(target.dataset.resource,target.dataset.id,target.dataset.status);
      else if(action==='complete-task') await completeTask(target.dataset.id);
      else if(action==='save-scan') await saveScan();
      else if(action==='delete-scan') await deleteScan(target.dataset.id);
      else if(action==='refresh-weather') { state.forceWeatherRefresh=true; if(state.route==='weather') await navigateToCurrent(); else goto('weather'); }
      else if(action==='markets-live') await searchLiveMarkets();
      else if(action==='load-scheme-matches') await loadSchemeMatches();
      else if(action==='resource-search') await resourceSearch(target.dataset.resource);
      else if(action==='notification-read') await updateNotificationRead(target.dataset.id);
      else if(action==='sync-drafts') await syncDrafts();
      else if(action==='clear-drafts') clearDrafts();
      else if(action==='remove-draft') removeDraft(target.dataset.id);
      else if(action==='voice-check') await checkVoiceIntent();
      else if(action==='voice-listen') listenAgain();
      else if(action==='family-dashboard') await familyDashboard();
      else if(action==='family-accept') await acceptFamilyHelper(target.dataset.id);
      else if(action==='remove-disease-photo') clearDiseasePhoto(true);
      else if(action==='replace-disease-photo') $('#diseaseImage')?.click();
      else if(action==='cancel-disease-analysis') cancelDiseaseAnalysis(true);
    } catch(e) { setToast(e.message || t('common.error'),'error'); }
  });

  document.addEventListener('submit', async event => {
    const form=event.target;
    if(form.id==='loginForm') return onLogin(event);
    if(form.id==='registerForm') return onRegister(event);
    if(form.id==='profileForm') return saveProfile(event);
    if(form.id==='recordForm') return onRecordSubmit(event);
    if(form.id==='diseaseForm') return onDiseaseSubmit(event);
    if(form.id==='recommendationForm') return submitCalc(event,'/api/recommendations','recommendationResult',{title:t('crop.recommendationResult','Model output')});
    if(form.id==='riskForm') return submitCalc(event,'/api/crop-risk','riskResult',{title:t('crop.riskResult','Rule-based risk factors')});
    if(form.id==='irrigationForm') return submitCalc(event,'/api/irrigation-advice','irrigationResult',{title:t('crop.irrigationResult','Irrigation reference')});
    if(form.id==='yieldForm') return submitCalc(event,'/api/yield-estimate','yieldResult',{title:t('crop.yieldResult','Yield reference')});
    if(form.id==='seedScanForm') return submitSeedScan(event);
    if(form.id==='confirmSeedFieldsForm') return confirmSeed(event);
    if(form.id==='packetCheckForm') return checkPacket(event);
    if(form.id==='qrCheckForm') return checkQr(event);
    if(form.id==='qrDecodeForm') return decodeQr(event);
    if(form.id==='germinationForm') return germination(event);
    if(form.id==='seedComplaintForm') return seedComplaint(event);
    if(form.id==='weatherForm') return submitWeatherForm(event);
    if(form.id==='marketSearchForm') return searchMarkets(event);
    if(form.id==='marketTrendForm') return loadMarketTrend(event);
    if(form.id==='netIncomeForm') return submitCalc(event,'/api/market-net-income','netIncomeResult',{title:t('finance.netResult','Net value scenario')});
    if(form.id==='breakEvenForm') return submitCalc(event,'/api/finance/break-even','breakEvenResult',{title:t('finance.breakResult','Break-even scenario')});
    if(form.id==='storageCalcForm') return submitCalc(event,'/api/storage-calculation','storageCalcResult',{title:t('finance.storageResult','Sell-now vs store scenario')});
    if(form.id==='evidenceForm') return uploadEvidence(event);
    if(form.matches('[data-admin-user]')) return loadAdminUser(event);
    if(form.matches('[data-moderate-resource]')) return submitModeration(event);
    if(form.id==='adminNoticeForm') return createAdminNotice(event);
  });
  document.addEventListener('change', event => {
    if(event.target.id==='diseaseImage') inspectDiseasePhoto(event.target.files?.[0] || null);
    if(event.target.matches('[data-scheme-status]') && event.target.value) transitionResource(event.target.dataset.resource,event.target.dataset.id,event.target.value);
  });
  $('#profileButton').addEventListener('click', () => {
    const menu=$('#profileMenu');const open=menu.hidden;menu.hidden=!open;$('#profileButton').setAttribute('aria-expanded',String(open));
    if (open) window.requestAnimationFrame(() => menu.querySelector('button, a[href]')?.focus({preventScroll:true}));
  });
  $('#voiceButton').addEventListener('click',openVoice);
  $('#readButton').addEventListener('click',readAloud);
  $('#notificationsButton').addEventListener('click',()=>goto('notifications'));
  $('#voiceListenAgain').addEventListener('click',listenAgain);
  $('#voiceConfirm').addEventListener('click',confirmVoiceIntent);
  $('#profileDialog').addEventListener('close',()=>$('#profileButton').setAttribute('aria-expanded','false'));
  $('#recordDialog').addEventListener('close',()=>{state.editingRecord=null;state.editingResource=null;});
  window.addEventListener('hashchange',()=>{ navigateToCurrent(); });
  window.addEventListener('resize',()=>{ const menu=$('#profileMenu'); if (menu && !menu.hidden) { menu.hidden=true; $('#profileButton').setAttribute('aria-expanded','false'); } });
  window.addEventListener('online',()=>{connectionState();setToast(t('status.online'),'success');});
  window.addEventListener('offline',()=>{connectionState();setToast(t('status.offline'),'warning');});
  document.addEventListener('visibilitychange',()=>document.documentElement.classList.toggle('rm-tab-hidden',document.hidden));
  document.addEventListener('keydown',event=>{
    const menu=$('#profileMenu');
    const menuOpen=menu && !menu.hidden;
    if (menuOpen && ['ArrowDown','ArrowUp','Home','End'].includes(event.key)) {
      const controls=[...menu.querySelectorAll('button:not(:disabled), a[href]')];
      if (controls.length) {
        const current=controls.indexOf(document.activeElement);
        const next=event.key==='Home'?0:event.key==='End'?controls.length-1:event.key==='ArrowDown'?(current+1+controls.length)%controls.length:(current<=0?controls.length-1:current-1);
        event.preventDefault(); controls[next].focus({preventScroll:true});
      }
    }
    if(event.key==='Escape') {
      const wasOpen=menuOpen;
      if(menu) menu.hidden=true; $('#profileButton').setAttribute('aria-expanded','false');
      if(wasOpen) $('#profileButton').focus({preventScroll:true});
    }
  });
  document.addEventListener('pointerdown',event=>{
    const wrap=$('.profile-wrap'); const menu=$('#profileMenu');
    if(wrap && menu && !wrap.contains(event.target) && !menu.hidden) { menu.hidden=true; $('#profileButton').setAttribute('aria-expanded','false'); }
  });

  async function bootstrap() {
    connectionState();
    try { state.locales.en=await fetchJsonAsset(`${localeRoot}en.json`,{}); }
    catch { state.locales.en={}; setToast('English language resources could not be loaded. Some text may use readable fallbacks.','warning'); }
    try { state.locales.te=await fetchJsonAsset(`${localeRoot}te.json`,{}); }
    catch { state.locales.te={}; }
    try { state.resources=await fetchJsonAsset(resourceConfigUrl,{}); }
    catch(e) { state.resources={}; setToast(t('errors.resourceConfig','Resource field schema unavailable. Record editing is disabled.'),'error'); }
    await refreshSession();
    applyTranslations();
    if (!location.hash) history.replaceState(null,'',`${location.pathname}${location.search}#/home`);
    await navigateToCurrent();
  }


  bootstrap();
})();
