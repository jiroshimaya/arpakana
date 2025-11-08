"""ARPAbet phoneme helpers."""

from __future__ import annotations
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def _normalize_phoneme(token: str) -> str:
    """Upper-case token, stripping trailing stress digits (e.g. ``AH0`` → ``AH``)."""

    trimmed = token.strip().upper()
    while trimmed and trimmed[-1].isdigit():
        trimmed = trimmed[:-1]
    return trimmed


_VOWEL_MAP: dict[str, tuple[str, ...]] = {
    "AA": ("a",),
    "AE": ("a",),
    "AH": ("a",),
    "AO": ("o",),
    "AW": ("a", "ウ"),
    "AX": ("a",),
    "AXR": ("a", "ー"), # 事前に"AX R"に変換するため、不要だが、念の為に残す
    "AY": ("a", "イ"),
    "EH": ("e",),
    "ER": ("a", "ー"), # 事前に"AX R"に変換するため、不要だが、念の為に残す
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

# Mapping for standalone consonants (not combined with vowels)
# This includes final consonants, consonant clusters, and cluster-fill special cases
_STANDALONE_CONSONANTS: dict[tuple[str, ...], str] = {
    # Single consonants
    ("B",): "ブ",
    ("CH",): "チ",
    ("D",): "ド",
    ("DH",): "ズ",
    ("DX",): "ル",
    ("F",): "フ",
    ("G",): "グ",
    ("JH",): "ジ",
    ("K",): "ク",
    ("L",): "ル",
    ("M",): "ン",
    ("N",): "ン",
    ("NG",): "ン",
    ("NX",): "ン",
    ("P",): "プ",
    ("R",): "ー",
    ("S",): "ス",
    ("SH",): "シュ",
    ("T",): "トゥ",
    ("TH",): "ス",
    ("V",): "ヴ",
    ("Z",): "ズ",
    ("ZH",): "ジュ",
    # Consonant clusters
    ("T", "S"): "ツ",
}

# Consonant clusters for sokuon insertion
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

def _expand_vowel_with_r(phoneme: list[str]) -> list[str]:
    """Expand 'ER' phonemes into 'AX R' sequences."""
    # "ER"や"AXR"を単語境界・空白で正規表現置換
    _map = {"ER": "AX R", "AXR": "AX R"}
    replaced = []
    for p in phoneme:
        if p in _map:
            replaced.extend(_map[p].split())
        else:
            replaced.append(p)
    return replaced

def _normalize_vowel(phoneme: list[str]) -> list[str]:
    """Normalize vowel phonemes in the input string."""

    _map = {k: list(v) for k, v in _VOWEL_MAP.items()}
    replaced: list[str] = []

    for idx, p in enumerate(phoneme):
        prev_token = phoneme[idx - 1] if idx > 0 else ""
        next_token = phoneme[idx + 1] if idx + 1 < len(phoneme) else ""

        if p == "AA" and prev_token == "W":
            replaced.append("o")
            continue

        if p == "AH" and next_token in {"N", "NG", "NX"}:
            replaced.append("o")
            continue

        if p in _map:
            replaced.extend(_map[p])
        else:
            replaced.append(p)

    return replaced

def _insert_sokuon(phoneme: list[str]) -> list[str]:
    """Insert sokuon markers before consonant clusters."""
    if not phoneme:
        return []

    result = [phoneme[0]]
    sokuon_clusters = [list(cluster) for cluster in sorted(_SOKUON_CLUSTERS, key=len, reverse=True)]
    vowels = {"a", "i", "u", "e", "o"}

    for i in range(1, len(phoneme)):
        for cluster in sokuon_clusters:
            cluster_len = len(cluster)
            if phoneme[i : i + cluster_len] == cluster and phoneme[i - 1] in vowels:
                result.append("ッ")
                break
        result.append(phoneme[i])

    return result

def _apply_cv_rules(phoneme: list[str]) -> list[str]:
    phoneme_string = " ".join(phoneme)
    _map = {}
    for key, table in _CV_TABLE.items():
        for vowel_core, kana in table.items():
            _map[" ".join(key + (vowel_core,))] = kana
    _sorted_keys = sorted(_map.keys(), key=lambda x: -len(x.split()))
    for k in _sorted_keys:
        phoneme_string = re.sub(rf"\b{k}\b", _map[k], phoneme_string)

    return phoneme_string.split()

def _apply_standalone_consonant_rules(phoneme: list[str]) -> list[str]:
    phoneme_string = " ".join(phoneme)
    _map_items = sorted(_STANDALONE_CONSONANTS.items(), key=lambda x: -len(x[0]))
    for key, kana in _map_items:
        phoneme_string = re.sub(rf"\b{' '.join(key)}\b", kana, phoneme_string)
    return phoneme_string.split()

def _convert_unknown_token(phoneme: list[str], unknown: str) -> list[str]:
    """Convert unknown tokens in the phoneme list."""
    # カナ（カタカナ1文字以上）以外はunknownに変換
    kana_pattern = re.compile(r"^[\u30A0-\u30FFー]+$")
    return [p if kana_pattern.match(p) else unknown for p in phoneme]

def _delete_continuous_long_marks(phoneme: list[str]) -> list[str]:
    """Delete continuous long mark 'ー'."""
    result = []
    prev_was_long = False
    for p in phoneme:
        if p == "ー":
            if prev_was_long:
                continue
            prev_was_long = True
        else:
            prev_was_long = False
        result.append(p)
    return result

def arpabet_to_kana(phonemes: str | Iterable[str], *, unknown: str = "?") -> str:
    """Convert ARPAbet phoneme tokens (space separated) to Katakana."""

    tokens = phonemes.split() if isinstance(phonemes, str) else list(phonemes)

    normalized = [_normalize_phoneme(token) for token in tokens if token.strip()]

    expanded_r = _expand_vowel_with_r(normalized)
    normalized_vowels = _normalize_vowel(expanded_r)
    with_sokuon = _insert_sokuon(normalized_vowels)
    after_cv = _apply_cv_rules(with_sokuon)
    after_standalone = _apply_standalone_consonant_rules(after_cv)
    with_unknowns = _convert_unknown_token(after_standalone, unknown)
    cleaned = _delete_continuous_long_marks(with_unknowns)

    return "".join(cleaned)


__all__ = ["arpabet_to_kana"]
