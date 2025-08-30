### Project

This project aims to generate git history based on json file.

*Note: You can find a `json` example file in the `example/`
directory.*

### Config

Your `json` file must start with a `config` object as follow :
```json
"config" : { 
    "path": "test",
    "author": "John Doe",
    "email": "john@doe.com",
    "message": "Initial commit",
    "date": "2020-02-22T23:42:00"
  }
```
- `path`: The path where the `.git` folder can be found or
should be created.
In case of a new repository, you **can** provide following the
arguments:
- `author`
- `email`
- `message`
- `date`

If not provided default value will be used.

### Actions

Then your `json` file must contains a *list* of action.

This is the list of all the available action:
- new-branch
- checkout
- commit
- squash (*pending...*)
- merge
- copy

#### new-branch
Example: Create branch dev from master
```json
{
  "action": "new-branch",
  "base-branch": "master",
  "branch-name": "dev"
}
```

#### checkout
Example: Checkout to a target branch
```json
{
  "action": "checkout",
  "branch-name": "dev"
}
```

#### commit
Example: Commit changes from files list
```json
{
  "action": "commit",
  "branch": "master",
  "author": "John Doe",
  "email": "john@doe.com",
  "message": "Add README.md & requirement.txt",
  "date": "2020-02-22T23:42:00",
  "files": [
    "README.md",
    "requirement.txt"
  ]
}
```

#### squash
*pending...*
```
# Squash the last 10th commit on branch `dev`
action: squash
  branch: dev
  number: 10
```

#### merge
Example: Merge branch `dev` onto `master`
```json
{
  "action": "merge",
  "source-branch": "dev",
  "target-branch": "master",
  "squash" : false,
  "author": "John Doe",
  "email": "john@doe.com",
  "date": "2020-02-22T23:42:00"
}
```

#### copy
Example: copy folder & file list from src to dst path
```json
{
  "action": "copy",
  "dst-folder": "test",
  "src": [
    "/tmp/README.md",
    "/tmp/requirement.txt"
  ],
  "dst": [
    "README.md",
    "requirement.txt"
  ]
}
```
