# 🧬 HematoScan Frontend

**AI-powered blood cancer detection interface** — React SPA for analyzing CBC blood tests and microscopic blood smear images.

Built with **React 19**, **TypeScript**, **Vite**, **PrimeReact**, and **Tailwind CSS**.

---

## 📋 Overview

The frontend provides a complete clinical dashboard for blood cancer screening with two analysis methods:

| Method | Page | Input | 
|--------|------|-------|
| **🖼️ Image Analysis** | `/upload-image` | Microscopic blood smear image upload |
| **🔬 CBC Blood Test** | `/blood-test` | 10 Complete Blood Count parameters |

Results are displayed with confidence scores, prediction labels (Normal / Leukemia / Lymphoma / Myeloma), and detailed metadata.

---

## 🖥️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **React 19** | UI framework |
| **TypeScript** | Type-safe development |
| **Vite** | Build tool & dev server (HMR) |
| **PrimeReact 10** | UI component library (DataTable, Charts, Cards, Tags, FileUpload) |
| **Tailwind CSS v4** | Utility-first styling |
| **React Router v7** | Client-side routing & auth guards |
| **Axios** | HTTP client with cookie-based auth |
| **Chart.js** | Bar charts & pie charts (Dashboard) |
| **Recharts** | Data visualization |
| **Lucide React** | Icon library |
| **PrimeIcons** | Additional icon set |

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── main.tsx                  # Entry point — PrimeReact provider + Tailwind
│   ├── App.tsx                   # Router setup with route protection
│   ├── index.css                 # Tailwind + PrimeReact theme overrides + animations
│   ├── vite-env.d.ts
│   │
│   ├── context/
│   │   └── AuthContext.tsx       # Auth state (user, login, register, logout)
│   │
│   ├── types/
│   │   └── index.ts              # BloodTestData, DetectionResult, DashboardStats
│   │
│   ├── utils/
│   │   └── api.ts                # Axios client with all API functions
│   │
│   ├── components/
│   │   ├── Layout.tsx            # App shell — navbar, sidebar, main content
│   │   ├── ImageUploader.tsx     # Drag & drop / click image upload widget
│   │   ├── ResultCard.tsx        # Rich prediction result card with confidence ring
│   │   └── StatCard.tsx          # Dashboard metric card
│   │
│   └── pages/
│       ├── Login.tsx             # Login/Register form with dark gradient theme
│       ├── Dashboard.tsx         # Stats overview + charts + recent results table
│       ├── UploadImage.tsx       # Image upload + analysis workflow
│       ├── BloodTest.tsx         # CBC parameter form + analysis workflow
│       ├── Results.tsx           # Searchable, paginated results table with detail view
│       ├── History.tsx           # Full detection history with filter & pagination
│       └── Settings.tsx          # App name + ML model mode configuration
│
├── index.html
├── package.json
├── vite.config.ts                # Vite config (React + Tailwind plugins)
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── .oxlintrc.json                # Oxlint rules
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js 20+**
- **npm** or **pnpm**

### Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at **http://localhost:5173**.

> The frontend expects the backend API at `http://localhost:8000`. Start the backend first — see the [backend README](../backend/README.md).

---

## 🧭 Pages & Routes

| Route | Page | Auth Required | Description |
|-------|------|:---:|-------------|
| `/login` | Login | ❌ | Login/Register with demo credentials |
| `/` | Dashboard | ✅ | Overview stats, monthly chart, detection distribution |
| `/upload-image` | Upload Image | ✅ | Upload blood smear image for AI analysis |
| `/blood-test` | Blood Test | ✅ | Enter 10 CBC parameters for AI prediction |
| `/results` | Results | ✅ | Paginated results table with detail view |
| `/history` | History | ✅ | Full history with search & filter |
| `/activity-logs` | Activity Logs | ✅ | Filterable table of all API activity |
| `/settings` | Settings | ✅ | App name & ML model mode configuration |

**Protected routes** redirect to `/login` if the user is unauthenticated.  
**Public routes** (`/login`) redirect to `/` if the user is already logged in.

---

## 🔐 Authentication

- **Cookie-based JWT** — Login sets an httpOnly cookie via the backend
- **Axios instance** uses `withCredentials: true` to send cookies automatically
- **AuthContext** manages user state globally
- **Login page** doubles as a registration form with animated toggle
- **Demo credentials** pre-populated: username `demo` / password `demo123`

### Auth Flow

1. User logs in → backend sets `access_token` cookie
2. `AuthContext` calls `GET /api/auth/me` to fetch user profile
3. Protected routes check `user` state; show spinner while loading
4. Logout clears the cookie and resets user state

---

## 🔌 API Integration

All API calls go through a centralized Axios client (`src/utils/api.ts`):

```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true,
  timeout: 30000,
});
```

**Key API functions:**

| Function | Endpoint | Description |
|----------|----------|-------------|
| `loginUser()` | `POST /auth/login` | Login |
| `registerUser()` | `POST /auth/register` | Register |
| `logoutUser()` | `POST /auth/logout` | Logout |
| `getMe()` | `GET /auth/me` | Current user |
| `uploadImage()` | `POST /predict/image` | Analyze image |
| `predictBloodTest()` | `POST /predict/blood-test` | Analyze CBC data |
| `getDetectionHistory()` | `GET /results` | List results |
| `getDetectionById()` | `GET /results/{id}` | Single result |
| `getDashboardStats()` | `GET /dashboard` | Dashboard data |
| `getSettings()` | `GET /settings` | App settings |
| `updateSettings()` | `PUT /settings` | Update settings |
| `getDlStatus()` | `GET /settings/deep-learning-status` | DL framework status |
| `getActivityLogs()` | `GET /activities` | List activity logs (with filters) |
| `getActivityStats()` | `GET /activities/stats` | Activity log statistics |
| `getActivityLogById()` | `GET /activities/{id}` | Single activity log |

**Offline fallback:** If the backend is unavailable, pages fall back to mock data and local predictions, so the UI remains functional for demonstration purposes.

---

## 🎨 UI Features

- **Responsive sidebar** — collapsible with smooth transitions, mobile overlay
- **Dark gradient login** — animated particles, gradient blobs, glow effects
- **Confidence ring** — SVG circular progress indicator on result cards
- **Skeleton loading** — animated placeholders while results load
- **Search & filter** — results and history pages support patient name search
- **Pagination** — DataTable and DataView components with configurable page sizes
- **Prediction color coding** — color-coded badges and progress bars per prediction type
- **Low-confidence warnings** — amber alert when confidence is below 70%
- **Toast notifications** — PrimeReact Toast for success/error/info messages
- **📋 Activity Logs** — filterable DataTable with method/status/date/endpoint filters, stats chips showing method distribution, and 30s auto-refresh on Dashboard widget

---

## 📦 Available Scripts

```bash
npm run dev       # Start development server with HMR
npm run build     # TypeScript check + Vite production build
npm run preview   # Preview production build locally
npm run lint      # Run Oxlint
```

---

## 🧪 Prediction Labels & Colors

| Label | Color | Meaning |
|-------|-------|---------|
| **Normal** | 🟢 Emerald | No abnormal cells detected |
| **Leukemia** | 🔴 Rose | Acute/chronic leukemia detected |
| **Lymphoma** | 🟣 Violet | Hodgkin/Non-Hodgkin lymphoma suspected |
| **Myeloma** | 🟡 Amber | Multiple myeloma markers detected |

---

## ⚙️ Settings

The Settings page allows runtime configuration:

- **App Name** — displayed in the sidebar brand
- **Image Model Mode** — controls the prediction pipeline:
  - `Auto` (default) — Try CNN → Try OpenCV+GB → Fallback
  - `CNN Only` — Try CNN → Fallback
  - `OpenCV Only` — Try OpenCV+GB → Fallback
- **Deep Learning Status** — shows whether TensorFlow / PyTorch / CNN model file is available

---

## 🎯 Key Components

### `Layout.tsx`
The app shell with a sticky top navbar (brand, status indicator, user menu) and a collapsible sidebar with navigation links. Uses React Router's `<Outlet />` for page content.

### `ImageUploader.tsx`
A drop-zone-style upload widget with file preview, size display, and remove capability. Accepts JPG, PNG, WebP up to 10MB.

### `ResultCard.tsx`
Rich card displaying prediction results with:
- Gradient header with prediction icon and status badge
- SVG confidence ring with animated stroke
- Progress bar
- Metadata grid (method, patient, date)
- Low-confidence warning banner

### `StatCard.tsx`
Compact metric card with icon, title, value, optional subtitle and trend indicator.

---

## 🔗 Related

- **Root README** — full project overview: [../README.md](../README.md)
- **Backend API** — FastAPI server with ML models: [../backend/README.md](../backend/README.md)
