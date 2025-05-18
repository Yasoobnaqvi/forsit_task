from fastapi import FastAPI
from database import engine
from models import Base
from fastapi.middleware.cors import CORSMiddleware
from routes import router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="E-commerce Admin API", 
              description="API for e-commerce admin dashboard with sales, revenue, and inventory management")

origins = ["*"]  # Allow all origins

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins
    allow_credentials=True,  # Allow credentials such as cookies
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include the router
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the E-commerce Admin API"}

