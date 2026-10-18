# Model assets

- `crop_model.pkl`: supplied crop recommendation model. Treat it as a trusted-code artifact because pickle loading can execute code. Do not replace it with an unknown download.
- `plant_disease_model.h5`: supplied Keras disease model weights. The source reports 128×128 RGB input and 15 output classes.
- `MODEL_ASSET_MANIFEST.json`: byte sizes and SHA-256 checksums for the exact supplied files.

The disease class-name mapping is not embedded here. See `../MODEL_PROVENANCE.md` and `../data/DISEASE_LABELS_REQUIRED.md`. The application intentionally does not treat the template as the real `data/disease_labels.json`.
