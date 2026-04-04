from google.adk.agents.llm_agent import Agent

def get_recent_commits(engineer_id: str) -> list[dict]:
    """Returns a list of recent simulated learning commits for an engineer."""
    commits = {
        "test_engineer_id": [
            {
                "commit_id": "c101",
                "message": "Add fast API route",
                "diff_summary": "Added 3 routes without rate limiting"
            },
            {
                "commit_id": "c102",
                "message": "Fix database query",
                "diff_summary": "N+1 query issue found in ORM usage"
            },
        ],
        "test_engineer_cloud": [
            {
                "commit_id": "c201",
                "message": "Add AWS S3 bucket for user uploads",
                "diff_summary": "Bucket created with public read access by default"
            }
        ],
        "test_engineer_search": [
            {
                "commit_id": "c301",
                "message": "Implement text search over product table",
                "diff_summary": "Added ILIKE query with leading wildcard '%term%'"
            }
        ]
    }
    return commits.get(engineer_id, [])

def analyze_commit(commit_id: str) -> dict:
    """Analyzes a specific commit for learning opportunities."""
    mock_analysis = {
        "c101": {
            "learning_opportunity": "Rate Limiting in APIs",
            "details": "The implementation lacks basic rate limiting, exposing the system to potential DDoS attacks or excessive resource consumption."
        },
        "c102": {
            "learning_opportunity": "Database Optimization (N+1 queries)",
            "details": "The current ORM usage leads to N+1 query problems, significantly degrading performance for large datasets."
        },
        "c201": {
            "learning_opportunity": "Cloud Security: Open Bucket Access",
            "details": "The S3 bucket was created with public read access, which could lead to data leakage. It's recommended to make buckets private and use signed URLs for public access."
        },
        "c301": {
            "learning_opportunity": "Database Query Optimization: Leading Wildcard",
            "details": "Using a leading wildcard in an ILIKE query prevents the database from using standard indexes, resulting in a full table scan."
        }
    }
    return mock_analysis.get(
        commit_id,
        {"learning_opportunity": "None", "details": "No specific learning opportunities found for this commit."}
    )

def provide_nano_learning(topic: str) -> dict:
    """Provides a nano-learning module based on a topic."""
    learning_modules = {
        "Rate Limiting in APIs": "Nano-learning: Rate limiting restricts the number of requests a user can make in a given timeframe. Use libraries like 'slowapi' in FastAPI.",
        "Database Optimization (N+1 queries)": "Nano-learning: Use 'joinedload' or 'selectinload' in SQLAlchemy to eagerly load related objects in a single query.",
        "Cloud Security: Open Bucket Access": "Nano-learning: When provisioning object storage in the cloud, always default to private access. Use IAM policies to grant minimum necessary permissions and avoid making buckets completely public.",
        "Database Query Optimization: Leading Wildcard": "Nano-learning: For text search, consider using Full-Text Search extensions (like pg_trgm for PostgreSQL) or dedicated search engines (like Elasticsearch) instead of leading wildcards to maintain performance."
    }
    return {
        "topic": topic,
        "content": learning_modules.get(topic, f"General nano-learning on {topic}. Keep up the good work! Please review best practices in the team documentation.")
    }

root_agent = Agent(
    model='gemini-2.5-flash',
    name='learning_coach_agent',
    description="Analyzes engineer commits and provides proactive nano-learning moments based on identified learning opportunities.",
    instruction=(
        "You are a Technical Learning Coach. Your goal is to analyze an engineer's commits using 'get_recent_commits', "
        "evaluate them for improvements using 'analyze_commit', and then proactively deliver nano-learning moments using 'provide_nano_learning'. "
        "Always be encouraging and focus on continuous improvement."
    ),
    tools=[get_recent_commits, analyze_commit, provide_nano_learning],
)
