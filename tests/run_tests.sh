#!/bin/bash

# YouTube RAG System - Test Runner
# Run different types of tests with various options

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed"
    echo "Install with: pip install pytest pytest-cov pytest-asyncio"
    exit 1
fi

# Main menu
show_menu() {
    echo ""
    print_header "YouTube RAG System - Test Runner"
    echo ""
    echo "Select test type:"
    echo ""
    echo "  1) Run all tests"
    echo "  2) Run unit tests only"
    echo "  3) Run integration tests only"
    echo "  4) Run tests with coverage"
    echo "  5) Run specific test file"
    echo "  6) Run tests in watch mode"
    echo "  7) Run fast tests (skip slow)"
    echo "  8) Generate coverage report"
    echo "  9) Run with detailed output"
    echo "  0) Exit"
    echo ""
}

# Test runners
run_all_tests() {
    print_header "Running All Tests"
    pytest tests/ -v
}

run_unit_tests() {
    print_header "Running Unit Tests"
    pytest tests/ -v -m "not integration and not slow"
}

run_integration_tests() {
    print_header "Running Integration Tests"
    print_info "Note: This requires services to be running (ChromaDB, Ollama, etc.)"
    pytest tests/ -v -m integration
}

run_with_coverage() {
    print_header "Running Tests with Coverage"
    pytest tests/ -v --cov=app --cov-report=term --cov-report=html
    print_success "Coverage report generated at: htmlcov/index.html"
}

run_specific_file() {
    echo ""
    echo "Available test files:"
    ls -1 tests/test_*.py 2>/dev/null | nl
    echo ""
    read -p "Enter file number: " file_num
    
    file=$(ls -1 tests/test_*.py 2>/dev/null | sed -n "${file_num}p")
    
    if [ -n "$file" ]; then
        print_header "Running $file"
        pytest "$file" -v
    else
        print_error "Invalid selection"
    fi
}

run_watch_mode() {
    print_header "Running Tests in Watch Mode"
    print_info "Tests will re-run when files change"
    print_info "Press Ctrl+C to stop"
    
    if command -v pytest-watch &> /dev/null; then
        ptw tests/ -- -v
    else
        print_error "pytest-watch not installed"
        echo "Install with: pip install pytest-watch"
    fi
}

run_fast_tests() {
    print_header "Running Fast Tests (Skipping Slow Tests)"
    pytest tests/ -v -m "not slow"
}

generate_coverage() {
    print_header "Generating Coverage Report"
    pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
    print_success "HTML report: htmlcov/index.html"
    
    # Try to open report
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open htmlcov/index.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open htmlcov/index.html 2>/dev/null || echo "Open htmlcov/index.html in your browser"
    fi
}

run_detailed() {
    print_header "Running Tests with Detailed Output"
    pytest tests/ -vv --tb=long -s
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice [0-9]: " choice
    
    case $choice in
        1)
            run_all_tests
            ;;
        2)
            run_unit_tests
            ;;
        3)
            run_integration_tests
            ;;
        4)
            run_with_coverage
            ;;
        5)
            run_specific_file
            ;;
        6)
            run_watch_mode
            ;;
        7)
            run_fast_tests
            ;;
        8)
            generate_coverage
            ;;
        9)
            run_detailed
            ;;
        0)
            echo ""
            print_info "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid option. Please try again."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done