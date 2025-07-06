#!/bin/bash

echo "🧪 Testing Sentry Error Tracking..."
echo ""
echo "This script will trigger a test error in the frontend."
echo "Check your Sentry dashboard to see if the error appears with proper source maps."
echo ""

# Open browser with test error trigger
if command -v open &> /dev/null; then
    # macOS
    open "http://localhost:4200#test-error"
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "http://localhost:4200#test-error"
else
    echo "Please open: http://localhost:4200#test-error"
fi

echo ""
echo "📊 To check in Sentry:"
echo "1. Go to your Sentry dashboard"
echo "2. Open project 'front' in organization 'nda-hr'"
echo "3. Check Issues section for new errors"
echo "4. Verify that stack traces show original TypeScript code"
echo ""
echo "💡 You can also trigger errors manually in the app:"
echo "   - Click 'Show Debug Panel' button"
echo "   - Use any of the error trigger buttons"