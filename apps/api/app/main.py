from fastapi import FastAPI

app = FastAPI(
    title="RepoPilot API",
    description="AI Software Engineering Agent",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "repopilot-api",
    }
