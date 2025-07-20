import json
import logging
from typing import Optional

from fastapi import HTTPException

from utils.database import execute_query_json
from utils.redis_cache import get_redis_client, store_in_cache, get_from_cache, delete_cache
from models.product import Product

logger = logging.getLogger(__name__)

SERIES_CACHE_KEY = "product:stock:all"
CACHE_TTL = 30 * 60

async def get_products() -> list[Product]:
    redis_client = get_redis_client()
    cached_data = get_from_cache( redis_client , SERIES_CACHE_KEY )
    if cached_data:
        return [Product(**item) for item in cached_data]

    query = "select * from stock.products"
    query = "select top 200 * from stock.products"
    result = await execute_query_json(query)
    dict = json.loads(result)
    if not dict:
        raise HTTPException(status_code=404, detail="Series catalog not found")

    store_in_cache( redis_client , SERIES_CACHE_KEY , dict , CACHE_TTL )
    return [Product(**item) for item in dict]

async def create_product( serie_data: Product ) -> Product:
    max_id_query = " select isnull( max(id) , 0 ) max_id from stock.products "
    max_id_result = await execute_query_json(max_id_query)
    max_id_data = json.loads(max_id_result)
    if not max_id_data or len(max_id_data) == 0:
        raise HTTPException( status_code=500 , detail="Failed DB connection" )    

    current_max_id = max_id_data[0].get( 'max_id' , 0 )
    new_id = current_max_id + 1

    insert_query = """
        insert into stock.products(
		product_id
		, brand_name
		, manufacturer
		, price_inr
		, is_discontinued
		, dosage_form
		, pack_size
		, pack_unit
		, num_active_ingredients
		, primary_ingredient
		, primary_strength
		, active_ingredients
		, therapeutic_class
		, packaging_raw
		, manufacturer_raw
        ) values(
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """

    params = [
        new_id
        , product_data.brand_name
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
    cache_deleted = delete_cache( redis_client, SERIES_CACHE_KEY )

    return created_object
