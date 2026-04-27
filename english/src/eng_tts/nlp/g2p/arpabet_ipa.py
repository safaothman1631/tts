"""ARPABET ↔ IPA bidirectional mapping."""
from __future__ import annotations

# Reduced ARPABET → IPA. Stress markers (0/1/2) stripped.
ARPA_TO_IPA = {
    # Vowels
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ",
    "AY": "aɪ", "EH": "ɛ", "ER": "ɝ", "EY": "eɪ",
    "IH": "ɪ", "IY": "i", "OW": "oʊ", "OY": "ɔɪ",
    "UH": "ʊ", "UW": "u", "AX": "ə",
    # Consonants
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "F": "f",
    "G": "ɡ", "HH": "h", "JH": "dʒ", "K": "k", "L": "l",
    "M": "m", "N": "n", "NG": "ŋ", "P": "p", "R": "ɹ",
    "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "V": "v",
    "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ",
}


def arpabet_to_ipa(phonemes: list[str], with_stress: bool = True) -> str:
    """Convert ARPABET token list to an IPA string."""
    parts: list[str] = []
    for p in phonemes:
        stress = ""
        base = p
        if p and p[-1].isdigit():
            base, mark = p[:-1], p[-1]
            if with_stress:
                if mark == "1":
                    stress = "ˈ"
                elif mark == "2":
                    stress = "ˌ"
        ipa = ARPA_TO_IPA.get(base, "")
        if ipa:
            parts.append(stress + ipa)
        else:
            parts.append(base.lower())
    return "".join(parts)


_IPA_TO_ARPA = {v: k for k, v in ARPA_TO_IPA.items()}


def ipa_to_arpabet(ipa: str) -> list[str]:
    """Best-effort IPA → ARPABET. Greedy longest-match."""
    out: list[str] = []
    i = 0
    keys_sorted = sorted(_IPA_TO_ARPA, key=len, reverse=True)
    while i < len(ipa):
        if ipa[i] in {"ˈ", "ˌ", " ", ".", "-"}:
            i += 1
            continue
        for k in keys_sorted:
            if ipa.startswith(k, i):
                out.append(_IPA_TO_ARPA[k])
                i += len(k)
                break
        else:
            i += 1
    return out
