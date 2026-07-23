"""
train_model.py

Trains a simple RandomForest classifier on the Iris dataset and saves it
to disk with joblib. Run this once locally before building the Docker image.

Usage:
    python train_model.py
"""

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODEL_PATH = "app/model.joblib"


def main():
    data = load_iris()
    X, y = data.data, data.target
    feature_names = list(data.feature_names)
    target_names = list(data.target_names)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test accuracy: {acc:.4f}")

    # Bundle model + metadata together so the API doesn't need to hardcode anything
    bundle = {
        "model": model,
        "feature_names": feature_names,
        "target_names": target_names,
    }
    joblib.dump(bundle, MODEL_PATH)
    print(f"Saved model bundle to {MODEL_PATH}")


if __name__ == "__main__":
    main()
