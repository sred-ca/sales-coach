---
name: git-commit-push
description: Auto-commit all changes and push to GitHub (sred-ca/sales-coach). Stages tracked files, generates a commit message from the diff, and pushes to origin/main.
user_invocable: true
command: push
---

# Git Commit & Push

Automatically commit all changes in the sales-coach project and push to GitHub.

## Trigger

User says: `/push`, "push to github", "commit and push", "save to git", "push my changes"

## Steps

1. **Check for changes** — Run `git status` in the project root (`/Users/judebrown/Documents/Claude/sales-coach/`). If no changes exist, tell the user "Nothing to commit — working tree clean." and stop.

2. **Stage all changes** — Run `git add -A` to stage all new, modified, and deleted files. The `.gitignore` already excludes sensitive files (outputs/, evan-personal-goals.md, evan-profile.md, .DS_Store, __pycache__).

3. **Generate commit message** — Run `git diff --cached --stat` and `git diff --cached` to see what changed. Write a concise commit message:
   - First line: imperative mood, under 72 chars (e.g., "Update VAPI prompt with new coaching focus areas")
   - If multiple unrelated changes, summarize the most significant one in the first line
   - Add a blank line and bullet points for additional changes if needed
   - Always append: `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`

4. **Commit** — Run `git commit` with the generated message using a heredoc:
   ```bash
   git commit -m "$(cat <<'EOF'
   <commit message here>

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   EOF
   )"
   ```

5. **Push** — Run `git push origin main`. If it fails (e.g., remote has new commits), run `git pull --rebase origin main` first, then push again.

6. **Report** — Tell the user what was committed and pushed. Include the commit hash and a one-line summary.

## Important

- The remote is `git@github.com:sred-ca/sales-coach.git` (SSH)
- Always push to `main` branch
- Never force push
- The `.gitignore` excludes: outputs/, evan-personal-goals.md, evan-profile.md, archive/, .DS_Store, __pycache__/, *.pyc, .claude/settings.local.json
- `gh` CLI is at `~/.local/bin/gh` if needed for GitHub API operations
- Do NOT ask for confirmation — auto-commit and push immediately (user chose this preference)
