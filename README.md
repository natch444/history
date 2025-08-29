### Project

This project aims to generate git history.

### Actions

This is the list of all the available action :
- new-branch
- commit
- squash
- merge

#### new-branch
```
# Create branch dev from master
action: new-branch
  base-branch: master
  branch-name: dev
```

#### push

```
action: commit
  author: John Doe
  email: john.doe@sleepz.com
  date: 24/01/2023
  branch: dev
  files:
    - files/web.html
    - files/style.css
```

#### squash

```
# Squash the last 10th commit on branch `dev`
action: squash
  branch: dev
  number: 10
```

#### merge

```
# Merge branch `dev` onto `master`
action: merge
  src-branch: master
  trgt-branch: dev
```
