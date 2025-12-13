# 📄 AI Document Explainer

> **Helping international students, immigrants, and expats understand official documents in any language**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run-4285F4.svg)](https://cloud.google.com/run)

**🚀 Live Demo**: [https://ai-doc-explainer-49617484596.europe-west3.run.app/](https://ai-doc-explainer-49617484596.europe-west3.run.app/)

**💾 Cloud Storage**: Powered by [Cloudflare R2](https://www.cloudflare.com/products/r2/) - Privacy-first, encrypted document storage with zero egress fees

---

## 🌍 Why This Exists

Moving to a new country is hard. Understanding official documents in a foreign language is even harder.

Whether you're an **international student** dealing with university paperwork, an **immigrant** navigating visa documents, or an **expat** trying to understand your rental contract — this tool is for you.

**AI Document Explainer** uses GPT-4 to:

- 📖 Extract and translate complex legal documents
- ✅ Identify deadlines, obligations, and risks
- 💬 Answer your follow-up questions in plain language
- 🔒 Keep your documents private and secure

---

## 🎯 Who Is This For?

### 🎓 International Students

- University admission letters
- Scholarship agreements
- Housing contracts
- Visa documentation
- Health insurance policies

### 🌏 Immigrants & Expats

- Residence permits
- Work contracts
- Tax documents
- Rental agreements
- Government notices

### 💼 Freelancers & Contractors

- Client contracts
- Invoice requirements
- Legal notices
- Insurance documents

---

## ✨ Features

### 🤖 AI-Powered Analysis

- **Smart Extraction**: Handles PDFs and images (even scanned documents)
- **Multi-Language OCR**: English + German support (more languages coming)
- **Structured Insights**:
  - Clear summary in plain language
  - Important points highlighted
  - Deadlines with dates
  - Your obligations listed
  - Potential risks identified
  - Recommended next steps

### 💬 Interactive Chat

- Ask follow-up questions about your document
- Get clarification on confusing terms
- Understand implications in context

### ☁️ Optional Cloud Storage

- **Privacy-First**: Disabled by default
- **Encrypted**: AES-256 encryption at rest
- **User-Controlled**: You decide what to store
- **Cloudflare R2**: No egress fees, GDPR-friendly

### 🔒 Privacy & Security

- **No Persistent Storage**: Documents deleted after analysis (unless you opt-in)
- **Rate Limiting**: 10 analyses per 24 hours to prevent abuse
- **Local Processing**: OCR happens on your device
- **Clear Disclaimers**: Not legal advice, just helpful insights

### 🚀 Production-Ready

- **Fully Containerized**: Docker + Docker Compose
- **Auto-Scaling**: Deploy to Google Cloud Run
- **Database Support**: SQLite (default) or PostgreSQL
- **Monitoring**: Built-in health checks

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-document-reader.git
cd ai-document-reader

# Create environment file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run with Docker
docker build -t ai-doc-explainer .
docker run -d -p 8501:8501 --env-file .env ai-doc-explainer

# Open in browser
open http://localhost:8501
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# macOS:
brew install tesseract tesseract-lang

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-deu

# Set environment variable
export OPENAI_API_KEY="your_key_here"

# Run the app
streamlit run app.py
```

---

## 🌐 Deploy to Production

### Google Cloud Run (Easiest)

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Deploy
gcloud run deploy ai-doc-explainer \
  --source . \
  --region europe-west3 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="your_key"
```

**See full deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📋 Environment Variables

| Variable                | Required | Description                  | Default                    |
| ----------------------- | -------- | ---------------------------- | -------------------------- |
| `OPENAI_API_KEY`        | ✅ Yes   | Your OpenAI API key          | -                          |
| `DATABASE_URL`          | ❌ No    | PostgreSQL connection string | `sqlite:///./documents.db` |
| `ENABLE_OBJECT_STORAGE` | ❌ No    | Enable Cloudflare R2 storage | `false`                    |
| `R2_ACCOUNT_ID`         | ❌ No    | Cloudflare R2 account ID     | -                          |
| `R2_ACCESS_KEY_ID`      | ❌ No    | R2 access key                | -                          |
| `R2_SECRET_ACCESS_KEY`  | ❌ No    | R2 secret key                | -                          |
| `R2_BUCKET_NAME`        | ❌ No    | R2 bucket name               | `ai-documents`             |

---

## 💰 Cost Transparency

### OpenAI API Costs

- **Model**: GPT-4o-mini
- **Cost per document**: ~$0.01 - $0.05
- **Estimated monthly** (100 docs): $10-20

### Cloud Storage (Optional)

- **Cloudflare R2 Free Tier**: 10GB storage, 1M writes/month
- **No egress fees**
- **Estimated**: Free for most users

### Hosting

- **Google Cloud Run Free Tier**: 2M requests/month
- **After free tier**: ~$5-20/month

**Total for moderate use**: $10-30/month

---

## 🛡️ Legal Disclaimer

> **IMPORTANT**: This tool provides AI-generated summaries and insights for informational purposes only. It is **NOT legal advice** and should not be relied upon as such.
>
> - Always consult a qualified legal professional for important decisions
> - Verify all information with official sources
> - The AI may make mistakes or miss important details
> - You are responsible for your own decisions

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs**: Open an issue with details
2. **Suggest features**: Share your ideas
3. **Add languages**: Help with OCR language support
4. **Improve docs**: Better documentation helps everyone

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:

- [Streamlit](https://streamlit.io/) - Web framework
- [OpenAI GPT-4](https://openai.com/) - AI analysis
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Text extraction
- [Cloudflare R2](https://www.cloudflare.com/products/r2/) - Cloud storage
- [Docker](https://www.docker.com/) - Containerization

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/ai-document-reader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/ai-document-reader/discussions)

---

## 🌟 Star This Project

If this tool helped you understand an important document, please consider giving it a star ⭐

It helps others discover this tool and motivates continued development!

---

<p align="center">
  Made with ❤️ for international students, immigrants, and expats worldwide
</p>
