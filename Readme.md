# 🚢 TitanicAI Chat Agent

A conversational AI chatbot for analyzing the Titanic dataset, built with **FastAPI**, **LangChain**, **Groq (LLaMA-3.3-70B)**, and **Streamlit**.

**Developer:** [Girish Shirsat](https://exploregms.wordpress.com/)  
**GitHub:** [github.com/girishshirsat](https://github.com/girishshirsat)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python |
| AI Inference | Groq API — `llama-3.3-70b-versatile` |
| Memory | LangChain `InMemoryChatMessageHistory` |
| Frontend | Streamlit |
| Data | Pandas + NumPy |
| Charts | Matplotlib + Seaborn |

> **Why Groq?** HuggingFace's free Inference API no longer supports open models reliably. Groq provides a completely free API with ultra-fast inference (sub-second responses) and access to top-tier models like LLaMA-3.3-70B — which is significantly smarter than Mistral-7B.

---

## Setup

### 1. Clone & install dependencies
```bash
git clone https://github.com/girishshirsat/titanic-chatbot
cd titanic-chatbot
pip install -r requirements.txt
```

### 2. Get a free Groq API key
1. Go to **https://console.groq.com**
2. Sign up → click **API Keys** → **Create API Key**
3. Copy the key (starts with `gsk_...`)

### 3. Create a `.env` file
```
GROQ_API_KEY=gsk_your_key_here
```

### 4. Place the dataset
Make sure `Titanic-Dataset.csv` is in the same directory as `main.py`.

### 5. Start the FastAPI backend
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Start the Streamlit frontend (new terminal)
```bash
streamlit run client.py
```

Open **http://localhost:8501** in your browser 🚀

---

## Project Structure

```
chatbot/
├── main.py               ← FastAPI backend + Groq AI agent
├── client.py             ← Streamlit frontend
├── Titanic-Dataset.csv   ← Dataset
├── requirements.txt      ← Dependencies
├── .env                  ← Your Groq API key (don't commit this)
└── README.md
```

---

## Key Features

### Dynamic Context Injection
Instead of a fixed static prompt, the backend detects what the question is about and injects the exact relevant data from pandas into the LLM prompt:
- Asked for names → actual filtered name list injected
- Asked for age group (e.g. 10-20) → matching passenger rows injected
- Asked for survival stats → full breakdown table injected

### Session Memory
Each chat session maintains full conversation history via LangChain `InMemoryChatMessageHistory`. The LLM can accurately recall previous questions within the session. When the user navigates back to the home page and starts a new chat, the old session is cleared from the backend automatically.

### Dynamic Visualizations
The LLM can trigger chart generation by including a structured `<chart>` JSON tag in its response. Supported chart types: `histogram`, `bar`, `pie`, `scatter`, `box` — all rendered in a dark navy/cyan theme matching the UI.

### Example Questions
- "What percentage of passengers were male?"
- "List the names of all male passengers in a table"
- "Show me a histogram of passenger ages"
- "How many males were in the age group 10-20?"
- "What was the survival rate by passenger class?"
- "Show me a pie chart of embarkation ports"
- "What was my first question?" ← memory recall

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send a message, get AI response + optional chart |
| DELETE | `/session/{id}` | Clear a session's memory |
| GET | `/health` | Health check |
| GET | `/dataset/summary` | Basic dataset statistics |