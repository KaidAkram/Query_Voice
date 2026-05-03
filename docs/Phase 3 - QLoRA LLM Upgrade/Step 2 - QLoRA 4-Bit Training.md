# Phase 3, Step 2 — QLoRA 4-Bit Training Configuration
===================================================

## 🧠 Technical Strategy
To fine-tune the **Qwen-2.5-Coder-7B** model on a single 8GB GPU, we implemented a sophisticated QLoRA (Quantized Low-Rank Adaptation) strategy.

## ⚙️ Model Loading & Quantization
We used **BitsAndBytes** to quantize the model weights to 4-bit upon loading.
- **Dtype:** `torch.bfloat16`
- **Quant Type:** `nf4` (NormalFloat4)
- **Double Quant:** Enabled to save an additional ~0.4 bits per parameter.

## 🛠️ LoRA Parameters
- **Rank (r):** 16
- **Alpha:** 32
- **Target Modules:** All linear layers in the transformer block.
- **Total Trainable Parameters:** ~40 Million (0.52% of total).

## 🚀 Optimization Settings
- **Optimizer:** `paged_adamw_32bit` (prevents OOM by offloading to CPU RAM).
- **Gradient Checkpointing:** Enabled to minimize activation memory.
- **Learning Rate:** 2e-4 with a constant scheduler.
- **Batch Size:** 1 with 16 steps of Gradient Accumulation.

## 📈 Performance
- **Time per iteration:** ~51 seconds (on original 20k dataset) -> optimized by sampling to 3,000 rows.
- **Final Epochs:** 2
- **Training Time:** ~5.5 Hours.
