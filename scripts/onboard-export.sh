#!/usr/bin/env bash
set -euo pipefail

# Agent Memory System — Onboarding Export
# Imports a structured onboarding export file into the memory repo.
#
# Usage:
#   bash scripts/onboard-export.sh <export-file>
#   bash scripts/onboard-export.sh < export-file
#   <agent output> | bash scripts/onboard-export.sh
#
# The export file should follow the format in scripts/onboard-export-template.md,
# with three sections: "## Identity Profile", "## Session Summary", "## Session Reflection".

usage() {
    echo "Usage: onboard-export.sh [<export-file>]"
    echo ""
    echo "Imports an onboarding export into the memory repo."
    echo ""
    echo "The export file follows the template in scripts/onboard-export-template.md."
    echo "If no file is given, reads from stdin."
    echo ""
    echo "Options:"
    echo "  --dry-run    Show what would be written without making changes"
    echo "  -h, --help   Show this help message"
}

DRY_RUN=false
INPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "Unknown option: $1"; usage; exit 1 ;;
        *)
            if [[ -n "$INPUT_FILE" ]]; then
                echo "Error: multiple input files specified."
                usage; exit 1
            fi
            INPUT_FILE="$1"; shift ;;
    esac
done

# Validate we're in the right directory
if [[ ! -f "README.md" ]] || [[ ! -d "meta" ]]; then
    echo "Error: onboard-export.sh must be run from the root of the agent-memory-seed repository."
    exit 1
fi

# Read input
if [[ -n "$INPUT_FILE" ]]; then
    if [[ ! -f "$INPUT_FILE" ]]; then
        echo "Error: file not found: $INPUT_FILE"
        exit 1
    fi
    INPUT=$(cat "$INPUT_FILE")
else
    if [[ -t 0 ]]; then
        echo "Error: no input file specified and stdin is a terminal."
        echo "Provide an export file as an argument, or pipe input via stdin."
        usage
        exit 1
    fi
    INPUT=$(cat)
fi

# --- Parse sections ---
# Extract content between the three known top-level sections, stripping HTML comments.
# The Identity Profile section may contain its own ## sub-headers (e.g., ## Role and context),
# so we split only on the three known section boundaries.

KNOWN_SECTIONS="^## Identity Profile$|^## Session Summary$|^## Session Reflection$"

extract_section() {
    local section_name="$1"
    local content="$2"
    # Get everything after "## $section_name" until the next known section or end of file.
    # Then strip HTML comments.
    echo "$content" \
        | awk -v sect="## ${section_name}" -v boundary="${KNOWN_SECTIONS}" '
            BEGIN { found=0 }
            $0 == sect { found=1; next }
            found && $0 ~ boundary { found=0 }
            found { print }
        ' \
        | sed '/^<!--/,/^-->$/d' \
        | sed 's/<!--.*-->//g'
}

IDENTITY_CONTENT=$(extract_section "Identity Profile" "$INPUT")
SESSION_SUMMARY=$(extract_section "Session Summary" "$INPUT")
SESSION_REFLECTION=$(extract_section "Session Reflection" "$INPUT")

# Trim leading/trailing blank lines
trim() {
    echo "$1" | sed '/./,$!d' | sed -e :a -e '/^\n*$/{$d;N;ba' -e '}'
}

IDENTITY_CONTENT=$(trim "$IDENTITY_CONTENT")
SESSION_SUMMARY=$(trim "$SESSION_SUMMARY")
SESSION_REFLECTION=$(trim "$SESSION_REFLECTION")

# Validate we got something
if [[ -z "$IDENTITY_CONTENT" ]]; then
    echo "Error: No content found in '## Identity Profile' section."
    echo "Make sure the export file follows the template in scripts/onboard-export-template.md."
    exit 1
fi

if [[ -z "$SESSION_SUMMARY" ]]; then
    echo "[warn] No content found in '## Session Summary' section. Skipping chat record."
fi

# --- Prepare output ---
TODAY=$(date +%Y-%m-%d)
CHAT_DIR="chats/$(date +%Y/%m/%d)/chat-001"

echo "=== Onboarding Export ==="
echo ""

# 1. Write identity/profile.md
PROFILE_FILE="identity/profile.md"
PROFILE_CONTENT="---
source: user-stated
origin_session: ${CHAT_DIR}
created: ${TODAY}
last_verified: ${TODAY}
trust: high
---

${IDENTITY_CONTENT}"

echo "[plan] Write identity profile to: $PROFILE_FILE"

# 2. Write identity/SUMMARY.md
SUMMARY_CONTENT="# Identity Summary

User profile created via onboarding export on ${TODAY}.

See [profile.md](profile.md) for the full portrait."

echo "[plan] Update identity summary: identity/SUMMARY.md"

# 3. Write chat record (if session summary provided)
if [[ -n "$SESSION_SUMMARY" ]]; then
    echo "[plan] Create chat record: ${CHAT_DIR}/"

    CHAT_SUMMARY_CONTENT="---
source: user-stated
origin_session: ${CHAT_DIR}
created: ${TODAY}
last_verified: ${TODAY}
trust: high
---

# Session Summary — Onboarding

${SESSION_SUMMARY}"

    if [[ -n "$SESSION_REFLECTION" ]]; then
        REFLECTION_CONTENT="# Session Reflection — Onboarding

${SESSION_REFLECTION}"
        echo "[plan] Write reflection: ${CHAT_DIR}/reflection.md"
    fi
fi

# 4. Update chats/SUMMARY.md
# Only write when the file is absent or still holds the default placeholder.
# Real history is present when the file exists and does NOT contain the
# "*No conversations yet.*" sentinel that ships with the template repo.
chats_summary_has_history() {
    local f="chats/SUMMARY.md"
    [[ -f "$f" ]] && ! grep -q '\*No conversations yet\.' "$f"
}

CHATS_SUMMARY_CONTENT="# Chat History Summary

## ${TODAY}

- **chat-001** — First session: onboarding. User profile created."

if chats_summary_has_history; then
    echo "[plan] SKIP chats/SUMMARY.md — existing history detected (would overwrite)"
else
    echo "[plan] Update chat summary: chats/SUMMARY.md"
fi
echo ""

# --- Execute or dry-run ---
if [[ "$DRY_RUN" == true ]]; then
    echo "=== Dry run — no files written ==="
    echo ""
    echo "--- ${PROFILE_FILE} ---"
    echo "$PROFILE_CONTENT"
    echo ""
    echo "--- identity/SUMMARY.md ---"
    echo "$SUMMARY_CONTENT"
    if [[ -n "$SESSION_SUMMARY" ]]; then
        echo ""
        echo "--- ${CHAT_DIR}/SUMMARY.md ---"
        echo "$CHAT_SUMMARY_CONTENT"
        if [[ -n "$SESSION_REFLECTION" ]]; then
            echo ""
            echo "--- ${CHAT_DIR}/reflection.md ---"
            echo "$REFLECTION_CONTENT"
        fi
    fi
    echo ""
    if chats_summary_has_history; then
        echo "--- chats/SUMMARY.md ---"
        echo "[skip] Existing chat history detected — chats/SUMMARY.md will NOT be overwritten."
        echo "       To update it, edit the file manually and add the new entry."
    else
        echo "--- chats/SUMMARY.md ---"
        echo "$CHATS_SUMMARY_CONTENT"
    fi
    echo ""
    echo "Run without --dry-run to write these files."
    exit 0
fi

# Write identity profile
echo "$PROFILE_CONTENT" > "$PROFILE_FILE"
echo "[ok] Wrote $PROFILE_FILE"

# Write identity summary
echo "$SUMMARY_CONTENT" > "identity/SUMMARY.md"
echo "[ok] Updated identity/SUMMARY.md"

# Write chat record
if [[ -n "$SESSION_SUMMARY" ]]; then
    mkdir -p "$CHAT_DIR"
    echo "$CHAT_SUMMARY_CONTENT" > "${CHAT_DIR}/SUMMARY.md"
    echo "[ok] Wrote ${CHAT_DIR}/SUMMARY.md"

    if [[ -n "$SESSION_REFLECTION" ]]; then
        echo "$REFLECTION_CONTENT" > "${CHAT_DIR}/reflection.md"
        echo "[ok] Wrote ${CHAT_DIR}/reflection.md"
    fi
fi

# Update chats/SUMMARY.md — only when no real history exists yet
if chats_summary_has_history; then
    echo "[skip] chats/SUMMARY.md already contains session history — not overwritten."
    echo "       Add the new entry manually:"
    echo "         ## ${TODAY}"
    echo "         - **chat-001** — First session: onboarding. User profile created."
else
    echo "$CHATS_SUMMARY_CONTENT" > "chats/SUMMARY.md"
    echo "[ok] Updated chats/SUMMARY.md"
fi

# Stage and commit
echo ""
git add identity/ chats/
GIT_NAME=$(git config user.name 2>/dev/null || true)
GIT_EMAIL=$(git config user.email 2>/dev/null || true)
if [[ -z "$GIT_NAME" ]] || [[ -z "$GIT_EMAIL" ]]; then
    echo "[warn] Git author identity not configured. Files are staged but not committed."
    echo "       Run: git commit -m '[system] Import onboarding profile'"
else
    git commit -m "[system] Import onboarding profile

Onboarding conducted on a read-only platform. Profile and session
record imported via onboard-export.sh on ${TODAY}."
    echo "[ok] Committed onboarding import"
fi

echo ""
echo "=== Export complete ==="
echo ""
echo "Your identity profile is now in the repo. On your next AI session,"
echo "the agent will read it and greet you with what it knows."
