import json
import logging
from typing import Optional

from fastapi import HTTPException

from utils.database import execute_query_json
from utils.redis_cache import get_redis_client, store_in_cache, get_from_cache, delete_cache
from models.product import Product

logger = logging.getLogger(__name__)

PRODUCTS_CACHE_KEY = "product:stock:all"
LAST_PRODUCT_CACHE_KEY = "product:stock:last"
CACHE_TTL = 30 * 60

async def get_product(id: int) -> Product:
    redis_client = get_redis_client()
    cached_data = get_from_cache( redis_client , LAST_PRODUCT_CACHE_KEY )
    if cached_data and cached_data[0].product_id == id:
        return cached_data[0]

    query = f"SELECT * FROM STOCK.PRODUCTS WHERE PRODUCT_ID = { id }"
    result = await execute_query_json(query)
    dict = json.loads(result)

    if not dict:
        raise HTTPException(status_code=404, detail="Product not found")

    store_in_cache( redis_client , LAST_PRODUCT_CACHE_KEY , dict , CACHE_TTL )
    return dict[0]

async def get_products(dosage_form: str, is_discontinued: bool, pack_unit: str, therapeutic_class: str) -> list[Product]:
    redis_client = get_redis_client()
    cached_data = get_from_cache( redis_client , PRODUCTS_CACHE_KEY )
    if cached_data:
        return [Product(**item) for item in cached_data]

    query = "SELECT * FROM STOCK.PRODUCTS"

    where = []
    params = []

    if is_discontinued is not None:
        where.append("IS_DISCONTINUED = ?")
        params.append(is_discontinued)
    if dosage_form:
        where.append("DOSAGE_FORM = ?")
        params.append(dosage_form)
    if pack_unit:
        where.append("PACK_UNIT = ?")
        params.append(pack_unit)
    if therapeutic_class:
        where.append("PACK_UNIT = ?")
        params.append(therapeutic_class)
    if where:
        query += " WHERE " + " AND ".join(where)

    result = await execute_query_json(query, tuple(params))
    dict = json.loads(result)
    if not dict:
        raise HTTPException(status_code=404, detail="Products catalog not found")

    store_in_cache( redis_client , PRODUCTS_CACHE_KEY , dict , CACHE_TTL )
    return [Product(**item) for item in dict]

async def create_product( product_data: Product ) -> Product:
    insert_query = """
        INSERT INTO STOCK.PRODUCTS(
		BRAND_NAME
		, MANUFACTURER
		, PRICE_INR
		, IS_DISCONTINUED
		, DOSAGE_FORM
		, PACK_SIZE
		, PACK_UNIT
		, NUM_ACTIVE_INGREDIENTS
		, PRIMARY_INGREDIENT
		, PRIMARY_STRENGTH
		, ACTIVE_INGREDIENTS
		, THERAPEUTIC_CLASS
		, PACKAGING_RAW
		, MANUFACTURER_RAW
        ) VALUES(
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """

    params = [
        product_data.brand_name
        , product_data.manufacturer
        , product_data.price_inr
        , product_data.is_discontinued
        , product_data.dosage_form
        , product_data.pack_size
        , product_data.pack_unit
        , product_data.num_active_ingredients
        , product_data.primary_ingredient
        , product_data.primary_strength
        , product_data.active_ingredients
        , product_data.therapeutic_class
        , product_data.packaging_raw
        , product_data.manufacturer_raw
    ]

    insert_result = await execute_query_json( insert_query , params, needs_commit=True )

    max_id_query = " SELECT ISNULL( MAX(PRODUCT_ID) , 0 ) MAX_ID FROM STOCK.PRODUCTS "
    max_id_result = await execute_query_json(max_id_query)
    max_id_data = json.loads(max_id_result)
    if not max_id_data or len(max_id_data) == 0:
        raise HTTPException( status_code=500 , detail="Failed DB connection" )    

    new_id = max_id_data[0].get( 'max_id' , 0 )

    created_object = Product(
        product_id = new_id,
        brand_name = product_data.brand_name,
        manufacturer = product_data.manufacturer,
        price_inr = product_data.price_inr,
        is_discontinued = product_data.is_discontinued,
        dosage_form = product_data.dosage_form,
        pack_size = product_data.pack_size,
        pack_unit = product_data.pack_unit,
        num_active_ingredients = product_data.num_active_ingredients,
        primary_ingredient = product_data.primary_ingredient,
        primary_strength = product_data.primary_strength,
        active_ingredients = product_data.active_ingredients,
        therapeutic_class = product_data.therapeutic_class,
        packaging_raw = product_data.packaging_raw,
        manufacturer_raw = product_data.manufacturer_raw
    )

    redis_client = get_redis_client()
    cache_deleted = delete_cache( redis_client, PRODUCTS_CACHE_KEY )

    return created_object
