"""
app/fastapi_main.py

"""
from fastapi import FastAPI
from app.routers import immeub_billings, books  # , items
app = FastAPI(title="My Scalable API")


# Register routers with global configurations
app.include_router(
  immeub_billings.router,
  prefix="/immeub",
  tags=["Immeuble Operations"]
)

app.include_router(
  books.router,
  prefix="/books",
  tags=["Books Operations"]
)


@app.get("/")
async def root():
    return {"message": "Welcome to the central API"}
