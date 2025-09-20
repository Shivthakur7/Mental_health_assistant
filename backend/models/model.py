import os
from pathlib import Path
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import model manager
from .model_manager import ensure_model_available

# Ensure model is available before proceeding
if not ensure_model_available():
    raise RuntimeError("Failed to download or locate ONNX model. Please check your internet connection and try again.")

# Paths
ONNX_DIR = Path("./onnx_model")
QUANT_MODEL_PATH = ONNX_DIR / "model_quantized.onnx"
MODEL_PATH = ONNX_DIR / "model.onnx"

# Load tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained(str(ONNX_DIR))
except Exception as e:
    logger.error(f"Failed to load tokenizer: {e}")
    raise RuntimeError("Failed to load tokenizer. Model may be corrupted.")

# Prefer quantized model if available
onnx_model_file = QUANT_MODEL_PATH if QUANT_MODEL_PATH.exists() else MODEL_PATH
if not onnx_model_file.exists():
    raise FileNotFoundError(
        f"ONNX model not found at {onnx_model_file}. This should not happen after model_manager check."
    )

# Initialize ONNX Runtime session (CPU)
try:
    session = ort.InferenceSession(str(onnx_model_file), providers=["CPUExecutionProvider"])
    logger.info(f"Successfully loaded ONNX model: {onnx_model_file}")
except Exception as e:
    logger.error(f"Failed to initialize ONNX session: {e}")
    raise RuntimeError("Failed to initialize ONNX model session.")


def softmax(logits: np.ndarray) -> np.ndarray:
    # Numerically stable softmax
    shift = logits - logits.max(axis=-1, keepdims=True)
    exp = np.exp(shift)
    return exp / exp.sum(axis=-1, keepdims=True)


def analyze_mood(text: str):
    # Tokenize to NumPy tensors
    inputs = tokenizer(text, return_tensors="np", padding=True, truncation=True)

    # Map inputs to ORT inputs with correct dtypes (int64 expected by model)
    ort_inputs = {}
    for k, v in inputs.items():
        arr = np.asarray(v)
        if arr.dtype != np.int64:
            arr = arr.astype(np.int64)
        ort_inputs[k] = arr

    # Run inference
    ort_outputs = session.run(None, ort_inputs)
    logits = ort_outputs[0]

    probs = softmax(logits)
    label_id = int(np.argmax(probs, axis=-1)[0])
    score = float(probs[0][label_id])

    label = "POSITIVE" if label_id == 1 else "NEGATIVE"
    mood_score = score if label == "POSITIVE" else -score
    return mood_score, label
