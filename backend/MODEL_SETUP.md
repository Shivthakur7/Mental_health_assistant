# Model Setup Guide

## Automatic Model Download

This application uses an ONNX model for sentiment analysis. The model will be **automatically downloaded** when the application starts if it's not already present.

### How it works:

1. **First Run**: When you start the server for the first time, the application will:
   - Check if the ONNX model exists in `./onnx_model/`
   - If not found, automatically download `distilbert-base-uncased-finetuned-sst-2-english` from Hugging Face
   - Convert it to ONNX format
   - Save it locally for future use

2. **Subsequent Runs**: The application will use the locally cached model for faster startup.

### Model Details:
- **Model**: DistilBERT base uncased finetuned on SST-2
- **Task**: Sentiment Analysis (Positive/Negative)
- **Size**: ~255MB (original), ~64MB (quantized version if available)
- **Format**: ONNX for optimized inference

### Manual Model Download:

If you want to pre-download the model, you can run:

```bash
cd backend
python -m models.model_manager
```

Or use the original export script:

```bash
cd backend
python utils/export_onnx.py
```

### Deployment Notes:

- **VM/Cloud Deployment**: The model will be downloaded automatically on first startup
- **Docker**: Include model download in your startup script or let it download on first run
- **Production**: Consider pre-downloading the model in your build process for faster startup

### Dependencies Required:

The following packages are needed for model download (already in requirements.txt):
- `optimum[onnxruntime]`
- `transformers`
- `onnxruntime`

### Troubleshooting:

1. **Internet Connection**: Model download requires internet access
2. **Disk Space**: Ensure ~300MB free space for model files
3. **Permissions**: Write access needed for `./onnx_model/` directory

### File Structure After Download:

```
backend/onnx_model/
├── config.json
├── model.onnx
├── model_quantized.onnx (if quantization is run)
├── special_tokens_map.json
├── tokenizer.json
├── tokenizer_config.json
└── vocab.txt
```

**Note**: These model files are excluded from Git via `.gitignore` to keep the repository size manageable.
