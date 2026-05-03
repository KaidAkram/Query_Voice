# Phase 3, Step 0 — ML Dependencies & GPU Stack
============================================

## 🚀 Execution Instructions
The machine learning stack was installed using:
```bash
pip install torch torchvision torchaudio transformers datasets evaluate scikit-learn peft bitsandbytes trl
```

## 📦 Core Component Breakdown

### 1. PyTorch (`torch`)
The engine for tensor calculus and backpropagation. Essential for GPU-accelerated training on the RTX 3070 Ti.

### 2. Hugging Face Stack
- **`transformers`:** Model loading and tokenization.
- **`datasets`:** Optimized data streaming for training.
- **`peft`:** Parameter-Efficient Fine-Tuning (LoRA/QLoRA).
- **`trl`:** Supervised Fine-Tuning (SFT) Trainer.

### 3. BitsAndBytes
Enables **4-bit quantization**, allowing our 7-billion parameter model to fit within 8GB of VRAM.
