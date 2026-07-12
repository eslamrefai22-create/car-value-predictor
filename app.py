"""
Car Purchase Budget Estimator
------------------------------
Flask backend that loads a pre-trained AdaBoost(ExtraTrees) regression
model to estimate how much a customer is likely to spend on a car,
based on their financial profile.
"""

import os
import logging

import joblib
import numpy as np
from flask import Flask, render_template, request, jsonify

# --------------------------------------------------------------------------
# App & logging setup
# --------------------------------------------------------------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "Model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "Scaler.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "model", "Columns.pkl")

# --------------------------------------------------------------------------
# Load model artifacts once, at startup
# --------------------------------------------------------------------------
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    columns = joblib.load(COLUMNS_PATH)
    logger.info("Model, scaler and columns loaded successfully.")
    logger.info("Expected columns: %s", columns)
except Exception as exc:  # pragma: no cover
    logger.exception("Failed to load model artifacts: %s", exc)
    model = scaler = columns = None

# Order of features the model was trained on (target column excluded)
FEATURE_ORDER = ["gender", "age", "annual Salary", "credit card debt", "net worth"]

# Gender encoding used during training (standard convention for this dataset)
GENDER_MAP = {"female": 0, "male": 1}


def build_feature_vector(payload: dict) -> np.ndarray:
    """Validate the incoming payload and build the model-ready feature array."""

    gender_raw = str(payload.get("gender", "")).strip().lower()
    if gender_raw not in GENDER_MAP:
        raise ValueError("النوع لازم يكون Male أو Female")
    gender = GENDER_MAP[gender_raw]

    try:
        age = float(payload.get("age"))
        salary = float(payload.get("salary"))
        debt = float(payload.get("debt"))
        net_worth = float(payload.get("net_worth"))
    except (TypeError, ValueError) as exc:
        raise ValueError("تأكد إن كل الحقول المالية أرقام صحيحة") from exc

    if not (16 <= age <= 100):
        raise ValueError("العمر لازم يكون بين 16 و 100 سنة")
    if salary < 0 or debt < 0 or net_worth < 0:
        raise ValueError("القيم المالية لازم تكون أكبر من أو تساوي صفر")

    # Only 'net worth' was standard-scaled at training time
    net_worth_scaled = scaler.transform([[net_worth]])[0][0]

    features = np.array([[gender, age, salary, debt, net_worth_scaled]])
    return features


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if model is None or scaler is None:
        return jsonify({"error": "الموديل مش متاح حاليًا، حاول تاني لاحقًا"}), 503

    payload = request.get_json(silent=True) or {}

    try:
        features = build_feature_vector(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        prediction = float(model.predict(features)[0])
        prediction = max(0.0, prediction)
    except Exception as exc:  # pragma: no cover
        logger.exception("Prediction failed: %s", exc)
        return jsonify({"error": "حصل خطأ غير متوقع أثناء التوقع"}), 500

    return jsonify({"prediction": round(prediction, 2)})


@app.route("/health")
def health():
    ok = model is not None and scaler is not None
    return jsonify({"status": "ok" if ok else "unavailable"}), (200 if ok else 503)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
