from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.routers import holdings, prices
app = FastAPI(title="Portfolio Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict this later
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(holdings.router)
app.include_router(prices.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()