from onnxruntime.quantization import quantize_dynamic, QuantType
from pathlib import Path

INPUT_MODEL = Path("./onnx_model/model.onnx")
OUTPUT_MODEL = Path("./onnx_model/model_quantized.onnx")


def main():
    if not INPUT_MODEL.exists():
        raise FileNotFoundError(f"ONNX model not found at {INPUT_MODEL}. Run export_onnx.py first.")

    OUTPUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
    print(f"Quantizing {INPUT_MODEL} -> {OUTPUT_MODEL}")
    quantize_dynamic(
        model_input=str(INPUT_MODEL),
        model_output=str(OUTPUT_MODEL),
        weight_type=QuantType.QInt8,
    )
    print("Quantization complete.")


if __name__ == "__main__":
    main()
