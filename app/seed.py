import asyncio
import argparse

from db import get_client, init_db


# Placeholder data to seed the database
SAMPLE_BRANDS = [
	("Joshtin.dev", "justin castro", "active"),
	("La casita de papel", "Sulays perez", "pending"),
	("Signa", "Daniel Estrada", "inactive"),
	("Dnamyk Solutions", "Silfredo Blanco", "active"),
	("Visual Studio Code", "Microsoft Inc", "active"),
]


async def seed(reset: bool = False):
	client = get_client()
	await init_db()

	if reset:
		# Danger: clears all data
		await client.execute("DELETE FROM brands;")

	# Only seed if empty
	try:
		res = await client.execute("SELECT COUNT(*) AS cnt FROM brands;")
		# libsql-python returns rows with dict-like access typically
		rows = getattr(res, "rows", None) or getattr(res, "data", None) or []
		count = 0
		if rows:
			row0 = rows[0]
			if isinstance(row0, dict):
				count = row0.get("cnt", 0)
			else:
				# Fallback for tuple-like rows
				count = row0[0] if row0 else 0
	except Exception:
		# If count fails, proceed to insert blindly
		count = 0

	if count > 0 and not reset:
		print(f"Brands table already has {count} rows. Skipping seeding.")
		return

	for brand, holder, status in SAMPLE_BRANDS:
		# Simple inserts; using literals to avoid parameter API differences
		stmt = (
			"INSERT INTO brands (brand, holder, status) "
			f"VALUES ('{brand}', '{holder}', '{status}');"
		)
		await client.execute(stmt)

	print(f"Inserted {len(SAMPLE_BRANDS)} placeholder brands.")

	# Best-effort: close client to avoid unclosed session warnings when used as a script
	try:
		close = getattr(client, "close", None)
		if close:
			# close may be async or sync depending on client implementation
			if asyncio.iscoroutinefunction(close):
				await close()
			else:
				close()
	except Exception:
		# Ignore if the client doesn't support close or already closed
		pass


def main():
	parser = argparse.ArgumentParser(description="Seed placeholder data into brands table.")
	parser.add_argument(
		"--reset",
		action="store_true",
		help="Delete all existing rows in brands before seeding.",
	)
	args = parser.parse_args()
	asyncio.run(seed(reset=args.reset))


if __name__ == "__main__":
	main()
