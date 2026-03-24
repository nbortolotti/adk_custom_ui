
## Init and install dependencies
uv init
uv sync

## Run FastAPI server
uv run backend.py

## Run the agent
uv run adk run <agent_directory>


## Run the agents with UI

uv run adk web --port 8000

