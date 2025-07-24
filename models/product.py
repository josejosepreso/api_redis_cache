from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Product(BaseModel):
    product_id: int = Field(
        ge = 1,
        description = "Auto-generated ID"
    )

    brand_name: Optional['str'] = Field(
        default = None
    )

    manufacturer: Optional['str'] = Field(
        default = None
    )

    price_inr: Optional['float'] = Field(
        default = None
    )

    is_discontinued: Optional['bool'] = Field(
        default = None
    )

    dosage_form: Optional['str'] = Field(
        default = None
    )
    
    pack_size: Optional['int'] = Field(
        default = None
    )

    pack_unit: Optional['str'] = Field(
        default = None
    )

    num_active_ingredients: Optional['int'] = Field(
        default = None
    )

    primary_ingredient: Optional['str'] = Field(
        default = None
    )

    primary_strength: Optional['str'] = Field(
        default = None
    )

    active_ingredients: Optional['str'] = Field(
        default = None
    )

    therapeutic_class: Optional['str'] = Field(
        default = None
    )

    packaging_raw: Optional['str'] = Field(
        default = None
    )

    manufacturer_raw: Optional['str'] = Field(
        default = None
    )
