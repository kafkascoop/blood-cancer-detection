<div align="center">

# 🧬 HematoScan — Blood Cancer Detection System

**AI-powered blood cancer screening from CBC tests and microscopic blood smear images**

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](backend/)
[![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react)](frontend/)
[![ML](https://img.shields.io/badge/ML-scikit--learn-F7931E?logo=scikitlearn)](backend/app/ml/)
[![Database](https://img.shields.io/badge/Database-MongoDB-47A248?logo=mongodb)](backend/app/database.py)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

## 📋 Overview

HematoScan is a full-stack AI application that assists in detecting blood cancers (Leukemia, Lymphoma, Myeloma) through two diagnostic methods:

| Method | Input | Model | Accuracy |
|--------|-------|-------|----------|
| **🔬 CBC Blood Test** | 10 Complete Blood Count parameters | Random Forest (scikit-learn) | ~98.5% |
| **🖼️ Blood Smear Image** | Microscopic blood sample image | Gradient Boosting / CNN (TensorFlow) | ~96.9% |

The system uses **trained ML models** with automatic **rule-based fallback** when models are unavailable, ensuring the application always produces a result.

> **⚠️ Disclaimer:** This is a research/educational tool and is **not** approved for clinical or diagnostic use. Always consult a healthcare professional for medical decisions.

---

## 🏗️ Architecture

```
blood-cancer-detection/
├── frontend/          # React + TypeScript + Vite SPA
│   ├── src/
│   │   ├── pages/     # Dashboard, Upload, BloodTest, Results, History, Settings
│   │   ├── components/# Layout, ImageUploader, ResultCard, StatCard
│   │   ├── context/   # AuthContext (JWT cookie-based auth)
│   │   ├── utils/     # API client (Axios)
│   │   └── types/     # TypeScript interfaces
│   └── ...
├── backend/           # FastAPI + MongoDB + ML
│   ├── app/
│   │   ├── routers/   # auth, predictions, results, dashboard, settings, activities
│   │   ├── services/  # auth, model_service (ML), prediction (fallback), activity_logger
│   │   ├── models/    # Pydantic schemas (user, detection, activity)
│   │   ├── ml/        # Training pipelines, synthetic data generation, trained models
│   │   ├── config.py  # Environment-based configuration
│   │   └── database.py# MongoDB connection (Motor async driver)
│   └── data/          # Exported CSV datasets
└── README.md          # ← You are here
```

### How It Works

1. **User authenticates** via login (JWT stored in httpOnly cookie)
2. **Two analysis paths:**
   - **Blood Test:** User enters 10 CBC parameters → Random Forest model predicts Normal/Leukemia/Lymphoma/Myeloma
   - **Image Upload:** User uploads a microscopic blood smear image → OpenCV extracts 10 morphological features → Gradient Boosting (or CNN) classifies
3. **Results saved** to MongoDB with prediction, confidence score, and metadata
4. **Dashboard** shows stats, monthly trends, and detection distribution

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11**
- **Node.js 20+**
- **MongoDB** running locally (default: `mongodb://localhost:27017`)

### 1. Clone & Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd blood-cancer-detection

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=hematoscan
JWT_SECRET_KEY=change-this-to-a-secure-random-key
CORS_ORIGIN=http://localhost:5173
EOF

# Frontend setup (separate terminal)
cd frontend
npm install
```

### 2. Seed Demo User & Start

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
python -m app.seed                  # Creates demo/demo123 user
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173** and log in with:

| Field | Value |
|-------|-------|
| Username | `demo` |
| Password | `demo123` |

### 3. Train Models (Optional)

```bash
cd backend
source .venv/bin/activate

# Generate synthetic data & train both models
python -m app.ml.train --generate --samples 2000

# Train only the blood test model from CSV
python -m app.ml.train --csv-cbc ./data/cbc_dataset.csv --no-image
```

---

## 🖥️ Tech Stack

### Backend

| Technology | Purpose |
|-----------|---------|
| **FastAPI** 0.138 | Web framework with async support |
| **MongoDB + Motor** | Async database with automatic index creation |
| **JWT (python-jose) + bcrypt** | Cookie-based authentication |
| **scikit-learn** | Random Forest (CBC) & Gradient Boosting (Image) models |
| **TensorFlow/Keras** | Optional CNN for deep learning image analysis |
| **OpenCV** | Image feature extraction (cell count, morphology, texture) |
| **Pydantic v2** | Data validation and settings management |

### Frontend

| Technology | Purpose |
|-----------|---------|
| **React 19** | UI framework |
| **TypeScript** | Type-safe development |
| **Vite** | Build tool and dev server |
| **PrimeReact** | UI component library (DataTable, Charts, Cards, etc.) |
| **Tailwind CSS** | Utility-first styling |
| **Recharts / Chart.js** | Data visualization (bar charts, pie charts) |
| **Axios** | HTTP client with cookie support |
| **Lucide React** | Icon library |

---

## 🔌 API Endpoints

Base URL: `http://localhost:8000`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | Health check | No |
| `POST` | `/api/auth/register` | Create account | No |
| `POST` | `/api/auth/login` | Login (sets JWT cookie) | No |
| `POST` | `/api/auth/logout` | Logout (clears cookie) | No |
| `GET` | `/api/auth/me` | Current user profile | Yes |
| `POST` | `/api/predict/image` | Analyze blood smear image | Yes |
| `POST` | `/api/predict/blood-test` | Analyze CBC parameters | Yes |
| `GET` | `/api/results` | List detection results | Yes |
| `GET` | `/api/results/{id}` | Get single result | Yes |
| `GET` | `/api/dashboard` | Stats + recent results | Yes |
| `GET` | `/api/settings` | Get app settings | Yes |
| `PUT` | `/api/settings` | Update app settings | Yes |
| `GET` | `/api/settings/deep-learning-status` | Check DL framework status | Yes |
| `GET` | `/api/activities` | List activity logs (with filters) | Yes |
| `GET` | `/api/activities/stats` | Get activity log statistics | Yes |
| `GET` | `/api/activities/{id}` | Get single activity log | Yes |

Full interactive documentation at **http://localhost:8000/docs** (Swagger UI).

---

## 🧪 ML Model Training

### Trained Models

| Model | Algorithm | Features | Accuracy |
|-------|-----------|----------|----------|
| `blood_test_model.pkl` | Random Forest (200 estimators) | 10 CBC parameters | ~98.5% |
| `image_model.pkl` | Gradient Boosting (150 estimators) | 10 image features | ~96.9% |
| `cnn_image_model.keras` | CNN / MobileNetV2 (optional) | Raw image pixels | Varies |

### Training CLI

```bash
# From synthetic data
python -m app.ml.train --generate

# From your own CSV datasets
python -m app.ml.train --csv-cbc ./my_cbc_data.csv --csv-img ./my_image_data.csv

# Train CNN (requires TensorFlow)
python -m app.ml.train_cnn --data-dir ./blood_cell_images --epochs 50

# Export datasets only
python -m app.ml.train --export --samples 3000

# Show dataset statistics
python -m app.ml.train --stats ./data/cbc_dataset.csv
```

### Prediction Pipeline

The image analysis uses a **3-tier fallback** strategy (configurable in Settings):

```
User uploads image
    │
    ├─ [Auto mode] Try CNN → Try OpenCV+GB → Fallback
    ├─ [CNN mode]  Try CNN → Fallback
    └─ [OpenCV mode] Try OpenCV+GB → Fallback
```

**Image features extracted by OpenCV:**
- Cell count & size distribution
- Nucleus-to-cytoplasm ratio
- Color channel intensities
- Texture contrast & homogeneity
- Blast-like cell percentage

---

## 📁 Project Structure (Detailed)

```
blood-cancer-detection/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Environment settings (pydantic-settings)
│   │   ├── database.py             # MongoDB connection & indexes
│   │   ├── dependencies.py         # JWT cookie auth dependency
│   │   ├── seed.py                 # Demo user seeder
│   │   ├── models/                 # Pydantic schemas
│   │   │   ├── user.py             # UserCreate, UserLogin, UserResponse
│   │   │   ├── detection.py        # BloodTestData, DetectionResponse, Stats
│   │   │   └── activity.py         # ActivityLogEntry, ActivityLogResponse, ActivityLogStats
│   │   ├── routers/                # API route handlers
│   │   │   ├── auth.py             # Register, login, logout
│   │   │   ├── predictions.py      # Image upload & blood test analysis
│   │   │   ├── results.py          # Detection history
│   │   │   ├── dashboard.py        # Stats & charts data
│   │   │   ├── settings.py         # App configuration
│   │   │   └── activities.py       # Activity log queries & stats
│   │   ├── services/               # Business logic
│   │   │   ├── auth.py             # Password hashing, JWT creation
│   │   │   ├── model_service.py    # ML model loading & inference
│   │   │   ├── prediction.py       # Prediction routing & fallbacks
│   │   │   └── activity_logger.py  # Auto-logging middleware (all API calls)
│   │   └── ml/                     # Machine learning
│   │       ├── data.py             # Synthetic data & image feature extraction
│   │       ├── train.py            # scikit-learn training pipeline
│   │       ├── train_cnn.py        # TensorFlow CNN training
│   │       ├── download_datasets.py# Dataset download utilities
│   │       └── models/             # Saved model files
│   ├── data/                       # CSV datasets
│   ├── requirements.txt
│   └── .env                        # Environment variables (not tracked)
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                # React entry point
│   │   ├── App.tsx                 # Router & route protection
│   │   ├── index.css               # Tailwind + PrimeReact theme overrides
│   │   ├── context/
│   │   │   └── AuthContext.tsx      # Auth state management
│   │   ├── pages/
│   │   │   ├── Login.tsx           # Authentication (login/register)
│   │   │   ├── Dashboard.tsx       # Stats overview
│   │   │   ├── UploadImage.tsx     # Image upload & analysis
│   │   │   ├── BloodTest.tsx       # CBC form & analysis
│   │   │   ├── Results.tsx         # Detailed results viewer
│   │   │   ├── History.tsx         # Full detection history
│   │   │   ├── ActivityLogs.tsx    # Filterable activity log viewer
│   │   │   └── Settings.tsx        # App & model configuration
│   │   ├── components/             # Reusable UI
│   │   ├── utils/
│   │   │   └── api.ts              # Axios API client
│   │   └── types/index.ts          # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
│
├── notebooks/
│   └── HematoScan_Pipeline.ipynb   # Jupyter notebook for exploration
│
└── README.md                       # This file
```

---

## ⚙️ Configuration

### Backend (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | `hematoscan` | Database name |
| `JWT_SECRET_KEY` | *(required)* | Secret for JWT signing |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry (24h) |
| `CORS_ORIGIN` | *(required)* | Frontend URL (e.g. `http://localhost:5173`) |
| `UPLOAD_DIR` | `uploads` | Image storage directory |
| `MAX_UPLOAD_SIZE_MB` | `10` | Max upload file size |

### Runtime Settings (via Settings UI)

| Setting | Options | Description |
|---------|---------|-------------|
| `app_name` | String (max 64 chars) | Display name in sidebar |
| `image_model_mode` | `auto` / `cnn` / `opencv` | Image prediction pipeline mode |

---

## 🧑‍💻 Development

### Run with hot reload

```bash
# Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```

### Lint & Build

```bash
# Frontend
cd frontend
npm run lint       # Oxlint
npm run build      # TypeScript check + Vite build

# Backend
cd backend && source .venv/bin/activate
# (Uses FastAPI's built-in validation)
```

### Database

- MongoDB indexes are created **automatically** on application startup
- Collections: `users`, `detections`, `settings`, `activity_logs`
- Users indexed by `email` (unique, sparse) and `username` (unique)
- Detections indexed by `user_id` + `created_at`
- Activity logs indexed by `created_at`, `method`, `status_code`, `user_id`, with **90-day TTL auto-expiry**

---

## 🔐 Authentication Flow

1. **Login:** User submits credentials → backend validates → sets `access_token` httpOnly cookie
2. **Subsequent requests:** Cookie automatically sent with `withCredentials: true`
3. **Protected routes:** `get_current_user` dependency reads cookie, decodes JWT, fetches user
4. **Logout:** Cookie is cleared by the backend

> **Security note:** The `secure` flag is `false` by default (for local development). Set to `true` in production with HTTPS.

---

## 📊 Key Features

- **🔐 User Authentication:** Register/login with JWT cookie-based sessions
- **📊 Interactive Dashboard:** Overview with stats cards, monthly bar chart, and detection distribution pie chart
- **🖼️ Image Analysis:** Upload blood smear images for AI-based cell morphology analysis
- **🔬 CBC Blood Test Analysis:** Form-based input of 10 blood parameters for cancer prediction
- **📋 Results & History:** Paginated, searchable, filterable history with detail views
- **⚙️ Settings:** Customize app name and model prediction mode (Auto/CNN/OpenCV)
- **💡 Multiple ML Models:** Random Forest, Gradient Boosting, and optional CNN (TensorFlow)
- **🔄 Smart Fallback:** Automatic fallback to rule-based prediction if models are unavailable
- **📋 Activity Logging:** Automatic middleware captures all API calls with method, endpoint, status, duration, and user attribution. Filterable UI with method/status/date/endpoint filters, stats aggregation, and 30s auto-refresh on Dashboard
- **🗑️ Auto-cleanup:** 90-day TTL index on MongoDB automatically expires old activity logs
- **📁 Offline-ready:** Works with mock data when backend is unavailable

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), and [PrimeReact](https://primereact.org/)
- ML models trained on synthetic medical data generated from known clinical patterns
- Icons by [Lucide](https://lucide.dev/)
- Charts by [Chart.js](https://www.chartjs.org/) and [Recharts](https://recharts.org/)

---

<div align="center">
  <sub>Built with ❤️ for early blood cancer detection research</sub>
</div>
