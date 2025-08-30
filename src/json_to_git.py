import json
from history import *



# TODO: Handle all actions


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
    length = len(action["src"])
    dst_folder = action["dst-folder"]
    for i in range(length):
        copy_file(action["src"][i], f"{dst_folder}/{action["dst"][i]}")

def read_json(path_to_file):
    print(f"Start parsing: {path_to_file}")
    with open(path_to_file, 'r') as file: 
        data = json.load(file)
        repo = load_config(data["config"])

        for action in data["actions"]:
            match action["action"]:
                case "copy":
                    print("copy")
                    action_copy(action)
                case "commit":
                    print("commit")
                case _:
                    print("match nothing")
                    
