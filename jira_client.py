import requests
from jira_token_manager import get_valid_access_token

CLOUD_ID = "aaf3ee41-766b-44b8-8b12-92b0e035861f"
JIRA_API_BASE = f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3"

def fetch_issues_by_jql(jql, token_file="jira_token.json", max_results=100):
    token = get_valid_access_token(token_file)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    response = requests.get(
        f"{JIRA_API_BASE}/search",
        headers=headers,
        params={
            "jql": jql,
            "maxResults": max_results,
            "fields": "key,summary,issuetype,fixVersions"
        }
    )
    response.raise_for_status()
    return response.json()["issues"]
