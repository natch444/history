import os
import datetime
from pathlib import Path
import pygit2
import shutil

# Author : natch
# Assistant : Lumo by Proton

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def iso_to_timestamp(iso_str: str) -> int:
    """Convert an ISO‑8601 string to a POSIX timestamp (seconds)."""
    dt = datetime.datetime.fromisoformat(iso_str)
    return int(dt.timestamp())


def signature(name: str, email: str, when: int = None) -> pygit2.Signature:
    """
    Build a pygit2.Signature.
    If ``when`` is omitted the current time is used.
    """
    if when is None:
        when = int(datetime.datetime.now().timestamp())
    else:
        when = iso_to_timestamp(when)
    return pygit2.Signature(name=name, email=email, time=when, offset=0)

def copy_file(source_path, dest_path):
    try:
        shutil.copy(source_path, dest_path)
        print(f"File copied from {source_path} to {dest_path}")
    except Exception as e:
        print(f"Error: {e}")

# ----------------------------------------------------------------------
# Initialise or open a repository
# ----------------------------------------------------------------------
def get_repo(repo_path: Path) -> pygit2.Repository:
    """
    Return a Repository object.
    - If ``repo_path`` exists and contains a .git directory → open it.
    - Otherwise create a brand‑new repo at that location.
    """
    if (repo_path / ".git").exists():
        print(f"Opening existing repository at {repo_path}")
        return pygit2.Repository(str(repo_path))
    else:
        print(f"Initialising new repository at {repo_path}")
        repo_path.mkdir(parents=True, exist_ok=True)
        return pygit2.init_repository(str(repo_path), bare=False)


# ----------------------------------------------------------------------
# Branch creation helpers
# ----------------------------------------------------------------------
def create_branch(repo: pygit2.Repository, name: str, start_point: str = "HEAD"):
    """
    Create a new branch ``name`` that points at ``start_point`` (a ref name or SHA).
    Returns the newly created Branch object.
    """
    target = repo.revparse_single(start_point).oid
    branch = repo.create_branch(name, repo.get(target))
    print(f"Created branch '{name}' at {target}")
    return branch


def checkout_branch(repo: pygit2.Repository, branch_name: str):
    """
    Checkout ``branch_name`` (updates HEAD and the working directory).
    """
    ref = f"refs/heads/{branch_name}"
    branches_list = list(repo.branches)
    if branch_name not in branches_list:
        print("Branch name not found! Abort...")
        return
    repo.checkout(ref)
    print(f"Checked out branch '{branch_name}'")


# ----------------------------------------------------------------------
# Staging & committing
# ----------------------------------------------------------------------
def write_file(repo_path: Path, relative_path: str, content: str):
    """
    Write ``content`` to ``repo_path/relative_path`` (creates directories as needed).
    """
    full_path = repo_path / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)
    print(f"Wrote file {relative_path}")


def stage_files(repo: pygit2.Repository, paths):
    """
    Add ``paths`` (list of strings relative to the repo root) to the index.
    """
    index = repo.index
    for p in paths:
        index.add(p) # adds or updates the entry
        index.write()
    print(f"Staged {len(paths)} file(s): {', '.join(paths)}")

def initial_commit(
        repo: pygit2.Repository,
        message: str,
        author_name: str,
        author_email: str,
        committer_name: str = None,
        committer_email: str = None,
        author_date_iso: str = None,
        committer_date_iso: str = None,
        ):
    """
    Create initial_commit for an new repo
    """
    index = repo.index
    index.add_all()
    index.write()
    ref = "HEAD"
    author = None
    committer = None
    if author_name is not None and author_email is not None:
        author = signature(author_name, author_email, author_date_iso)
    if committer_name is not None and committer_email is not None:
        committer = signature(committer_name, committer_email, committer_date_iso)
    tree = index.write_tree()
    parents = []

    # Assuming that at least one of these two is not None
    if author is None:
        author = committer
    else:
        committer = author
    repo.create_commit(ref, author, committer, message, tree, parents) 


def commit_changes(
        repo: pygit2.Repository,
        message: str,
        author_name: str,
        author_email: str,
        committer_name: str = None,
        committer_email: str = None,
        author_date_iso: str = None,
        committer_date_iso: str = None,
        ):
    """
    Create a commit from the current index.
    You can pass explicit ISO‑8601 timestamps for author/committer dates.
    """
    # Resolve the current tree from the index
    tree = repo.index.write_tree()
    # Determine parents – usually the current HEAD (empty repo has none)
    parents = []
    try:
        if repo.head.target != None:
            parents.append(repo.head.target)
    except ValueError:
        # No HEAD yet (first commit)
        pass

    author_sig = signature(author_name, author_email, when=author_date_iso)
    committer_sig = signature(
        committer_name or author_name,
        committer_email or author_email,
        when=committer_date_iso or author_date_iso,
        )

    # Finally create the commit
    commit_oid = repo.create_commit(
            "HEAD", # update HEAD to point at the new commit
            author_sig,
            committer_sig,
            message,
            tree,
            parents,
            )
    print(f"New commit {commit_oid} – {message}")
    return commit_oid



def merge_branches(
            repo: pygit2.Repository,
            source: str,
            target: str,
            squash: bool = False,
            author_name: str = "John Dodo",
            author_email: str = "john@dodo.zzz",
            author_date_iso: str = None
            ):
    """
    Merge ``source`` into ``target``.
    If ``squash`` is True we perform a squash merge (single commit on target).
    """
    # Checkout the target branch first
    checkout_branch(repo, target)

    # Resolve OIDs
    source_oid = repo.revparse_single(source).oid
    target_oid = repo.head.target

    # Perform the merge analysis
    merge_result, _ = repo.merge_analysis(source_oid)
    if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
        print(f"{target} is already up‑to‑date with {source}. Nothing to do.")
        return

    # Do the actual merge
    repo.merge(source_oid)

    # Check for conflicts
    if repo.index.conflicts is not None:
        print("Conflicts detected! Aborting merge.")
        for conflict in repo.index.conflicts:
            print(f" - {conflict[0].path}")
        repo.state_cleanup()
        return

    # At this point the index contains the merged result.
    if squash:
        # Squash: create a single commit without a merge commit.
        # We reuse the index tree but set the parent to the current target only.
        tree = repo.index.write_tree()
        author = signature(
                        author_name,
                        author_email,
                        author_date_iso)
        committer = author

        msg = f"Squash merge {source} into {target}"
        squash_oid = repo.create_commit(
                "HEAD",
                author,
                committer,
                msg,
                tree,
                [target_oid],
                )
        print(f"Squash‑merged {source} -> {target} as {squash_oid}")
    else:
        # Normal merge commit (two parents)
        tree = repo.index.write_tree()

        author = signature(
                        author_name,
                        author_email,
                        author_date_iso)
        committer = author

        msg = f"Merge branch '{source}' into '{target}'"
        merge_oid = repo.create_commit(
                "HEAD",
                author,
                committer,
                msg,
                tree,
                [target_oid, source_oid],
                )
        print(f"Merge commit {merge_oid}")

        # Clean up the merge state
        repo.state_cleanup()
