#!/bin/bash
# create-roadmap-issues.sh
# This script creates GitHub issues based on the roadmap items
# Usage: ./create-roadmap-issues.sh [--dry-run]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository configuration
REPO="${GITHUB_REPOSITORY:-fwdslsh/giv}"
DRY_RUN=false

# Parse command line arguments
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}Running in dry-run mode. No issues will be created.${NC}"
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) is required but not installed.${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}You are not authenticated with GitHub CLI.${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${BLUE}Creating roadmap issues for repository: ${REPO}${NC}"

# Function to create milestone
create_milestone() {
    local title="$1"
    local description="$2"
    local due_date="$3"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY RUN] Would create milestone: ${title}${NC}"
        return
    fi
    
    echo -e "${GREEN}Creating milestone: ${title}${NC}"
    if [[ -n "$due_date" ]]; then
        gh api repos/"$REPO"/milestones \
            --method POST \
            --field title="$title" \
            --field description="$description" \
            --field due_on="$due_date" || true
    else
        gh api repos/"$REPO"/milestones \
            --method POST \
            --field title="$title" \
            --field description="$description" || true
    fi
}

# Function to create label
create_label() {
    local name="$1"
    local color="$2"
    local description="$3"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY RUN] Would create label: ${name}${NC}"
        return
    fi
    
    echo -e "${GREEN}Creating label: ${name}${NC}"
    gh api repos/"$REPO"/labels \
        --method POST \
        --field name="$name" \
        --field color="$color" \
        --field description="$description" || true
}

# Calculate dates
three_months=$(date -d '+3 months' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -v +3m +%Y-%m-%dT%H:%M:%SZ)
six_months=$(date -d '+6 months' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -v +6m +%Y-%m-%dT%H:%M:%SZ)
nine_months=$(date -d '+9 months' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -v +9m +%Y-%m-%dT%H:%M:%SZ)
twelve_months=$(date -d '+12 months' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -v +12m +%Y-%m-%dT%H:%M:%SZ)

echo -e "${BLUE}Creating milestones...${NC}"

# Create milestones
create_milestone "v0.7.0 - Documentation & Testing" \
    "High priority documentation improvements and comprehensive testing" \
    "$three_months"

create_milestone "v0.8.0 - Enhanced Content Generation" \
    "Medium priority content generation improvements" \
    "$six_months"

create_milestone "v0.9.0 - Template System & UX" \
    "Template system enhancements and user experience improvements" \
    "$nine_months"

create_milestone "v1.0.0 - Advanced Features" \
    "Advanced features and performance optimizations" \
    "$twelve_months"

create_milestone "Future - Vision Features" \
    "Long-term vision items and experimental features"

echo -e "${BLUE}Creating labels...${NC}"

# Priority labels
create_label "priority: high" "d73a49" "Must be implemented soon"
create_label "priority: medium" "fbca04" "Important for future releases"
create_label "priority: low" "0e8a16" "Nice to have features"
create_label "priority: future" "f9d0c4" "Long-term vision items"

# Category labels
create_label "category: documentation" "5319e7" "Documentation improvements"
create_label "category: testing" "1d76db" "Testing and quality assurance"
create_label "category: content-generation" "ff6b35" "Content generation features"
create_label "category: templates" "e99695" "Template system enhancements"
create_label "category: ui-ux" "7057ff" "User interface and experience"
create_label "category: advanced" "008672" "Advanced features"
create_label "category: performance" "ffd700" "Performance and optimization"
create_label "category: distribution" "8b4513" "Distribution and packaging"

# Type labels
create_label "type: feature" "0e8a16" "New feature"
create_label "type: enhancement" "a2eeef" "Enhancement to existing feature"
create_label "type: research" "d4c5f9" "Research or investigation needed"
create_label "type: bug" "d73a49" "Something isn't working"
create_label "type: question" "cc317c" "Further information is requested"

# Effort labels
create_label "effort: small" "c2e0c6" "1-2 days of work"
create_label "effort: medium" "ffeaa7" "3-7 days of work"
create_label "effort: large" "fab1a0" "1-2 weeks of work"
create_label "effort: epic" "ff7675" "Multiple weeks, needs breaking down"

# Status labels
create_label "status: triage" "e1e4e8" "Needs initial review and categorization"
create_label "roadmap" "1f883d" "Item from the project roadmap"

echo -e "${GREEN}✅ Milestones and labels created successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review the created milestones and labels in GitHub"
echo "2. Use the issue templates to create roadmap issues"
echo "3. Reference the .github/ROADMAP_ISSUES.md file for detailed issue content"
echo "4. Consider creating a GitHub Project to organize the roadmap items"
echo ""
echo -e "${YELLOW}Note: Some milestones or labels may already exist and creation might be skipped.${NC}"

if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YELLOW}This was a dry run. No actual changes were made.${NC}"
    echo "Remove --dry-run to create the milestones and labels."
fi