#!/bin/bash
# Combines prompt_base.md with a workflow description and runs Claude Code
# to autonomously generate and test protocol files in the simulation.
#
# Usage:
#   ./run_agent.sh <path-to-workflow-description>
#   ./run_agent.sh projects/prism/prompt_workflow.md
#
# The workflow description file should contain a "# Workflow" section
# with high-level experiment steps. See projects/prism/prompt_workflow.md
# for an example.

set -e

if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 <path-to-workflow-description>"
    echo ""
    echo "Combines projects/prism/prompt_base.md with the given workflow"
    echo "description, then runs Claude Code to generate and test protocol"
    echo "files in the Isaac Sim simulation."
    echo ""
    echo "Example:"
    echo "  $0 projects/prism/prompt_workflow.md"
    exit 1
fi

WORKFLOW_FILE="$1"
PROMPT_BASE="projects/prism/prompt_base.md"
PROMPT_OUTPUT="projects/prism/prompt.md"

if [ ! -f "$PROMPT_BASE" ]; then
    echo "Error: prompt_base.md not found at $PROMPT_BASE"
    exit 1
fi

if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "Error: Workflow description not found at $WORKFLOW_FILE"
    exit 1
fi

# Combine base prompt with workflow description
cat "$PROMPT_BASE" > "$PROMPT_OUTPUT"
echo "" >> "$PROMPT_OUTPUT"
cat "$WORKFLOW_FILE" >> "$PROMPT_OUTPUT"

echo "Combined prompt written to $PROMPT_OUTPUT"
echo "Launching Claude Code..."

claude -p "$PROMPT_OUTPUT"
