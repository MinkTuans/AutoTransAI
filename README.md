# AutoTransAi

Unified 6-Stage AI Video Translation, Dubbing & Automation Platform.

## Quick Start

### Windows Desktop Launcher
Double-click `AutoTransAi.bat` or run:
```bash
run_app.bat
```

### Manual Development Setup

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```
