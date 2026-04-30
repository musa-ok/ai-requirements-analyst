from fastapi import FastAPI


app = FastAPI(
    title="AI-RA Backend",
    version="0.1.0",
    description="AI-Driven Requirements Analyst API",
)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok"}
