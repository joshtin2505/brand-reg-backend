from typing import Literal, Optional
from pydantic import BaseModel, Field


class BrandCreate(BaseModel):
	brand: str = Field(..., min_length=1)
	holder: str = Field(..., min_length=1)
	status: Literal["active", "pending", "inactive"] = "pending"


class BrandUpdate(BaseModel):
	brand: Optional[str] = Field(None, min_length=1)
	holder: Optional[str] = Field(None, min_length=1)
	status: Optional[Literal["active", "pending", "inactive"]] = None


class Brand(BaseModel):
	id: int
	brand: str
	holder: str
	status: Literal["active", "pending", "inactive"]
	created_at: Optional[str] = None
