#!/bin/bash
# Quick Test Script for Paper2Sim Phase 1
# 快速测试 Paper2Sim Phase 1 能力

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Paper2Sim Phase 1 Quick Test${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"

echo -e "${YELLOW}Project root: ${PROJECT_ROOT}${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "❌ Error: Cannot find project root. Please run from the tests directory."
    exit 1
fi

cd "$PROJECT_ROOT"

# Function to run a test
run_test() {
    local test_name=$1
    local test_cmd=$2
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Running: ${test_name}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if eval "$test_cmd"; then
        echo ""
        echo -e "${GREEN}✅ ${test_name}: PASSED${NC}"
        return 0
    else
        echo ""
        echo -e "${YELLOW}⚠️  ${test_name}: FAILED${NC}"
        return 1
    fi
}

# Default to basic test if no argument provided
TEST_LEVEL=${1:-basic}

case "$TEST_LEVEL" in
    basic)
        echo "Running basic validation (no paper required)..."
        echo ""
        run_test "Basic Validation" \
            "python paper2sim/tests/test_phase1.py --test-suite basic"
        ;;
    
    example)
        echo "Running test with example paper..."
        echo ""
        run_test "Example Paper Test" \
            "python paper2sim/tests/test_phase1.py --paper paper2sim/tests/example_paper_simple.md --output ./test_phase1_output_example"
        ;;
    
    full)
        echo "Running full test suite..."
        echo ""
        
        # Run basic test
        run_test "Basic Validation" \
            "python paper2sim/tests/test_phase1.py --test-suite basic"
        
        echo ""
        
        # Run example paper test
        run_test "Example Paper Test" \
            "python paper2sim/tests/test_phase1.py --paper paper2sim/tests/example_paper_simple.md --output ./test_phase1_output_example"
        ;;
    
    *)
        echo "Usage: $0 [basic|example|full]"
        echo ""
        echo "Options:"
        echo "  basic   - Run basic validation (no paper required)"
        echo "  example - Test with provided example paper"
        echo "  full    - Run all tests"
        echo ""
        echo "Default: basic"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Test completed!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "For detailed usage, see: paper2sim/tests/TEST_PHASE1_USAGE.md"
echo ""
