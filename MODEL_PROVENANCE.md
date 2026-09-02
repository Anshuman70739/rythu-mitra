# Disease Model Provenance

The supplied artifact is `plant_disease_model.h5`. Inspection on 2026-08-15 found:

- Keras model input: `(None, 128, 128, 3)`
- Keras model output: `(None, 15)`
- HDF5 metadata: backend, Keras version, model configuration, and training configuration only
- No HDF5 label/class attributes
- No label/class file in the repository
- No disease training dataset, class-index JSON, or disease training script in the repository

Therefore there is no authoritative class mapping available locally. The application returns `Model class N`, marks `label_verified: false`, and explicitly recommends professional confirmation. It will use `data/disease_labels.json` only if the owner supplies a verified 15-entry mapping from the original dataset/model source. The application never infers or guesses disease names from output indices.
