from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World", "status": "working"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/test")
def test():
    return {"test": "ok"}

@app.get("/faturas")
def faturas():
    return [
        {"id": 1, "nome": "Cliente 1", "valor": 100.00},
        {"id": 2, "nome": "Cliente 2", "valor": 200.00}
    ] 