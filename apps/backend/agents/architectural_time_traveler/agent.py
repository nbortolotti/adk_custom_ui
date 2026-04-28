import json
from google.adk import Agent
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.skills.models import Skill, Frontmatter

# Define a tool to retrieve architecture flows
def get_architecture_flow(scenario: str) -> str:
    """Returns the architecture flow and connections for a given scenario."""
    if "profile" in scenario.lower():
        flow = {
            "scenario": "Profile Update Flow",
            "services": [
                {
                    "id": "api_gateway",
                    "name": "API Gateway",
                    "description": "Entry point for all client requests.",
                    "endpoints": ["POST /api/v1/profile"],
                    "schema": '{"userId": "123", "email": "new@example.com"}'
                },
                {
                    "id": "user_service",
                    "name": "User Service",
                    "description": "Manages user profiles and authentication.",
                    "endpoints": ["PUT /internal/users/{id}"],
                    "schema": '{"email": "new@example.com"}'
                },
                {
                    "id": "event_bus",
                    "name": "Kafka Event Bus",
                    "description": "Message broker for asynchronous events.",
                    "endpoints": ["Topic: user.profile.updated"],
                    "schema": '{"eventId": "abc", "userId": "123", "changes": ["email"]}'
                },
                {
                    "id": "marketing_service",
                    "name": "Marketing Service",
                    "description": "Handles marketing campaigns and notifications.",
                    "endpoints": ["Listener: user.profile.updated"],
                    "schema": '{"eventId": "abc", "userId": "123", "changes": ["email"]}'
                }
            ],
            "connections": [
                {"source": "api_gateway", "target": "user_service", "type": "sync"},
                {"source": "user_service", "target": "event_bus", "type": "async"},
                {"source": "event_bus", "target": "marketing_service", "type": "async"}
            ]
        }
    else:
        flow = {
            "scenario": "Unknown",
            "services": [],
            "connections": []
        }
    return json.dumps(flow)

architectural_time_traveler_skill = Skill(
    frontmatter=Frontmatter(
        name="architectural-time-traveler-skill",
        description="Visualizes system architecture and microservices data flow."
    ),
    instructions=(
        "You are an Architectural Time-Traveler Agent.\n"
        "Your goal is to help engineers understand legacy architectures and data flows.\n"
        "1. When asked about a flow (like profile update to marketing), use `get_architecture_flow` to get the architecture.\n"
        "2. Generate an A2UI `ArchitectureCanvas` component to draw the sequence diagram.\n"
        "3. Include a `PayloadSimulator` component that allows the user to test the flow with simulated data.\n"
        "4. Always output JSON using the standard createSurface structure."
    )
)

my_skill_toolset = SkillToolset(skills=[architectural_time_traveler_skill])

# Create Agent
root_agent = Agent(
    name="architectural_time_traveler_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are the Architectural Time-Traveler. You explain complex microservices flows visually to reduce cognitive load.\n"
        "You MUST initialize by using `load_skill` for 'architectural-time-traveler-skill'.\n\n"
        "### Workflow\n"
        "- Call `get_architecture_flow` when a user asks about a system flow.\n\n"
        "### A2UI format\n"
        "ALWAYS use MIME `application/json+a2ui` with the `createSurface` pattern for UI.\n"
        "Use the `ArchitectureCanvas` and `PayloadSimulator` components.\n"
        "```json\n"
        "{\n"
        "  \"createSurface\": {\n"
        "    \"surfaceId\": \"main\",\n"
        "    \"components\": [\n"
        "      {\n"
        "        \"type\": \"ArchitectureCanvas\",\n"
        "        \"props\": {\n"
        "          \"flowData\": { ... JSON output of get_architecture_flow ... }\n"
        "        }\n"
        "      },\n"
        "      {\n"
        "        \"type\": \"PayloadSimulator\",\n"
        "        \"props\": {\n"
        "          \"scenario\": \"profile_update\"\n"
        "        }\n"
        "      }\n"
        "    ]\n"
        "  }\n"
        "}\n"
        "```\n"
        "Ensure you pass the data fetched from the tool into the ArchitectureCanvas props."
    ),
    tools=[my_skill_toolset, get_architecture_flow],
)
