import json
import logging
from typing import Optional

from fastapi import HTTPException

from utils.database import execute_query_json
from utils.redis_cache import get_redis_client, store_in_cache, get_from_cache, delete_cache
from models.product import Product

logger = logging.getLogger(__name__)

GET_PRODUCTS_QUERY = "SELECT TOP 150000 * FROM STOCK.PRODUCTS"

PRODUCTS_CACHE_KEY = "catalog"
ALL_PRODUCTS_CACHE_KEY = f"{PRODUCTS_CACHE_KEY}:all"
CACHE_TTL = 30 * 60

def __get_products_list(items: dict) -> list[Product]:
    return [Product(**item) for item in items]

async def get_all_products() -> list[Product]:
    redis_client = get_redis_client()
    cached_data = get_from_cache( redis_client , ALL_PRODUCTS_CACHE_KEY )
    if cached_data:
        return __get_products_list(cached_data)

    result = await execute_query_json(GET_PRODUCTS_QUERY)
    dict = json.loads(result)
    if not dict:
        raise HTTPException(status_code = 404, detail = "Products catalog not found")

    store_in_cache( redis_client , ALL_PRODUCTS_CACHE_KEY , dict , CACHE_TTL )
    return __get_products_list(dict)

async def get_products(dosage_form: str, is_discontinued: bool, pack_unit: str, therapeutic_class: str) -> list[Product]:
    categories = [is_discontinued, dosage_form, pack_unit, therapeutic_class]

    if all(map(lambda a: a is None, categories)):
        return get_all_products()

    query = GET_PRODUCTS_QUERY + " WHERE "

    where = []
    cache_key = PRODUCTS_CACHE_KEY

    if is_discontinued is not None:
        where.append("IS_DISCONTINUED = ?")
        cache_key += f":is_discontinued={ is_discontinued }"
    if dosage_form:
        where.append("DOSAGE_FORM = ?")
        cache_key += f":dosage_form={ dosage_form }"
    if pack_unit:
        where.append("PACK_UNIT = ?")
        cache_key += f":pack_unit={ pack_unit }"
    if therapeutic_class:
        where.append("THERAPEUTIC_CLASS = ?")
        cache_key += f":therapeutic_class={ therapeutic_class }"
    if where:
        query += " AND ".join(where)

    params = list(filter(lambda a: a is not None, categories))

    redis_client = get_redis_client()
    cached_data = get_from_cache( redis_client , cache_key )
    if cached_data:
        return __get_products_list(cached_data)

    result = await execute_query_json(query, params)
    dict = json.loads(result)
    if not dict:
        raise HTTPException(status_code = 404, detail = "Products catalog not found")

    store_in_cache( redis_client , cache_key , dict , CACHE_TTL )
    return __get_products_list(dict)

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

    insert_result = await execute_query_json( insert_query , params, needs_commit = True )

    max_id_query = " SELECT ISNULL( MAX(PRODUCT_ID) , 0 ) MAX_ID FROM STOCK.PRODUCTS "
    max_id_result = await execute_query_json(max_id_query)
    max_id_data = json.loads(max_id_result)
    if not max_id_data or len(max_id_data) == 0:
        raise HTTPException( status_code = 500 , detail = "Failed DB connection" )    

    new_id = max_id_data[0].get( 'max_id' , 0 ) + 1

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

    cache_key = PRODUCTS_CACHE_KEY
    cache_key += f":is_discontinued={ product_data.is_discontinued }"
    cache_key += f":dosage_form={ product_data.dosage_form }"
    cache_key += f":pack_unit={ product_data.pack_unit }"
    cache_key += f":therapeutic_class={ product_data.therapeutic_class }"

    cache_key_cats = cache_key.replace("catalog:", "").split(":")

    def matches_any_key(curr_cats, stored_cats) -> bool:
        return any(map(lambda t: t[0] == t[1], [(curr, stored) for curr in curr_cats for stored in stored_cats]))

    redis_client = get_redis_client()

    for stored_key in redis_client.scan_iter("catalog:*"):
        if matches_any_key(cache_key_cats, stored_key.replace("catalog:", "").split(":")):
            cache_deleted = delete_cache( redis_client, stored_key )

    return created_object
