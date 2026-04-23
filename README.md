# FinSight AI

Full-stack financial insights platform powered by ML and LLMs.

## Tech Stack
- **Backend**: Python 3.12, FastAPI, Pydantic v2
- **Frontend**: React 19, Vite, Tailwind CSS 4, Zustand, React Query
- **ML**: scikit-learn, XGBoost, SHAP
- **LLM**: Anthropic Claude 3.5 Sonnet
- **Database**: Supabase (PostgreSQL + Auth + RLS)
- **Deployment**: Docker, Docker Compose, Nginx

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Supabase Account
- Anthropic API Key

### Setup
1. Clone the repository
2. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Fill in your credentials in `.env`
4. Start the services:
   ```bash
   docker-compose up --build
   ```

## Project Structure
- `backend/`: FastAPI application and ML pipeline
- `frontend/`: React application with Tailwind 4
- `nginx/`: Reverse proxy configuration
- `ml/`: Model training and prediction logic

## API Endpoints
- `GET /health`: Check system status
- `POST /api/v1/...`: Business logic (to be implemented)

## License
MIT
