#!/bin/bash

# Test crash endpoints for all services

echo "=== Testing Crash Endpoints for Sentry Demo ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local service=$1
    local endpoint=$2
    local url=$3
    
    echo -e "${YELLOW}Testing $service - $endpoint${NC}"
    
    # Use curl with error handling
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [[ "$response" == "500" ]] || [[ "$response" == "504" ]]; then
        echo -e "${GREEN}✓ $endpoint returned expected error ($response)${NC}"
    elif [[ "$response" == "200" ]]; then
        echo -e "${GREEN}✓ $endpoint returned success (200)${NC}"
    elif [[ "$response" == "000" ]]; then
        echo -e "${RED}✗ $endpoint - Service not reachable${NC}"
    else
        echo -e "${YELLOW}⚠ $endpoint returned unexpected status: $response${NC}"
    fi
    echo ""
}

echo "=== Python Game Engine Service (Port 8082) ==="
test_endpoint "Game Engine" "/debug/crash" "http://localhost:8082/debug/crash"
test_endpoint "Game Engine" "/debug/error/value" "http://localhost:8082/debug/error/value"
test_endpoint "Game Engine" "/debug/error/type" "http://localhost:8082/debug/error/type"
test_endpoint "Game Engine" "/debug/memory-leak" "http://localhost:8082/debug/memory-leak"
test_endpoint "Game Engine" "/debug/async-error" "http://localhost:8082/debug/async-error"

echo "=== Python Analytics Service (Port 8084) ==="
test_endpoint "Analytics" "/api/debug/crash" "http://localhost:8084/api/debug/crash"
test_endpoint "Analytics" "/api/debug/validation-error" "http://localhost:8084/api/debug/validation-error"
test_endpoint "Analytics" "/api/debug/database-error" "http://localhost:8084/api/debug/database-error"
test_endpoint "Analytics" "/api/debug/timeout" "http://localhost:8084/api/debug/timeout"
test_endpoint "Analytics" "/api/debug/memory-spike" "http://localhost:8084/api/debug/memory-spike"

echo "=== Node.js Payment Service (Port 8083) ==="
test_endpoint "Payment" "/debug/crash" "http://localhost:8083/debug/crash"
test_endpoint "Payment" "/debug/promise-rejection" "http://localhost:8083/debug/promise-rejection"
test_endpoint "Payment" "/debug/memory-leak" "http://localhost:8083/debug/memory-leak"
test_endpoint "Payment" "/debug/event-loop-block" "http://localhost:8083/debug/event-loop-block"
test_endpoint "Payment" "/debug/stack-overflow" "http://localhost:8083/debug/stack-overflow"

echo "=== Go API Gateway (Port 8080) ==="
test_endpoint "API Gateway" "/api/v1/debug/panic/panic-test" "http://localhost:8080/api/v1/debug/panic/panic-test"

echo ""
echo "=== Test Complete ==="
echo "Check your Sentry dashboard for the captured errors!"
echo ""
echo "Note: Some endpoints return 200 OK because they handle errors gracefully."
echo "The errors are still sent to Sentry even with 200 responses."