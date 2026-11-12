# DocuVault AI — Document Management System with AI Search

A modern, complete, and functional Document Management System with AI-powered search, text extraction, OCR, and automated document summarization. Built for university evaluations, software engineering internships, and live demonstrations.

---

## ⚡ Quick Start

### Option 1: Double-Click Launcher
Double-click **`run.bat`** in the project root directory. It will start the server and open `http://127.0.0.1:8000` in your default browser.

### Option 2: Python Command Line
```powershell
# Navigate to the folder
cd "c:\Users\DELL\OneDrive\Documents\DocumentManagement_with AI"

# Start the unified single-file server
python app.py
```
Open **`http://127.0.0.1:8000`** in your browser.

### Option 3: Direct Browser Launch (No Server Needed)
Simply open **`index.html`** directly in Chrome or Edge. The UI includes a built-in client engine and pre-seeded documents that work offline.

---

## 📂 Project Structure

```
DocumentManagement_with AI/
│
├── app.py                     # Single-file complete REST API backend (Python + SQLite)
├── index.html                 # Unified, modern SaaS frontend UI (Responsive)
├── run.bat                    # One-click Windows starter script
├── dms_database.db            # SQLite database with seeded sample documents
├── INTERNSHIP_DEMO_GUIDE.md   # Viva & evaluation presentation defense guide
├── media/documents/           # Uploaded files storage directory
└── templates/ & static/       # Multi-template Django assets (if running via Django)
```

---

## 🚀 Key Features

1. **Dashboard & Analytics**:
   - Total document counts, AI summaries generated, active user metrics.
   - Interactive bar chart showing category distribution (Technical, Finance, Legal, HR, Marketing).
   - Recent uploads activity feed.

2. **Document Repository & Library**:
   - Grid View & Table View modes.
   - Filtering by Category, File Type (PDF, DOCX, TXT, PNG/JPG), and Sorting.
   - Status indicators (`Completed`, `Pending`, `Processing`).

3. **AI Search Engine**:
   - Full-text search across titles, descriptions, extracted text, and summaries.
   - Live snippet extraction with highlighted matching search terms.

4. **Document Details & AI Summarizer**:
   - AI Executive Summary with key bullet takeaways.
   - Auto-generated domain tags.
   - Extracted text / OCR viewer with 1-click clipboard copy.
   - Instant file download.

5. **Upload & Ingestion Pipeline**:
   - Drag-and-drop file upload with progress bar.
   - Automatic format detection, text extraction, and automated summary creation.

6. **Role-Based Access Control (RBAC)**:
   - Admin, Manager, and Employee tiers with documented permission scopes.
