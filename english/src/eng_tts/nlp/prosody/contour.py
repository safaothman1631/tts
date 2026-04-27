"""Heuristic pitch / duration / energy assignment per phoneme.

Used only when the acoustic backend is NOT end-to-end (FastSpeech2 path).
For VITS / StyleTTS2 these values are advisory.
"""
from __future__ import annotations

from ...core.frame import Token, Utterance
from ..syllabify import is_vowel

# Mean phoneme durations (seconds) for a neutral US English speaker
_MEAN_DUR = {
    "AA": 0.110, "AE": 0.105, "AH": 0.060, "AO": 0.115, "AW": 0.150,
    "AY": 0.150, "EH": 0.090, "ER": 0.110, "EY": 0.130, "IH": 0.070,
    "IY": 0.105, "OW": 0.130, "OY": 0.150, "UH": 0.090, "UW": 0.115,
    "B": 0.070, "CH": 0.110, "D": 0.060, "DH": 0.045, "F": 0.090,
    "G": 0.065, "HH": 0.055, "JH": 0.105, "K": 0.080, "L": 0.060,
    "M": 0.075, "N": 0.060, "NG": 0.085, "P": 0.090, "R": 0.055,
    "S": 0.110, "SH": 0.115, "T": 0.080, "TH": 0.085, "V": 0.060,
    "W": 0.060, "Y": 0.050, "Z": 0.085, "ZH": 0.090,
}
_DEFAULT_DUR = 0.080
_BASE_F0 = 130.0  # Hz for neutral male; female speakers scale up


def assign(utt: Utterance) -> Utterance:
    for tok in utt.tokens:
        if not tok.phonemes:
            continue
        durs: list[float] = []
        for p in tok.phonemes:
            base = p.rstrip("012")
            d = _MEAN_DUR.get(base, _DEFAULT_DUR)
            stress = int(p[-1]) if p[-1].isdigit() else 0
            if stress == 1:
                d *= 1.20
            elif stress == 2:
                d *= 1.05
            durs.append(d)
        tok.duration = sum(durs)
        # Pitch: stressed vowel +20%, unstressed -10%
        peak_stress = max((int(p[-1]) for p in tok.phonemes if p[-1].isdigit()), default=0)
        if peak_stress == 1:
            tok.pitch = _BASE_F0 * 1.20
        elif peak_stress == 2:
            tok.pitch = _BASE_F0 * 1.05
        else:
            tok.pitch = _BASE_F0 * 0.95
        # Energy: open vowels louder
        open_vowels = sum(1 for p in tok.phonemes if p.rstrip("012") in {"AA", "AE", "AO", "AW"})
        tok.energy = 0.7 + 0.05 * open_vowels
    return utt
