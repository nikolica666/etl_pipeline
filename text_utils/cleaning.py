import re

# --- Precompiled regex patterns for performance ---
INVISIBLE_BREAKS = re.compile(r'[\u00AD\u200B\u200C\u200D\u2060\uFEFF]', flags=re.UNICODE)
HYPHENS = r'[-\u2010\u2011]'  # normal hyphen, typographic hyphen, non-breaking hyphen

# modes
PAT_CONSERVATIVE = re.compile(rf'(\w){HYPHENS}\n\s*(\w)', flags=re.UNICODE)
PAT_AGGRESSIVE = re.compile(rf'(\w+){HYPHENS}\n\s*(\w+)', flags=re.UNICODE)
PAT_BALANCED = re.compile(rf'(\w{{2,}}){HYPHENS}\n\s*(\w{{2,}})', flags=re.UNICODE)
PAT_NAIVE = re.compile(rf'{HYPHENS}\n\s*', flags=re.UNICODE)
PAT_REMAINING = re.compile(rf'{HYPHENS}\n\s*', flags=re.UNICODE)

def fix_word_breaks(text: str, mode: str = "balanced") -> str:
    """
    Fixes word breaks caused by hyphenation across lines.

    Modes:
      - 'conservative': joins only lowercase + lowercase splits (safest)
      - 'balanced': joins when both sides have at least 2 letters (default)
      - 'aggressive': joins all word–word splits (riskier)
      - 'naive': removes any hyphen + newline without validation

    Works with Croatian letters (č, ć, ž, š, đ) and other Unicode alphabets.
    """
    # 1) remove invisible break characters
    text = INVISIBLE_BREAKS.sub('', text)

    # 2) join broken words based on mode
    if mode == "conservative":
        text = PAT_CONSERVATIVE.sub(r'\1\2', text)
    elif mode == "aggressive":
        text = PAT_AGGRESSIVE.sub(r'\1\2', text)
    elif mode == "naive":
        text = PAT_NAIVE.sub('', text)
    else:  # balanced
        text = PAT_BALANCED.sub(r'\1\2', text)

    # 3) for any remaining hyphen+newline combos, keep hyphen and drop newline
    text = PAT_REMAINING.sub('-', text)

    return text

def clean_text(text):

    # 1. Normalize line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 2. Fix hyphenation (informa- tion -> information)
    text = fix_word_breaks(text)

    # 3. Replace control characters with a space (preserves word separation)
    text = re.sub(r'[\x00-\x1F]+', ' ', text)
 
    # 4. Replace sequences of 5+ dots with a space ('main menu')
    # THIS CAN BE IMPROVED (e.g. currently trailing numbers are left)
    #text = re.sub(r'\.{5,}', ' ', text)
    text = re.sub(r'\.{6,}\s*\d*\s*', ' ', text)

    # 5. Replace single line breaks with a space, keep double line breaks
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    # 6. Normalize whitespace ([\s+,' '] entire doc is one big paragraph, hurts embed and retrieve)
    text = re.sub(r'[ \t]+', ' ', text)

    # 7. Remove bracketed references [1], [2], etc.
    text = re.sub(r'\[\d+\]', '', text)

    # 8. Normalize dashes and quotes
    text = re.sub(r'[–—−]', '-', text)      # dashes
    text = re.sub(r'[“”]', '"', text)       # double quotes
    text = re.sub(r"[‘’]", "'", text)       # single quotes

    # 9. Unicode normalization
    # THIS WILL REMOVE SUBSCRIPTS/SUPERSCRIPTS - NOT USING ATM
    # text = unicodedata.normalize("NFKC", text)

    # 10. Remove universal PDF page markers like [PAGE 11]
    text = re.sub(r'\[PAGE \d+\]', '', text)

    return text.strip()

