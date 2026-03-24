from google.adk.agents.llm_agent import Agent

def get_class_details(user_id: str) -> dict:
    """Returns developer introduction class details for a user."""
    return {"status": "success", "user_id": user_id, "class_details": "Clase de Flujo de Trabajo de Desarrolladores con Gemini"}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='class_details_agent',
    description="Tells the current class details for a user.",
    instruction="Eres un asistente útil. Usa 'get_class_details' para dar información.",
    tools=[get_class_details],
)
