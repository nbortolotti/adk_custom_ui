import os
import subprocess
from google.adk import Agent

# Exercise path
REPO_PATH = "./tmp_repo_user_1"
if not os.path.exists(REPO_PATH):
    os.makedirs(REPO_PATH)

def run_git_command(command: str) -> str:
    """
    Executes a command in the student's local repository and returns the result.
    
    Args:
        command: The git command to execute (e.g., 'git status', 'git rev-parse --is-inside-work-tree', etc.)
    """
    try:
        result = subprocess.run(
            command, shell=True, cwd=REPO_PATH, 
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return f"Success:\n{result.stdout}"
        else:
            return f"Error:\n{result.stderr}"
    except Exception as e:
        return f"Exception: {str(e)}"

# Agent configuration
root_agent = Agent(
    model='gemini-2.5-flash',
    name='git_tutor_agent',
    description="Git Tutor Agent that hands out tasks to students and validates them using Git commands.",
    instruction=(
        "You are a Personal Git Tutor (" "GitTutorAgent" "). "
        "Your objective is to teach the student Git by assigning them a series of tasks, validating if they completed them, and helping them if they fail.\n\n"
        "Here are the tasks you need to guide the user through, one by one:\n"
        "1. Initialize a git repository. (Validation: 'test -d .git'). Hint: 'git init'\n"
        "2. Create a file called 'readme.md' and add it to the staging area. (Validation: 'git ls-files --stage | grep readme.md'). Hint: 'touch readme.md' then 'git add readme.md'\n"
        "3. Make the first commit with message 'First commit'. (Validation: 'git log --oneline'). Hint: 'git commit -m \"First commit\"'\n\n"
        "Instructions:\n"
        "- When the user starts or asks what to do, present the CURRENT task.\n"
        "- Wait for the user to tell you they have done it.\n"
        "- Once the user says they completed the task, you MUST use the `run_git_command` tool to run the validation check for that task.\n"
        "- If the tool returns success, congratulate them and move to the next task.\n"
        "- If it fails, give them the hint and ask them to try again.\n"
        "- Be encouraging, speak in English, and act as a helpful teacher!"
    ),
    tools=[run_git_command],
)
