"""Optional reproducible trainer for the crop recommendation model.

The deployed prototype uses the supplied `crop_model.pkl`; this script is not run
by the web app. Supply a licensed CSV containing the seven expected feature
columns and a `label` column rather than relying on a personal cache path.
"""
import argparse
import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a crop recommendation model from a local CSV.")
    parser.add_argument("dataset", type=Path, help="CSV with N,P,K,temperature,humidity,ph,rainfall,label")
    parser.add_argument("--output", type=Path, default=Path("crop_model.pkl"))
    args = parser.parse_args()
    df = pd.read_csv(args.dataset)
    required = set(FEATURES + ["label"])
    missing = required - set(df.columns)
    if missing: raise SystemExit(f"Dataset is missing columns: {', '.join(sorted(missing))}")
    x, y = df[FEATURES], df["label"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(x_train, y_train)
    print(f"Validation accuracy: {accuracy_score(y_test, model.predict(x_test)):.2%}")
    with args.output.open("wb") as file: pickle.dump(model, file)
    print(f"Saved {args.output}")


if __name__ == "__main__": main()
