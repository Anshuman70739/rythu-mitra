# Rythu Mitra Frontend Manual Test Checklist

Use a development/test account and non-sensitive sample data. Record PASS only after you actually perform a check. Otherwise use FAIL, BLOCKED or UNVERIFIED.

## Viewports

- [ ] 320px wide
- [ ] 360px wide
- [ ] 390px wide
- [ ] 430px wide
- [ ] 768px wide
- [ ] 1024px wide
- [ ] Large desktop (at least 1280px)
- [ ] No page-level horizontal scrolling; no clipped Telugu; fixed navigation does not cover the final form control; dialogs remain usable with the mobile keyboard open.

## Language

- [ ] English: every primary route, form, empty state, loading state, error state and dialog.
- [ ] Telugu: every primary route, form, empty state, loading state, error state and dialog.
- [ ] Long Telugu headings and button labels wrap naturally.
- [ ] Missing Telugu translations fall back to readable English rather than showing raw translation keys.
- [ ] Ask a native Telugu speaker to review draft translations before using with real farmers.

## Navigation and accessibility

- [ ] Skip link moves to main content.
- [ ] Tab/Shift+Tab can reach all controls; visible focus indicator remains visible.
- [ ] Sidebar, four-item mobile navigation, More section, Back/Forward and refresh work.
- [ ] Unknown route shows the not-found view and a working home link.
- [ ] Route change updates document title and focus without trapping focus.
- [ ] Profile menu works with keyboard arrows, Escape, outside click and route changes.
- [ ] Open and close every dialog with its close button and Escape; focus returns to the triggering control.
- [ ] Screen reader announces loading/result/error updates without reading large content blocks repeatedly.

## Crop Health photo flow

- [ ] Valid JPEG, PNG and WebP image shows preview.
- [ ] Empty, non-image, corrupt and over-limit files receive helpful errors.
- [ ] Replace and remove photo controls work; previous preview is cleared and object URLs are released.
- [ ] Quality checks are clearly advisory, not a diagnosis or guarantee.
- [ ] Image preview remains responsive for high-resolution phone photos.
- [ ] Analysis loading uses an indeterminate status rather than a fake percentage.
- [ ] Cancel analysis stops the request where the browser permits and prevents stale results from appearing.
- [ ] Navigate away during quality-check/analysis; stale responses do not update a different route.
- [ ] Backend result is explicitly preliminary; label verification is visible; ambiguous/missing confidence is withheld.
- [ ] Saving/history/expert review is shown as available only when the backend response supports it.

## Data trust and failure states

- [ ] Missing district/city does not silently use a guessed location for weather.
- [ ] Missing weather/market/provider data is shown as unavailable, not filled with realistic-looking fake data.
- [ ] LIVE, CACHED, DEMO, MODEL OUTPUT, CURATED and USER ENTERED statuses are visible wherever the backend provides them.
- [ ] Raw backend exception text is not exposed in farmer-facing messages.
- [ ] Slow/offline network, server errors, 401, 403, 404, 413, 422 and 429 receive understandable feedback.
- [ ] English and Telugu errors have useful text; no raw translation keys appear.

## Motion and reduced motion

- [ ] Contour signature draws once and does not restart on every minor interaction.
- [ ] Photo scan line only indicates preview checking, not diagnosis.
- [ ] Step progress, result reveal, task/status transition, dialog and offline banner are restrained.
- [ ] With OS `prefers-reduced-motion` enabled, signature/scan/looping motion is removed or reduced and content stays understandable.
- [ ] When the tab is hidden, nonessential animation pauses.
- [ ] Test on a low-end Android device or CPU-throttled browser for scrolling, uploads and control responsiveness.

## Final check

- [ ] Browser console has no uncaught JavaScript errors.
- [ ] Network panel shows no repeated/racing requests caused by route changes.
- [ ] Do not deploy until critical failures, actual model labels, provider status, auth/session and privacy behaviours are checked against the running backend.
