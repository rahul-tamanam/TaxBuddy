"""
Text preprocessing for IRS tax documents.
Cleans extracted PDF text so it is readable and useful for the LLM and retrieval.
"""

import re
import unicodedata
from typing import Optional


# ---------------------------------------------------------------------------
# IRS-specific patterns (headers, footers, print metadata)
# ---------------------------------------------------------------------------

# Print/production metadata (often at start of page)
IRS_PRINT_METADATA = re.compile(
    r"(?:Userid|Schema|Leadpct|Pt\.\s*size|Draft\s+Ok\s+to\s+Print|AH\s+XSL/XML)\s*:?\s*[^\n]*\n?",
    re.IGNORECASE,
)
IRS_FILEID_LINE = re.compile(
    r"Fileid:\s*[^\n]*\n",
    re.IGNORECASE,
)
IRS_PAGE_OF = re.compile(
    r"Page\s+\d+\s+of\s+\d+\s+[^\n]*\n?",
    re.IGNORECASE,
)
IRS_MUST_REMOVE = re.compile(
    r"The\s+type\s+and\s+rule\s+above\s+prints\s+on\s+all\s+proofs[^\n]*MUST\s+be\s+removed\s+before\s+printing\.\s*\n?",
    re.IGNORECASE,
)
IRS_PUB_PAGE_FOOTER = re.compile(
    r"Publication\s+\d+\s*\(\d{4}\)\s*(?:Catalog\s+Number\s+[\dA-Z]+\s*)?(?:\w+\s+\d+[\s\-]*)?\d*\s*\n?",
    re.IGNORECASE,
)
IRS_PUB_CHAPTER_FOOTER = re.compile(
    r"Publication\s+\d+\s*\(\d{4}\)\s+Chapter\s+\d+[^\n]*\n?",
    re.IGNORECASE,
)
IRS_INSTRUCTIONS_FOOTER = re.compile(
    r"Instructions\s+for\s+Form\s+\d+[A-Z\-]*\s*\(\d{4}\)\s+\d*\s*\n?",
    re.IGNORECASE,
)
IRS_DEPT_TREASURY = re.compile(
    r"Department\s+of\s+the\s+Treasury\s*[^\n]*\n?Internal\s+Revenue\s+Service[^\n]*\n?",
    re.IGNORECASE,
)
IRS_CATALOG_LINE = re.compile(
    r"Catalog\s+Number\s+[\dA-Z]+\s*\n?",
    re.IGNORECASE,
)
# TOC lines: "Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . 1"
IRS_TOC_DOTS = re.compile(
    r"^[^\n]*\s+\.\s+(\.\s*){3,}\s*\d+\s*$",
    re.MULTILINE,
)
# Standalone "Page N" or "Chapter N" at start of line (repeated footer fragments)
IRS_STANDALONE_PAGE = re.compile(
    r"^(?:Page|Chapter)\s+\d+\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def _fix_hyphenated_line_breaks(text: str) -> str:
    """
    Join words broken across lines by hyphen, e.g. "deter-\\nmine" -> "determine".
    Only joins when the hyphen is at end of line and the next line continues the word.
    """
    # Pattern: word characters, hyphen, newline, optional space, word continuation
    def join_hyphen(match: re.Match) -> str:
        before = match.group(1)
        after = match.group(2)
        return before + after

    return re.sub(
        r"([a-zA-Z0-9]+)-\s*\n\s*([a-zA-Z][a-zA-Z0-9]*)",
        join_hyphen,
        text,
    )


def _join_soft_line_breaks(text: str) -> str:
    """
    Join lines that are clearly continuations (line ends without . ? ! : ; and next line
    starts with lowercase or digit). Preserves paragraph breaks (blank lines) and
    list/section starts (next line starts with capital or bullet).
    """
    lines = text.split("\n")
    if not lines:
        return text
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip empty lines (keep as paragraph break)
        if not line.strip():
            result.append("")
            i += 1
            continue
        # Look ahead: if next line is not empty and current doesn't end with sentence end,
        # and next line starts with lowercase or digit, join with space
        while i + 1 < len(lines):
            next_line = lines[i + 1]
            if not next_line.strip():
                break
            stripped = line.rstrip()
            if not stripped:
                break
            last_char = stripped[-1]
            first_next = next_line.lstrip()
            if not first_next:
                break
            first_char = first_next[0]
            # Sentence end or colon/semicolon: do not join
            if last_char in ".?!:;":
                break
            # Next line starts with capital and looks like new sentence (optional)
            if first_char.isupper() and last_char in ")\"":
                break
            # Join: current line continues on next (e.g. "income\nfrom sources")
            if first_char.islower() or first_char.isdigit() or last_char in "(-'\"":
                line = line.rstrip() + " " + next_line.lstrip()
                i += 1
                continue
            break
        result.append(line)
        i += 1
    return "\n".join(result)


def _clean_table_blocks(text: str) -> str:
    """
    - Remove empty [TABLE]...[/TABLE] blocks.
    - Normalize table row separators and trim cell content.
    - Optionally remove table blocks that are exact duplicates of surrounding body text
      (we do a simple pass: if a [TABLE] block's inner text is very similar to the
      preceding few lines, we could drop it; for now we only remove empty and trim).
    """
    # Remove empty tables
    text = re.sub(r"\[\s*TABLE\s*\]\s*\[\s*/\s*TABLE\s*\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[\s*TABLE\s*\]\s*\[\s*TABLE\s*\]", "[TABLE]", text, flags=re.IGNORECASE)

    # Normalize multiple newlines inside tables to single newline
    def clean_one_table(match: re.Match) -> str:
        inner = match.group(1)
        # Trim each line and collapse multiple spaces inside cells
        lines = [re.sub(r"\s+", " ", line).strip() for line in inner.split("\n") if line.strip()]
        return "[TABLE]\n" + "\n".join(lines) + "\n[/TABLE]\n"

    text = re.sub(
        r"\[TABLE\](.*?)\[/TABLE\]",
        clean_one_table,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return text


def _normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces, normalize newlines, trim."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n +", "\n", text)
    return text.strip()


def _unicode_and_typography(text: str) -> str:
    """Normalize unicode and fix common typography."""
    # NFKC helps with compatibility characters
    text = unicodedata.normalize("NFKC", text)
    # Ligatures
    text = text.replace("\ufb01", "fi")  # ﬁ
    text = text.replace("\ufb02", "fl")  # ﬂ
    # Dashes
    text = text.replace("\u2013", "-")  # en dash
    text = text.replace("\u2014", " - ")  # em dash
    # Smart quotes
    text = text.replace("\u2018", "'")
    text = text.replace("\u2019", "'")
    text = text.replace("\u201c", '"')
    text = text.replace("\u201d", '"')
    return text


def preprocess_irs_text(
    text: str,
    *,
    fix_hyphenation: bool = True,
    join_soft_breaks: bool = True,
    remove_irs_metadata: bool = True,
    clean_tables: bool = True,
    normalize_whitespace: bool = True,
    unicode_fixes: bool = True,
) -> str:
    """
    Clean IRS document text for better LLM and retrieval use.

    Args:
        text: Raw extracted text from a page or chunk.
        fix_hyphenation: Join words broken across lines (e.g. "deter-\\nmine").
        join_soft_breaks: Join lines that are continuations of the same sentence.
        remove_irs_metadata: Remove headers, footers, print metadata.
        clean_tables: Remove empty [TABLE] blocks and normalize table text.
        normalize_whitespace: Collapse spaces and normalize newlines.
        unicode_fixes: Apply unicode normalization and typography fixes.

    Returns:
        Cleaned text.
    """
    if not text or not text.strip():
        return text

    if unicode_fixes:
        text = _unicode_and_typography(text)

    if remove_irs_metadata:
        text = IRS_PRINT_METADATA.sub("", text)
        text = IRS_FILEID_LINE.sub("", text)
        text = IRS_PAGE_OF.sub("", text)
        text = IRS_MUST_REMOVE.sub("", text)
        text = IRS_PUB_PAGE_FOOTER.sub("", text)
        text = IRS_PUB_CHAPTER_FOOTER.sub("", text)
        text = IRS_INSTRUCTIONS_FOOTER.sub("", text)
        text = IRS_DEPT_TREASURY.sub("", text)
        text = IRS_CATALOG_LINE.sub("", text)
        text = IRS_TOC_DOTS.sub("", text)
        # Remove standalone "Page N" / "Chapter N" lines (footer fragments)
        text = IRS_STANDALONE_PAGE.sub("", text)
        # Legacy: form codes in middle of text
        text = re.sub(r"\(Form\s+\d+[A-Z\-]*\)", "", text)
        text = re.sub(r"Cat\.\s*No\.\s*\d+[A-Z]?", "", text, flags=re.IGNORECASE)

    if fix_hyphenation:
        text = _fix_hyphenated_line_breaks(text)

    if join_soft_breaks:
        text = _join_soft_line_breaks(text)

    if clean_tables:
        text = _clean_table_blocks(text)

    if normalize_whitespace:
        text = _normalize_whitespace(text)

    return text


def preprocess_chunk_text(chunk_text: str) -> str:
    """
    Apply the same preprocessing to a single chunk (e.g. when loading from
    all_chunks.json for re-embedding or when building chunks from already-
    processed pages). Safe to call on already-cleaned text (idempotent enough).
    """
    return preprocess_irs_text(chunk_text)
