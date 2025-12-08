# Export GitHub Starred Repos

A small script to export a user's starred GitHub repositories into a Markdown file.

## Installation

### Prerequisites

1. **Git** - Clone the repository
   - Download from [git-scm.com](https://git-scm.com/)
   - Install with default options
   - Verify: Open PowerShell and run `git --version`

2. **Python** - Run the script
   - Download from [python.org](https://python.org/)
   - Install Python 3.7 or higher
   - **Important**: Check "Add Python to PATH" during installation
   - Verify: Open PowerShell and run `python --version`

### Setup

1. **Clone the repository**
   ```powershell
   git clone https://github.com/THEgrison/GithubStars-exporter.git
   cd GithubStars-exporter
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Get a GitHub Personal Access Token**
   - Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
   - Click "Generate new token (classic)"
   - Select scope: `public_repo` (to read public starred repos)
   - Copy the token (you'll need it next)

## Usage

### Option 1: Using Environment Variable

```powershell
# Set the token
$env:GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"

# Run the script
python "export_starred.py" --username YOUR_GITHUB_USERNAME
```

### Option 2: Pass Token Directly

```powershell
python "export_starred.py" --username YOUR_GITHUB_USERNAME --token ghp_YOUR_TOKEN_HERE --output mystars.md
```

## Examples

```powershell
# Export with default output file (starred_repos.md)
python "export_starred.py" --username octocat

# Export to custom file
python "export_starred.py" --username octocat --output my_stars.md

# Using environment variable for security
$env:GITHUB_TOKEN = "ghp_abc123..."
python "export_starred.py" --username octocat
```

## Notes

- The script uses the GitHub REST API and respects rate limits.
- Without a token: 60 requests/hour per IP
- With a token: 5,000 requests/hour per user
- Output is formatted as Markdown with repository links and descriptions
