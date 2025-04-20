import json
import os
import requests

STATE_FILE = "scraper/state.json"

# Read the current state from the state.json file
with open(STATE_FILE, 'r') as f:
    state = json.load(f)

# Get GitHub token and username from environment variables
GH_TOKEN = os.getenv("GH_TOKEN")
USERNAME = os.getenv("GITHUB_ACTOR")

# Calculate the new repository index
new_index = state['repo_index'] + 1
new_repo = f"wikiscraper-{new_index:03d}"

# GitHub API endpoint for creating a new repository
url = "https://api.github.com/user/repos"
payload = {
    "name": new_repo,  # Name of the new repo
    "private": False  # Make the repository public (set to True for private)
}
headers = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Create a new GitHub repository
res = requests.post(url, headers=headers, json=payload)

if res.status_code == 201:
    print(f"✅ Created new repo: {new_repo}")

    # Set the remote URL for the new repo
    os.system(f"git remote set-url origin https://{USERNAME}:{GH_TOKEN}@github.com/{USERNAME}/{new_repo}.git")

    # Add all changes and push to the new repo
    os.system("git add . && git commit -m 'Auto: Repo Rotation' && git push origin main")

    # Update the state.json with the new repo index and reset the file number
    state['repo_index'] = new_index
    state['current_file_number'] = 1  # Reset to start from the first file in the new repo

    # Overwrite the existing state.json with the updated state
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"✅ Updated state.json and pushed to GitHub")
else:
    print(f"❌ Failed to create repo: {res.text}")
