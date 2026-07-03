# 🤖 AI Powered Debt Relief & Financial Recovery Platform
**Try it out 🔗- https://ai-powered-debt-relief-financial-re.vercel.app**

An AI-powered full-stack web application that helps borrowers analyze their financial condition, predict a realistic debt settlement amount, and generate a professional debt negotiation letter using Google Gemini AI.

Built using **React + Vite**, **FastAPI**, **SQLite**, **SQLAlchemy**, and **Google Gemini AI**.

---

# Features

- User Registration & Login (JWT Authentication)
- Debt & Financial Health Analysis
- AI-powered Settlement Recommendation
- AI-generated Negotiation Letter
- Financial Health Score Calculation
- Borrower Rights Information
- Settlement History
- REST API with Swagger Documentation
- Responsive User Interface

---

# Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | React 19, React Router, Vite |
| Backend | FastAPI, Uvicorn |
| Database | SQLite, SQLAlchemy |
| Authentication | JWT, Passlib |
| AI | Google Gemini API |
| Language | Python, JavaScript |

---

# Project Structure

```text
AI Powered Debt Relief & Financial Recovery Platform/
│
├── Backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── Database/
│   ├── models.py
│   ├── crud.py
│   ├── schemas.py
│   └── auth.py
│
├── Frontend/
│   └── vite-project/
│       ├── src/
│       ├── public/
│       └── package.json
│
└── README.md
```

---

# Local Setup

## 1. Clone Repository

```bash
git clone https://github.com/Chetanjangid-dev/AI-Powered-Debt-Relief-Financial-Recovery-Platform.git

cd AI-Powered-Debt-Relief-Financial-Recovery-Platform
```

---

# Backend Setup

Move into the Backend folder.

```bash
cd Backend
```

### Create Virtual Environment

**Windows**

```bash
python -m venv venv
```

### Activate Virtual Environment

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create a `.env` file inside the Backend directory

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### Run Backend

```bash
uvicorn app.main:app --reload
```

Backend will run at:

```
http://localhost:8000
```

Swagger API Documentation:

```
http://localhost:8000/docs
```

---

# Frontend Setup

Open another terminal.

Move into the frontend folder.

```bash
cd Frontend/vite-project
```

### Install Packages

```bash
npm install
```

### Create a `.env` file

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Start Frontend

### Method 1 (Recommended)

```bash
npm run dev
```

### Method 2 (If `npm run dev` doesn't work)

```bash
node .\node_modules\vite\bin\vite.js
```

Frontend will run at:

```
http://localhost:5173
```

---

# Deployment

## Backend (Render)

```
https://ai-powered-debt-relief-financial.onrender.com
```

## Frontend (Vercel)

```
https://ai-powered-debt-relief-financial-re.vercel.app
```

### Frontend Environment Variable

```env
VITE_API_BASE_URL=https://ai-powered-debt-relief-financial.onrender.com
```

After updating the environment variable, redeploy the frontend on Vercel.

---

# API Endpoints

| Endpoint | Method |
|----------|--------|
| `/api/auth/register` | POST |
| `/api/auth/login` | POST |
| `/api/dashboard` | GET |
| `/api/settlement/predict` | POST |
| `/api/negotiation/generate` | POST |
| `/api/rights` | GET |
| `/api/history` | GET |

---

# AI Features

The application uses **Google Gemini AI** to:

- Generate professional debt negotiation letters
- Recommend settlement strategies
- Provide personalized financial guidance

If the Gemini API is unavailable, the backend automatically falls back to the built-in rule-based recommendation system.

---

# Future Improvements

- Loan Management Dashboard
- Payment Tracking
- Settlement History from Database
- Multi-user Support
- Email Notifications
- PDF Report Generation
- PostgreSQL/MySQL Support
- Admin Dashboard

---

# Contributors

- **Chetan Jangid**
- **Manthan suwalanka**
- **khushi jain**
- **chetali jaiswal**
- **bhanu sharma**

---

# License

This project was developed for educational and learning purposes.
These are documented in detail in [Troubleshooting.md](docs/Troubleshooting.md) and [Future_Improvements.md](docs/Future_Improvements.md) — read those before making changes, since "the API doesn't do what I expect" is very likely explained there.
