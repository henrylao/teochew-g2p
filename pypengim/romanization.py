"""
Conversion between multiple Teochew romanization schemes.

Internally this repo's Teochew pinyin (``initial + final + tone digit``, e.g. ``zui2``) is the
intermediate representation; every other scheme is a one-way Teochew-pinyin -> target mapping,
with tables under ``pypengim/data/romanization/``.

Supported schemes (``scheme`` parameter):

    pengim    Teochew pinyin (default, passthrough)
    dieghv    Dieghv
    fielde    Fielde (diacritic tones)
    puj       Pe̍h-ūe-jī, diacritic tones
    pujn      Pe̍h-ūe-jī, digit tones
    pujs      Pe̍h-ūe-jī, superscript tones
    ggn       Gaginang Peng'im, digit tones
    ggns      Gaginang Peng'im, superscript tones
    chen      Chen Enquan's Teochew scheme, digit tones
    ipa       IPA (handled by pyPengIm.to_IPA; an integrated entry point is also provided here)

Initial/final tables for Pe̍h-ūe-jī, Fielde, Dieghv, and Gaginang were compiled from pengim-js
(MIT License, Copyright (c) 2024 Learn Teochew).
"""
import os
import re
import unicodedata

from .syllable import INITIALS, NASALS

_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'romanization')

SUPERSCRIPT = {'1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸'}

# scheme name -> (mapping file, tone style, display name)
SCHEMES = {
    'pengim': (None, 'digit', '潮拼 (Peng\'im)'),
    'dieghv': ('dieghv.txt', 'digit', '潮语拼音 (Dieghv)'),
    'fielde': ('fielde.txt', 'fielde', '斐尔德拼音 (Fielde)'),
    'puj':    ('puj.txt', 'puj', '白话字 (符号声调)'),
    'pujn':   ('puj.txt', 'digit', '白话字 (数字声调)'),
    'pujs':   ('puj.txt', 'super', '白话字 (上标数字声调)'),
    'ggn':    ('ggn.txt', 'digit', '家己人拼音 (数字声调)'),
    'ggns':   ('ggn.txt', 'super', '家己人拼音 (上标数字声调)'),
    'chen':   ('chen_enquan.txt', 'digit', '陈恩泉拼音'),
}

# Tone diacritics: tones 1 and 4 are unmarked
_PUJ_TONES = {'2': '\u0301', '3': '\u0300', '5': '\u0302', '6': '\u0303', '7': '\u0304', '8': '\u030d'}
_FIELDE_TONES = {'2': '\u0301', '3': '\u0300', '5': '\u0302', '6': '\u0306', '7': '\u0304', '8': '\u0302'}
_TONE_MARKS = {'puj': _PUJ_TONES, 'fielde': _FIELDE_TONES}

_tables = {}


def _load_table(filename):
    """Load a mapping file; return {'ini': {}, 'fin': {}, 'nas': {}}"""
    if filename in _tables:
        return _tables[filename]
    table = {'ini': {}, 'fin': {}, 'nas': {}}
    section = None
    with open(os.path.join(_ROOT, filename), 'r', encoding='utf-8') as fr:
        for line in fr:
            line = line.strip()
            if not line:
                continue
            if line.startswith('%'):
                if line.startswith('% 声母'):
                    section = 'ini'
                elif line.startswith('% 韵母'):
                    section = 'fin'
                elif line.startswith('% 纯鼻音'):
                    section = 'nas'
                continue
            if section is None or '#' not in line:
                continue
            key, value = line.split('#', 1)
            table[section][key] = unicodedata.normalize('NFC', value)
    _tables[filename] = table
    return table


def available_schemes():
    """Return {scheme_name: display_name}, for GUI dropdowns."""
    return {k: v[2] for k, v in SCHEMES.items()}


def split_syllable(pinyin):
    """Split a Teochew syllable into (initial, final, tone, is_syllabic_nasal).

    Valid input looks like ``zui2``, ``ng5``; invalid (non-hanzi chars, English words) returns None.
    """
    if len(pinyin) < 2 or pinyin[-1] not in '12345678':
        return None
    tone, body = pinyin[-1], pinyin[:-1]
    if body in NASALS:
        return '', body, tone, True
    if body[0] not in INITIALS:
        return '', body, tone, False
    k = 2 if body[:2] in ('bh', 'gh', 'ng') else 1
    return body[:k], body[k:], tone, False


def _add_tone_mark(toneless, tone, marks):
    """Place the diacritic on the syllable's main vowel: a/e/o/u/ṳ/w first, then i, then n/m."""
    mark = marks.get(tone)
    if mark is None:
        return toneless
    text = unicodedata.normalize('NFD', toneless)
    idx = None
    for pattern in (r'[aeouw]', r'i', r'[nm]'):
        m = re.search(pattern, text)
        if m:
            idx = m.start()
            break
    if idx is None:
        return toneless
    # dotted ṳ / o̤ have a combining mark after them; the tone mark must come after that
    end = idx + 1
    while end < len(text) and unicodedata.combining(text[end]) and text[end] == '\u0324':
        end += 1
    return unicodedata.normalize('NFC', text[:end] + mark + text[end:])


def convert_syllable(pinyin, scheme='pengim'):
    """Convert one Teochew syllable to the target scheme. Unrecognized input passes through."""
    if scheme not in SCHEMES:
        raise ValueError("未知拼音方案: {}，可选: {}".format(scheme, ', '.join(SCHEMES)))
    filename, tone_style, _ = SCHEMES[scheme]
    if filename is None:
        return pinyin

    parts = split_syllable(pinyin)
    if parts is None:
        return pinyin
    initial, final, tone, is_nasal = parts
    table = _load_table(filename)

    if is_nasal:
        body = table['nas'].get(final)
    else:
        ini = table['ini'].get(initial, '') if initial else ''
        fin = table['fin'].get(final) if final else ''
        body = None if (initial and initial not in table['ini']) or fin is None else ini + fin
    if body is None:
        return pinyin

    if tone_style == 'digit':
        return body + tone
    if tone_style == 'super':
        return body + SUPERSCRIPT[tone]
    return _add_tone_mark(body, tone, _TONE_MARKS[tone_style])


def convert_sequence(pinyin_seq, scheme='pengim'):
    """Convert a space-separated Teochew pinyin sequence; polyphone candidates in ``a|b`` form convert one by one."""
    if scheme == 'pengim':
        return pinyin_seq
    out = []
    for token in pinyin_seq.split(' '):
        out.append('|'.join(convert_syllable(p, scheme) for p in token.split('|')))
    return ' '.join(out)


# ---------------------------------------------------------------------------
# Reverse: other schemes -> Teochew pinyin. With this, any pair of schemes can convert (via Teochew pinyin).
# ---------------------------------------------------------------------------

_TONE_CHARS = {'̀', '́', '̂', '̃', '̄', '̆', '̍'}
_SUPERSCRIPT_REVERSE = {v: k for k, v in SUPERSCRIPT.items()}
_PUJ_TONES_REVERSE = {v: k for k, v in _PUJ_TONES.items()}
# Fielde writes both tone 5 and tone 8 as ^, distinguished only by entering-tone endings, so leave it out of this table
_FIELDE_TONES_REVERSE = {'́': '2', '̀': '3', '̆': '6', '̄': '7'}

# Disambiguation when one spelling maps to several Teochew pinyin forms.
# In Chen Enquan both en and ng are written wn; en never appears in the dictionary, so prefer ng
_REVERSE_PREFER = {'chen_enquan.txt': {'wn': 'ng', 'hwn': 'hng'}}

_reverse_tables = {}


def _reverse_table(filename):
    """Build a reverse index {'syl': spelling of the whole syllable (toneless) -> Teochew pinyin,
    'nas': syllabic-nasal spelling -> Teochew pinyin}.

    Index by whole syllable rather than initial and final separately: in some schemes initial and
    final spellings run together, e.g. Chen Enquan's hwn can be h+wn or the whole spelling of hng.
    """
    if filename in _reverse_tables:
        return _reverse_tables[filename]
    table = _load_table(filename)
    syl = {}
    for ini in [''] + list(table['ini']):
        ini_written = table['ini'][ini] if ini else ''
        for fin, fin_written in table['fin'].items():
            syl.setdefault(ini_written + fin_written, ini + fin)
    nas = {written: py for py, written in table['nas'].items()}
    for written, py in _REVERSE_PREFER.get(filename, {}).items():
        nas[written] = py
    syl.update(nas)       # syllabic nasals take priority over the "initial+final" split
    result = {'syl': syl, 'nas': nas}
    _reverse_tables[filename] = result
    return result


def _is_entering(toneless):
    """Entering tone: ends in p t k h, or nasalized entering (Pe̍h-ūe-jī ⁿh, Fielde hⁿ — h followed by ⁿ)."""
    return bool(re.search(r'[ptkh]ⁿ?$', toneless))


def _parse_tone(text, tone_style):
    """Split (toneless spelling, tone digit) out of a target-scheme spelling. Tone is None if unrecognized."""
    if tone_style == 'digit':
        if text and text[-1] in '12345678':
            return text[:-1], text[-1]
        return text, None
    if tone_style == 'super':
        if text and text[-1] in _SUPERSCRIPT_REVERSE:
            return text[:-1], _SUPERSCRIPT_REVERSE[text[-1]]
        return text, None
    # diacritic schemes (Pe̍h-ūe-jī, Fielde): tone marks are standalone combining chars in NFD
    decomposed = unicodedata.normalize('NFD', text)
    marks = [c for c in decomposed if c in _TONE_CHARS]
    plain = unicodedata.normalize('NFC', ''.join(c for c in decomposed if c not in _TONE_CHARS))
    if not marks:   # tones 1 and 4 are unmarked; distinguish by entering tone
        return plain, '4' if _is_entering(plain) else '1'
    mark = marks[0]
    if tone_style == 'fielde' and mark == '̂':   # Fielde ^: entering finals are tone 8, else tone 5
        return plain, '8' if _is_entering(plain) else '5'
    table = _PUJ_TONES_REVERSE if tone_style == 'puj' else _FIELDE_TONES_REVERSE
    return plain, table.get(mark)


def to_pengim_syllable(text, scheme):
    """Restore one syllable of a scheme to Teochew pinyin. Returns None if unrecognized."""
    if scheme not in SCHEMES:
        raise ValueError("未知拼音方案: {}，可选: {}".format(scheme, ', '.join(SCHEMES)))
    filename, tone_style, _ = SCHEMES[scheme]
    if filename is None:
        return text
    plain, tone = _parse_tone(unicodedata.normalize('NFC', text), tone_style)
    if tone is None or not plain:
        return None
    # tone marks other than 5/8 in Pe̍h-ūe-jī/Fielde may be unrelated to tone; always compare in NFC
    py = _reverse_table(filename)['syl'].get(plain)
    return None if py is None else py + tone


def to_pengim_sequence(seq, scheme):
    """Restore a scheme's pinyin sequence to Teochew pinyin, same format as convert_sequence.
    Unrecognized tokens pass through unchanged."""
    if scheme == 'pengim':
        return seq
    out = []
    for token in seq.split(' '):
        out.append('|'.join(to_pengim_syllable(p, scheme) or p for p in token.split('|')))
    return ' '.join(out)


def convert_between(seq, from_scheme, to_scheme):
    """Convert between any two romanization schemes (via Teochew pinyin)."""
    return convert_sequence(to_pengim_sequence(seq, from_scheme), to_scheme)
