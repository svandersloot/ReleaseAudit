import argparse
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from config_loader import load_config
from bitbucket_api import fetch_commits
from excel_loader import load_jira_excel
from commit_processor import extract_stories
from excel_writer import write_excel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_args() -> argparse.Namespace:
    # If the user accidentally runs a CSV/XLSX file as the Python script
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith((".csv", ".xlsx")):
        print(
            "It looks like you tried to run a data file as the script. "
            "Run:\n  python main.py --jira-excel \"%s\"" % sys.argv[1]
        )
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Compare Jira issues against Bitbucket commits"
    )
    parser.add_argument(
        "--jira-excel", required=True, help="Path to exported Jira Excel or CSV file"
    )
    parser.add_argument("--config", default="config.json", help="Path to JSON config file")
    parser.add_argument("--develop-branch", help="Develop branch name override")
    parser.add_argument("--release-branch", help="Release branch name override")
    return parser.parse_args()


def build_branches(args, config: Dict[str, str]) -> List[str]:
    develop = args.develop_branch or config.get("develop_branch", "develop")
    release = args.release_branch or config.get("release_branch", "release")
    return [develop, release]


def process_repo(
    repo_name: str,
    app_name: str,
    branches: List[str],
    cfg: Dict[str, str],
    jira_story_data: Dict[str, dict],
    cutoff: datetime,
    freeze: datetime,
    auth,
    headers,
    limit: int,
    develop_branch: str,
    git_story_numbers: Dict[str, str],
    commit_hashes: Dict[str, str],
) -> List[dict]:
    results = []
    for branch in branches:
        commits = fetch_commits(cfg["bitbucket_base_url"], repo_name, branch, auth, headers, limit, start_date=cutoff, end_date=freeze)
        for commit in commits:
            extracted = extract_stories(
                commit=commit,
                fix_version=cfg.get("fix_version", ""),
                jira_story_data=jira_story_data,
                app_name=app_name,
                commit_hash=commit["id"],
                branch=branch,
                cutoff_date_obj=cutoff,
                code_freeze_date=freeze,
                develop_branch=develop_branch,
                git_story_numbers=git_story_numbers,
                commit_hashes=commit_hashes,
                exclude_patterns=[],
            )
            results.extend(extracted)
    return results


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_config(str(config_path))

    # Required environment variables loaded by config_loader
    bitbucket_email = os.getenv("BITBUCKET_EMAIL")
    bitbucket_token = os.getenv("BITBUCKET_TOKEN")
    if not bitbucket_email or not bitbucket_token:
        raise EnvironmentError("BITBUCKET_EMAIL and BITBUCKET_TOKEN must be set in .env")

    repos = config.get("repos", {})
    develop_branch = args.develop_branch or config.get("develop_branch", "develop")
    release_branch = args.release_branch or config.get("release_branch", "release")
    fix_version = config.get("fix_version", "")
    base_url = os.getenv(
        "BITBUCKET_BASE_URL",
        config.get("bitbucket_base_url", "https://bitbucket.example.com/rest/api/1.0"),
    )
    commit_limit = int(config.get("commit_fetch_limit", 25))
    cutoff_days = int(config.get("cutoff_days_before_code_freeze", 28))
    freeze_days = int(config.get("code_freeze_days_before_release", 17))

    release_date = datetime.strptime(fix_version.replace("Mobilitas ", ""), "%Y.%m.%d") if fix_version else datetime.now()
    code_freeze_date = release_date - timedelta(days=freeze_days)
    cutoff_date = code_freeze_date - timedelta(days=cutoff_days)

    jira_story_data = load_jira_excel(args.jira_excel)

    auth = (bitbucket_email, bitbucket_token)
    headers = {"Accept": "application/json"}

    all_commits: Dict[str, List[dict]] = {}
    git_story_numbers: Dict[str, str] = {}
    commit_hashes: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for repo_name, app_name in repos.items():
            futures[executor.submit(
                process_repo,
                repo_name,
                app_name,
                [develop_branch, release_branch],
                {
                    "bitbucket_base_url": base_url,
                    "fix_version": fix_version,
                },
                jira_story_data,
                cutoff_date,
                code_freeze_date,
                auth,
                headers,
                commit_limit,
                develop_branch,
                git_story_numbers,
                commit_hashes,
            )] = (repo_name, app_name)

        for future in as_completed(futures):
            repo_name, app_name = futures[future]
            try:
                commits = future.result()
                if commits:
                    all_commits.setdefault(app_name, []).extend(commits)
            except Exception as exc:
                logger.error("Failed processing %s: %s", repo_name, exc)

    missing = [story for story in jira_story_data if story not in git_story_numbers]
    missing_data = [jira_story_data[s] | {"Missing From": "Git", "Notes": ""} for s in missing]

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    output_file = f"gitxjira_report_{timestamp}.xlsx"
    write_excel(all_commits, missing_data, output_file)
    logger.info("Report written to %s", output_file)


if __name__ == "__main__":
    main()
