from typing import Optional, Literal, Union
from pydantic import BaseModel, ConfigDict, Field

class BooleanSchema(BaseModel):
    type: Literal["boolean"] = "boolean"
    default: Optional[bool] = None
    description: Optional[str] = None
    title: Optional[str] = None
    
    model_config = ConfigDict(extra='allow')

class StringSchema(BaseModel):
    type: Literal["string"] = "string"
    default: Optional[str] = None
    description: Optional[str] = None
    format: Optional[Literal["uri", "email", "date", "date-time"]] = None
    maxLength: Optional[int] = None
    minLength: Optional[int] = None
    title: Optional[str] = None

    model_config = ConfigDict(extra='allow')

class NumberSchema(BaseModel):
    type: Literal["number", "integer"]
    default: Optional[float] = None
    description: Optional[str] = None
    maximum: Optional[float] = None
    minimum: Optional[float] = None
    title: Optional[str] = None

    model_config = ConfigDict(extra='allow')

class TitledSingleSelectEnumSchema(BaseModel):
    type: Literal["string"] = "string"
    oneOf: list[dict[str, str]] # Structure: {const: string, title: string}
    default: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None

    model_config = ConfigDict(extra='allow')

class UntitledSingleSelectEnumSchema(BaseModel):
    type: Literal["string"] = "string"
    enum: list[str]
    default: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None

    model_config = ConfigDict(extra='allow')

SingleSelectEnumSchema = Union[UntitledSingleSelectEnumSchema, TitledSingleSelectEnumSchema]

class TitledMultiSelectEnumSchema(BaseModel):
    type: Literal["array"] = "array"
    items: dict[str, list[dict[str, str]]] # Structure: {anyOf: [{const: string, title: string}]}
    default: Optional[list[str]] = None
    description: Optional[str] = None
    maxItems: Optional[int] = None
    minItems: Optional[int] = None
    title: Optional[str] = None

    model_config = ConfigDict(extra='allow')

class UntitledMultiSelectEnumSchema(BaseModel):
    type: Literal["array"] = "array"
    items: dict[str, dict[str, list[str]]] # Structure: {type: "string", enum: [...]}
    default: Optional[list[str]] = None
    description: Optional[str] = None
    maxItems: Optional[int] = None
    minItems: Optional[int] = None
    title: Optional[str] = None

    model_config = ConfigDict(extra='allow')

MultiSelectEnumSchema = Union[UntitledMultiSelectEnumSchema, TitledMultiSelectEnumSchema]

# Legacy support
class LegacyTitledEnumSchema(BaseModel):
    type: Literal["string"] = "string"
    enum: list[str]
    enumNames: Optional[list[str]] = None
    default: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None

    model_config = ConfigDict(extra='allow')

EnumSchema = Union[SingleSelectEnumSchema, MultiSelectEnumSchema, LegacyTitledEnumSchema]

PrimitiveSchemaDefinition = Union[StringSchema, NumberSchema, BooleanSchema, EnumSchema]
