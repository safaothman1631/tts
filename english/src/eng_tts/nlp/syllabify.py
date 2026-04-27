"""Maximum-onset / sonority syllabification."""
from __future__ import annotations

ARPABET_VOWELS = {
    "AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY",
    "IH", "IY", "OW", "OY", "UH", "UW",
}


def is_vowel(p: str) -> bool:
    return p.rstrip("012") in ARPABET_VOWELS


def syllabify_arpabet(phonemes: list[str]) -> list[list[str]]:
    """Split an ARPABET phoneme sequence into syllables.

    Heuristic: each syllable contains exactly one vowel; consonants are
    attached to the *following* vowel via maximum onset principle.
    """
    if not phonemes:
        return []
    syllables: list[list[str]] = []
    current: list[str] = []
    for p in phonemes:
        if is_vowel(p):
            if current and any(is_vowel(x) for x in current):
                # Split: keep last 1-2 consonants as next onset
                onset_len = 0
                for c in reversed(current):
                    if is_vowel(c):
                        break
                    onset_len += 1
                onset_len = min(onset_len, 2)  # max onset
                if onset_len > 0 and onset_len < len(current):
                    syllables.append(current[:-onset_len])
                    current = current[-onset_len:]
                else:
                    syllables.append(current)
                    current = []
            current.append(p)
        else:
            current.append(p)
    if current:
        syllables.append(current)
    return syllables
