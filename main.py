from fastapi import FastAPI
from routers import controller
app = FastAPI()
app.include_router(controller.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="::1", port=20032)

