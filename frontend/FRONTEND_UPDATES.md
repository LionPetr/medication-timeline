# Frontend Update Instructions

## Update App.js to use environment variables

In `frontend/src/App.js`, add this line at the top of the file (after imports):

```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

Then replace the two fetch URLs:

**Old:**
```javascript
"http://localhost:8000/api/patients/1/timeline/"
```

**New:**
```javascript
`${API_URL}/api/patients/1/timeline/`
```

**Old:**
```javascript
"http://localhost:8000/api/patients/1/undated_medications/"
```

**New:**
```javascript
`${API_URL}/api/patients/1/undated_medications/`
```

## Create .env.production file

In `frontend/` folder, create a file named `.env.production`:

```
REACT_APP_API_URL=https://your-backend-name.onrender.com
```

(Replace `your-backend-name` with your actual Render service name after deployment)

## Test locally

The default `http://localhost:8000` will still work for local development.
