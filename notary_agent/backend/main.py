from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.auth.routes import router as auth_router
from backend.drafts.partnership.routes import router as partnership_router  # ✅
from backend.drafts.rent.routes import router as rent_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register all routers here
app.include_router(auth_router)
app.include_router(partnership_router)
app.include_router(rent_router)


@app.get("/")
def root():
    return {"message": "NotaryAI backend is running"}
