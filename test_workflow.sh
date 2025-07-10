#!/bin/bash

# Test script to validate workflow components locally
set -e

echo "Testing workflow components..."

# Test both directories
for dir in "k8s-analyzer" "k8s-reporter"; do
    echo "Testing $dir..."
    
    # Check if directory exists
    if [ ! -d "$dir" ]; then
        echo "Error: Directory $dir does not exist"
        exit 1
    fi
    
    cd "$dir"
    
    # Check if pyproject.toml exists
    if [ ! -f "pyproject.toml" ]; then
        echo "Error: pyproject.toml not found in $dir"
        exit 1
    fi
    
    # Check if tests directory exists
    if [ ! -d "tests" ]; then
        echo "Error: tests directory not found in $dir"
        exit 1
    fi
    
    # Check if src directory exists
    if [ ! -d "src" ]; then
        echo "Error: src directory not found in $dir"
        exit 1
    fi
    
    echo "✓ $dir structure is valid"
    
    cd ..
done

echo "All checks passed! Workflow structure is valid."
