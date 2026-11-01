from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize relational user authentication tables
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "🔐 Production-grade Authentication & Role-Based Access Control (RBAC) microservice "
        "implementing OAuth2 password flow, JWT cryptographic signing, token rotation, "
        "and bcrypt salted password hashing."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root_endpoint():
    """Service landing endpoint with API metadata and documentation links."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe endpoint."""
    return {"status": "healthy"}


# Mount functional routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
