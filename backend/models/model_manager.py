import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_model_available():
    """
    Ensures that the ONNX model is available. If not, downloads and converts it.
    Returns True if model is ready, False if there was an error.
    """
    onnx_dir = Path("./onnx_model")
    model_path = onnx_dir / "model.onnx"
    quant_model_path = onnx_dir / "model_quantized.onnx"
    
    # Check if any model exists
    if model_path.exists() or quant_model_path.exists():
        logger.info("ONNX model found, ready to use.")
        return True
    
    logger.info("ONNX model not found. Downloading and converting...")
    
    try:
        # Import here to avoid issues if dependencies aren't installed
        from optimum.onnxruntime import ORTModelForSequenceClassification
        from transformers import AutoTokenizer
        
        MODEL_ID = "distilbert-base-uncased-finetuned-sst-2-english"
        
        # Create directory
        onnx_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Loading model and tokenizer: {MODEL_ID}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = ORTModelForSequenceClassification.from_pretrained(MODEL_ID, export=True)
        
        logger.info(f"Saving ONNX model to {onnx_dir}")
        model.save_pretrained(str(onnx_dir))
        tokenizer.save_pretrained(str(onnx_dir))
        
        logger.info("Model download and conversion completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"Required packages not installed: {e}")
        logger.error("Please install: pip install optimum[onnxruntime] transformers")
        return False
    except Exception as e:
        logger.error(f"Error downloading/converting model: {e}")
        return False

def download_model_if_needed():
    """
    Downloads the model if it's not available. This is a wrapper for ensure_model_available
    that can be called from other modules.
    """
    return ensure_model_available()

if __name__ == "__main__":
    # Allow running this script directly to download the model
    success = ensure_model_available()
    if success:
        print("Model is ready!")
        sys.exit(0)
    else:
        print("Failed to prepare model!")
        sys.exit(1)
