# 📝 Workshop Summary CLI Tool

This CLI tool extracts, analyzes, and summarizes `.mp4` video recordings of workshop sessions.

It performs the following:
- 🎙️ Converts speech to text using OpenAI Whisper
- 🧑‍💼 Extracts speaker names from MS Teams UI via OCR
- 🧠 Segments discussions into topics and generates summaries
- ✅ Extracts action items and schedules tasks for "Tomorrow" or "Next Week"
- 📄 Outputs a clean PDF summary report

---

## 📦 Requirements

Make sure you have:
- Python 3.8+
- `ffmpeg` installed and in your system PATH
- Tesseract OCR installed:
  - Windows: [Download here](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt install tesseract-ocr`

Install Python dependencies:

```bash
pip install -r requirements.txt
