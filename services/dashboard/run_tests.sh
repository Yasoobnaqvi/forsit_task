#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create tests directory if it doesn't exist
mkdir -p tests

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed.${NC}"
    echo "Installing test dependencies..."
    pip install -r requirements.txt
fi

# Print header
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}Running E-commerce Admin API Test Suite${NC}"
echo -e "${GREEN}=======================================${NC}"

# Function to run tests and check exit status
run_tests() {
    echo -e "${YELLOW}Running $1...${NC}"
    $2
    exit_status=$?
    
    if [ $exit_status -eq 0 ]; then
        echo -e "${GREEN}$1 passed!${NC}"
    else
        echo -e "${RED}$1 failed with exit status $exit_status${NC}"
        failed=1
    fi
    echo
}

# Initialize failure flag
failed=0

# Run unit/integration tests
run_tests "API Tests" "pytest tests/test_api.py -v"

# Run seed data tests
run_tests "Seed Data Tests" "pytest tests/test_seed_data.py -v"

# Summary
echo -e "${GREEN}=======================================${NC}"
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
else
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
fi
echo -e "${GREEN}=======================================${NC}"

echo -e "\n${YELLOW}Note: To run load tests, use:${NC}"
echo -e "locust -f tests/locustfile.py"
echo -e "Then open http://localhost:8089 in your browser\n"

exit $failed 