import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables, close_engine
from routers import todos

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

origins = [
        "http://localhost:64019"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router)

@app.get("/")
def home():
    return {"message": "To-Do List API"}