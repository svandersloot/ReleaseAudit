# Git vs Jira Excel Report

This tool compares Jira issues exported to Excel against Bitbucket commit history.

## Setup

1. Create a Python 3.9 environment.
2. Install dependencies (including `python-dotenv`):
   ```bash
   pip install -r requirements.txt
   ```
   The script will attempt this automatically if modules are missing.
3. Copy `.env.example` to `.env` and fill in your Bitbucket credentials.
4. Set `BITBUCKET_BASE_URL` in `.env` if your Bitbucket host differs from the
   default (`https://bitbucket.example.com/rest/api/1.0`).
5. Optionally adjust `config.json` to list repositories and branches.

## Usage

Export issues from Jira as an Excel file (`.xlsx`) or CSV file containing columns such as *Issue key*, *Summary*, *Issue type*, *Components*, and *Fix version(s)*.

Run the tool:

```bash
python main.py --jira-excel path/to/jira.xlsx
```
CSV files can be provided in the same way:
```bash
python main.py --jira-excel path/to/jira.csv
```
If your file name contains spaces, wrap it in quotes:
```bash
python main.py --jira-excel "Release Audit.csv"
```
Ensure you run `main.py` as the script (the `.csv` file should be passed with `--jira-excel`).

Additional options:

- `--develop-branch` specify a different develop branch.
- `--release-branch` specify a different release branch.
- `--config` path to configuration JSON.

The script outputs an Excel report `gitxjira_report_<timestamp>.xlsx` with Jira stories, commit details, and any stories missing from Git.
