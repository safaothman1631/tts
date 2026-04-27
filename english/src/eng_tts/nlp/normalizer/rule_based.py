"""Production-grade rule-based text normalizer for English TTS.

Handles 18+ classes of "non-standard words" (NSW):
    cardinal, ordinal, year, decade, decimal, fraction, currency,
    percent, phone, time, date, range, math, units, url, email,
    hashtag, acronym, abbreviation, roman numeral, symbols, unicode,
    emoji.

Order of operations matters — multi-character entities are matched first
to prevent inner-fragment misclassification.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import inflect
from num2words import num2words

from ...core.interfaces import INormalizer
from ...core.registry import register

_LEX_DIR = Path(__file__).with_name("lexicons")


def _load_json(name: str) -> Any:
    with open(_LEX_DIR / name, encoding="utf-8") as f:
        return json.load(f)


_INFLECT = inflect.engine()
_ABBREV = _load_json("abbreviations.json")
_ACRO = _load_json("acronyms.json")
_CURR = _load_json("currencies.json")
_UNITS = _load_json("units.json")

_ACRO_WORD: set[str] = {a.upper() for a in _ACRO.get("word_style", [])}
_ACRO_SPELL: set[str] = {a.upper() for a in _ACRO.get("spell_style", [])}

# ─── Regex patterns (compiled once) ────────────────────────────────────────

# URL — http(s)://, www.
_RE_URL = re.compile(
    r"\b(?:https?://|www\.)[^\s<>\"']+",
    re.IGNORECASE,
)
_RE_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")

# Phone: +1-555-123-4567, (555) 123-4567, 555.123.4567
_RE_PHONE = re.compile(
    r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
)

# Time: 3:30, 3:30pm, 14:00
_RE_TIME = re.compile(
    r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?|AM|PM|am|pm)?\b",
    re.IGNORECASE,
)

# Date: 12/25/2024, 2024-12-25, Dec 25 2024, 25 December 2024
_RE_DATE_NUM = re.compile(
    r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b"
)
_RE_DATE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}

# Currency: $1,250.50, €10, £5.99, USD 100, 100 USD
_CURR_SYMBOLS = "".join(re.escape(k) for k in _CURR if len(k) == 1)
_RE_CURRENCY = re.compile(
    rf"([{_CURR_SYMBOLS}])\s*([\d,]+(?:\.\d+)?)|"
    rf"\b(USD|EUR|GBP|JPY|INR|KRW|RUB)\s*([\d,]+(?:\.\d+)?)|"
    rf"([\d,]+(?:\.\d+)?)\s*(USD|EUR|GBP|JPY|INR|KRW|RUB)\b"
)

# Percent: 25%, 25.5%
_RE_PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")

# Year alone (1000–2999, or 'XXs decade)
_RE_YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2}|21[0-9]{2})s?\b")
_RE_DECADE_APOS = re.compile(r"['\u2019](\d{2})s\b")

# Ordinal: 1st 2nd 3rd 21st 22nd
_RE_ORDINAL = re.compile(r"\b(\d+)(st|nd|rd|th)\b", re.IGNORECASE)

# Fraction: 1/2 3/4 (avoid dates by ordering)
_RE_FRACTION = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")

# Decimal: 3.14
_RE_DECIMAL = re.compile(r"\b(\d+)\.(\d+)\b")

# Range: 10-20
_RE_RANGE = re.compile(r"\b(\d+)\s*[-\u2013\u2014]\s*(\d+)\b")

# Math: 2+2=4, 5x3, 5*3
_RE_MATH = re.compile(r"(\d+)\s*([+\-*/×÷=<>])\s*(\d+)")

# Number with commas: 1,234,567
_RE_THOUSANDS = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")

# Plain integer
_RE_INT = re.compile(r"-?\b\d+\b")

# Roman numerals (after a name like "Henry VIII"). Conservative: only 1-3999 patterns.
_RE_ROMAN_AFTER_NAME = re.compile(
    r"\b([A-Z][a-z]+)\s+(M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))\b"
)

# Hashtag, mention
_RE_HASHTAG = re.compile(r"#(\w+)")
_RE_MENTION = re.compile(r"@(\w+)")

# Standalone all-caps token (potential acronym)
_RE_ALLCAPS = re.compile(r"\b([A-Z]{2,6})\b")

# Symbols to spell out (when surrounded by non-words)
_SYMBOL_MAP = {
    "&": " and ",
    "+": " plus ",
    "@": " at ",
    "*": " star ",
    "=": " equals ",
    "<": " less than ",
    ">": " greater than ",
    "/": " slash ",
    "\\": " backslash ",
    "^": " caret ",
    "~": " tilde ",
    "|": " pipe ",
    "_": " underscore ",
}

_DIGIT_WORD = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
}


def _spell_digits(s: str) -> str:
    return " ".join(_DIGIT_WORD.get(c, c) for c in s if c.isdigit())


def _num_words(n: int) -> str:
    return num2words(n, lang="en")


def _fnum_words(x: float) -> str:
    return num2words(x, lang="en")


def _ordinal_words(n: int) -> str:
    return num2words(n, to="ordinal", lang="en")


def _year_words(year: int) -> str:
    if 1100 <= year <= 1999:
        first, second = year // 100, year % 100
        if second == 0:
            return f"{_num_words(first)} hundred"
        if second < 10:
            return f"{_num_words(first)} oh {_num_words(second)}"
        return f"{_num_words(first)} {_num_words(second)}"
    if 2000 <= year <= 2009:
        return f"two thousand{'' if year == 2000 else ' ' + _num_words(year - 2000)}"
    if 2010 <= year <= 2099:
        return f"twenty {_num_words(year - 2000)}"
    return _num_words(year)


@register("normalizer", "rule_based")
class RuleBasedNormalizer(INormalizer):
    """The default rule-based text normalizer."""

    name = "rule_based"

    def __init__(
        self,
        expand_acronyms: bool = True,
        expand_currencies: bool = True,
        expand_dates: bool = True,
        expand_phones: bool = True,
        expand_urls: bool = True,
        expand_emojis: bool = False,
        expand_symbols: bool = True,
    ) -> None:
        self.expand_acronyms = expand_acronyms
        self.expand_currencies = expand_currencies
        self.expand_dates = expand_dates
        self.expand_phones = expand_phones
        self.expand_urls = expand_urls
        self.expand_emojis = expand_emojis
        self.expand_symbols = expand_symbols

    # ─── Public API ────────────────────────────────────────────────────

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        out = self._normalize_unicode(text)

        # 1. Multi-char entities first
        if self.expand_urls:
            out = _RE_URL.sub(self._sub_url, out)
            out = _RE_EMAIL.sub(self._sub_email, out)
        if self.expand_phones:
            out = _RE_PHONE.sub(self._sub_phone, out)
        if self.expand_dates:
            out = _RE_DATE_ISO.sub(self._sub_date_iso, out)
            out = _RE_DATE_NUM.sub(self._sub_date_num, out)
        out = _RE_TIME.sub(self._sub_time, out)
        if self.expand_currencies:
            out = _RE_CURRENCY.sub(self._sub_currency, out)
        out = _RE_PERCENT.sub(self._sub_percent, out)

        # 2. Date words (Month DD, YYYY)
        if self.expand_dates:
            out = self._expand_text_dates(out)

        # 3. Numbers with comma thousands → strip commas before number expansion
        out = _RE_THOUSANDS.sub(lambda m: m.group(0).replace(",", ""), out)

        out = _RE_DECADE_APOS.sub(self._sub_decade_apos, out)
        out = _RE_YEAR.sub(self._sub_year, out)
        out = _RE_ORDINAL.sub(self._sub_ordinal, out)
        out = _RE_FRACTION.sub(self._sub_fraction, out)
        out = _RE_DECIMAL.sub(self._sub_decimal, out)
        out = _RE_RANGE.sub(self._sub_range, out)
        out = _RE_MATH.sub(self._sub_math, out)

        # 4. Roman numerals after names
        out = _RE_ROMAN_AFTER_NAME.sub(self._sub_roman_after_name, out)

        # 5. Units (after numbers expanded the *number* part is now words; need to handle "5 kg" pattern)
        out = self._expand_units(out)

        # 6. Hashtags and mentions
        out = _RE_HASHTAG.sub(lambda m: " hashtag " + self._spell_or_word(m.group(1)) + " ", out)
        out = _RE_MENTION.sub(lambda m: " at " + self._spell_or_word(m.group(1)) + " ", out)

        # 7. Abbreviations (Dr., Mrs., etc.)
        out = self._expand_abbreviations(out)

        # 8. Acronyms (NASA vs FBI)
        if self.expand_acronyms:
            out = _RE_ALLCAPS.sub(self._sub_acronym, out)

        # 9. Symbols
        if self.expand_symbols:
            out = self._expand_symbols(out)

        # 10. Plain remaining integers
        out = _RE_INT.sub(self._sub_int, out)

        # 11. Final whitespace cleanup
        out = re.sub(r"\s+", " ", out).strip()
        return out

    # ─── Substitution callbacks ────────────────────────────────────────

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        # Smart quotes → ascii, dashes → ascii
        repl = {
            "\u2018": "'", "\u2019": "'",
            "\u201C": '"', "\u201D": '"',
            "\u2013": "-", "\u2014": "-",
            "\u2026": "...",
            "\u00A0": " ",
        }
        for a, b in repl.items():
            text = text.replace(a, b)
        # NFKC for compat decomposition (e.g. ﬁ → fi)
        return unicodedata.normalize("NFKC", text)

    @staticmethod
    def _sub_url(m: re.Match[str]) -> str:
        url = m.group(0)
        url = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
        url = url.replace("www.", "w w w dot ")
        url = url.replace(".", " dot ").replace("/", " slash ").replace("-", " dash ")
        url = url.replace(":", " colon ")
        return f" {url} "

    @staticmethod
    def _sub_email(m: re.Match[str]) -> str:
        local, _, domain = m.group(0).partition("@")
        return f" {local.replace('.', ' dot ').replace('-', ' dash ')} at {domain.replace('.', ' dot ')} "

    @staticmethod
    def _sub_phone(m: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", m.group(0))
        return " " + " ".join(_DIGIT_WORD[d] for d in digits) + " "

    @staticmethod
    def _sub_time(m: re.Match[str]) -> str:
        h, mi = int(m.group(1)), int(m.group(2))
        ampm = (m.group(4) or "").replace(".", "").lower()
        sec = m.group(3)
        if h > 24 or mi > 59:
            return m.group(0)
        if ampm in {"am", "pm"}:
            disp_h = h if 1 <= h <= 12 else (12 if h == 0 else h - 12)
            mi_words = "" if mi == 0 else (
                f" oh {_num_words(mi)}" if mi < 10 else f" {_num_words(mi)}"
            )
            return f" {_num_words(disp_h)}{mi_words} {ampm[0]} {ampm[1]} "
        # 24h
        if mi == 0:
            return f" {_num_words(h)} hundred hours "
        if mi < 10:
            return f" {_num_words(h)} oh {_num_words(mi)} "
        sec_w = f" and {_num_words(int(sec))} seconds" if sec else ""
        return f" {_num_words(h)} {_num_words(mi)}{sec_w} "

    @staticmethod
    def _format_date(year: int, month: int, day: int) -> str:
        month_name = datetime(2000, month, 1).strftime("%B")
        return f" {month_name} {_ordinal_words(day)} {_year_words(year)} "

    def _sub_date_iso(self, m: re.Match[str]) -> str:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return self._format_date(y, mo, d)
        except ValueError:
            return m.group(0)

    def _sub_date_num(self, m: re.Match[str]) -> str:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000 if y < 50 else 1900
        # Heuristic: assume MM/DD/YYYY (US). If first > 12, swap.
        month, day = (a, b) if a <= 12 else (b, a)
        try:
            return self._format_date(y, month, day)
        except ValueError:
            return m.group(0)

    def _expand_text_dates(self, text: str) -> str:
        # "December 25, 2024", "Dec 25 2024", "25 December 2024"
        pattern = re.compile(
            r"\b(" + "|".join(_MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s*(\d{4}))?\b",
            re.IGNORECASE,
        )

        def repl(m: re.Match[str]) -> str:
            month = _MONTHS[m.group(1).lower()]
            day = int(m.group(2))
            year = int(m.group(3)) if m.group(3) else None
            month_name = datetime(2000, month, 1).strftime("%B")
            base = f" {month_name} {_ordinal_words(day)}"
            if year:
                base += f" {_year_words(year)}"
            return base + " "

        text = pattern.sub(repl, text)

        pattern2 = re.compile(
            r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + "|".join(_MONTHS) + r")(?:\s+(\d{4}))?\b",
            re.IGNORECASE,
        )

        def repl2(m: re.Match[str]) -> str:
            day = int(m.group(1))
            month = _MONTHS[m.group(2).lower()]
            year = int(m.group(3)) if m.group(3) else None
            month_name = datetime(2000, month, 1).strftime("%B")
            base = f" {month_name} {_ordinal_words(day)}"
            if year:
                base += f" {_year_words(year)}"
            return base + " "

        return pattern2.sub(repl2, text)

    def _sub_currency(self, m: re.Match[str]) -> str:
        if m.group(1) and m.group(2):       # symbol then amount
            sym, amt = m.group(1), m.group(2)
        elif m.group(3) and m.group(4):     # CODE then amount
            sym, amt = m.group(3), m.group(4)
        else:                                # amount then CODE
            sym, amt = m.group(6), m.group(5)
        info = _CURR.get(sym, {})
        if not info:
            return m.group(0)
        amt = amt.replace(",", "")
        if "." in amt:
            whole, frac = amt.split(".")
            iw = int(whole)
            ic = int(frac.ljust(2, "0")[:2])
            unit = info["name"] if iw == 1 else info.get("plural", info["name"] + "s")
            sub = info.get("subunit", "cent") if ic == 1 else info.get("subunit_plural", "cents")
            if ic == 0:
                return f" {_num_words(iw)} {unit} "
            return f" {_num_words(iw)} {unit} and {_num_words(ic)} {sub} "
        iw = int(amt)
        unit = info["name"] if iw == 1 else info.get("plural", info["name"] + "s")
        return f" {_num_words(iw)} {unit} "

    @staticmethod
    def _sub_percent(m: re.Match[str]) -> str:
        n = float(m.group(1))
        if n.is_integer():
            return f" {_num_words(int(n))} percent "
        return f" {_fnum_words(n)} percent "

    @staticmethod
    def _sub_year(m: re.Match[str]) -> str:
        token = m.group(0)
        plural = token.endswith("s")
        year = int(token.rstrip("s"))
        words = _year_words(year)
        return f" {words}{'s' if plural else ''} "

    @staticmethod
    def _sub_decade_apos(m: re.Match[str]) -> str:
        yy = int(m.group(1))
        # Heuristic: '90s → nineties (1990s); '20s → twenties
        full = 1900 + yy if yy >= 30 else 2000 + yy
        return " " + _year_words(full) + "s "

    @staticmethod
    def _sub_ordinal(m: re.Match[str]) -> str:
        return " " + _ordinal_words(int(m.group(1))) + " "

    @staticmethod
    def _sub_fraction(m: re.Match[str]) -> str:
        n, d = int(m.group(1)), int(m.group(2))
        if d == 0:
            return m.group(0)
        special = {(1, 2): "one half", (1, 3): "one third", (1, 4): "one quarter",
                   (3, 4): "three quarters", (2, 3): "two thirds"}
        if (n, d) in special:
            return " " + special[(n, d)] + " "
        return f" {_num_words(n)} {_ordinal_words(d)}{'s' if n != 1 else ''} "

    @staticmethod
    def _sub_decimal(m: re.Match[str]) -> str:
        whole, frac = m.group(1), m.group(2)
        return f" {_num_words(int(whole))} point {_spell_digits(frac)} "

    @staticmethod
    def _sub_range(m: re.Match[str]) -> str:
        return f" {_num_words(int(m.group(1)))} to {_num_words(int(m.group(2)))} "

    @staticmethod
    def _sub_math(m: re.Match[str]) -> str:
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        op_words = {
            "+": "plus", "-": "minus", "*": "times", "×": "times",
            "/": "divided by", "÷": "divided by", "=": "equals",
            "<": "less than", ">": "greater than",
        }
        return f" {_num_words(a)} {op_words.get(op, op)} {_num_words(b)} "

    @staticmethod
    def _sub_int(m: re.Match[str]) -> str:
        return " " + _num_words(int(m.group(0))) + " "

    @staticmethod
    def _sub_roman_after_name(m: re.Match[str]) -> str:
        name = m.group(1)
        roman = m.group(2)
        n = _roman_to_int(roman)
        if n == 0 or n > 30:  # safety
            return m.group(0)
        return f"{name} the {_ordinal_words(n)}"

    def _expand_units(self, text: str) -> str:
        # match "<digits> <unit>" — note this runs *before* int substitution
        units_sorted = sorted(_UNITS.keys(), key=len, reverse=True)
        for u in units_sorted:
            esc = re.escape(u)
            pattern = re.compile(rf"(\d+(?:\.\d+)?)\s*{esc}(?![A-Za-z])")
            text = pattern.sub(lambda m, name=_UNITS[u]: f" {m.group(1)} {name} ", text)
        return text

    @staticmethod
    def _expand_abbreviations(text: str) -> str:
        for abbrev, full in _ABBREV.items():
            pattern = re.compile(r"(?<!\w)" + re.escape(abbrev) + r"(?!\w)")
            text = pattern.sub(" " + full + " ", text)
        return text

    @staticmethod
    def _spell_or_word(token: str) -> str:
        upper = token.upper()
        if upper in _ACRO_WORD:
            return token.lower()
        if upper in _ACRO_SPELL or (token.isupper() and len(token) <= 5):
            return " ".join(token)
        return token

    def _sub_acronym(self, m: re.Match[str]) -> str:
        token = m.group(1)
        if token in _ACRO_WORD:
            return token.lower()
        if token in _ACRO_SPELL:
            return " " + " ".join(token) + " "
        # Heuristic: 2-5 uppercase letters with no vowels-only pattern → spell
        if 2 <= len(token) <= 5:
            vowels = sum(1 for c in token if c in "AEIOU")
            if vowels == 0 or vowels == len(token):
                return " " + " ".join(token) + " "
            # Mixed: assume spell
            return " " + " ".join(token) + " "
        return token

    @staticmethod
    def _expand_symbols(text: str) -> str:
        # Replace standalone symbols (surrounded by spaces or word boundaries)
        for sym, word in _SYMBOL_MAP.items():
            text = re.sub(r"(?<=\s)" + re.escape(sym) + r"(?=\s)", word, text)
            text = re.sub(r"(?<=\w)" + re.escape(sym) + r"(?=\w)", word, text)
        return text


def _roman_to_int(s: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total, prev = 0, 0
    for ch in reversed(s):
        v = values.get(ch, 0)
        if v == 0:
            return 0
        total += v if v >= prev else -v
        prev = v
    return total
