from fastapi import FastAPI
from api.auth.router import router as login_router

app = FastAPI()

products = [
    {"id": 1, "name": "Product 1", "price": 10.99},
    {"id": 2, "name": "Product 2", "price": 19.99},
    {"id": 3, "name": "Product 3", "price": 5.99},
]

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/prod/{item_id}")
async def read_product(item_id: str):
    for product in products:
        if product["id"] == int(item_id):
            return product
    return {"message": "Product not found"}

@app.patch("/prod/{item_id}")
async def update_product(item_id: str, updated_product: dict):
    for product in products:
        if product["id"] == int(item_id):
            product.update(updated_product)
            return product
    return {"message": "Product not found"}

app.include_router(login_router)