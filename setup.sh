#!/usr/bin/env bash
set -euo pipefail

# Agent Memory System — Post-clone setup script
# Personalizes the template repo for a new user.

INTERACTIVE=true
REMOTE=""

usage() {
    echo "Usage: setup.sh [OPTIONS]"
    echo ""
    echo "Personalizes the agent-memory-seed template after cloning."
    echo ""
    echo "Options:"
    echo "  --non-interactive    Skip prompts, use defaults"
    echo "  --remote <url>       Set the git remote origin"
    echo "  -h, --help           Show this help message"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --non-interactive) INTERACTIVE=false; shift ;;
        --remote)
            if [[ $# -lt 2 ]] || [[ -z "${2-}" ]]; then
                echo "Error: --remote requires a URL argument."
                usage; exit 1
            fi
            REMOTE="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Validate we're in the right directory
if [[ ! -f "README.md" ]] || [[ ! -d "meta" ]]; then
    echo "Error: setup.sh must be run from the root of the agent-memory-seed repository."
    exit 1
fi

echo "=== Agent Memory System Setup ==="
echo ""

# 1. Set today's date in CHANGELOG.md
TODAY=$(date +%Y-%m-%d)
if grep -q '\[YYYY-MM-DD\] Initial system creation' CHANGELOG.md 2>/dev/null; then
    sed -i.bak "s/\[YYYY-MM-DD\] Initial system creation/[$TODAY] Initial system creation/" CHANGELOG.md
    rm -f CHANGELOG.md.bak
    echo "[ok] Set creation date to $TODAY in CHANGELOG.md"
else
    echo "[skip] CHANGELOG.md creation date already set"
fi

# 2. Initialize git if needed
if [[ ! -d ".git" ]]; then
    git init
    echo "[ok] Initialized git repository"
else
    echo "[skip] Git repository already initialized"
fi

# 3. Set remote if provided or prompt
if [[ -n "$REMOTE" ]]; then
    git remote remove origin 2>/dev/null || true
    git remote add origin "$REMOTE"
    echo "[ok] Set remote origin to $REMOTE"
elif [[ "$INTERACTIVE" == true ]]; then
    echo ""
    read -rp "Git remote URL (leave blank to skip): " REMOTE_INPUT
    if [[ -n "$REMOTE_INPUT" ]]; then
        git remote remove origin 2>/dev/null || true
        git remote add origin "$REMOTE_INPUT"
        echo "[ok] Set remote origin to $REMOTE_INPUT"
    else
        echo "[skip] No remote set"
    fi
fi

# 4. Make initial commit if no commits exist
if ! git rev-parse HEAD >/dev/null 2>&1; then
    # Check git author identity before committing
    GIT_NAME=$(git config user.name 2>/dev/null || true)
    GIT_EMAIL=$(git config user.email 2>/dev/null || true)
    if [[ -z "$GIT_NAME" ]] || [[ -z "$GIT_EMAIL" ]]; then
        echo "[warn] Git author identity not configured (user.name / user.email unset)."
        echo "       Skipping initial commit. Run these commands to configure, then commit manually:"
        echo "         git config user.name  \"Your Name\""
        echo "         git config user.email \"you@example.com\""
        echo "         git add -A && git commit -m '[system] Initialize agent memory system'"
    else
        git add -A
        git commit -m "[system] Initialize agent memory system

Created from agent-memory-seed template on $TODAY."
        echo "[ok] Created initial commit"
    fi
else
    echo "[skip] Repository already has commits"
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Read QUICKSTART.md for platform-specific setup instructions."
echo "  2. Start a session with your AI — it will run the onboarding skill"
echo "     and ask you a few questions to build your initial profile."
echo "  3. Your memory system grows from there."
echo ""
echo "For the full architecture, see README.md."
