# WorkflowVdAi

Local-first Script-to-Video production pipeline.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
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

## Architecture
See [PLAN.md](PLAN.md) and [PROCESS.md](PROCESS.md) for full details.
