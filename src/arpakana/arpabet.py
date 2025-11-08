"""ARPAbet phoneme helpers (optimized without sacrificing clarity)."""

from __future__ import annotations
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# --------------------
# small fast helpers / precompiled stuff
# --------------------

_DIGITS = "0123456789"
_VOWELS = {"a", "i", "u", "e", "o"}
_KANA_RE = re.compile(r"^[\u30A0-\u30FFー]+$")

def _normalize_phoneme(token: str) -> str:
    """Upper-case token, stripping trailing stress digits (e.g. AH0 → AH)."""
    return token.strip().upper().rstrip(_DIGITS)

_VOWEL_MAP: dict[str, tuple[str, ...]] = {
    "AA": ("a",),
    "AE": ("a",),
    "AH": ("a",),
    "AO": ("o",),
    "AW": ("a", "ウ"),
    "AX": ("a",),
    "AXR": ("a", "ー"),  # 互換性維持（事前に "AX R" へ展開する想定）
    "AY": ("a", "イ"),
    "EH": ("e",),
    "ER": ("a", "ー"),   # 互換性維持（事前に "AX R" へ展開する想定）
    "EY": ("e", "イ"),
    "IH": ("i",),
    "IX": ("i",),
    "IY": ("i", "ー"),
    "OW": ("o", "ウ"),
    "OY": ("o", "イ"),
    "OH": ("o", "ー"),
    "UH": ("u",),
    "UW": ("u", "ー"),
    "UX": ("u",),
}

_CV_TABLE: dict[tuple[str, ...], dict[str, str]] = {
    # Single consonants
    (): {"a": "ア", "i": "イ", "u": "ウ", "e": "エ", "o": "オ"},
    ("B",): {"a": "バ", "i": "ビ", "u": "ブ", "e": "ベ", "o": "ボ"},
    ("CH",): {"a": "チャ", "i": "チ", "u": "チュ", "e": "チェ", "o": "チョ"},
    ("D",): {"a": "ダ", "i": "ディ", "u": "ドゥ", "e": "デ", "o": "ド"},
    ("DH",): {"a": "ダ", "i": "ディ", "u": "ドゥ", "e": "デ", "o": "ド"},
    ("DX",): {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    ("F",): {"a": "ファ", "i": "フィ", "u": "フ", "e": "フェ", "o": "フォ"},
    ("G",): {"a": "ガ", "i": "ギ", "u": "グ", "e": "ゲ", "o": "ゴ"},
    ("HH",): {"a": "ハ", "i": "ヒ", "u": "フ", "e": "ヘ", "o": "ホ"},
    ("JH",): {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    ("K",): {"a": "カ", "i": "キ", "u": "ク", "e": "ケ", "o": "コ"},
    ("L",): {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    ("M",): {"a": "マ", "i": "ミ", "u": "ム", "e": "メ", "o": "モ"},
    ("N",): {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ"},
    ("NG",): {"a": "ンガ", "i": "ンギ", "u": "ング", "e": "ンゲ", "o": "ンゴ"},
    ("NX",): {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ"},
    ("P",): {"a": "パ", "i": "ピ", "u": "プ", "e": "ペ", "o": "ポ"},
    ("R",): {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    ("S",): {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},
    ("SH",): {"a": "シャ", "i": "シ", "u": "シュ", "e": "シェ", "o": "ショ"},
    ("T",): {"a": "タ", "i": "ティ", "u": "トゥ", "e": "テ", "o": "ト"},
    ("TH",): {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},
    ("V",): {"a": "ヴァ", "i": "ヴィ", "u": "ヴ", "e": "ヴェ", "o": "ヴォ"},
    ("W",): {"a": "ワ", "i": "ウィ", "u": "ウ", "e": "ウェ", "o": "ウォ"},
    ("Y",): {"a": "ヤ", "i": "イ", "u": "ユ", "e": "イェ", "o": "ヨ"},
    ("Z",): {"a": "ザ", "i": "ズィ", "u": "ズ", "e": "ゼ", "o": "ゾ"},
    ("ZH",): {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    # Combined consonants
    ("K", "Y"): {"a": "キャ", "i": "キィ", "u": "キュ", "e": "キェ", "o": "キョ"},
    ("G", "Y"): {"a": "ギャ", "i": "ギィ", "u": "ギュ", "e": "ギェ", "o": "ギョ"},
    ("S", "Y"): {"a": "シャ", "i": "シィ", "u": "シュ", "e": "シェ", "o": "ショ"},
    ("Z", "Y"): {"a": "ジャ", "i": "ジィ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    ("T", "Y"): {"a": "チャ", "i": "チィ", "u": "チュ", "e": "チェ", "o": "チョ"},
    ("D", "Y"): {"a": "ジャ", "i": "ジィ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    ("H", "Y"): {"a": "ヒャ", "i": "ヒィ", "u": "ヒュ", "e": "ヒェ", "o": "ヒョ"},
    ("B", "Y"): {"a": "ビャ", "i": "ビィ", "u": "ビュ", "e": "ビェ", "o": "ビョ"},
    ("P", "Y"): {"a": "ピャ", "i": "ピィ", "u": "ピュ", "e": "ピェ", "o": "ピョ"},
    ("M", "Y"): {"a": "ミャ", "i": "ミィ", "u": "ミュ", "e": "ミェ", "o": "ミョ"},
    ("R", "Y"): {"a": "リャ", "i": "リィ", "u": "リュ", "e": "リェ", "o": "リョ"},
    ("L", "Y"): {"a": "リャ", "i": "リィ", "u": "リュ", "e": "リェ", "o": "リョ"},
    ("N", "Y"): {"a": "ニャ", "i": "ニィ", "u": "ニュ", "e": "ニェ", "o": "ニョ"},
    ("F", "Y"): {"a": "フャ", "i": "フィ", "u": "フュ", "e": "フェ", "o": "フョ"},
    ("T", "S"): {"a": "ツァ", "i": "ツィ", "u": "ツ", "e": "ツェ", "o": "ツォ"},
}

_STANDALONE_CONSONANTS: dict[tuple[str, ...], tuple[str, ...]] = {
    ("B",): ("ブ",),
    ("CH",): ("チ",),
    ("D",): ("ド",),
    ("DH",): ("ズ",),
    ("DX",): ("ル",),
    ("F",): ("フ",),
    ("G",): ("グ",),
    ("JH",): ("ジ",),
    ("K",): ("ク",),
    ("L",): ("ル",),
    ("M",): ("ン",),
    ("N",): ("ン",),
    ("NG",): ("ン",),
    ("NX",): ("ン",),
    ("P",): ("プ",),
    ("R",): ("ア",),
    ("S",): ("ス",),
    ("SH",): ("シュ",),
    ("T",): ("トゥ",),
    ("TH",): ("ス",),
    ("V",): ("ヴ",),
    ("Z",): ("ズ",),
    ("ZH",): ("ジュ",),
    ("T", "S"): ("ツ",),
}

_SOKUON_CLUSTERS: set[tuple[str, ...]] = {
    ("CH",),
    ("SH",),
    ("JH",),
    ("ZH",),
    ("T", "S"),
}

_SILENCES = {"", "SIL", "SP", "SPN"}

_KNOWN_PHONEMES: set[str] = (
    set(_VOWEL_MAP)
    | {symbol for key in _CV_TABLE for symbol in key}
    | {symbol for cluster in _STANDALONE_CONSONANTS for symbol in cluster}
    | _SILENCES
)

# --------------------
# precomputed maps for fast sequence replacement
# --------------------

# 子音群 + 母音 → カナ の完全展開（最長一致のため長さ別も保持）
_CV_SEQ2KANA: dict[tuple[str, ...], str] = {}
for cons, table in _CV_TABLE.items():
    for vcore, kana in table.items():
        _CV_SEQ2KANA[(*cons, vcore)] = kana
_R_SEQ2KANA: dict[tuple[str, ...], str] = {k:v for k, v in _CV_SEQ2KANA.items() if k and k[0] == "R"}  # R単独用

# 照合に使う長さ一覧を降順で（最長一致）
_CV_LENGTHS_DESC = sorted({len(k) for k in _CV_SEQ2KANA.keys()}, reverse=True)
_R_LENGTHS_DESC = sorted({len(k) for k in _R_SEQ2KANA.keys()}, reverse=True)
_STANDALONE_LENGTHS_DESC = sorted({len(k) for k in _STANDALONE_CONSONANTS.keys()}, reverse=True)

def _expand_vowel_with_r(phoneme: list[str]) -> list[str]:
    """Expand 'ER'/'AXR' → 'AX R'."""
    replaced: list[str] = []
    for p in phoneme:
        if p == "ER" or p == "AXR":
            replaced.extend(("AX", "R"))
        else:
            replaced.append(p)
    return replaced

def _normalize_vowel(phoneme: list[str]) -> list[str]:
    """Normalize vowel phonemes with context-sensitive tweaks."""
    out: list[str] = []
    for p in phoneme:

        if p in _VOWEL_MAP:
            out.extend(_VOWEL_MAP[p])  # tupleのままでOK
        else:
            out.append(p)
    return out

def _insert_sokuon(phoneme: list[str]) -> list[str]:
    """Insert sokuon 'ッ' before certain clusters when preceded by a vowel."""
    if not phoneme:
        return []
    result = [phoneme[0]]
    # 最長一致のため長さ降順
    cluster_lengths = sorted({len(c) for c in _SOKUON_CLUSTERS}, reverse=True)

    i = 1
    n = len(phoneme)
    while i < n:
        for L in cluster_lengths:
            if i + L <= n and tuple(phoneme[i:i+L]) in _SOKUON_CLUSTERS and result[-1] in _VOWELS:
                result.append("ッ")
                break
        result.append(phoneme[i])
        i += 1
    return result

def _apply_cv_r_rules(tokens: list[str]) -> list[str]:
    """Apply 'R' phoneme conversion rules based on preceding vowel."""
    out: list[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for L in _R_LENGTHS_DESC:
            if i + L <= n:
                key = tuple(tokens[i:i+L])
                kana = _R_SEQ2KANA.get(key)
                if kana is not None:
                    out.append(kana)
                    i += L
                    matched = True
                    break
        if not matched:
            out.append(tokens[i])
            i += 1
    return out
def _apply_standalone_r_rules(tokens: list[str]) -> list[str]:
    if not tokens:
        return []
    out: list[str] = []
    out.append("ア" if tokens[0] == "R" else tokens[0])
    for i, phoneme in enumerate(tokens[1:], start=1):
        if phoneme == "R":
            if tokens[i - 1] in {"a", "o"}:
                out.append("ー")
            elif tokens[i - 1] == "ー":
                pass
            else:
                out.append("ア")
        else:
            out.append(phoneme)        
    return out

def _apply_r_rules(tokens: list[str]) -> list[str]:
    """Token-wise longest-match replacement for 'R' phoneme."""
    after_cv = _apply_cv_r_rules(tokens)
    after_standalone = _apply_standalone_r_rules(after_cv)
    return after_standalone
    
def _apply_cv_rules(tokens: list[str]) -> list[str]:
    """Token-wise longest-match replacement using precomputed CV map."""
    out: list[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for L in _CV_LENGTHS_DESC:
            if i + L <= n:
                key = tuple(tokens[i:i+L])
                kana = _CV_SEQ2KANA.get(key)
                if kana is not None:
                    out.append(kana)
                    i += L
                    matched = True
                    break
        if not matched:
            out.append(tokens[i])
            i += 1
    return out
def _apply_standalone_consonant_rules(tokens: list[str]) -> list[str]:
    """Replace standalone consonant sequences with kana."""
    out: list[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for L in _STANDALONE_LENGTHS_DESC:
            if i + L <= n:
                key = tuple(tokens[i:i+L])
                kana = _STANDALONE_CONSONANTS.get(key)
                if kana is not None:
                    out.extend(kana)
                    i += L
                    matched = True
                    break
        if not matched:
            out.append(tokens[i])
            i += 1
    return out

def _convert_unknown_token(phoneme: list[str], unknown: str) -> list[str]:
    """Convert unknown (非カナ) を unknown に置換。"""
    return [p if _KANA_RE.match(p) else unknown for p in phoneme]

def _delete_continuous_long_marks(phoneme: list[str]) -> list[str]:
    """Collapse consecutive 'ー'."""
    result: list[str] = []
    prev_long = False
    for p in phoneme:
        if p == "ー":
            if prev_long:
                continue
            prev_long = True
        else:
            prev_long = False
        result.append(p)
    return result

def arpabet_to_kana(phonemes: str | Iterable[str], *, unknown: str = "?") -> str:
    """Convert ARPAbet phoneme tokens (space separated) to Katakana."""
    tokens = phonemes.split() if isinstance(phonemes, str) else list(phonemes)
    normalized = [_normalize_phoneme(t) for t in tokens if t.strip()]

    expanded_r = _expand_vowel_with_r(normalized)
    normalized_vowels = _normalize_vowel(expanded_r)
    with_sokuon = _insert_sokuon(normalized_vowels)
    after_r = _apply_r_rules(with_sokuon)
    after_cv = _apply_cv_rules(after_r)
    after_standalone = _apply_standalone_consonant_rules(after_cv)
    with_unknowns = _convert_unknown_token(after_standalone, unknown)
    cleaned = _delete_continuous_long_marks(with_unknowns)

    return "".join(cleaned)


__all__ = ["arpabet_to_kana"]