from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import create_db_and_tables, close_engine
from routers import todos, auth
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_db_and_tables()
    print("Database initialized.")
    yield
    # Shutdown
    await close_engine()
    print("Database engine closed.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(auth.router)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
        )

app.include_router(todos.router)

@app.get("/")
def home():
    return {"message": "To-Do List API"}