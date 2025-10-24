# Cycling Coaching Dashboard — React (MUI MD3) Frontend

This is a Vite + React + Material UI (MD3) frontend scaffold for your Cycling Coaching platform.

## Quick start

```bash
# 1) Copy this folder into your repo as /frontend
# 2) Configure API base (optional)
cp .env.example .env
# edit .env and set VITE_API_BASE to your backend URL (default: http://localhost:8000)

# 3) Install deps & run
npm install
npm run dev

# Build for production
npm run build
npm run preview
```

## Project structure

```
frontend/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── theme.js
│   ├── api.js
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   └── RideAnalysis.jsx
│   └── components/
│       └── RideCard.jsx
├── index.html
├── package.json
├── vite.config.js
└── .env.example
```

## Notes
- Uses Material UI v6 (MD3).
- Buttons are non-uppercase, rounded corners, MD3 palette.
- Calls the backend routes: `/api/rides/`, `/api/rides/{fname}`, `/api/report/generate/{fname}`.
