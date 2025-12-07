# Quick Fix for 405 Errors

## The Problem
405 "Method Not Allowed" errors are happening because:
1. Flask-Login is trying to redirect when user is not authenticated
2. Session cookies might not be persisting properly
3. The unauthorized handler needs to return JSON, not HTML

## Solution Applied

1. **Added unauthorized handler** - Returns JSON instead of HTML redirect
2. **Fixed session persistence** - Made session permanent and modified
3. **Updated CORS settings** - Better cookie handling

## What You Need to Do

1. **RESTART your Flask server** (very important!):
   ```bash
   # Stop the server (Ctrl+C)
   python app.py
   ```

2. **Clear browser cookies** for localhost:5000:
   - Open browser DevTools (F12)
   - Go to Application/Storage tab
   - Clear all cookies for localhost:5000
   - Or use Incognito/Private mode

3. **Test again**:
   - Register/Login
   - Try creating a note
   - Try creating a flashcard
   - Try AI Assistant

## If Still Not Working

Check browser console (F12) for errors and share them.

The fixes are in place - you just need to restart the server and clear cookies!

