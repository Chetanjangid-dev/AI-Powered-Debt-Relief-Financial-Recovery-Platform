from fastapi import FastAPI

app = FastAPI(title="AI Powered Debt Relief & Financial Recovery Platform")


@app.get("/")
def root():
    return {"message": "Backend is running"}