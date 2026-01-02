from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base

from app.models import book_model, loan_model, reservation_model, user_model

from app.routers import book_router, loan_router, reservation_router, user_router, sanction_router, auth_router

app = FastAPI(title="Library API")

# Routers de la API
app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(book_router.router, prefix="/books", tags=["Books"])
app.include_router(loan_router.router, prefix="/loans", tags=["Loans"])
app.include_router(reservation_router.router, prefix="/reservations", tags=["Reservations"])
app.include_router(sanction_router.router, prefix="/sanctions", tags=["Sanctions"]) 
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # o restringe a tus puertos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# FRONT: templates + static
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=FileResponse)
def serve_index():
    return "app/static/index.html"
