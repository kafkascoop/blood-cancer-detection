# HematoScan Backend API

FastAPI backend for the Blood Cancer Detection application. Provides AI-powered prediction from CBC blood test parameters and microscopic blood smear images, with MongoDB storage and cookie-based JWT authentication.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.138 |
| **Server** | Uvicorn (ASGI) |
| **Database** | MongoDB via Motor (async driver) |
| **Auth** | JWT (python-jose) + bcrypt (passlib) |
| **ML** | scikit-learn (Random Forest / Gradient Boosting) |
| **Image Processing** | OpenCV 4.13 |
| **Validation** | Pydantic v2 |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry, CORS, lifespan
│   ├── config.py               # Environment settings (pydantic-settings)
│   ├── database.py             # Motor MongoDB connection + indexes
│   ├── dependencies.py         # get_current_user via JWT cookie
│   │
│   ├── models/
│   │   ├── user.py             # UserCreate, UserLogin, UserResponse
│   │   └── detection.py        # BloodTestData, DetectionResponse, DetectionStats
│   │
│   ├── routers/
│   │   ├── auth.py             # POST /api/auth/register, /login, /logout, GET /me
│   │   ├── predictions.py      # POST /api/predict/image, /blood-test
│   │   ├── results.py          # GET /api/results, /api/results/{id}
│   │   └── dashboard.py        # GET /api/dashboard (stats + recent)
│   │
│   ├── services/
│   │   ├── auth.py             # bcrypt hashing, JWT create/decode
│   │   ├── model_service.py    # ML model loading (cached) + inference
│   │   └── prediction.py       # Public API: routes to ML model or fallback
│   │
│   └── ml/
│       ├── data.py             # Data generation, CSV export/import, feature extraction
│       ├── train.py            # Training pipeline with CLI (argparse)
│       └── models/
│           ├── blood_test_model.pkl    # Trained Random Forest (98.5% acc)
│           └── image_model.pkl         # Trained Gradient Boosting (96.9% acc)
│
├── data/                       # Exported CSV datasets
│   ├── cbc_dataset_*.csv       # CBC training data (6000 samples)
│   └── image_dataset_*.csv     # Image feature training data (6000 samples)
│
├── uploads/                    # Uploaded blood smear images
├── .venv/                      # Python virtual environment
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- MongoDB running locally (default: `mongodb://localhost:27017`)

### 2. Environment Setup

Create a `.env` file in the `backend/` directory:

```bash
cd backend
cat > .env << 'EOF'
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=hematoscan
JWT_SECRET_KEY=change-this-to-a-secure-random-key-in-production
JWT_EXPIRE_MINUTES=1440
CORS_ORIGIN=http://localhost:5173
EOF
```

### 3. Activate Virtual Environment & Start

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

Interactive docs at `http://localhost:8000/docs` (Swagger UI).

---

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Create a new user | No |
| POST | `/api/auth/login` | Login, sets httpOnly JWT cookie | No |
| POST | `/api/auth/logout` | Clear the JWT cookie | No |
| GET | `/api/auth/me` | Get current user profile | Yes |

**Register request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepass123",
  "full_name": "John Doe"
}
```

**Login response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "667e...", "email": "user@example.com",
    "username": "johndoe", "full_name": "John Doe",
    "created_at": "2026-06-26T10:00:00Z"
  }
}
```

> **Auth flow**: Login sets an `access_token` httpOnly cookie. All protected endpoints read this cookie automatically. No `Authorization` header needed.

### Predictions (`/api/predict`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/predict/image` | Upload blood smear image for analysis | Yes |
| POST | `/api/predict/blood-test` | Submit CBC parameters for analysis | Yes |

**Image upload** (multipart/form-data):
| Field | Type | Description |
|-------|------|-------------|
| `file` | File | JPG, PNG, or WebP (max 10MB) |
| `patient_name` | String | Patient identifier |

**Blood test** (multipart/form-data):
| Field | Type | Description |
|-------|------|-------------|
| `patient_name` | String | Patient identifier |
| `blood_data` | String | JSON string of CBC parameters |

**CBC Parameters** (`blood_data` JSON):
| Field | Unit | Normal Range |
|-------|------|-------------|
| `wbc` | ×10³/µL | 4.5–11.0 |
| `rbc` | ×10⁶/µL | 4.7–6.1 |
| `hemoglobin` | g/dL | 13.8–17.2 |
| `platelets` | ×10³/µL | 150–450 |
| `neutrophils` | % | 40–80 |
| `lymphocytes` | % | 20–40 |
| `monocytes` | % | 2–10 |
| `eosinophils` | % | 1–6 |
| `basophils` | % | 0–1 |
| `blast_cells` | % | 0–5 |

**Prediction Response:**
```json
{
  "id": "667eabc123...",
  "user_id": "667e...",
  "patient_name": "John Doe",
  "type": "blood_test",
  "prediction": "Normal",
  "confidence": 0.9865,
  "status": "completed",
  "image_data": null,
  "blood_test_data": { "wbc": 7.5, ... },
  "notes": null,
  "created_at": "2026-06-26T10:30:00Z",
  "updated_at": "2026-06-26T10:30:00Z"
}
```

**Prediction labels:**
| Label | Meaning |
|-------|---------|
| `Normal` | No abnormal cells detected |
| `Benign` | Non-cancerous abnormalities detected |
| `Malignant` | Cancerous cells detected |

### Results (`/api/results`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/results` | List all detection results (paginated) | Yes |
| GET | `/api/results/{id}` | Get a single result by ID | Yes |

**Query parameters for list:** `limit` (default: 20), `skip` (default: 0)

### Dashboard (`/api/dashboard`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/dashboard` | Get stats & recent 5 results | Yes |

**Response:**
```json
{
  "stats": {
    "total_tests": 147,
    "normal_results": 118,
    "abnormal_detections": 23,
    "pending_results": 6,
    "monthly_tests": [12, 15, 18, ...]
  },
  "recent_results": [...]
}
```

### Activity Logs (`/api/activities`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/activities` | List activity logs (with filters) | Yes |
| GET | `/api/activities/stats` | Get aggregated log statistics | Yes |
| GET | `/api/activities/{id}` | Get a single log entry | Yes |

**Query parameters for list:** `method`, `status_code`, `endpoint` (regex), `date_from`, `date_to`, `user_only`, `limit` (default: 50), `skip`

**Stats Response:**
```json
{
  "total_logs": 1250,
  "method_counts": { "GET": 800, "POST": 350, "PUT": 60, "DELETE": 40 },
  "status_code_counts": { "2xx Success": 1100, "4xx Client Error": 120, "5xx Server Error": 30 },
  "endpoint_counts": { "/api/auth/me": 200, "/api/dashboard": 150, ... },
  "monthly_logs": [90, 85, 110, ...]
}
```

---

## ML Model Training

### Overview

Two trained models are included:

| Model | Algorithm | Accuracy | Features |
|-------|-----------|----------|----------|
| **Blood Test** | Random Forest | 98.5% | 10 CBC parameters |
| **Image Analysis** | Gradient Boosting | 96.9% | 10 extracted image features |

The models were trained on synthetic data generated from known medical patterns. When real data is not available, the models fall back to rule-based simulation.

### CLI Usage

```bash
# Activate environment
source .venv/bin/activate

# Train from synthetic data (default)
python -m app.ml.train --generate

# Export datasets to CSV, then train
python -m app.ml.train --export --samples 2000

# Train from your own CSV datasets
python -m app.ml.train --csv-cbc ./my_cbc_data.csv --csv-img ./my_image_data.csv

# Train only blood test model (skip image)
python -m app.ml.train --csv-cbc ./data.csv --no-image

# Show dataset statistics
python -m app.ml.train --stats ./data/cbc_dataset.csv

# More samples for better accuracy
python -m app.ml.train --generate --samples 5000
```

### Training from CSV

When you have real medical data, prepare a CSV with:
- **Column names**: matching the feature names (`wbc`, `rbc`, `hemoglobin`, ...)
- **Target column**: named `target` with values `Normal`, `Benign`, or `Malignant`

```bash
python -m app.ml.train --csv-cbc ./real_cbc_data.csv --no-image
```

### How Prediction Works

1. **Prediction requested** → `prediction.py` checks if ML models exist
2. **Models available** → `model_service.py` loads cached models, runs inference
3. **Models unavailable** → Falls back to rule-based simulation
4. **Models are cached** in memory after first load for fast subsequent predictions

### Image Feature Extraction

For image uploads, OpenCV extracts these features from the blood smear image:

| Feature | Description |
|---------|-------------|
| `cell_count` | Number of cells detected via contour analysis |
| `cell_size_mean` | Average cell area |
| `cell_size_std` | Cell size variation |
| `nucleus_ratio_mean` | Nucleus-to-cytoplasm ratio estimate |
| `blue_intensity` | Average blue channel intensity |
| `red_intensity` | Average red channel intensity |
| `texture_contrast` | Image contrast (gray std dev) |
| `texture_homogeneity` | Image homogeneity |
| `blast_like_cells_pct` | Percentage of blast-like cells |

---

## Configuration

All settings are in `app/config.py` and can be overridden via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | `hematoscan` | Database name |
| `JWT_SECRET_KEY` | `change-me...` | Secret for JWT signing |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry (24h) |
| `CORS_ORIGIN` | `http://localhost:5173` | Frontend URL for CORS |
| `UPLOAD_DIR` | `uploads` | Image storage directory |
| `MAX_UPLOAD_SIZE_MB` | `10` | Max image size |

---

## Authentication Details

- **Cookie-based**: JWT is stored in an httpOnly, `SameSite=Lax` cookie
- **Secure flag**: `false` by default (set `true` in production with HTTPS)
- **Expiry**: 24 hours by default (configurable via `JWT_EXPIRE_MINUTES`)
- **Frontend**: Must use `withCredentials: true` in axios/fetch for cookies to be sent
- **CORS**: Backend must have `allow_credentials=True` and explicit `allow_origins` (no wildcard)

---

## Development

### Run with hot reload
```bash
uvicorn app.main:app --reload --port 8000
```

### Check the API
```bash
curl http://localhost:8000/
# {"message":"HematoScan API is running","version":"1.0.0"}

curl http://localhost:8000/docs
# Swagger UI
```

### Database
- MongoDB indexes are created automatically on startup
- Collections: `users`, `detections`, `activity_logs`
- Users have unique indexes on `email` and `username`
- Detections are indexed by `user_id` + `created_at`
- Activity logs are indexed by `created_at`, `method`, `status_code`, `user_id`, with 90-day TTL auto-expiry

---

## Frontend Integration

The frontend (React + PrimeReact + Tailwind) communicates with the backend via:

- **Axios instance** with `baseURL: http://localhost:8000/api` and `withCredentials: true`
- **Snake_case** backend responses are mapped to **camelCase** in the frontend API utility
- **FormData** is used for both image uploads and blood test submissions
- **JWT cookie** is set by the backend and automatically sent with every request

See `frontend/src/utils/api.ts` for the complete API client.
