# Travel Agent Planner - AI SDLC & Project Rules

## Zasady współpracy (AI SDLC)
1. **Pracujemy małymi krokami:** Nie generujemy całej aplikacji naraz. Każda sesja to konkretny, realizowalny krok.
2. **Tłumaczenie decyzji:** Wyjaśniamy kluczowe koncepcje przy wprowadzaniu nowych wzorców (zwłaszcza Python, Kubernetes, nowa infrastruktura).
3. **Jakość ponad szybkość:** Od początku dbamy o typowanie, czystą strukturę, lintowanie i testowalność kodu.

## Architektura i Stack Technologiczny
* **Frontend (`frontend/`):** React + TypeScript + Vite + Tailwind CSS.
  * Linter: ESLint + Prettier
  * Testy E2E: Cypress
* **Backend (`backend/`):** Python 3.12+ + FastAPI + Pydantic.
  * Agent: Własna pętla agentowa (tool-calling loop / ReAct) napisana od zera. Brak LangChain/CrewAI.
  * Linter: Ruff
  * Testy: Pytest (z mockowaniem)
* **MCP Server (`mcp-server/`):** Python + oficjalne SDK Model Context Protocol.
  * Baza danych (przyszłość): PostgreSQL
* **Infrastruktura:** Docker (multi-stage), Docker Compose, Kubernetes (`k8s/`), HPA.
* **CI/CD:** GitHub Actions (lint -> unit -> docker build -> E2E).

## Przydatne komendy
### MCP Server
* Tworzenie środowiska wirtualnego: `python -m venv .venv` oraz aktywacja `.venv\Scripts\Activate.ps1`
* Uruchomienie testów: `pytest tests/` (z poziomu katalogu `mcp-server/`)
* Linter (Ruff): `ruff check src/ tests/`
