# Research Coach Chatbot

This project is a Python-based chatbot developed as part of a university
mini-project. The chatbot functions as an academic research assistant and
uses a conversational interface in English.

The application runs locally using Flask and a locally hosted large language
model. It is not designed to run directly on GitHub Pages.

---

## Requirements

- Python 3.10+
- pip
- Ollama (for local LLM inference)

---

## How to Run the Chatbot Locally

1. Clone the repository:
   git clone https://github.com/USERNAME/REPO_NAME.git
   cd REPO_NAME

2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Install Ollama separately and pull a model:
   https://ollama.com
   ollama pull llama3.1:8b

5. Run the application:
   python app.py

6. Open a browser and go to:
   http://127.0.0.1:5000

---

## Notes

This project uses a locally hosted language model for text generation.
As a result, it must be run locally and cannot be deployed on GitHub Pages.
