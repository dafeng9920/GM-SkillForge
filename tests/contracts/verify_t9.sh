#!/bin/bash
# T9 Delivery Verification Script
#
# Usage: ./tests/contracts/verify_t9.sh
#
# This script verifies T9 deliverables:
# 1. Schema files exist and are valid JSON
# 2. Python modules exist and can be imported
# 3. Sample files exist and are valid
# 4. Evidence levels are correctly defined (E1-E5)
# 5. Coverage statement structure is correct

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "T9 Delivery Verification"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
PASSED=0
FAILED=0

# Helper function
check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

# ============================================================================
# 1. Schema Files
# ============================================================================
echo "1. Checking schema files..."

SCHEMA_FILES=(
    "skillforge/src/contracts/coverage_statement.schema.json"
    "skillforge/src/contracts/evidence_level.schema.json"
)

for file in "${SCHEMA_FILES[@]}"; do
    full_path="$PROJECT_ROOT/$file"
    if [ -f "$full_path" ]; then
        if python -c "import json; json.load(open(r'$full_path'))" 2>/dev/null; then
            check_pass "$file exists and is valid JSON"
        else
            check_fail "$file is not valid JSON"
        fi
    else
        check_fail "$file does not exist"
    fi
done

echo ""

# ============================================================================
# 2. Python Modules
# ============================================================================
echo "2. Checking Python modules..."

PYTHON_MODULES=(
    "skillforge.src.contracts.coverage_statement"
    "skillforge.src.contracts.evidence_level"
)

for module in "${PYTHON_MODULES[@]}"; do
    if python -c "import $module" 2>/dev/null; then
        check_pass "$module can be imported"
    else
        check_fail "$module cannot be imported"
    fi
done

echo ""

# ============================================================================
# 3. Sample Files
# ============================================================================
echo "3. Checking sample files..."

SAMPLE_FILES=(
    "tests/contracts/T9/coverage_statement.sample.json"
    "tests/contracts/T9/evidence_level.json"
)

for file in "${SAMPLE_FILES[@]}"; do
    full_path="$PROJECT_ROOT/$file"
    if [ -f "$full_path" ]; then
        if python -c "import json; json.load(open(r'$full_path'))" 2>/dev/null; then
            check_pass "$file exists and is valid JSON"
        else
            check_fail "$file is not valid JSON"
        fi
    else
        check_fail "$file does not exist"
    fi
done

echo ""

# ============================================================================
# 4. Evidence Level Definitions
# ============================================================================
echo "4. Checking evidence level definitions (E1-E5)..."

EVIDENCE_FILE="$PROJECT_ROOT/tests/contracts/T9/evidence_level.json"

if [ -f "$EVIDENCE_FILE" ]; then
    # Count levels
    LEVEL_COUNT=$(python -c "
import json
data = json.load(open(r'$EVIDENCE_FILE'))
print(len(data.get('levels', [])))
")

    if [ "$LEVEL_COUNT" -eq 5 ]; then
        check_pass "Exactly 5 evidence levels defined (E1-E5)"
    else
        check_fail "Expected 5 levels, found $LEVEL_COUNT"
    fi

    # Check level IDs
    LEVEL_IDS=$(python -c "
import json
data = json.load(open(r'$EVIDENCE_FILE'))
print(','.join(sorted([l['level_id'] for l in data.get('levels', [])])))
")

    if [ "$LEVEL_IDS" = "E1,E2,E3,E4,E5" ]; then
        check_pass "All evidence level IDs correct (E1-E5)"
    else
        check_fail "Evidence level IDs incorrect: $LEVEL_IDS"
    fi

    # Check strength ordering
    STRENGTHS=$(python -c "
import json
data = json.load(open(r'$EVIDENCE_FILE'))
print(','.join([str(l['strength']) for l in data.get('levels', [])]))
")

    if [ "$STRENGTHS" = "1,2,3,4,5" ]; then
        check_pass "Evidence levels correctly ordered by strength (1-5)"
    else
        check_fail "Strength ordering incorrect: $STRENGTHS"
    fi
else
    check_fail "evidence_level.json not found"
fi

echo ""

# ============================================================================
# 5. Coverage Statement Structure
# ============================================================================
echo "5. Checking coverage statement structure..."

SAMPLE_FILE="$PROJECT_ROOT/tests/contracts/T9/coverage_statement.sample.json"

if [ -f "$SAMPLE_FILE" ]; then
    # Check required fields
    REQUIRED_FIELDS=(
        "statement_id"
        "artifact_id"
        "artifact_type"
        "declared_at"
        "declared_by"
        "covered_items"
        "uncovered_items"
        "exclusions"
        "coverage_summary"
    )

    MISSING=0
    for field in "${REQUIRED_FIELDS[@]}"; do
        if ! python -c "
import json
data = json.load(open(r'$SAMPLE_FILE'))
if '$field' not in data:
    exit(1)
" 2>/dev/null; then
            check_fail "Missing required field: $field"
            ((MISSING++))
        fi
    done

    if [ $MISSING -eq 0 ]; then
        check_pass "All required fields present in coverage_statement.sample.json"
    fi

    # Check evidence levels in covered items
    VALID_LEVELS=$(python -c "
import json
data = json.load(open(r'$SAMPLE_FILE'))
valid = True
for item in data.get('covered_items', []):
    if item.get('evidence_level') not in ['E1', 'E2', 'E3', 'E4', 'E5']:
        valid = False
        break
print(int(valid))
")

    if [ "$VALID_LEVELS" -eq 1 ]; then
        check_pass "All covered items have valid evidence levels"
    else
        check_fail "Some covered items have invalid evidence levels"
    fi
fi

echo ""

# ============================================================================
# 6. Test Suite
# ============================================================================
echo "6. Running test suite..."

if python -m pytest tests/contracts/test_t9_coverage.py -v --tb=short 2>&1 | grep -q "passed"; then
    TOTAL=$(python -m pytest tests/contracts/test_t9_coverage.py -v 2>&1 | grep -o "[0-9]* passed" | grep -o "[0-9]*")
    check_pass "Test suite passed ($TOTAL tests)"
else
    check_fail "Test suite failed or not found"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ T9 DELIVERY VERIFIED${NC}"
    exit 0
else
    echo -e "${RED}✗ T9 DELIVERY HAS ISSUES${NC}"
    exit 1
fi
