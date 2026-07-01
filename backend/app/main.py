from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_db, close_db
from app.routers import auth, predictions, results, dashboard
from app.routers import settings as settings_router
from app.routers import activities as activities_router
from app.config import settings
from app.services.activity_logger import ActivityLoggerMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS - important for cookie auth (allow_credentials=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register activity logger middleware (before routers to wrap all requests)
app.add_middleware(ActivityLoggerMiddleware)

# Register routers
app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(results.router)
app.include_router(dashboard.router)
app.include_router(settings_router.router)
app.include_router(activities_router.router)


@app.get("/")
async def home():
    return {"message": "HematoScan API is running", "version": settings.app_version}
