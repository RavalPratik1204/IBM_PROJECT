# SwachhAI Gujarat 🗑️

**Agentic AI for Smarter Waste Management and Better Citizen Services**

*Gujarat Hackathon 2026 — Challenge 18: Municipal Solid Waste & Circular Economy Agent*

---

> ⚠️ **Synthetic Demo Data** — All sample data is generated for demonstration purposes. Not official municipal data.

---

## Problem Statement

Gujarat's municipalities face critical challenges in urban waste management:
- Citizens have no effective channel to report waste problems in local languages
- Municipal officers lack real-time data to prioritize collection
- Waste collection routes are manually planned, inefficient, and reactive
- No cross-ward analytics to identify systemic failures

**SwachhAI Gujarat** solves this with a true Agentic AI platform connecting citizens, AI agents, and municipal operations.

---

## Solution Architecture

```
CITIZEN (Text/Voice/Chat in Gujarati, Hindi, English)
                 │
                 ▼
    GRIEVANCE INTAKE AGENT
    (Classify, Extract, Validate)
                 │
                 ▼
    MUNICIPAL ROUTING AGENT
    (Dept → Ward → Priority → Team)
                 │
         ┌───────┴────────┐
         ▼                ▼
  ROUTE OPTIMIZATION   SEGREGATION
       AGENT              AGENT
  (Nearest-neighbor)  (AI Guidance)
         │
         ▼
  AGENT ORCHESTRATOR + DATABASE
         │
         ▼
  WARD ANALYTICS AGENT → MUNICIPAL DASHBOARD
```

---

## The 5 Agents

| Agent | Goal | Method |
|---|---|---|
| **Grievance Intake** | Understand citizen complaint in any language | IBM Granite/Groq LLM + deterministic fallback |
| **Municipal Routing** | Assign to correct dept/ward/team | Rules engine + LLM reasoning |
| **Segregation** | Guide waste categorization | LLM + static knowledge base |
| **Route Optimization** | Minimize collection distance | Priority-nearest-neighbor algorithm |
| **Ward Analytics** | Surface operational insights | DB aggregation + AI summary |

---

## IBM Technologies Used

| Technology | Role |
|---|---|
| **IBM Granite** (via watsonx.ai) | Primary LLM for complaint classification, routing reasoning, segregation guidance |
| **IBM watsonx.ai** | Hosted endpoint for Granite model inference |
| **IBM Cloud Code Engine** | Target deployment platform (Phase 15) |
| **IBM Bob** | Complete development workflow — architecture, code generation, testing, prompts, documentation |

### IBM Bob Development Workflow
IBM Bob was used throughout all 15 development phases:
- Designed the agentic architecture
- Generated all backend agent code, API routes, and database schemas
- Wrote all system prompts for Granite and Groq
- Created unit tests and AI evaluation dataset
- Generated this documentation

---

## Groq Integration

Groq provides high-speed LLM inference as a secondary provider.

| Use Case | Provider |
|---|---|
| Complaint classification, routing reasoning | IBM Granite (primary) |
| Fast conversational chat | Groq llama-3.3-70b-versatile |
| Language detection assist | Groq llama-3.1-8b-instant |
| Fallback when IBM unavailable | Groq |

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11 + FastAPI |
| **Frontend** | React 18 + TypeScript + Vite + TailwindCSS |
| **Database** | SQLite (dev) → PostgreSQL (prod) |
| **ORM** | SQLAlchemy 2.0 |
| **AI (primary)** | IBM Granite via watsonx.ai |
| **AI (secondary)** | Groq API (llama-3.3-70b-versatile) |
| **Auth** | JWT + bcrypt |
| **Maps** | Leaflet.js + OpenStreetMap (free, no key) |
| **Voice** | Web Speech API (EN/HI) + Groq Whisper (GU) |
| **Charts** | Recharts |

---

## Project Structure

```
swachhai-gujarat/
├── backend/
│   ├── app/
│   │   ├── agents/          # 5 AI agents + orchestrator
│   │   ├── ai/
│   │   │   ├── providers/   # IBM Granite + Groq adapters
│   │   │   ├── router/      # AI provider router
│   │   │   └── prompts/     # System prompts
│   │   ├── api/routes/      # FastAPI endpoints
│   │   ├── core/            # Config, DB, security
│   │   └── models/          # SQLAlchemy ORM models
│   ├── scripts/             # seed_demo_data.py
│   └── tests/               # Unit + AI eval tests
├── frontend/
│   └── src/
│       ├── pages/citizen/   # Citizen portal
│       ├── pages/municipal/ # Municipal dashboard
│       ├── services/        # API client
│       └── store/           # Zustand state
├── .env.example
└── start.ps1
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone and configure

```bash
git clone https://github.com/your-org/swachhai-gujarat.git
cd swachhai-gujarat
cp .env.example .env
# Edit .env and add your API keys (see Environment Variables section)
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python scripts/seed_demo_data.py
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

### 4. Run the application

**Windows (PowerShell):**
```powershell
# From swachhai-gujarat/ root:
.\start.ps1
```

**Manual:**
```bash
# Terminal 1 (backend):
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 (frontend):
cd frontend
npm run dev
```

Access:
- **Citizen Portal:** http://localhost:5173
- **Municipal Dashboard:** http://localhost:5173/municipal
- **API Docs:** http://localhost:8000/api/docs

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key from console.groq.com |
| `IBM_API_KEY` | Phase 10+ | IBM Cloud API key |
| `IBM_PROJECT_ID` | Phase 10+ | watsonx.ai project ID |
| `JWT_SECRET` | Yes | Random secret for JWT signing |
| `SECRET_KEY` | Yes | App secret key |
| `DATABASE_URL` | Yes | SQLite or PostgreSQL URL |
| `PRIMARY_LLM_PROVIDER` | Yes | `ibm` or `groq` |
| `FALLBACK_LLM_PROVIDER` | Yes | `groq` |
| `DEMO_MODE` | Optional | `true` to enable demo mode |

See `.env.example` for all variables.

---

## Demo Login Credentials

After running `seed_demo_data.py`:

| Role | Email | Password |
|---|---|---|
| Admin | admin@swachhai.demo | admin123 |
| Municipal Officer | officer@swachhai.demo | officer123 |
| Citizen | citizen1@demo.swachhai | citizen123 |

---

## Testing

```bash
cd backend

# Unit tests
pytest tests/unit/ -v

# AI evaluation tests (no API key required)
pytest tests/ai_eval/ -v

# All tests
pytest tests/ -v
```

Current test result: **49/49 tests pass**

---

## Demo Script (3–5 minutes)

1. Open http://localhost:5173 (Citizen Portal)
2. Click "Report Issue" → type in Gujarati: `મારા વિસ્તારમાં ત્રણ દિવસથી કચરો ઉઠ્યો નથી.`
3. Submit — watch the AI process it
4. Navigate to `/track/{ticket_id}` — see the agent activity log
5. Switch to http://localhost:5173/municipal
6. See the complaint appear on the dashboard
7. Go to Route Optimization → select a ward → Run Optimization
8. Go to Ward Analytics → see KPIs
9. Go to Agent Monitor → see live AI logs and provider stats
10. Go to Chat → ask segregation question in any language

---

## Security

- API keys stored in `.env` only — never in source code
- JWT authentication on all protected endpoints
- Role-based access control (citizen / officer / admin)
- bcrypt password hashing
- Input validation via Pydantic
- Rate limiting via SlowAPI
- No citizen PII in AI request logs

---

## Challenge 18 Coverage

| Requirement | Status |
|---|---|
| Route Optimization Agent | ✅ Implemented (priority-nearest-neighbor) |
| Segregation Compliance Agent | ✅ Implemented (AI + knowledge base) |
| Multilingual Grievance Intake (Chat/Voice) | ✅ Implemented (EN/HI/GU) |
| Municipal Routing Agent | ✅ Implemented (rules + LLM) |
| Ward Analytics Dashboard | ✅ Implemented (KPIs + charts) |
| IBM Granite | ✅ Integrated (watsonx.ai) |
| IBM Cloud | ✅ watsonx.ai + Code Engine (deployment) |
| IBM Bob | ✅ Complete development workflow |

---

*Built for Gujarat Hackathon 2026 — Challenge 18*  
*⚠️ All sample data is synthetic and for demonstration purposes only.*
