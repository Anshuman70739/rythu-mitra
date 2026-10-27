# Model Card — Plant Disease Image Classifier

## Intended use

If provenance and evaluation are verified, this model may provide a preliminary image-classification result to help a farmer decide whether to seek expert advice. It must not be treated as a confirmed diagnosis or as a basis for unreviewed chemical dosing.

## Artifact and current state

- Artifact: `models/plant_disease_model.h5`.
- Inference adapter: `rythu_mitra_backend/services/models.py`.
- The adapter requires a verified `disease_labels.json` class-order list, compatible model preprocessing, and matching output dimension.
- CI currently detects the weight file but reports `disease_model_bundle_usable=false` and `disease_labels_exists=false`.
- **Status: BLOCKED.** Do not return a disease name until the original class order and preprocessing are verified.

## Evidence status

| Item | Status |
|---|---|
| Weight file present | Verified by CI file-presence check |
| TensorFlow model loads in CI | NOT VERIFIED |
| Original class order / label map | MISSING / NOT VERIFIED |
| Image preprocessing and input shape | NOT VERIFIED end-to-end |
| Dataset source/licence/version | NOT VERIFIED |
| Held-out evaluation and per-class metrics | NOT VERIFIED |
| Field photos from Telangana with expert labels | NOT VERIFIED |
| Unknown/non-leaf/blur/low-light handling quality | NOT VERIFIED |
| Confidence threshold calibration | NOT VERIFIED |

## Required recovery steps

1. Locate the exact dataset and training code used to create this artifact, including its licence and class-to-index ordering.
2. Recreate the label list from the original training pipeline—not from guesses, filenames from unrelated datasets, or model output count alone.
3. Verify the model's expected image dimensions, color channel order, normalization, output activation, and output dimension.
4. Evaluate on a genuinely held-out split and report per-class precision, recall, F1, confusion matrix, and abstention behavior.
5. Test corrupt/oversized images, non-leaf photos, unsupported crops, blur, low light, and low-confidence predictions.
6. Keep the API in an explicit unavailable state until the above checks pass.

## Farmer safety

A model output is preliminary. It is not a confirmed diagnosis and cannot guarantee a treatment. If symptoms are severe or uncertain, refer the farmer to a local agriculture officer or Krishi Vigyan Kendra. Do not invent pesticide or fertilizer doses.
