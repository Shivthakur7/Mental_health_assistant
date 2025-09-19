from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer
from pathlib import Path

MODEL_ID = "distilbert-base-uncased-finetuned-sst-2-english"
OUTPUT_DIR = Path("./onnx_model")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Loading model and tokenizer: {MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = ORTModelForSequenceClassification.from_pretrained(MODEL_ID, export=True)

    print(f"Saving ONNX model to {OUTPUT_DIR}")
    model.save_pretrained(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    print("Done. Files in ./onnx_model ready.")


if __name__ == "__main__":
    main()
