# PolicyPal AI

PolicyPal AI is a contract analysis system that helps users understand legal documents by extracting important clauses, assessing potential risks, and answering questions about the uploaded contract.
---
## Features

- Upload PDF contracts
- Automatic text extraction and preprocessing
- Intelligent document chunking
- Semantic search using vector embeddings
- Contract clause extraction
- Risk assessment
- Executive summary generation
- Question Answering over uploaded contracts
- Interactive Streamlit interface

---

## Tech Stack
- Python
- Streamlit
- ChromaDB
- Sentence Transformers
- PyMuPDF
- NumPy
---

## Installation

Clone the repository.

```bash
git clone https://github.com/Abha1604/PolicyPal-AI.git
cd PolicyPal-AI
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

---

## Configure OpenRouter

Create an API key at [OpenRouter](https://openrouter.ai/keys). For local
development, create `.streamlit/secrets.toml` and add:

```toml
OPENROUTER_API_KEY = "your-openrouter-api-key"
```

In Streamlit Community Cloud, add the same TOML entry under **App settings →
Secrets**. Do not commit the secrets file or put the key in application code.
The app uses OpenRouter's `openrouter/free` model router, which may have
request limits and may select different free models over time.

---

## Running the Application

Start the Streamlit application.

```bash
streamlit run app.py
```

---

## Workflow

```
Upload PDF
      ↓
Extract Text
      ↓
Clean Text
      ↓
Create Chunks
      ↓
Generate Embeddings
      ↓
Store in ChromaDB
      ↓
Retrieve Relevant Chunks
      ↓
Risk Analysis & Question Answering
```

---

## Team

- Abha
- Devika
- Anuja
- Anshu
- Dimpal

---

## License

This project was developed as part of an academic capstone project.