#!/bin/bash
# Quick diagnostic script to check frontend UI

echo "=== Frontend UI Diagnostic ==="
echo ""

echo "1. Checking if dev server is running..."
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "✅ Dev server is running on port 3000"
else
    echo "❌ Dev server NOT running"
    echo "   Run: cd frontend && npm run dev"
    exit 1
fi

echo ""
echo "2. Testing HTTP response..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Server responding (HTTP $RESPONSE)"
else
    echo "❌ Server not responding correctly (HTTP $RESPONSE)"
fi

echo ""
echo "3. Checking if index.html is served..."
HTML=$(curl -s http://localhost:3000 2>/dev/null | grep -o "<div id=\"root\">" || echo "")
if [ ! -z "$HTML" ]; then
    echo "✅ HTML structure correct"
else
    echo "❌ HTML structure issue"
fi

echo ""
echo "4. Checking if React bundle is loading..."
JS_CHECK=$(curl -s http://localhost:3000/src/main.tsx 2>/dev/null | grep -o "ReactDOM" || echo "")
if [ ! -z "$JS_CHECK" ]; then
    echo "✅ React bundle accessible"
else
    echo "❌ React bundle not loading"
fi

echo ""
echo "5. Checking if CSS is loading..."
CSS_CHECK=$(curl -s http://localhost:3000/src/index.css 2>/dev/null | grep -o "@tailwind" || echo "")
if [ ! -z "$CSS_CHECK" ]; then
    echo "✅ CSS accessible"
else
    echo "❌ CSS not loading"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Open http://localhost:3000 in your browser"
echo "2. Open Developer Tools (F12)"
echo "3. Check Console tab for errors"
echo "4. Check Network tab - ensure all files load (status 200)"
echo "5. Check Elements tab - verify #root has content"

