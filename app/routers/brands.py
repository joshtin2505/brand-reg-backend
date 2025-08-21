from typing import List, Any

from fastapi import APIRouter, HTTPException

from app.db import get_client
from app.schemas.brand import Brand, BrandCreate, BrandUpdate


router = APIRouter(prefix="/brands", tags=["brands"])


def _row_to_brand(row: Any) -> Brand:
	"""Convert a DB row (dict-like, object-like, or tuple) to a Brand model."""
	# dict-like
	if isinstance(row, dict):
		return Brand(
			id=row.get("id"),
			brand=row.get("brand"),
			holder=row.get("holder"),
			status=row.get("status"),
			created_at=row.get("created_at"),
		)
	# attribute-like (e.g., Row with .id)
	try:
		return Brand(
			id=getattr(row, "id"),
			brand=getattr(row, "brand"),
			holder=getattr(row, "holder"),
			status=getattr(row, "status"),
			created_at=getattr(row, "created_at", None),
		)
	except Exception:
		# tuple-like fallback by positional order from our SELECT
		return Brand(
			id=row[0],
			brand=row[1],
			holder=row[2],
			status=row[3],
			created_at=row[4] if len(row) > 4 else None,
		)


@router.post("", response_model=Brand, status_code=201)
async def create_brand(payload: BrandCreate):
	client = get_client()
	try:
		res = await client.execute(
			"INSERT INTO brands (brand, holder, status) VALUES (?, ?, ?) RETURNING id, brand, holder, status, created_at;",
			[payload.brand, payload.holder, payload.status],
		)
		row = res.rows[0]
		return _row_to_brand(row)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Brand])
async def list_brands():
	client = get_client()
	try:
		res = await client.execute(
			"SELECT id, brand, holder, status, created_at FROM brands ORDER BY id ASC;"
		)
		return [_row_to_brand(row) for row in res.rows]
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get("/{brand_id}", response_model=Brand)
async def get_brand(brand_id: int):
	client = get_client()
	try:
		res = await client.execute(
			"SELECT id, brand, holder, status, created_at FROM brands WHERE id = ?;",
			[brand_id],
		)
		print(res.rows)
		if not res.rows:
			raise HTTPException(status_code=404, detail="Brand not found")
		return _row_to_brand(res.rows[0])
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.put("/{brand_id}", response_model=Brand)
async def update_brand(brand_id: int, payload: BrandUpdate):
	client = get_client()
	try:
		# Fetch current record
		res = await client.execute(
			"SELECT id, brand, holder, status, created_at FROM brands WHERE id = ?;",
			[brand_id],
		)
		if not res.rows:
			raise HTTPException(status_code=404, detail="Brand not found")
		current = res.rows[0]
		# Extract current values robustly
		def _get(r, key, idx):
			try:
				return r[key]
			except Exception:
				try:
					return getattr(r, key)
				except Exception:
					return r[idx]

		new_brand = payload.brand or _get(current, "brand", 1)
		new_holder = payload.holder or _get(current, "holder", 2)
		new_status = payload.status or _get(current, "status", 3)

		res2 = await client.execute(
			"""
			UPDATE brands
			SET brand = ?, holder = ?, status = ?
			WHERE id = ?
			RETURNING id, brand, holder, status, created_at;
			""",
			[new_brand, new_holder, new_status, brand_id],
		)
		return _row_to_brand(res2.rows[0])
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{brand_id}", status_code=204)
async def delete_brand(brand_id: int):
	client = get_client()
	try:
		res = await client.execute(
			"DELETE FROM brands WHERE id = ? RETURNING id;", [brand_id]
		)
		if not res.rows:
			raise HTTPException(status_code=404, detail="Brand not found")
		return
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
