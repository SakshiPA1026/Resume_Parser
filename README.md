# Resume Parser

![License](https://img.shields.io/badge/license-MIT-blue.svg)

A robust web application for parsing resumes, extracting relevant information with NLP, and storing results securely in a cloud database. Built with Python, Flask, and Firebase, this app supports PDF/DOCX uploads, AI-powered parsing, and secure credential management.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture & Workflow](#architecture--workflow)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [How to Use](#how-to-use)
- [API Endpoints](#api-endpoints)
- [Dependencies](#dependencies)
- [Terminal Commands](#terminal-commands)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

Resume Parser is a web application designed to automate the extraction of structured information from resumes. It leverages advanced NLP models (Gemini/OpenAI via LangChain) to parse resumes, extract candidate details, and store them in a secure Firestore database. The app is ideal for recruiters, HR teams, and developers building HR tech solutions.

**Key Technologies:**
- Python 3.x
- Flask (web framework)
- LangChain & Gemini/OpenAI (NLP)
- Firebase Firestore (database)
- Docker-ready (optional)

---


## Features
- **Resume Upload:** Supports PDF and DOCX file uploads via a web interface.
- **Automated Parsing:** Uses AI/NLP to extract:
  - Name, Email, Phone
  - Skills
  - Education (degree, institution, year, marks/CGPA)
  - Work Experience (title, company, dates, description)
- **Data Storage:** Saves parsed results in Google Firebase Firestore (NoSQL, cloud-based).
- **Resume Download:** Generate and download resumes in PDF or DOCX formats after parsing/editing.
- **Web Dashboard:** View, search, and manage all parsed resumes.
- **Security:** Credentials and uploads are handled securely; sensitive files are gitignored.
- **API Ready:** Core functionality is accessible via HTTP endpoints for integration.

---


## Architecture & Workflow

1. **User uploads a resume** (PDF/DOCX) via the web UI.
2. **File is saved** to the `uploads/` directory (not committed to git).
3. **Text is extracted** using PDF/DOCX parsers (`fitz`, `python-docx`).
4. **NLP model (Gemini/OpenAI via LangChain)** processes the text and extracts structured fields.
5. **User reviews/edits** the parsed data in a web form.
6. **Data is stored** in Firebase Firestore via the `database.py` module.
7. **Resumes can be viewed, edited, deleted, or downloaded** as PDF/DOCX from the dashboard.

---

## Project Structure

```
Resume_Parser/
├── app.py                  # Main Flask app (routes, upload, parse, dashboard)
├── database.py             # Firestore DB logic (insert, fetch, delete resumes)
├── resume_parser.py        # NLP parsing logic (PDF/DOCX extraction, AI parsing)
├── requirements.txt        # Python dependencies
├── static/                 # JS/CSS static files (for frontend)
├── templates/              # HTML templates (Jinja2 for Flask)
├── uploads/                # Uploaded resumes (excluded from git)
├── .env                    # Environment variables (excluded from git)
├── resume-parser-*.json    # Firebase Admin SDK key (excluded from git)
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
```

**Key Files:**
- `app.py`: Flask app, routes for upload, parse, view, download, delete.
- `resume_parser.py`: Functions for text extraction and AI-powered parsing.
- `database.py`: Handles Firestore integration and CRUD operations.
- `requirements.txt`: All Python dependencies (see [Dependencies](#dependencies)).
- `static/` and `templates/`: Frontend assets and HTML pages.

---


## Setup Instructions

### 1. Clone the repository
```sh
git clone https://github.com/your-username/Resume_Parser.git
cd Resume_Parser
```

### 2. Create and activate a virtual environment
```sh
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_or_openai_api_key_here
FLASK_ENV=development
# Add FIREBASE_CREDENTIALS_JSON if deploying to Render
```

### 5. Add your Firebase Admin SDK key
- Download your Firebase service account key JSON from the Firebase console.
- Place it in the project root (e.g., `resume-parser-xxxx-firebase-adminsdk-xxxx.json`).
- This file is already in `.gitignore` for security.

### 6. Run the Flask app
```sh
python app.py
```

### 7. Open the web app
Visit [http://localhost:5000](http://localhost:5000) in your browser.

**Troubleshooting:**
- Ensure Python 3.8+ is installed.
- If you get credential errors, verify your `.env` and Firebase key file.
- For cloud deployment (e.g., Render), set environment variables in the dashboard and use `FIREBASE_CREDENTIALS_JSON` as a string.

---


3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up your `.env` file:**
   Create a `.env` file in the root directory with the following content:
   ```env
   GEMINI_API_KEY=your_gemini_or_openai_api_key_here
   FLASK_ENV=development
   # Add other environment variables as needed
   ```

5. **Add your Firebase Admin SDK key:**
   - Download your Firebase service account key JSON.
   - Place it in the project root (e.g., `resume-parser-xxxx-firebase-adminsdk-xxxx.json`).
   - This file is already in `.gitignore` for security.

---

## Environment Variables

| Variable                | Description                                      |
|-------------------------|--------------------------------------------------|
| `GEMINI_API_KEY`        | Gemini or OpenAI API key for NLP/AI parsing      |
| `FLASK_ENV`             | Flask environment (`development` or `production`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Firebase Admin SDK JSON (local dev) |
| `FIREBASE_CREDENTIALS_JSON` | JSON string for Firebase key (cloud deploy)      |

**Never commit your `.env` or credentials JSON to GitHub!**

---


## How to Use

1. **Start the Flask app:**
   ```sh
   python app.py
   ```
2. **Open your browser:** Go to [http://localhost:5000](http://localhost:5000)
3. **Upload a resume:** Use the upload form to select a PDF or DOCX file.
4. **Review and edit:** Parsed fields are displayed in a form. Edit if needed.
5. **Save:** Submit the form to save the parsed data to Firestore.
6. **View/manage resumes:** Use the dashboard to view, download, or delete resumes.

### Example Workflow
- Upload: `resume.pdf`
- Extracted: Name, Email, Skills, Education, Work Experience
- Edit: Correct any parsing errors
- Save: Data stored in Firestore
- Download: Generate PDF/DOCX from parsed data

---


## API Endpoints

| Endpoint                  | Method | Description                                      |
|---------------------------|--------|--------------------------------------------------|
| `/`                       | GET    | Main upload page                                 |
| `/parse`                  | POST   | Upload and parse a resume file                   |
| `/submit_form`            | POST   | Save edited/parsed resume data                   |
| `/resumes`                | GET    | View all parsed resumes (dashboard)              |
| `/resume/<resume_id>`     | GET    | View details of a single resume                  |
| `/resume/<resume_id>/download/<file_type>` | GET | Download resume as PDF or DOCX                   |
| `/resume/<resume_id>/delete` | POST | Delete a resume                                  |

All endpoints return HTML pages or JSON responses as appropriate.

---

## Dependencies

Key dependencies (see `requirements.txt` for full list):
- `Flask`: Web framework
- `firebase-admin`: Firebase Admin SDK for Python
- `google-cloud-firestore`: Firestore database
- `langchain`, `langchain-google-genai`: NLP/AI parsing
- `python-dotenv`: Loads environment variables
- `fitz` (PyMuPDF): PDF text extraction
- `python-docx`: DOCX file parsing and generation
- `reportlab`: PDF generation

Install all dependencies with:
```sh
pip install -r requirements.txt
```

---


## Terminal Commands

- **Initialize git:**
  ```sh
  git init
  ```
- **Add all files except those in `.gitignore`:**
  ```sh
  git add .
  ```
- **Commit changes:**
  ```sh
  git commit -m "Initial commit"
  ```
- **Add GitHub remote:**
  ```sh
  git remote add origin https://github.com/your-username/Resume_Parser.git
  ```
- **Push to GitHub:**
  ```sh
  git branch -M main
  git push -u origin main
  ```

---

## Security Notes

- `.env` and Firebase Admin SDK JSON are in `.gitignore` and must never be committed.
- If secrets are accidentally pushed, remove them from git history and rotate your keys immediately.
- Use environment variables for all credentials in production.
- For more, see [GitHub’s secret scanning documentation](https://docs.github.com/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/working-with-push-protection-from-the-command-line#resolving-a-blocked-push).

---


## Contributing

Contributions are welcome! To contribute:
1. Fork this repository and clone your fork.
2. Create a new branch for your feature or fix.
3. Make your changes and test thoroughly.
4. Ensure code style and security best practices are followed.
5. Submit a pull request with a clear description of your changes.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Contact

For issues, suggestions, or support:
- Open an issue on GitHub
- Contact the maintainer at [your-email@example.com]
MIT License