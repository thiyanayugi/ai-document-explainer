# AI Document Explainer 📄

A production-ready web application that helps users understand official documents by extracting text and providing AI-powered analysis with clear explanations, deadlines, obligations, risks, and actionable next steps.

## 🎯 Features

- **Multi-format Support**: Upload PDFs, PNG, JPG, JPEG, or TIFF files
- **Smart Text Extraction**:
  - PyMuPDF for PDF text extraction
  - Automatic OCR fallback for scanned documents using Tesseract
  - Support for English and German languages
- **AI-Powered Analysis**: OpenAI GPT-4 analyzes documents and provides:
  - Clear summary in simple English
  - Important points and key information
  - Deadlines and time-sensitive items
  - Your obligations and responsibilities
  - Potential risks and consequences
  - Recommended next steps
  - Actionable checklist
- **Database Persistence**: Store analysis history (SQLite by default, PostgreSQL/Supabase ready)
- **Privacy-Focused**:
  - No raw document logging
  - Clear privacy disclaimers
  - Delete history feature
- **Production-Ready**: Fully containerized with Docker

## 🚀 Quick Start

### Prerequisites

- Docker (recommended) OR
- Python 3.11+ with pip
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Option 1: Run with Docker (Recommended)

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd ai_document_reader
   ```

2. **Build the Docker image**:

   ```bash
   docker build -t ai-doc-explainer .
   ```

3. **Run the container**:

   ```bash
   docker run -e OPENAI_API_KEY=your_api_key_here -p 8501:8501 ai-doc-explainer
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

### Option 2: Run Locally

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd ai_document_reader
   ```

2. **Install system dependencies** (Ubuntu/Debian):

   ```bash
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu poppler-utils
   ```

3. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

6. **Run the application**:

   ```bash
   streamlit run app.py
   ```

7. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Database Configuration
DATABASE_URL=sqlite:///./documents.db  # Default SQLite

# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# For Supabase:
# DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres
```

### File Upload Limits

- **Maximum file size**: 20 MB
- **Supported formats**: PDF, PNG, JPG, JPEG, TIFF

## 🏗️ Architecture

### Technology Stack

- **Frontend & Backend**: Streamlit
- **Language**: Python 3.11+
- **LLM**: OpenAI GPT-4o-mini
- **PDF Processing**: PyMuPDF (fitz)
- **OCR**: Tesseract OCR
- **Database**: SQLAlchemy ORM (SQLite/PostgreSQL)
- **Containerization**: Docker

### Project Structure

```
ai_document_reader/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env.example          # Environment variable template
├── .gitignore           # Git ignore patterns
├── README.md            # This file
└── database/
    ├── __init__.py
    └── models.py        # SQLAlchemy models
```

## 🔒 Privacy & Security

### What We Do

- ✅ Validate file types and sizes
- ✅ Use environment variables for API keys
- ✅ Store only AI-generated summaries (not raw documents)
- ✅ Provide clear privacy disclaimers
- ✅ Allow users to delete their history

### What We Don't Do

- ❌ Log raw document content
- ❌ Store uploaded files on disk
- ❌ Hardcode API keys or secrets
- ❌ Share data with third parties (except OpenAI for analysis)

### Important Notice

**Document text is sent to OpenAI's API for analysis.** While we don't log the raw content, it is processed by OpenAI according to their [privacy policy](https://openai.com/policies/privacy-policy). Do not upload documents containing highly sensitive personal information unless you accept this risk.

## 📊 Database

The application uses SQLAlchemy ORM for database operations, making it easy to switch between database backends.

### Default: SQLite

By default, the app uses SQLite with a local `documents.db` file. This is perfect for development and small deployments.

### PostgreSQL / Supabase

For production deployments, set the `DATABASE_URL` environment variable:

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Supabase
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres
```

## 🧪 Testing

### Test with Sample Documents

1. Upload a PDF document (e.g., rental contract, government letter)
2. Wait for text extraction and OCR (if needed)
3. Review the AI analysis
4. Check the action items and deadlines
5. View raw extracted text in the collapsible section

### Verify Docker Deployment

```bash
# Build
docker build -t ai-doc-explainer .

# Run
docker run -e OPENAI_API_KEY=your_key -p 8501:8501 ai-doc-explainer

# Test
curl http://localhost:8501/_stcore/health
```

## 🚧 Future Improvements

- [ ] Automatic language detection for OCR
- [ ] Download analysis as PDF report
- [ ] User authentication and multi-user support
- [ ] Token usage tracking and cost estimation
- [ ] Support for additional formats (DOCX, RTF)
- [ ] Batch document processing
- [ ] Document comparison feature
- [ ] Email notifications for deadlines
- [ ] Integration with calendar apps

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For questions or issues, please open an issue on the repository.

---

**Built with ❤️ using Streamlit and OpenAI**
