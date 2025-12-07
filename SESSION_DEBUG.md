# Session Debugging Guide

## The Problem
"Unauthorized. Please log in." errors after successful login.

## What We Know
✅ Backend sessions WORK (Python test confirms)
✅ Cookies are being set correctly
✅ Routes are registered properly
❌ Browser isn't sending cookies with requests

## Solution Steps

### Step 1: Check How You're Accessing the App

**CRITICAL:** You MUST access the app via:
```
http://localhost:5000
```

NOT:
- `file:///C:/Users/.../index.html` ❌
- Opening HTML file directly ❌

### Step 2: Check Browser Console

1. Open browser DevTools (F12)
2. Go to **Application** tab → **Cookies** → `http://localhost:5000`
3. After login, you should see:
   - `session` cookie
   - `remember_token` cookie

If cookies are NOT there, the browser is blocking them.

### Step 3: Check Network Tab

1. Go to **Network** tab
2. Login
3. Check the login request:
   - Look for `Set-Cookie` in Response Headers
   - Should see `session=...` and `remember_token=...`

4. Check next request (like `/api/auth/me`):
   - Look for `Cookie` in Request Headers
   - Should see the session cookie being sent

### Step 4: Browser Settings

Some browsers block cookies. Try:
1. **Chrome**: Settings → Privacy → Cookies → Allow all cookies
2. **Edge**: Settings → Cookies → Allow all cookies
3. **Firefox**: Settings → Privacy → Cookies → Accept all

### Step 5: Use Incognito Mode

Try in Incognito/Private mode to rule out extensions blocking cookies.

## Quick Test

After login, open browser console and run:
```javascript
document.cookie
```

You should see the session cookie. If not, cookies are being blocked.

## If Still Not Working

The backend is correct. The issue is browser cookie handling. You may need to:
1. Check browser security settings
2. Disable extensions
3. Try a different browser
4. Check if antivirus is blocking cookies

