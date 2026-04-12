import pathlib
from typing import List
from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

# 1. Definition of ADK Skills (Tools)
# These will be registered as additional tools in the SkillToolset
# and activated when the onboarding_tutor_skill is loaded.
def get_team_content(team_name: str) -> str:
    """Fetches specific documentation for the engineering team."""
    docs = {
        "backend": "Stack: Python/FastAPI. Repo: github.com/org/main-api. CI/CD: Jenkins.",
        "frontend": "Stack: React/TypeScript. Design System: Tailwind. Repo: github.com/org/ui-kit.",
        "devops": "Infrastructure: AWS (Terraform). Monitoring: Datadog & Sentry."
    }
    return docs.get(team_name.lower(), "General Tech Docs: Check the Notion 'Engineering' workspace.")

def manage_onboarding_calendar(action: str, activity: str = "") -> str:
    """Manages onboarding sessions.
    
    Args:
        action: The action to perform. Choose from 'query' (to check a specific session), 'list' (to see all scheduled sessions), or 'add' (to schedule a new activity).
        activity: The name of the session (required for 'query' and 'add'). Examples: 'security training', 'architecture overview'.
    """
    onboarding_schedule = {
        "security training": "Monday at 10:00 AM",
        "architecture overview": "Tuesday at 2:00 PM",
        "hr sync": "Wednesday at 9:00 AM"
    }
    action_low = action.lower()
    if action_low == "query":
        if not activity:
            return "Please provide the name of the activity you want to query."
        time = onboarding_schedule.get(activity.lower())
        if time:
            return f"The session '{activity}' is scheduled for {time}."
        return f"I couldn't find a session named '{activity}'. Try 'list' to see all sessions."
    elif action_low == "list":
        schedule_str = "\n".join([f"- {act}: {time}" for act, time in onboarding_schedule.items()])
        return f"Current Onboarding Schedule:\n{schedule_str}"
    
    return f"Activity '{activity}' has been successfully added to your first-week calendar."

def generate_check_in_questions(topic: str) -> List[str]:
    """Generates generic comprehension questions about onboarding materials."""
    return [
        f"Based on the {topic} docs, what are the first 3 steps to set up the local env?",
        f"Who is the point of contact for {topic} blockers?",
        f"Where is the production deployment checklist for {topic} located?"
    ]

# 2. Skill Loading
# Load the skill from the local 'skills' directory.
onboarding_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "_skills" / "onboarding-tutor-skill"
)

# 3. Toolset Configuration
# We use SkillToolset to manage the skill and its associated tools.
my_skill_toolset = skill_toolset.SkillToolset(
    skills=[onboarding_skill],
    additional_tools=[get_team_content, manage_onboarding_calendar, generate_check_in_questions]
)

# 4. Agent Configuration
root_agent = Agent(
    model='gemini-2.5-flash',
    name='onboarding_tutor_agent',
    description="Tech Onboarding Assistant that uses specialized skills to help new hires.",
    instruction=(
        "You are the Tech Onboarding Assistant. Your goal is to help new hires integrate quickly. "
        "You have access to specialized skills. You MUST use the `list_skills` and `load_skill` tools "
        "to discover and understand your capabilities. "
        "Once you load a skill, follow its instructions exactly and use the newly available tools to help the user. "
        "Always be welcoming and helpful to new members of the company."
    ),
    tools=[my_skill_toolset],
)
