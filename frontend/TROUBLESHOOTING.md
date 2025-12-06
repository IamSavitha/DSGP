# Frontend Troubleshooting Guide

If your UI is not showing, check the following:

## 1. Check if Frontend Server is Running

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

## 2. Check Browser Console

Open your browser's Developer Tools (F12) and check:
- **Console tab**: Look for JavaScript errors
- **Network tab**: Check if files are loading (200 status)
- **Elements tab**: Check if `<div id="root"></div>` exists and has content

## 3. Common Issues

### Issue: Blank White Screen
**Solution:**
- Check browser console for errors
- Verify all dependencies are installed: `npm install`
- Clear browser cache and hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Issue: "Cannot find module" errors
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: CSS not loading
**Solution:**
- Verify Tailwind is configured in `tailwind.config.js`
- Check that `index.css` is imported in `main.tsx`
- Rebuild: `npm run build`

### Issue: React not rendering
**Solution:**
- Check that `#root` element exists in `index.html`
- Verify `main.tsx` is correctly importing and rendering App
- Check browser console for React errors

## 4. Verify Installation

```bash
cd frontend
npm install
npm run dev
```

## 5. Test in Browser

1. Open: http://localhost:3000
2. Open Developer Tools (F12)
3. Check Console for errors
4. Check Network tab for failed requests

## 6. Quick Fix Commands

```bash
# Stop all processes
pkill -f vite
pkill -f node

# Clean and reinstall
cd frontend
rm -rf node_modules .vite dist
npm install

# Start fresh
npm run dev
```

