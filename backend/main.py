from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router

from routes.wallet import router as wallet_router
from routes.transactions import router as transactions_router
from routers.alias import router as alias_router #added by maithri
from compliance.routes.compliance import router as compliance_router


app = FastAPI(title="Payshield API")

# Allows your frontend (running on a different port during local dev,
# e.g. Vite's localhost:5173) to actually call this API from the browser.
# Tighten allow_origins to your real frontend URL before any real deploy —
# "*" is fine for a hackathon demo, not for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transactions_router)

app.include_router(alias_router) #added by maithri
app.include_router(compliance_router)

@app.get("/health")
def health():
    return {"status": "ok"}