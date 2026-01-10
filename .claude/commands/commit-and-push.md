---
description: Stage all changes, create a commit with a meaningful message, and push to remote
allowed-tools: Bash(git:*), Bash(rm:*), Bash(pkill:*)
---

Perform these steps:

0. **Cleanup first**: Remove any lighthouse reports or temp files:
   ```bash
   rm -r .lighthouse-reports/ *.report.html 2>/dev/null || true
   pkill -f "python3 -m http.server 8888" 2>/dev/null || true
   ```
1. Run `git status` to see all changes
2. Run `git diff` to understand what changed
3. Stage all changes with `git add .`
4. Create a commit with a clear, concise message that describes what changed and why
5. Pull with rebase (`git pull --rebase`) - sync with any remote changes
6. Push to the current branch

If the user provided additional context: $ARGUMENTS
Use that context to inform the commit message.

Commit message format:
- Use conventional commits style (feat:, fix:, docs:, refactor:, etc.)
- Keep the first line under 30 characters