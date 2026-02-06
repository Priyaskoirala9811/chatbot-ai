# Research Coach (Web Chatbot)

A Python (Flask) web chatbot that helps plan academic research:
- topic → research question starters
- keyword packs + Boolean search strings
- word-count-aware outline
- claim checker for overly absolute language
- TF-IDF retrieval over a research-skills knowledge base (advanced NLP)
- optional explain mode showing similarity + keywords

## Run (macOS / Linux)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
