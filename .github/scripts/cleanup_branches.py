import argparse
from datetime import datetime, timedelta
from github import Github

def main(dry_run):
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")  # e.g., "usuario/repo"
    g = Github(token)
    repo = g.get_repo(repo_name)

    main_branch = repo.default_branch
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    branches_to_delete = []

    for branch in repo.get_branches():
        if branch.name in [main_branch, "develop"]:  # Ejemplo: mantener ramas importantes
            continue

        # Verificar si la rama está fusionada:
        pr_list = repo.get_pulls(state='closed', base=main_branch, head=f"{repo.owner.login}:{branch.name}")
        merged = any(pr.is_merged() for pr in pr_list)
        if not merged:
            continue

        # Verificar inactividad:
        commit = repo.get_commit(branch.commit.sha)
        commit_date = commit.commit.author.date
        if commit_date > cutoff_date:
            continue

        branches_to_delete.append(branch.name)

    if dry_run:
        print("Dry-run: Las siguientes ramas se eliminarían:")
        for b in branches_to_delete:
            print(f"- {b}")
    else:
        for b in branches_to_delete:
            ref = repo.get_git_ref(f"heads/{b}")
            ref.delete()
            print(f"Eliminada la rama: {b}")

if __name__ == "__main__":
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Ejecuta en modo simulación")
    args = parser.parse_args()
    main(args.dry_run)
