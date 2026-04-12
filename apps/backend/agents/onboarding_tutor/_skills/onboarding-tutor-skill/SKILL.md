---
name: onboarding-tutor-skill
description: Specialized skill for tech onboarding, providing documentation, schedule, and quizzes.
metadata:
  adk_additional_tools:
    - get_team_content
    - manage_onboarding_calendar
    - generate_check_in_questions
---

# Tech Onboarding Skill

This skill helps new hires integrate by providing:
1.  **Technical Documentation**: Use `get_team_content` for specific stack details.
2.  **Onboarding Calendar**: Use `manage_onboarding_calendar` to manage sessions. Set `action='list'` to see everything, `action='query'` to check a specific session, or `action='add'` to schedule something.
3.  **Knowledge Checks**: Use `generate_check_in_questions` to quiz new hires on what they've learned.

## Guidelines
- Always use `action='list'` if the user asks for their schedule or "what meetings do I have".
- Use `action='query'` if they ask about a specific session (e.g., "when is security training?").
- Always check the team documentation first when a user asks about the stack.
- Remind users about upcoming sessions from the schedule if they seem lost.
- Use quizzes to ensure the new hire is comfortable with their team's specific tools.
