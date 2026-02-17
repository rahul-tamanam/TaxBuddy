"""
Create searchable chunks from treaty and visa JSON for RAG.
Output has the same schema as PDF chunks so they can be merged and embedded.
"""

import json
from pathlib import Path


def treaty_to_chunks(treaty_data: dict) -> list:
    """Convert treaty_lookup.json entries to chunk dicts (same schema as document chunks)."""
    chunks = []
    for country, info in treaty_data.items():
        if info.get("has_treaty"):
            conditions = "\n".join(f"  - {c}" for c in info.get("conditions", []))
            text = (
                f"Tax treaty: United States and {country}. "
                f"Student/trainee article: {info.get('student_article', 'N/A')}. "
                f"Student exemption: {info.get('student_exemption', 'N/A')}. "
                f"Duration: {info.get('duration', 'N/A')}. "
                f"Effective date: {info.get('effective_date', 'N/A')}. "
                f"Conditions for exemption: {conditions}. "
                f"Source: {info.get('source', 'Publication 901')}."
            )
        else:
            text = (
                f"{country} does not have a tax treaty with the United States. "
                f"No treaty-based exemptions apply. Source: {info.get('source', 'Publication 901')}."
            )
        text = text.strip()
        words = len(text.split())
        chunks.append({
            "text": text,
            "metadata": {
                "source": "treaty_lookup",
                "page": country,
                "chunk_index": len(chunks) + 1,
                "context": f"Tax treaty - {country}",
                "char_count": len(text),
                "word_count": words,
            },
            "chunk_id": f"treaty_lookup_{country.replace(' ', '_')}",
        })
    return chunks


def visa_to_chunks(visa_data: dict) -> list:
    """Convert visa_types.json entries to chunk dicts (same schema as document chunks)."""
    chunks = []
    for visa_type, info in visa_data.items():
        income = "; ".join(info.get("typical_income", []))
        forms = ", ".join(info.get("required_forms", []))
        text = (
            f"Visa type {visa_type}: {info.get('description', '')}. "
            f"Exempt individual: {info.get('exempt_individual', '')}. "
            f"FICA exempt: {info.get('fica_exempt', '')}. "
            f"Exempt duration: {info.get('exempt_duration', 'N/A')}. "
            f"Typical income: {income}. "
            f"Required forms: {forms}. "
            f"Notes: {info.get('notes', '')}."
        )
        text = text.strip()
        words = len(text.split())
        chunks.append({
            "text": text,
            "metadata": {
                "source": "visa_types",
                "page": visa_type,
                "chunk_index": len(chunks) + 1,
                "context": f"Visa - {visa_type}",
                "char_count": len(text),
                "word_count": words,
            },
            "chunk_id": f"visa_types_{visa_type.replace('-', '_')}",
        })
    return chunks


def create_supplementary_chunks(
    processed_dir: str = "data/processed",
    output_dir: str = "data/chunked",
) -> Path:
    """Build supplementary chunks from treaty and visa JSON; write to supplementary_chunks.json."""
    processed_dir = Path(processed_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    chunk_index_offset = 0

    treaty_file = processed_dir / "treaty_lookup.json"
    if treaty_file.exists():
        with open(treaty_file, "r", encoding="utf-8") as f:
            treaty_data = json.load(f)
        treaty_chunks = treaty_to_chunks(treaty_data)
        for c in treaty_chunks:
            c["metadata"]["chunk_index"] = chunk_index_offset + c["metadata"]["chunk_index"]
        chunk_index_offset += len(treaty_chunks)
        all_chunks.extend(treaty_chunks)

    visa_file = processed_dir / "visa_types.json"
    if visa_file.exists():
        with open(visa_file, "r", encoding="utf-8") as f:
            visa_data = json.load(f)
        visa_chunks = visa_to_chunks(visa_data)
        for c in visa_chunks:
            c["metadata"]["chunk_index"] = chunk_index_offset + c["metadata"]["chunk_index"]
        all_chunks.extend(visa_chunks)

    out_file = output_dir / "supplementary_chunks.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    return out_file


def main():
    out = create_supplementary_chunks()
    print(f"✅ Wrote {len(json.load(open(out, encoding='utf-8')))} supplementary chunks to {out}")


if __name__ == "__main__":
    main()
