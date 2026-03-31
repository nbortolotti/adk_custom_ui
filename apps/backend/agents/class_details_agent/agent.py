from google.adk.agents.llm_agent import Agent

def get_class_details(user_id: str) -> dict:
    """Returns developer introduction class details for a user."""
    return {"status": "success", "user_id": user_id, "class_details": "Gemini Developer Workflow Class"}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='class_details_agent',
    description="Tells the current class details for a user.",
    instruction="You are a helpful assistant. Use 'get_class_details' to provide information.",
    tools=[get_class_details],
)
