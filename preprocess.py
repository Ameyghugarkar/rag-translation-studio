import re
import importlib.util
import os
from symspellpy import SymSpell, Verbosity

# 1. INITIALIZE SYMSPELL

sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)

spec = importlib.util.find_spec("symspellpy")
if spec and spec.submodule_search_locations:
    dict_dir = spec.submodule_search_locations[0]
    dictionary_path = os.path.join(dict_dir, "frequency_dictionary_en_82_765.txt")
    if not sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1):
        raise FileNotFoundError(f"Dictionary failed to load from: {dictionary_path}")
else:
    raise ImportError("symspellpy not found. Run: pip install symspellpy")


# 2. CHARACTER MAPPING
OCR_TRANSLATE_TABLE = str.maketrans({
    '€': 'e', '7': 't',
})

def clean_ocr_tokens(text):
    """Replaces OCR symbols only inside word-like tokens. Protects emails and dates."""
    def replace_logic(match):
        word = match.group(0)

        # Protect emails
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', word):
            return word

        # Protect pure numbers and date-like tokens (16/03/2026, 2025-26, etc.)
        if re.match(r'^\d+([\/\-\.]\d+)*$', word):
            return word

        # Protect tokens that are mostly digits (e.g. "2026" "17")
        digit_ratio = sum(c.isdigit() for c in word) / len(word)
        if digit_ratio > 0.5:
            return word

        word = word.translate(OCR_TRANSLATE_TABLE)
        word = word.replace('rn', 'm')
        return word

    return re.sub(r'\b[a-zA-Z0-9€370@~]+\b', replace_logic, text)


# 3. PDF STRUCTURE CLEANING
def clean_pdf_structure(text):
    # Normalize unicode quotes
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')

    # Remove page number markers
    text = re.sub(r'\bpage\s*\d+(\s*of\s*\d+)?\.?\b', '', text, flags=re.IGNORECASE)

    # Fix line-break hyphens ONLY (preserves "well-known", "domain-specific")
    text = re.sub(r'(\w)-\n\s*(\w)', r'\1\2', text)

    # Collapse all whitespace/newlines to single space
    text = re.sub(r'\s+', ' ', text)

    # Remove stray non-alphanumeric characters attached to words (~ _ ` etc.)
    text = re.sub(r'(?<=[a-zA-Z])[~_`](?=[a-zA-Z])', '', text)

    # Fix stray punctuation splitting words (v-alue, of'ten, s_ignificant)
    text = re.sub(r'(?<=[a-zA-Z])[-_\'](?=[a-zA-Z])', '', text)
    return text.strip()


# 4. SPELL CHECK
def fast_spell_correct(text):
    words = text.split()
    corrected = []

    SPELL_CLEAN = str.maketrans({'3': 'e', '1': 'i', '0': 'o', '7': 't', '@': 'a'})

    for word in words:
        # Protect emails
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', word):
            corrected.append(word)
            continue

        # Skip short words, ALL-CAPS, pure numbers
        if len(word) < 6 or word.isupper() or re.match(r'^\d+$', word):
            corrected.append(word)
            continue

        # OCR symbols present — clean temp copy for lookup only
        if re.search(r'[310@7€]', word):
            temp = word.translate(SPELL_CLEAN)
            temp = re.sub(r'[^a-zA-Z]', '', temp)
            if len(temp) < 6:
                corrected.append(word)  # fragment, leave for LLM
                continue
            suggestions = sym_spell.lookup(temp, Verbosity.CLOSEST, max_edit_distance=2)
            corrected.append(suggestions[0].term if suggestions else word)
            continue

        # Normal spell check — scale edit distance by word length
        if word.isalpha():
            if len(word) <= 6:
                max_dist = 1   # short words: only 1 edit allowed
            elif len(word) <= 10:
                max_dist = 2   # medium words: 2 edits
            else:
                max_dist = 3   # long words: 3 edits

            suggestions = sym_spell.lookup(
                word, Verbosity.CLOSEST, max_edit_distance=max_dist
            )

            # Extra guard: only accept if suggestion is close enough
            if suggestions:
                suggestion = suggestions[0].term
                # Reject if edit distance ratio is too high (>30% of word changed)
                edit_dist = suggestions[0].distance
                if edit_dist / len(word) <= 0.3:
                    corrected.append(suggestion)
                else:
                    corrected.append(word)  # too different, leave for LLM
            else:
                corrected.append(word)
        else:
            corrected.append(word)

    return " ".join(corrected)



# 5. VALIDATION & CLASSIFICATION MODULE
#    Returns structured issues with severity levels:
#      - critical : will likely break translation accuracy
#      - warning  : may degrade quality, should be reviewed
#      - info     : minor / auto-fixable, logged for audit trail

# Severity levels ranked for sorting
SEVERITY_RANK = {"critical": 0, "warning": 1, "info": 2}

def validate(text: str) -> dict:
    """
    Analyses raw input text and returns a structured validation report.
    Call this BEFORE preprocess() to show the issue dashboard in the UI.

    Returns:
        {
            "has_critical": bool,
            "summary": {"critical": int, "warning": int, "info": int},
            "issues": [
                {
                    "type": str,        # category label
                    "severity": str,    # "critical" | "warning" | "info"
                    "msg": str,         # human-readable description
                    "detail": str       # optional: the offending snippet
                },
                ...
            ]
        }
    """
    issues = []

    # --- CRITICAL ISSUES ---

    # Empty or whitespace-only input
    if not text or not text.strip():
        issues.append({
            "type": "input",
            "severity": "critical",
            "msg": "Input text is empty.",
            "detail": ""
        })
        # No point running further checks
        return _build_report(issues)

    # Extremely short input (likely incomplete)
    if len(text.strip()) < 10:
        issues.append({
            "type": "input",
            "severity": "critical",
            "msg": "Input is too short to translate meaningfully (< 10 characters).",
            "detail": text.strip()
        })

    # High OCR noise ratio — if >30% of words look corrupted, flag as critical
    words = text.split()
    noise_words = [w for w in words if re.search(r'[€37@~]', w) and not re.match(r'.+@.+\..+', w)]
    if words and (len(noise_words) / len(words)) > 0.30:
        issues.append({
            "type": "ocr_noise",
            "severity": "critical",
            "msg": f"High OCR noise detected: {len(noise_words)}/{len(words)} words appear corrupted.",
            "detail": ", ".join(noise_words[:5]) + ("..." if len(noise_words) > 5 else "")
        })

    # --- WARNING ISSUES ---

    # Double spaces
    double_spaces = re.findall(r' {2,}', text)
    if double_spaces:
        issues.append({
            "type": "formatting",
            "severity": "warning",
            "msg": f"Double (or more) spaces found at {len(double_spaces)} location(s).",
            "detail": f"e.g. {repr(double_spaces[0])}"
        })

    # Repeated punctuation (!!!, ???, ...)
    repeated_punct = re.findall(r'[!?.]{2,}', text)
    if repeated_punct:
        issues.append({
            "type": "punctuation",
            "severity": "warning",
            "msg": f"Repeated punctuation found: {len(repeated_punct)} instance(s).",
            "detail": ", ".join(set(repeated_punct[:5]))
        })

    # Line-break hyphens (broken words from PDF extraction)
    broken_hyphens = re.findall(r'\w-\n\s*\w', text)
    if broken_hyphens:
        issues.append({
            "type": "structure",
            "severity": "warning",
            "msg": f"Line-break hyphenation found: {len(broken_hyphens)} broken word(s) will be joined.",
            "detail": ", ".join(broken_hyphens[:3])
        })

    # Mixed quote styles (both " and \u201c present — inconsistent formatting)
    has_straight = '"' in text or "'" in text
    has_curly = any(c in text for c in ['\u2018', '\u2019', '\u201c', '\u201d'])
    if has_straight and has_curly:
        issues.append({
            "type": "formatting",
            "severity": "warning",
            "msg": "Mixed straight and curly quotes detected — will be normalized.",
            "detail": ""
        })

    # Possible inconsistent terminology: same base word with different capitalisation
    # e.g. "contract" and "Contract" and "CONTRACT" all present
    word_forms = {}
    for w in re.findall(r'\b[a-zA-Z]{4,}\b', text):
        key = w.lower()
        word_forms.setdefault(key, set()).add(w)
    inconsistent = {k: v for k, v in word_forms.items() if len(v) > 1 and not all(x.isupper() for x in v)}
    if inconsistent:
        sample = list(inconsistent.items())[:3]
        detail = "; ".join(f"{k}: {sorted(v)}" for k, v in sample)
        issues.append({
            "type": "consistency",
            "severity": "warning",
            "msg": f"Inconsistent capitalisation for {len(inconsistent)} term(s) — may cause terminology drift.",
            "detail": detail
        })

    # --- INFO ISSUES ---

    # Page number markers (auto-removed by cleaner)
    page_markers = re.findall(r'\bpage\s*\d+(?:\s*of\s*\d+)?\b', text, re.IGNORECASE)
    if page_markers:
        issues.append({
            "type": "structure",
            "severity": "info",
            "msg": f"{len(page_markers)} page number marker(s) found — will be removed automatically.",
            "detail": ", ".join(page_markers[:3])
        })

    # Unicode quote characters (auto-normalised)
    if has_curly:
        issues.append({
            "type": "formatting",
            "severity": "info",
            "msg": "Unicode/curly quotes detected — will be normalised to straight quotes.",
            "detail": ""
        })

    # Individual OCR noise tokens (low count — auto-fixable)
    if 0 < len(noise_words) <= int(0.30 * max(len(words), 1)):
        issues.append({
            "type": "ocr_noise",
            "severity": "info",
            "msg": f"{len(noise_words)} likely OCR-corrupted token(s) detected — will be auto-corrected.",
            "detail": ", ".join(noise_words[:5])
        })

    return _build_report(issues)


def _build_report(issues: list) -> dict:
    """Sorts issues by severity and builds the final report dict."""
    issues.sort(key=lambda x: SEVERITY_RANK.get(x["severity"], 99))
    summary = {"critical": 0, "warning": 0, "info": 0}
    for issue in issues:
        summary[issue["severity"]] = summary.get(issue["severity"], 0) + 1
    return {
        "has_critical": summary["critical"] > 0,
        "summary": summary,
        "issues": issues
    }


# 6. PREPROCESS  ← app.py calls this; returns plain str (unchanged)
def preprocess(text: str) -> str:
    """
    Cleans and normalises text for downstream RAG/LLM translation.
    Returns a plain string — compatible with app.py pipeline.

    For the validation report (UI severity dashboard), call validate(text)
    separately BEFORE calling preprocess().
    """
    text = clean_pdf_structure(text)
    text = clean_ocr_tokens(text)
    text = text.lower()
    text = fast_spell_correct(text)
    text = re.sub(r'[!?.]{2,}', '.', text)
    return text.strip()


# TEST
if __name__ == "__main__":
    sample = """The nodern developnient of th€ th3ory requires a con-
sideration of the spactial d1mensions involved, Acc0rding to
Prof€ssor H. Smiths r3s3arch (2021) . the "v-alue of the r3sultant"
is of’ten d1stort3d by m1s-read1ngs in the d@ta set. [12]
we finds that the th€rmodynanric l0ss€s is n~egligible; but
the d€v€l0pni€nt are cruc1al for the s€rv€r_01@research.edu
s_ignificant d€grada7ion in the m€asur€-
m€nt pr0c€ss have been observed?? it is a m1stake.
    """

    print("VALIDATION REPORT:")
    report = validate(sample)
    print(f"  Critical: {report['summary']['critical']}  "
          f"Warning: {report['summary']['warning']}  "
          f"Info: {report['summary']['info']}")
    print()
    for issue in report["issues"]:
        label = f"[{issue['severity'].upper()}]"
        detail = f" → {issue['detail']}" if issue.get("detail") else ""
        print(f"  {label:12s}  [{issue['type']}]  {issue['msg']}{detail}")

    print()
    
    print(preprocess(sample))