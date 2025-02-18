import argparse
import os
from datetime import datetime, timedelta, timezone
from github import Github

def main(dry_run):
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")  # e.g., "usuario/repo"
    g = Github(token)
    repo = g.get_repo(repo_name)

    main_branch = repo.default_branch
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)  # ✅ Use timezone-aware datetime

    branches_to_delete = []

    for branch in repo.get_branches():
        print(':::' * 30)
        print('branch:::', branch)
        print(':::' * 30)
        
        if branch.name in [main_branch, "develop"]:  # Keep important branches
            continue

        # Check if branch is merged
        pr_list = repo.get_pulls(state='closed', base=main_branch, head=f"{repo.owner.login}:{branch.name}")
        merged = any(pr.is_merged() for pr in pr_list)
        if not merged:
            continue

        # Check inactivity
        commit = repo.get_commit(branch.commit.sha)
        commit_date = commit.commit.author.date  # This is already timezone-aware

        if commit_date > cutoff_date:
            continue

        branches_to_delete.append(branch.name)

    if dry_run:
        print("Dry-run: The following branches would be deleted:")
        for b in branches_to_delete:
            print(f"- {b}")
    else:
        for b in branches_to_delete:
            ref = repo.get_git_ref(f"heads/{b}")
            ref.delete()
            print(f"Deleted branch: {b}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode")
    args = parser.parse_args()
    main(args.dry_run)
