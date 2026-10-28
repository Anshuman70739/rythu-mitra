# Fresh model training

Open [`colab_train_fresh_models.ipynb`](colab_train_fresh_models.ipynb) in Google Colab and select a GPU runtime. The notebook trains both models from scratch; it does not load any model or training data from this repository.

- Disease images download from the TensorFlow Datasets PlantVillage catalog. This is controlled-background imagery, so validation accuracy does not establish performance on farmer field photos.
- Crop recommendations use a new CSV downloaded from the [Mendeley crop recommendation dataset](https://data.mendeley.com/datasets/vynxnppr7j/1) (dataset page lists CC BY 4.0). Upload the CSV and map its actual headers in `COLUMN_MAP`; the notebook stops if the required seven backend inputs and label are not present.
- The output zip includes `crop_model.pkl`, `plant_disease_model.h5`, `disease_labels.json`, and validation/provenance reports. Install the model files under `models/` and the disease label list at `data/disease_labels.json`.

Colab training has not been run by this repository's CI. Review the output metrics and data license before using the artifacts. Model scores are not guarantees of field performance.

