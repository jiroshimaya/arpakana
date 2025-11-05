"""ARPAbet phoneme helpers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


def _normalize_phoneme(token: str) -> str:
    """Upper-case token, stripping trailing stress digits (e.g. ``AH0`` → ``AH``)."""

    trimmed = token.strip().upper()
    while trimmed and trimmed[-1].isdigit():
        trimmed = trimmed[:-1]
    return trimmed


@dataclass(frozen=True)
class VowelShape:
    """Describes a vowel row plus optional trailing kana suffix."""

    core: str
    suffix: str = ""
    standalone: str | None = None


_STANDALONE_CORE = {
    "a": "ア",
    "i": "イ",
    "u": "ウ",
    "e": "エ",
    "o": "オ",
}

_VOWELS: dict[str, VowelShape] = {
    "AA": VowelShape("a"),
    "AE": VowelShape("a"),
    "AH": VowelShape("a"),
    "AO": VowelShape("o", "ー"),
    "AW": VowelShape("a", "ウ"),
    "AX": VowelShape("a"),
    "AXR": VowelShape("a", "ー"),
    "AY": VowelShape("a", "イ"),
    "EH": VowelShape("e"),
    "ER": VowelShape("a", "ー"),
    "EY": VowelShape("e", "イ"),
    "IH": VowelShape("i"),
    "IX": VowelShape("i"),
    "IY": VowelShape("i", "ー"),
    "OW": VowelShape("o", "ウ"),
    "OY": VowelShape("o", "イ"),
    "OH": VowelShape("o", "ー"),
    "UH": VowelShape("u"),
    "UW": VowelShape("u", "ー"),
    "UX": VowelShape("u"),
}

_CV_TABLE: dict[str, dict[str, str]] = {
    "": {"a": "ア", "i": "イ", "u": "ウ", "e": "エ", "o": "オ"},
    "B": {"a": "バ", "i": "ビ", "u": "ブ", "e": "ベ", "o": "ボ"},
    "CH": {"a": "チャ", "i": "チ", "u": "チュ", "e": "チェ", "o": "チョ"},
    "D": {"a": "ダ", "i": "ディ", "u": "ドゥ", "e": "デ", "o": "ド"},
    "DH": {"a": "ダ", "i": "ディ", "u": "ドゥ", "e": "デ", "o": "ド"},
    "DX": {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    "F": {"a": "ファ", "i": "フィ", "u": "フ", "e": "フェ", "o": "フォ"},
    "G": {"a": "ガ", "i": "ギ", "u": "グ", "e": "ゲ", "o": "ゴ"},
    "HH": {"a": "ハ", "i": "ヒ", "u": "フ", "e": "ヘ", "o": "ホ"},
    "JH": {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    "K": {"a": "カ", "i": "キ", "u": "ク", "e": "ケ", "o": "コ"},
    "L": {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    "M": {"a": "マ", "i": "ミ", "u": "ム", "e": "メ", "o": "モ"},
    "N": {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ"},
    "NG": {"a": "ンガ", "i": "ンギ", "u": "ング", "e": "ンゲ", "o": "ンゴ"},
    "NX": {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ"},
    "P": {"a": "パ", "i": "ピ", "u": "プ", "e": "ペ", "o": "ポ"},
    "R": {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    "S": {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},
    "SH": {"a": "シャ", "i": "シ", "u": "シュ", "e": "シェ", "o": "ショ"},
    "T": {"a": "タ", "i": "ティ", "u": "トゥ", "e": "テ", "o": "ト"},
    "TH": {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},
    "V": {"a": "ヴァ", "i": "ヴィ", "u": "ヴ", "e": "ヴェ", "o": "ヴォ"},
    "W": {"a": "ワ", "i": "ウィ", "u": "ウ", "e": "ウェ", "o": "ウォ"},
    "Y": {"a": "ヤ", "i": "イ", "u": "ユ", "e": "イェ", "o": "ヨ"},
    "Z": {"a": "ザ", "i": "ズィ", "u": "ズ", "e": "ゼ", "o": "ゾ"},
    "ZH": {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
}

_COMBINED_CV_TABLE: dict[tuple[str, ...], dict[str, str]] = {
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
}

_FINAL_CONSONANTS = {
    "B": "ブ",
    "CH": "ッチ",
    "D": "ド",
    "DH": "ズ",
    "DX": "ル",
    "F": "フ",
    "G": "グ",
    "JH": "ッジ",
    "K": "ク",
    "L": "ル",
    "M": "ム",
    "N": "ン",
    "NG": "ング",
    "P": "プ",
    "R": "ー",
    "S": "ス",
    "SH": "シュ",
    "T": "トゥ",
    "TH": "ス",
    "V": "ヴ",
    "Z": "ズ",
    "ZH": "ジュ",
}

_SILENCES = {"", "SIL", "SP", "SPN"}

_CLUSTER_FILL_SPECIAL = {
    "N": "ン",
    "NX": "ン",
}

_KNOWN_PHONEMES: set[str] = (
    set(_VOWELS)
    | set(_CV_TABLE)
    | set(_FINAL_CONSONANTS)
    | _SILENCES
    | set(_CLUSTER_FILL_SPECIAL)
)


def _segment_unknown(token: str) -> list[str] | None:
    if not token:
        return []

    def _search(start: int) -> list[str] | None:
        if start == len(token):
            return []
        for end in range(len(token), start, -1):
            piece = token[start:end]
            if piece in _KNOWN_PHONEMES:
                tail = _search(end)
                if tail is not None:
                    return [piece, *tail]
        return None

    return _search(0)


def _map_consonant_vowel(consonant: str, vowel: VowelShape) -> str | None:
    table = _CV_TABLE.get(consonant)
    if not table:
        return None
    base = table.get(vowel.core)
    if not base:
        return None
    return base + vowel.suffix


def _map_cluster_to_vowel(consonants: list[str], vowel: VowelShape) -> str | None:
    if not consonants:
        return None
    if len(consonants) == 1:
        return _map_consonant_vowel(consonants[0], vowel)

    table = _COMBINED_CV_TABLE.get(tuple(consonants))
    if table is None:
        return None
    base = table.get(vowel.core)
    if base is None:
        return None
    return base + vowel.suffix


def _cluster_fill(consonant: str) -> str | None:
    special = _CLUSTER_FILL_SPECIAL.get(consonant)
    if special is not None:
        return special

    table = _CV_TABLE.get(consonant)
    if not table:
        return None
    return table.get("u")


def _map_standalone_vowel(vowel: VowelShape, unknown: str) -> str:
    if vowel.standalone is not None:
        return vowel.standalone + vowel.suffix

    base = _STANDALONE_CORE.get(vowel.core)
    if base is None:
        return unknown
    return base + vowel.suffix


def arpabet_to_kana(phonemes: str | Iterable[str], *, unknown: str = "?") -> str:
    """Convert ARPAbet phoneme tokens (space separated) to Katakana."""

    if isinstance(phonemes, str):
        tokens = phonemes.split()
    else:
        tokens = list(phonemes)

    normalized = [_normalize_phoneme(token) for token in tokens if token.strip()]

    expanded: list[str] = []
    for token in normalized:
        if token in _KNOWN_PHONEMES:
            expanded.append(token)
            continue
        parts = _segment_unknown(token)
        if parts:
            expanded.extend(parts)
            continue
        expanded.append(token)

    normalized = []
    for token in expanded:
        if token == "ER":
            normalized.extend(["AX", "R"])
        else:
            normalized.append(token)

    kana: list[str] = []
    idx = 0
    total = len(normalized)

    while idx < total:
        token = normalized[idx]

        if token in _SILENCES:
            idx += 1
            continue

        vowel = _VOWELS.get(token)
        if vowel:
            kana.append(_map_standalone_vowel(vowel, unknown))
            idx += 1
            continue

        lookahead = idx + 1
        while lookahead < total and normalized[lookahead] not in _VOWELS:
            lookahead += 1

        if lookahead < total:
            consonant_cluster = normalized[idx:lookahead]
            vowel_shape = _VOWELS[normalized[lookahead]]

            mapped_cluster = _map_cluster_to_vowel(consonant_cluster, vowel_shape)
            if mapped_cluster is not None:
                kana.append(mapped_cluster)
                idx = lookahead + 1
                continue

            if len(consonant_cluster) > 1:
                filler = _cluster_fill(token)
                kana.append(filler or unknown)
                idx += 1
                continue

            mapped_single = _map_consonant_vowel(token, vowel_shape)
            kana.append(mapped_single or unknown)
            idx = lookahead + 1
            continue

        final = _FINAL_CONSONANTS.get(token, unknown)
        if final == "ー" and kana and kana[-1].endswith("ー"):
            idx += 1
            continue
        kana.append(final)
        idx += 1

    return "".join(kana)


__all__ = ["arpabet_to_kana"]
