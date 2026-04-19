import json
from google.adk import Agent
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.skills.models import Skill, Frontmatter

# Define a tool to retrieve documentation resources
def get_onboarding_resources() -> str:
    """Returns a list of available documentation and resources for technical onboarding."""
    resources = [
        {
            "id": "eng_handbook",
            "title": "Google Engineering Practices",
            "description": "The official guide to code reviews and engineering standards used at Google.",
            "url": "https://google.github.io/eng-practices/",
            "tags": ["Standard", "Process"]
        },
        {
            "id": "a2ui_spec",
            "title": "A2UI Specification",
            "description": "Technical specification for the Agent-to-User Interface protocol.",
            "url": "https://a2ui.org/",
            "tags": ["SDK", "UI"]
        },
        {
            "id": "design_system",
            "title": "Corporate Design System",
            "description": "Material 3 design guidelines and components.",
            "url": "https://m3.material.io/",
            "tags": ["Design", "UX"]
        }
    ]
    return json.dumps(resources)

# Define Skill with the new Frontmatter requirement for v0.12+
onboarding_tutor_skill = Skill(
    frontmatter=Frontmatter(
        name="onboarding-tutor-skill",
        description="Provides guidance and documentation for new technical hires."
    ),
    instructions=(
        "You are a Technical Onboarding Tutor. Your goal is to help new engineers settle in.\n"
        "1. When asked for documentation or guides, ALWAYS use the `get_onboarding_resources` tool.\n"
        "2. Generate A2UI `DocCard` components with the retrieved data.\n"
        "3. Welcome new hires and help them find what they need."
    )
)

my_skill_toolset = SkillToolset(skills=[onboarding_tutor_skill])

# Create Agent
root_agent = Agent(
    name="onboarding_tutor_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a helpful Technical Onboarding Tutor.\n"
        "You MUST initialize by using `load_skill` for 'onboarding-tutor-skill'.\n\n"
        "### Workflow\n"
        "- Call `get_onboarding_resources` when documentation is requested.\n\n"
        "### A2UI format\n"
        "ALWAYS use MIME `application/json+a2ui` with the `createSurface` pattern for UI.\n"
        "```json\n"
        "{\n"
        "  \"createSurface\": {\n"
        "    \"surfaceId\": \"main\",\n"
        "    \"components\": [\n"
        "      {\n"
        "        \"type\": \"DocCard\",\n"
        "        \"props\": {\n"
        "          \"title\": \"Title\",\n"
        "          \"description\": \"Desc\",\n"
        "          \"url\": \"URL\",\n"
        "          \"tags\": [\"Tag\"]\n"
        "        }\n"
        "      }\n"
        "    ]\n"
        "  }\n"
        "}\n"
        "```"
    ),
    tools=[my_skill_toolset, get_onboarding_resources],
)
