---
description: Stage all changes, create a commit with a meaningful message, and push to remote
allowed-tools: Bash(git:*)
---

Perform these steps:

1. Run `git status` to see all changes
2. Run `git diff` to understand what changed
3. Stage all changes with `git add .`
4. Create a commit with a clear, concise message that describes what changed and why
5. Pull with rebase (`git pull --rebase`) - the remote may be ahead due to GitHub workflow
6. Push to the current branch

If the user provided additional context: $ARGUMENTS
Use that context to inform the commit message.

Commit message format:
- Use conventional commits style (feat:, fix:, docs:, refactor:, etc.)
- Keep the first line under 30 characters