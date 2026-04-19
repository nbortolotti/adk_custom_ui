# ADK Custom UI Workspace - Project Skills & Information

## 📦 Project Overview
- **Name**: ADK Custom UI Workspace (`adk-custom-ui-ws`)
- **Description**: A monorepo workspace for building custom user interfaces for AI agents powered by the Google ADK (Agent Development Kit). It separates the agentic backend logic from various frontend implementations (Streamlit for prototyping and Angular for production-grade UI).
- **Core Goal**: Demonstrate how to build scalable and modular agentic intelligence systems with multiple distinct UI layers.
- **Python requirement**: `>=3.12`

## 🏗️ Architecture & Structure

The repository follows a clean, decoupled application-first structure, organized within the `apps/` directory.

### 1. Backend (`apps/backend`)
The core reasoning engine and API layer where the agentic intelligence resides.
- **Frameworks**: FastAPI, Google ADK.
- **Configuration & Dependencies**: Managed by `uv`.
- **Functionality**:
    - Exposes a unified `/chat` REST endpoint to communicate with the agents.
    - Manages conversations and agent sessions using an `InMemorySessionService`.
    - Handles asynchronous execution and communication with Google GenAI models.
- **Agents Included** (`apps/backend/agents/`):
    - `class_details_agent`
    - `git_tutor_agent`
    - `learning_coach_agent`
    - `onboarding_tutor`

### 2. Streamlit Frontend (`apps/frontend`)
A rapid prototyping interface specifically designed for internal testing and prompt/response validation.
- **Frameworks**: Streamlit.
- **Configuration & Dependencies**: Managed by `uv`.
- **Functionality**:
    - Provides a fast, easy-to-run chat-based user interface.
    - Consumes the backend `/chat` API.

### 3. Angular Frontend (`apps/frontendangular`)
A high-quality, production-grade frontend meant for scalable, end-user experiences.
- **Frameworks**: Angular, Node.js.
- **Configuration & Dependencies**: Managed by `npm` (`package.json`).
- **Functionality**:
    - A fully featured, component-based chat application.
    - Showcases modern frontend architecture, state management, and service integration.
    - Communicates over HTTP with the FastAPI backend.

## 🛠️ Technology Stack
- **AI / LLM Framework**: Google ADK (Agent Development Kit), Google GenAI Models.
- **Backend API**: FastAPI (Python).
- **Package Managers**: 
    - Python: `uv` (Fast package and project manager for Python). Note: Uses `uv project` workspaces for managing the `backend` and `frontend` packages.
    - Node.js: `npm` (for the Angular app).
- **Frontends**: 
    - Streamlit (Python)
    - Angular (TypeScript/JavaScript, HTML, CSS)

## 🚀 Execution Guide

### Prerequisites
1. Ensure you have the required versions installed (`python >= 3.12`, `uv`, Node + `npm`).
2. Create a `.env` file in the `apps/backend/` directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Running the Backend (FastAPI + Google ADK)
```bash
cd apps/backend
uv sync
uv run backend.py
```
*Server runs at `http://localhost:8000`*

### Running the Streamlit App (Rapid Prototype)
```bash
cd apps/frontend
uv sync
uv run streamlit run frontend.py
```
*Streamlit runs locally (typically on port 8501)*

### Running the Angular App (Modern UI)
```bash
cd apps/frontendangular
npm install
npm start
```
*App runs at `http://localhost:4200`*
