# Git vs Jira Excel Report

This tool compares Jira issues exported to Excel against Bitbucket commit history.

## Setup

1. Create a Python 3.9 environment.
2. Install dependencies (including `python-dotenv`):
   ```bash
   pip install -r requirements.txt
   ```
   If you see `ModuleNotFoundError: No module named 'dotenv'`, it means the
   dependencies were not installed correctly.
3. Copy `.env.example` to `.env` and fill in your Bitbucket credentials.
4. Optionally adjust `config.json` to list repositories and branches.

## Usage

Export issues from Jira as an Excel file (`.xlsx`) containing columns such as *Issue key*, *Summary*, *Issue type*, *Components*, and *Fix version(s)*.

Run the tool:

```bash
python main.py --jira-excel path/to/jira.xlsx
```

Additional options:

- `--develop-branch` specify a different develop branch.
- `--release-branch` specify a different release branch.
- `--config` path to configuration JSON.

The script outputs an Excel report `gitxjira_report_<timestamp>.xlsx` with Jira stories, commit details, and any stories missing from Git.
