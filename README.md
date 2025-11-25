# 🎧 Speech-to-Text Transcriber (Whisper + Faster-Whisper)

Generate clean transcripts or SRT subtitles from any audio file using Whisper (via Faster-Whisper).

---

## 🌟 Features

- ✔ Supports **Whisper Medium model** (with GPU acceleration if available)
- ✔ **Two output modes**:

  - **SRT subtitles** (with timestamps)
  - **Plain text transcript**

- ✔ Automatically detects language
- ✔ Uses **Faster-Whisper** for high-speed inference
- ✔ Runs on **CPU or GPU** automatically (depending on your system)

---

# 🚀 1. Environment Setup (Conda)

Create and activate a new Conda environment:

```bash
conda create -n whisper python=3.10 -y
conda activate whisper
```

---

# ⚡ 2. Install PyTorch (with optional GPU support)

### If your computer has an NVIDIA GPU

Install CUDA-enabled PyTorch, eg:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### If your computer does NOT have a GPU

Install CPU-only PyTorch:

```bash
pip install torch torchvision torchaudio
```

You can still run the project — it simply uses CPU fallback.

---

# 🎤 3. Install Faster-Whisper

```bash
pip install faster-whisper
```

Faster-Whisper will automatically download the model you specify (e.g., `small`, `medium`, `medium.en`, `large-v2`, etc.) from HuggingFace on first run.

---

# 🎯 4. Choosing a Model

This project currently defaults to:

```python
model_size = "medium"
```

Because:

- Whisper **medium** provides a good balance of accuracy and speed
- It fits well into 6GB GPUs (e.g., RTX 4050)
- Users without GPUs can still run it on CPU

You may change:

```python
model_size = "small"
model_size = "medium"
model_size = "medium.en"
model_size = "large-v2"
model_size = "large-v3"
```

All official models are hosted at:
[https://huggingface.co/Systran](https://huggingface.co/Systran)

---

# 📁 5. Project Structure

---

# 📝 6. How to Run

## ➤ **Run SRT Subtitle Generator**

Script: `run-srt.py`

```bash
python run-srt.py
```

Output example:

```
SRT saved to：output-srt/yourfile - transcript.srt
Detected language 'en' with probability 0.98
```

---

## ➤ **Run Plain Text Transcript Generator**

Script: `run-txt.py`

```bash
python run-txt.py
```

Output example:

```
Transcription saved to: output-text/yourfile - transcript.txt
```

---

# 🧠 7. How It Works (Simplified Pipeline)

```
Audio (.mp3 / .wav / etc.)
      ↓
Faster-Whisper model (medium)
      ↓
Segment detection (start/end)
      ↓
Language detection
      ↓
Output:
    → SRT with timestamps
    → Plain text transcript
```

---

# 💬 8. License

Whisper & Faster-Whisper follow MIT License.
Model weights follow the HuggingFace license terms.
