"""
Internal helper — takes raw_cards_{doc_id}.json (card content without UUIDs/timestamps)
and writes finalized cards/{doc_id}.json with proper KnowledgeCard objects.

Usage:
    python scripts/_finalize_cards.py <doc_id>
"""
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import scripts.manifest as manifest_utils

CARDS_DIR = Path("./cards")
PARSED_DIR = Path("./parsed")
MANIFEST_PATH = PARSED_DIR / "manifest.json"


def main(doc_id: str) -> None:
    raw_path = CARDS_DIR / f"raw_{doc_id}.json"
    if not raw_path.exists():
        print(f"ERROR: {raw_path} not found")
        sys.exit(1)

    raw_cards = json.loads(raw_path.read_text(encoding="utf-8"))

    now = datetime.now(timezone.utc).isoformat()
    finalized = []
    for rc in raw_cards:
        card = {
            "card_id": str(uuid.uuid4()),
            "chunk_id": rc["chunk_id"],
            "doc_id": rc["doc_id"],
            "book_title": rc["book_title"],
            "author": rc.get("author"),
            "file_path": rc["file_path"],
            "page_ref": f"pp. {rc['page_start']}–{rc['page_end']}",
            "page_start": rc["page_start"],
            "page_end": rc["page_end"],
            "card_type": rc["card_type"],
            "title": rc["title"],
            "body": rc["body"],
            "tags": rc["tags"],
            "created_at": now,
            "model_used": "claude-sonnet-4-6",
        }
        finalized.append(card)

    out_path = CARDS_DIR / f"{doc_id}.json"
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(finalized, indent=2, ensure_ascii=False), encoding="utf-8")

    # Update manifest
    manifest = manifest_utils.load(MANIFEST_PATH)
    manifest_utils.update_stats(manifest, doc_id, {"card_count": len(finalized)})
    manifest_utils.mark_done(manifest, doc_id, "cards_generated")
    manifest_utils.save(MANIFEST_PATH, manifest)

    # Clean up raw file
    raw_path.unlink()

    print(f"Wrote {len(finalized)} cards → {out_path}")
    print(f"Manifest updated: cards_generated=true")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/_finalize_cards.py <doc_id>")
        sys.exit(1)
    main(sys.argv[1])
