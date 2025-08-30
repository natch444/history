import json
from history import *



def load_config(config):
    """
    In case of new repo, assuming author == committer
    """
    print("config")
    path = Path(config["path"]) if config["path"] else Path("./default_repo")
    repo = get_repo(path)

    if repo.is_empty:
        author = config["author"] or "John Dodo"
        email = config["email"] or "john@dodo.com"
        message = config["message"] or "Initial commit (default message)"
        date = config["date"]
        initial_commit(repo, message, author, email, date)

    return repo
    
def action_copy(action):
    """
    Copy files from source to destination
    """
    length = len(action["src"])
    dst_folder = action["dst-folder"]
    for i in range(length):
        copy_file(action["src"][i], f"{dst_folder}/{action["dst"][i]}")

def action_commit(repo, action):
    """
    Stage and commit files at once
    """
    # Ensure that we are on the right branch
    if action["branch"] :
        checkout_branch(repo, action["branch"])

    if len(action["files"]) == 0:
        print("Must have files to stage")
        exit(1)

    stage_files(repo, action["files"])

    commit_changes(
            repo,
            message=action["message"],
            author_name=action["author"],
            author_email=action["email"],
            author_date_iso=action["date"],
            )
    
def action_new_branch(repo, action):
    """
    Create a new branch from base branch
    """
    if action["base-branch"]:
        checkout_branch(repo, action["base-branch"])
    create_branch(repo, action["branch-name"])

def action_checkout(repo, action):
    """
    Checkout on branch name
    """
    checkout_branch(repo, action["branch-name"])

def action_merge(repo, action):
    """
    Merge source into target branch
    """
    merge_branches(
            repo,
            source=action["source-branch"],
            target=action["target-branch"],
            squash=action["squash"],
            author_name=action["author"],
            author_email=action["email"],
            author_date_iso=action["date"])

# TODO: Implements : 
# - squash ?

def read_json(path_to_file):
    print(f"Start parsing: {path_to_file}")
    with open(path_to_file, 'r') as file: 
        data = json.load(file)
        repo = load_config(data["config"])

        for action in data["actions"]:
            match action["action"]:
                case "copy":
                    action_copy(action)
                case "commit":
                    action_commit(repo, action)
                case "new-branch":
                    action_new_branch(repo, action)
                case "checkout":
                    action_checkout(repo, action)
                case "merge":
                    action_merge(repo, action)
                case _:
                    print("unrecognized option")
                    
