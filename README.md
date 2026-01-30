# RAG Quiz App

A intelligent quiz generator powered by **Retrieval-Augmented Generation (RAG)** that creates context-aware quiz questions from PDF documents and YouTube videos. Built with LangChain, OpenAI, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-1.2.7+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.53.1+-red.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)

## 🎯 Features

- **Multi-Source Support**: Generate quizzes from PDF documents and YouTube videos
- **AI-Powered Question Generation**: Uses OpenAI GPT models to create contextually relevant questions
- **Vector Database**: FAISS-based vector store for efficient semantic search
- **Configurable Difficulty**: Adjust number of questions (1-10) with dynamic difficulty levels
- **Score Tracking**: Save and retrieve quiz scores in PostgreSQL database
- **Web Interface**: Interactive Streamlit UI for seamless user experience
- **Docker Support**: Easy deployment with Docker Compose
- **RAG Pipeline**: Chunked document processing with embeddings for accurate retrieval

## 🏗️ Architecture

### Tech Stack

- **Frontend**: Streamlit (Python UI framework)
- **LLM**: OpenAI GPT models (ChatGPT)
- **Vector Store**: FAISS (Meta's vector database)
- **Embeddings**: OpenAI Embeddings API
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Document Processing**: LangChain with PDF and YouTube loaders
- **Text Splitting**: Recursive character-based chunking
- **Package Manager**: UV (fast Python package installer)
- **Containerization**: Docker & Docker Compose

### Project Structure

```
rag-quiz-app/
├── app.py                 # Main Streamlit application
├── main.py               # Alternative entry point
├── init_db.py            # Database initialization script
├── backend/
│   ├── __init__.py
│   ├── rag.py            # RAG pipeline (document processing & quiz generation)
│   └── database.py       # Database operations & score management
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Multi-container orchestration
├── pyproject.toml        # Project dependencies & metadata
├── .env                  # Environment variables (not tracked)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- PostgreSQL (or Docker)
- Git

### Option 1: Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rag-quiz-app.git
cd rag-quiz-app
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
```

3. **Install dependencies**
```bash
uv pip install -r requirements.txt
# or
pip install -e .
```

4. **Configure environment**
Create `.env` file:
```env
OPENAI_API_KEY=sk-your-api-key-here
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASS=securepassword123
DB_NAME=quiz_db
```

5. **Start PostgreSQL**
```bash
# Using Docker
docker run --name rag_quiz_db -e POSTGRES_PASSWORD=securepassword123 \
  -e POSTGRES_USER=admin -e POSTGRES_DB=quiz_db -p 5432:5432 postgres:latest
```

6. **Initialize database**
```bash
python init_db.py
```

7. **Run the app**
```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

### Option 2: Docker Deployment (Recommended)

1. **Clone and navigate**
```bash
git clone https://github.com/yourusername/rag-quiz-app.git
cd rag-quiz-app
```

2. **Configure environment**
Create `.env` file with your OpenAI API key (see above)

3. **Build and run**
```bash
docker-compose up --build
```

The app will be available at `http://localhost:8501`

## 📖 Usage

### 1. Upload Source Material

- **PDF Mode**: Upload any PDF document (textbooks, research papers, etc.)
- **YouTube Mode**: Paste a YouTube URL to extract transcript

### 2. Configure Quiz Parameters

- **Number of Questions**: Select 1-10 questions using the slider
- **API Key**: Provide OpenAI API key (in sidebar) if not set via environment

### 3. Generate Quiz

Click "Generate Quiz" to create AI-powered questions based on your source material.

### 4. Answer Questions

Complete the quiz and submit your answers to receive:
- Instant feedback on correctness
- Your score saved to the database
- Score history tracking

## 🔧 API Documentation

### `backend/rag.py`

#### `process_resource(file_path=None, youtube_url=None, api_key=None)`

Processes a PDF or YouTube source and returns a FAISS vector store.

**Parameters:**
- `file_path` (str): Path to PDF file
- `youtube_url` (str): YouTube video URL
- `api_key` (str): OpenAI API key

**Returns:**
- `FAISS`: Vector store containing embeddings and documents

**Example:**
```python
from backend.rag import process_resource

vectorstore = process_resource(
    file_path="document.pdf",
    api_key="sk-..."
)
```

#### `generate_quiz(vectorstore, num_questions=5, api_key=None)`

Generates quiz questions from the vector store using RAG.

**Parameters:**
- `vectorstore` (FAISS): Vector store from `process_resource()`
- `num_questions` (int): Number of questions to generate (1-10)
- `api_key` (str): OpenAI API key

**Returns:**
- `dict`: Quiz data with questions, options, and correct answers

**Example:**
```python
from backend.rag import generate_quiz

quiz = generate_quiz(
    vectorstore=vectorstore,
    num_questions=5,
    api_key="sk-..."
)
```

### `backend/database.py`

#### `save_score(score, total, source, num_questions, api_key=None)`

Saves quiz results to PostgreSQL database.

**Parameters:**
- `score` (int): Number of correct answers
- `total` (int): Total number of questions
- `source` (str): Document source name
- `num_questions` (int): Number of questions attempted
- `api_key` (str): OpenAI API key used

**Returns:**
- `bool`: True if successful

## 🗄️ Database Schema

### `quiz_scores` Table

```sql
CREATE TABLE quiz_scores (
    id SERIAL PRIMARY KEY,
    score INT NOT NULL,
    total INT NOT NULL,
    percentage FLOAT,
    source VARCHAR(255),
    num_questions INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 How RAG Works in This App

1. **Document Ingestion**: PDF or YouTube content is loaded
2. **Chunking**: Text is split into 2000-char chunks with 200-char overlap
3. **Embedding**: Chunks are converted to vector embeddings via OpenAI API
4. **Indexing**: Embeddings stored in FAISS for fast retrieval
5. **Retrieval**: Query finds top 4 most relevant chunks
6. **Augmentation**: Retrieved context is injected into prompt
7. **Generation**: LLM creates quiz questions grounded in source material

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'langchain.prompts'`
This occurs with mismatched LangChain versions. Ensure you're using:
```
langchain>=1.2.7
langchain-core>=0.1.0
langchain-community>=0.4.1
```

**Solution**: 
```bash
uv lock  # Update lock file
docker-compose build --no-cache  # Rebuild container
```

### `Connection error [Errno 11001] getaddrinfo failed`
OpenAI API is unreachable. Check:
- Internet connectivity
- API key validity at https://platform.openai.com
- Firewall/proxy settings
- API rate limits

### `Can't create a connection to host localhost and port 5432`
PostgreSQL not running.

**Solution**:
```bash
# Using Docker
docker run --name rag_quiz_db -e POSTGRES_PASSWORD=securepassword123 \
  -e POSTGRES_USER=admin -e POSTGRES_DB=quiz_db -p 5432:5432 postgres:latest

# Or use docker-compose
docker-compose up
```

## 📦 Dependencies

- **LangChain Stack**: LLM orchestration and RAG pipeline
- **OpenAI**: GPT models and embeddings API
- **Streamlit**: Web UI framework
- **FAISS**: Vector database for similarity search
- **SQLAlchemy**: Database ORM
- **pg8000**: PostgreSQL driver
- **PyPDF**: PDF document parsing
- **YouTube Transcript API**: YouTube content extraction

See `pyproject.toml` for complete dependency list.

## 🔐 Security Notes

- **API Keys**: Never commit `.env` files - use `.gitignore`
- **Database Credentials**: Rotate credentials in production
- **HTTPS**: Deploy with HTTPS in production environments
- **Rate Limiting**: Implement rate limiting for API endpoints

## 📝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙌 Acknowledgments

- [LangChain](https://langchain.com/) - RAG framework
- [Streamlit](https://streamlit.io/) - Web UI framework
- [OpenAI](https://openai.com/) - LLM and embeddings
- [Meta FAISS](https://faiss.ai/) - Vector search library

## 📧 Support

For issues, questions, or suggestions:
- Open an GitHub Issue
- Check existing issues for solutions
- Review troubleshooting section above

---

**Made using LangChain & OpenAI**