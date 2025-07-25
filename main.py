import uvicorn
import logging

from fastapi import FastAPI, Response, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from controllers.firebase import register_user_firebase, login_user_firebase
from controllers.product import get_products, create_product

from models.userregister import UserRegister
from models.userlogin import UserLogin
from models.product import Product

from utils.security import validateadmin
from utils.telemetry import setup_simple_telemetry, instrument_fastapi_app

logging.basicConfig( level=logging.INFO )
logger = logging.getLogger(__name__)
load_dotenv()

telemetry_enabled = setup_simple_telemetry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title="Series API",
    description="Series API Lab expert system",
    version="0.0.1",
    lifespan=lifespan
)

if telemetry_enabled:
    instrument_fastapi_app(app)
    logger.info("Application Insights enabled")
    logger.info("FastAPI Instrumented")
else:
    logger.warning("Application Insight disabled")

@app.get("/health")
async def _():
    return {
        "status": "healthy"
        , "version": "0.0.1"
    }

@app.get("/")
async def _(request: Request, response: Response):
    return {
        "hello": "world"
    }

@app.post("/signup")
async def _(user: UserRegister):
    result = await register_user_firebase(user)
    return result

@app.post("/login")
async def _(user: UserLogin):
    result = await login_user_firebase(user)
    return result

@app.get("/catalog")
async def _(
        dosage_form: str | None = None,
        is_discontinued: bool | None = None,
        pack_unit: str | None = None,
        therapeutic_class: str | None = None
):
    return await get_products(dosage_form, is_discontinued, pack_unit, therapeutic_class)

@app.post("/catalog", response_model = Product, status_code=201)
@validateadmin
async def _(request: Request, response: Response, product_data: Product) -> Product:
    product = await create_product(product_data)
    return product

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
