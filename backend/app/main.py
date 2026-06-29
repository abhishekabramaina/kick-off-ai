from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .models import * # Import models to ensure they are registered

# Create tables if they don't exist (Simple initialization)
# In a real production app, we would use Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Kickoff AI API")

# Configure CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Project Kickoff AI API"}

from .api import projects, resourcing, employees
app.include_router(projects.router)
app.include_router(resourcing.router)
app.include_router(employees.router)
