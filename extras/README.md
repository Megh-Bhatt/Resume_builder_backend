# AI Resume Generator

An intelligent resume generation system that uses LangGraph and LangChain to create tailored resumes based on existing resumes and job descriptions.

## Features

- 🤖 **Agentic Workflow**: Uses LangGraph for orchestrating multi-step AI operations
- 📄 **Smart Extraction**: Extracts user details from existing resumes
- 🎯 **Job-Tailored**: Generates relevant projects and skills based on job descriptions
- 📝 **LaTeX Generation**: Creates professional resumes using LaTeX templates
- 🔄 **Real-time Preview**: View and download generated resumes
- ⚡ **Modern UI**: Beautiful React interface with Tailwind CSS

## Architecture

### Backend (Python + FastAPI + LangGraph)

The backend implements an agentic workflow with the following nodes:

1. **Extract Resume Info**: Extracts name, email, phone, GitHub, LinkedIn, experiences, education, positions of responsibility, and certifications from existing resume
2. **Generate Projects**: Creates 3-4 relevant projects tailored to the job description
3. **Generate Skills**: Generates categorized technical skills aligned with job requirements
4. **Create Metadata**: Structures all information using the `create_resume_metadata` tool
5. **Generate LaTeX**: Replaces placeholders in LaTeX template with actual data
6. **Compile PDF**: Compiles LaTeX to PDF for download

### Frontend (React + Vite + Tailwind CSS)

- Clean, modern UI for uploading resumes and entering job descriptions
- Real-time generation status
- Preview and download options for generated resumes
- Detailed metadata display

## Prerequisites

### Backend Requirements
- Python 3.10+
- pdflatex (for LaTeX compilation)
- Anthropic API key

### Frontend Requirements
- Node.js 18+
- npm or yarn

## Installation

### 1. Install LaTeX

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install texlive-full
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
Download and install MiKTeX from https://miktex.org/download

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=your_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

Backend will run on `http://localhost:8000`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

## Usage

1. **Upload Resume**: Click the upload area and select your existing resume (PDF format)
2. **Enter Job Description**: Paste the job description in the text area
3. **Generate**: Click "Generate Tailored Resume" button
4. **Wait**: The AI will process your resume and generate tailored content (15-30 seconds)
5. **Preview/Download**: Once generated, you can preview the resume or download the PDF

## API Endpoints

### POST `/api/generate-resume`
Generates tailored resume from existing resume and job description.

**Request:**
- `resume_file`: PDF file (multipart/form-data)
- `job_description`: Text (form data)

**Response:**
```json
{
  "success": true,
  "metadata": { ... },
  "latex_code": "..."
}
```

### POST `/api/compile-latex`
Compiles LaTeX code to PDF.

**Request:**
- `latex_code`: LaTeX source code (form data)

**Response:**
```json
{
  "success": true,
  "pdf_base64": "..."
}
```

### GET `/health`
Health check endpoint.

## LangGraph Workflow

```
┌─────────────────┐
│  Extract Info   │
│  (from resume)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Generate Projects│
│  (AI-powered)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Skills │
│  (AI-powered)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Create Metadata  │
│  (tool call)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate LaTeX  │
│  (template)     │
└────────┬────────┘
         │
         ▼
       [END]
```

## Project Structure

```
ai-resume-generator/
├── backend/
│   ├── main.py              # FastAPI app with LangGraph workflow
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── main.jsx        # Entry point
│   │   └── index.css       # Tailwind styles
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── tailwind.config.js  # Tailwind configuration
│   └── index.html          # HTML template
└── README.md               # This file
```

## Customization

### LaTeX Template
The LaTeX template is embedded in `backend/main.py` in the `get_latex_template()` function. You can modify it to change the resume layout.

### Prompts
All AI prompts are in the node functions:
- `extract_resume_info()` - Resume extraction prompt
- `generate_projects()` - Project generation prompt
- `generate_skills()` - Skills generation prompt

### Styling
Frontend styles use Tailwind CSS. Modify `frontend/src/App.jsx` to change the UI.

## Troubleshooting

### LaTeX Compilation Fails
- Ensure pdflatex is installed and in PATH
- Check LaTeX logs in the API response
- Try compiling the LaTeX code manually to identify syntax errors

### API Key Issues
- Ensure `ANTHROPIC_API_KEY` is set in `.env`
- Verify your API key is valid and has sufficient credits

### CORS Errors
- Ensure backend is running on port 8000
- Check that frontend is configured to call `http://localhost:8000`

### PDF Not Displaying
- Check browser console for errors
- Verify PDF was successfully generated (check API response)
- Try downloading instead of previewing

## Technologies Used

- **Backend**: Python, FastAPI, LangGraph, LangChain, Anthropic Claude
- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons
- **Document Processing**: pdfplumber, PyPDF2, pdflatex
- **AI/ML**: Claude Sonnet 4 (via Anthropic API)

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on the GitHub repository.
