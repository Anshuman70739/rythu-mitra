# Pre-launch brand and trust checklist

## Applied in this candidate

- [x] Added `static/favicon.svg` and linked it from application and legal pages.
- [x] Replaced the vague guest headline and support copy with feature-specific language.
- [x] Removed decorative Unicode glyphs from feature-card icons in favor of inline SVG symbols.
- [x] Removed smooth scrolling, page reveal, panel-lift and shimmer effects. Kept only low-key color feedback and the loading state indicator.
- [x] Replaced pill-shaped language and profile controls with rectangular controls.
- [x] Replaced visible em dashes in the targeted UI strings and placeholder values.
- [x] Added `/privacy-policy` and `/terms-and-conditions` routes and dedicated pages.
- [x] Added legal links to the application footer.
- [x] Kept the existing Flask/Jinja plus vanilla JavaScript architecture.

## Must be completed by the project owner before public launch

- [ ] Choose and configure the custom domain and DNS records.
- [ ] Enable HTTPS and verify secure production cookies.
- [ ] Publish the real operator/institution name, postal address and monitored privacy/contact email.
- [ ] Confirm the server, database, uploads, logs and backups retention schedules and account deletion/data request workflow. The current UI does not provide complete account deletion or export functionality.
- [ ] Review privacy and terms pages with a qualified legal reviewer for the final deployment and applicable Indian law.
- [ ] Have a fluent Telugu reviewer validate the Telugu summaries; they are draft translations.
- [ ] Verify there are no AI-builder badges or vendor footer injections on the deployed site.
- [ ] Test on narrow phone, tablet and desktop with keyboard navigation and screen reader.
- [ ] Confirm model assets, disease labels, official market API key and weather credentials on the server, not in frontend JavaScript.
- [ ] Run live route tests and browser end-to-end tests after dependency installation.

## Important

A custom domain cannot be completed by editing this ZIP alone. It requires a selected hosting provider, a domain registered/controlled by the project owner, DNS configuration, and HTTPS setup after deployment. The legal pages are explicit pre-launch drafts because operator contact and retention policy were not provided in the source materials; do not represent them as legally reviewed final terms.
