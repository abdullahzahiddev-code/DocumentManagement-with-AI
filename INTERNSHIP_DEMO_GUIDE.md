# 🎓 Internship Project Defense & Viva Guide
## Project: DocuVault AI — Document Management System with AI Search

---

### 1. 🚀 How to Run the Project (Aik Click Mein Chalaane Ka Tareeqa)

Aap ke paas **2 aasaan tareeqay** hain:

#### Tareeqa 1: Direct Double Click (Sab Se Aasaan)
1. Project folder kholen: `DocumentManagement_with AI`
2. **`run.bat`** file par double-click karein.
   - Yeh automatically background server start karega aur browser mein `http://127.0.0.1:8000` open kar dega!

#### Tareeqa 2: Terminal / PowerShell
PowerShell ya Command Prompt kholen aur likhein:
```powershell
cd "c:\Users\DELL\OneDrive\Documents\DocumentManagement_with AI"
python app.py
```
Phir browser mein jayein:
👉 **`http://127.0.0.1:8000`**

#### Tareeqa 3: Offline Direct Browser Open (Zero Server / No Setup Needed)
Agar kisi evaluator ke laptop par Python na ho ya internet na ho:
- Seedha **`index.html`** file par double click kar ke Chrome ya Edge mein open kar lein!
- Frontend mein smart client-side storage aur mock AI engine built-in hai, project 100% smooth chalay ga!

---

### 2. 🌟 Project Features Overview (Evaluator Ko Kya Dikhana Hai)

1. **Enterprise Dashboard**:
   - Total Documents, AI Summaries Generated, OCR Pipeline status, aur Active Users count.
   - Category wise visual bar chart (Technical, Finance, Legal, HR, Marketing).
   - Recent uploads list with 1-click preview.

2. **Document Library (Repository)**:
   - **Grid View** aur **Table View** switcher.
   - Filters: Filter by Category, File Type (PDF, DOCX, TXT, PNG/JPG OCR), and Sorting.
   - Professional file badges (PDF = Red, DOCX = Blue, TXT = Gray, Image = Amber).

3. **AI Semantic Full-Text Search**:
   - Deep search bar across Title, Description, Extracted Text, and AI Summaries.
   - Keyword highlight snippet (`<mark>` tag ke sath query match show hoti hai).
   - Real-time match count.

4. **Document Details & AI Summarizer**:
   - Click any document to open detail modal.
   - **AI Executive Summary**: 2-3 concise summary sentences.
   - **Key Points**: Bulleted takeaways.
   - **AI Auto-Tags**: Generated keywords.
   - **Extracted Text / OCR viewer**: Complete extracted text stream with 1-click "Copy Text" button.
   - **Regenerate Summary** button and **Download** button.

5. **Document Ingestion (Upload Modal)**:
   - Drag & drop zone with file picker.
   - Title, Description, Category, Access Level (Public, Department, Private), and Tag inputs.
   - Automatic text extraction and auto-summary generation on upload.

6. **Role-Based Access Control (RBAC)**:
   - User Management view showing Admin, Manager, and Employee tiers with distinct permissions.

---

### 3. 🎯 Viva Questions & Answers (Examiner / Teacher Ke Sawalaat)

#### Q1: What is the architecture of this project?
**Answer:**
> "Sir/Ma'am, the project follows a modern decoupled architecture. The frontend is built using standard HTML5, CSS3 with a responsive modern SaaS design, and Vanilla JavaScript utilizing the Fetch API. The backend is implemented as a lightweight, single-file RESTful API server (`app.py`) backed by an SQLite relational database (`dms_database.db`). It provides full CRUD operations, full-text search indexing, text extraction, and an AI summarization pipeline."

#### Q2: How does the AI search work?
**Answer:**
> "The search engine indexes document titles, descriptions, raw extracted text, and AI-generated summaries into the database. When a user enters a query, the system performs a multi-field full-text query with pattern matching and contextual snippet extraction, highlighting matched terms in real-time."

#### Q3: How do you extract text from PDFs, DOCX, and scanned images?
**Answer:**
> "We support multiple formats:
> 1. **PDF**: Extracted using PyMuPDF (`fitz`) or binary text stream parsing.
> 2. **DOCX**: Extracted using `python-docx` or direct XML parsing of the document stream.
> 3. **Images & Scanned Documents**: Extracted via the Tesseract OCR engine with image preprocessing via Pillow.
> 4. **Plain Text**: Direct UTF-8 ingestion."

#### Q4: How does AI Summarization work if the external API key is missing?
**Answer:**
> "Our architecture implements graceful fallback. If an OpenAI or Gemini API key is configured, it calls the LLM endpoint for generative summaries. If the API key is not present or offline, our heuristic NLP engine extracts the most salient sentences, creates structured bullet points, and extracts top frequency domain keywords as suggested tags. This ensures the demo never crashes during an evaluation."

#### Q5: How is security and Role-Based Access Control (RBAC) handled?
**Answer:**
> "We define 3 hierarchical roles: Admin (full CRUD and user management), Manager (departmental access and document review), and Employee (standard upload and view permissions). Documents also enforce access levels: Public, Department, and Private."
