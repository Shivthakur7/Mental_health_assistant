import os
from pathlib import Path
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

# Paths
ONNX_DIR = Path("./onnx_model")
QUANT_MODEL_PATH = ONNX_DIR / "model_quantized.onnx"
MODEL_PATH = ONNX_DIR / "model.onnx"

if not ONNX_DIR.exists():
    raise FileNotFoundError(
        "onnx_model directory not found. Run export_onnx.py to generate the ONNX model first."
    )

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(str(ONNX_DIR))

# Prefer quantized model if available
onnx_model_file = QUANT_MODEL_PATH if QUANT_MODEL_PATH.exists() else MODEL_PATH
if not onnx_model_file.exists():
    raise FileNotFoundError(
        f"ONNX model not found at {onnx_model_file}. Run export_onnx.py (and quantize_onnx.py optionally)."
    )

# Initialize ONNX Runtime session (CPU)
session = ort.InferenceSession(str(onnx_model_file), providers=["CPUExecutionProvider"])


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
