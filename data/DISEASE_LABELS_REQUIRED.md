# Disease label mapping — required before disease names can be displayed

## Current status: BLOCKED — authoritative class names were not supplied

The supplied `models/plant_disease_model.h5` has 15 output classes according to the source archive's `MODEL_PROVENANCE.md`. Neither the source archive nor the HDF5 metadata includes the authoritative class-index-to-name mapping, the corresponding disease training dataset, or the disease training script. Therefore this bundle does **not** claim to know what classes 0–14 mean.

`disease_labels.template.json` is a 15-entry placeholder template using `null`. It is intentionally not read by the application. Do not rename it to `disease_labels.json` and do not replace the `null` entries with guessed labels.

## What to do when the original mapping is found

1. Obtain the exact mapping from the original model owner/training dataset or model-training code.
2. Confirm it has exactly 15 strings in the model's original output-index order (indices 0 through 14). Do not sort alphabetically unless that was how the model was trained.
3. Create `data/disease_labels.json` as a JSON list of those 15 exact labels, with no empty strings.
4. Run `python scripts/verify_model_assets.py --load-disease` in the project's virtual environment. This checks that the disease model loads and that the output count equals the label count; it still does not independently prove the semantic order is correct.
5. Test the scan workflow using appropriate sample images and retain the warning that results are preliminary, not a confirmed diagnosis.

Until that verified mapping exists, the disease endpoint should remain `UNAVAILABLE` instead of showing a guessed disease name. This is intentional and safer than falsely identifying a crop disease.
