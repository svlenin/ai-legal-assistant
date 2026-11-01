import json
import os
import asyncio
from pathlib import Path
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal, Base, engine
from app.models.legal_provision import LegalProvision


async def seed_knowledge_base():
    seed_file = Path(__file__).parent / "legal_knowledge_seed.json"
    if not seed_file.exists():
        print(f"Seed file not found at {seed_file}")
        return

    with open(seed_file, "r", encoding="utf-8") as f:
        provisions_data = json.load(f)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        for item in provisions_data:
            stmt = select(LegalProvision).where(LegalProvision.identifier == item["identifier"])
            result = await session.execute(stmt)
            existing = result.scalars().first()
            if not existing:
                provision = LegalProvision(
                    source_type=item["source_type"],
                    act_or_document_name=item["act_or_document_name"],
                    identifier=item["identifier"],
                    title=item["title"],
                    summary_simple=item["summary_simple"],
                    full_text=item["full_text"],
                    chapter_or_part=item.get("chapter_or_part"),
                    domain_category=item["domain_category"],
                    keywords=item.get("keywords", []),
                    provenance_source_url=item["provenance_source_url"]
                )
                session.add(provision)
        await session.commit()
    print(f"Successfully seeded {len(provisions_data)} legal knowledge provisions.")


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
