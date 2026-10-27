"""
Accent conversion: any accent -> any accent (via Fucheng as pivot).

Accent mapping tables ``pypengim/data/accent_convert/to_*.txt`` record ``hanzi_fucheng_syllable#target_syllable``
and only go Fucheng -> other. To reverse, or convert between two non-Fucheng accents, restore to Fucheng first:

* With known hanzi (``convert_char``, ``convert_word``): reverse-lookup by (hanzi, this accent's reading);
  over all 12000+ (char, reading) pairs in the dictionary, 99.9% restore uniquely.
* With only a syllable (``candidates``): one syllable may map to several Fucheng syllables;
  candidates are sorted by char count and are only a reference, not guaranteed unique.

Accent codes: tc Fucheng, ky Jieyang, st Shantou, th Chenghai, gz_c Gimzieh-classical, gz_g Gimzieh-general, ap Ampou.
"""
import collections
import os

import yaml

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
_ACCENT_DIR = os.path.join(_DATA_DIR, 'accent_convert')
_VOCAB_DIR = os.path.join(_DATA_DIR, 'char_dict')
_VOCAB_FILES = ('char_main.txt', 'char_extension.txt', 'char_low_frequency.txt')

BASE = 'tc'   # pivot accent: Fucheng


def _load_dict(path):
    """Load a ``key#value`` dictionary, skipping blank lines and % comments."""
    result = {}
    with open(path, 'r', encoding='utf-8') as fr:
        for line in fr:
            line = line.strip()
            if not line or line.startswith('%') or '#' not in line:
                continue
            key, value = line.split('#', 1)
            result[key] = value
    return result


class AccentConverter:
    """Accent conversion. Dictionaries and mapping tables load lazily on first use."""

    def __init__(self):
        self._names = {BASE: '府城'}
        self._forward = {}          # accent -> {'char_fucheng_syllable': [target_syllable, ...]}
        self._reverse = {}          # accent -> {(char, target_syllable): {fucheng_syllable, ...}}
        self._syllable_rev = {}     # accent -> {target_syllable: Counter({fucheng_syllable: n_chars})}
        self._char_prons = None     # char -> [fucheng_syllable, ...]
        self._word_rules = {}       # accent -> {word: [(fucheng_reading_list, target_reading_candidates), ...]}
        self._max_word_len = {}
        self._load_registry()

    # ---------------------------------------------------------------- loading
    def _load_registry(self):
        with open(os.path.join(_ACCENT_DIR, 'accent.yaml'), 'r', encoding='utf-8') as fr:
            config = yaml.safe_load(fr)
        self._paths = {}
        for code, item in config.items():
            self._names[code] = item['name']
            self._paths[code] = item['path']

    def accents(self):
        """Return {accent_code: accent_name}, including Fucheng."""
        return dict(self._names)

    def _check(self, accent):
        if accent not in self._names:
            raise ValueError("未知口音: {}，可选: {}".format(accent, ', '.join(self._names)))

    def _vocab(self):
        if self._char_prons is None:
            chars = collections.OrderedDict()
            for filename in _VOCAB_FILES:
                for ch, value in _load_dict(os.path.join(_VOCAB_DIR, filename)).items():
                    if len(ch) != 1:
                        continue
                    chars.setdefault(ch, [])
                    for py in value.split('|'):
                        py = py.replace('*', '')
                        if py not in chars[ch]:
                            chars[ch].append(py)
            self._char_prons = chars
        return self._char_prons

    def _load_tables(self, accent):
        """Load an accent table, split into char-level and word-level mappings.

        Char-level: ``char_fucheng_syllable#target_syllable``, multiple targets separated by |.
        Word-level: ``word_fucheng_readings#target_readings``, readings space-separated per char,
        multiple candidates per char separated by |, e.g. ``家己_ga1 gi7#ga1 di7|li7``.
        Only applies when the whole word appears and the Fucheng readings match.
        """
        chars, words = {}, collections.defaultdict(list)
        for key, value in _load_dict(os.path.join(_ACCENT_DIR, self._paths[accent])).items():
            key, value = key.replace('*', ''), value.replace('*', '')
            head, _, tc = key.partition('_')
            if len(head) == 1 and ' ' not in tc:
                chars[key] = value.split('|')
                continue
            tc_syls, targets = tc.split(), [t.split('|') for t in value.split()]
            if len(head) != len(tc_syls) or len(head) != len(targets):
                raise ValueError('{}: 词级映射字数与读音数不一致: {}#{}'.format(self._paths[accent], key, value))
            words[head].append((tc_syls, targets))
        self._forward[accent] = chars
        self._word_rules[accent] = dict(words)
        if words:
            self._max_word_len[accent] = max(len(w) for w in words)

    def _forward_table(self, accent):
        if accent not in self._forward:
            self._load_tables(accent)
        return self._forward[accent]

    def _word_table(self, accent):
        """word -> [(fucheng_reading_list, target_reading_candidates), ...]"""
        if accent == BASE:
            return {}
        if accent not in self._word_rules:
            self._load_tables(accent)
        return self._word_rules[accent]

    def _match_words(self, word, syllables, accent, side):
        """Longest-match left-to-right over word; return {start: (length, fucheng_readings, target_readings)}.

        side='tc': syllables are Fucheng reading candidates; the rule's Fucheng readings must appear among them;
        side='target': syllables are this accent's reading candidates; the rule's target readings must intersect them.
        """
        rules = self._word_table(accent)
        if not rules:
            return {}
        found, i = {}, 0
        while i < len(word):
            for length in range(min(self._max_word_len[accent], len(word) - i), 1, -1):
                hit = None
                for tc_syls, targets in rules.get(word[i:i + length], []):
                    cands = [set(x.replace('*', '') for x in s) for s in syllables[i:i + length]]
                    if side == 'tc':
                        ok = all(t in c for t, c in zip(tc_syls, cands))
                    else:
                        ok = all(set(t) & c for t, c in zip(targets, cands))
                    if ok:
                        hit = (length, tc_syls, targets)
                        break
                if hit:
                    found[i] = hit
                    i += length
                    break
            else:
                i += 1
        return found

    def convert_from_base(self, word, syllables, accent):
        """Fucheng readings -> target accent; try word-level mappings first, then convert per char.

        word is a hanzi string; syllables align one-to-one with the chars, each a list of Fucheng
        reading candidates for that char. Returns a list of the same structure (deduped, order kept).
        Readings with no mapping pass through unchanged.
        """
        self._check(accent)
        table = self._forward_table(accent) if accent != BASE else {}
        out = []
        for ch, prons in zip(word, syllables):
            merged = []
            for py in prons:
                # not in the table: keep as-is (including the * marker)
                for target in table.get('{}_{}'.format(ch, py.replace('*', ''))) or [py]:
                    if target not in merged:
                        merged.append(target)
            out.append(merged)
        if accent == BASE:
            return out
        for start, (length, tc_syls, targets) in self._match_words(word, syllables, accent, 'tc').items():
            for k in range(length):
                pos = start + k
                merged = []
                for py in syllables[pos]:
                    if py.replace('*', '') == tc_syls[k]:
                        items = targets[k]
                    else:
                        items = self._to_accent(word[pos], py.replace('*', ''), accent)
                    for target in items:
                        if target not in merged:
                            merged.append(target)
                out[pos] = merged
        return out

    def word_to_base(self, word, syllables, from_accent):
        """Readings of an accent -> Fucheng readings; word-level mappings first, then per char. Same structure as convert_from_base."""
        self._check(from_accent)
        out = []
        for ch, prons in zip(word, syllables):
            merged = []
            for py in prons:
                for tc in self.to_base(ch, py, from_accent):
                    if tc not in merged:
                        merged.append(tc)
            out.append(merged)
        for start, (length, tc_syls, targets) in self._match_words(word, syllables, from_accent, 'target').items():
            for k in range(length):
                pos = start + k
                merged = []
                for py in syllables[pos]:
                    items = [tc_syls[k]] if py in targets[k] else self.to_base(word[pos], py, from_accent)
                    for tc in items:
                        if tc not in merged:
                            merged.append(tc)
                out[pos] = merged
        return out

    def _to_accent(self, ch, tc_syllable, accent):
        """Fucheng (char, syllable) -> target accent's syllable list. Not in the table: same as Fucheng."""
        if accent == BASE:
            return [tc_syllable]
        return self._forward_table(accent).get('{}_{}'.format(ch, tc_syllable)) or [tc_syllable]

    def _reverse_table(self, accent):
        """(char, this accent's syllable) -> set of Fucheng syllables"""
        if accent not in self._reverse:
            rev = collections.defaultdict(set)
            for ch, prons in self._vocab().items():
                for tc in prons:
                    for target in self._to_accent(ch, tc, accent):
                        rev[(ch, target)].add(tc)
            self._reverse[accent] = rev
        return self._reverse[accent]

    def _syllable_table(self, accent):
        """this accent's syllable -> Counter({fucheng_syllable: how many dict chars map that way})"""
        if accent not in self._syllable_rev:
            rev = collections.defaultdict(collections.Counter)
            for ch, prons in self._vocab().items():
                for tc in prons:
                    for target in self._to_accent(ch, tc, accent):
                        rev[target][tc] += 1
            self._syllable_rev[accent] = rev
        return self._syllable_rev[accent]

    # ---------------------------------------------------------------- conversion
    def to_base(self, ch, syllable, from_accent):
        """With known hanzi, restore an accent's reading to a list of Fucheng syllables (usually just 1).

        If the char is not in the dictionary, or the reading is not one of this char's readings under
        this accent, fall back to syllable-level candidates; if that fails too, return as-is, no error.
        """
        self._check(from_accent)
        if from_accent == BASE:
            return [syllable]
        exact = self._reverse_table(from_accent).get((ch, syllable))
        if exact:
            return sorted(exact)
        cands = self.candidates(syllable, from_accent)
        return cands or [syllable]

    def convert_char(self, ch, syllable, from_accent, to_accent):
        """Single-char conversion: (hanzi, reading) under one accent -> reading list under another (deduped, order kept)."""
        self._check(to_accent)
        result = []
        for tc in self.to_base(ch, syllable, from_accent):
            for target in self._to_accent(ch, tc, to_accent):
                if target not in result:
                    result.append(target)
        return result

    def convert_word(self, word, syllables, from_accent, to_accent):
        """Word conversion. word is a hanzi string; syllables align one-to-one with the chars,
        each a list of candidate readings under from_accent.

        Returns a list with the same structure as syllables. Non-hanzi (length mismatch, None
        candidates, etc.) passes through unchanged. Word-level mappings (e.g. Jieyang 「家己」ga1 di7)
        apply in both the restore and the convert step.
        """
        self._check(from_accent)
        self._check(to_accent)
        base = self.word_to_base(word, syllables, from_accent)
        return self.convert_from_base(word, base, to_accent)

    def candidates(self, syllable, from_accent):
        """When only a syllable is known (no hanzi): return possible Fucheng syllables,
        sorted by how many dictionary chars map to them (most first)."""
        self._check(from_accent)
        if from_accent == BASE:
            return [syllable]
        counter = self._syllable_table(from_accent).get(syllable)
        if not counter:
            return []
        return [py for py, _ in counter.most_common()]

    def convert_syllable(self, syllable, from_accent, to_accent, top=1):
        """Rough conversion when only a syllable is known: take the most likely top Fucheng
        syllables, then convert to the target accent.

        One syllable may map to several Fucheng syllables (ambiguous reverse lookups are about
        8%–27%, depending on accent); results are reference-only. Provide hanzi and use
        convert_char / convert_word when possible.
        """
        self._check(to_accent)
        result = []
        for tc in self.candidates(syllable, from_accent)[:top] or [syllable]:
            # without hanzi, the target accent's spelling is "the most common spelling for dict chars with this Fucheng syllable"
            counter = collections.Counter()
            for ch, prons in self._vocab().items():
                if tc in prons:
                    for target in self._to_accent(ch, tc, to_accent):
                        counter[target] += 1
            for target, _ in counter.most_common(1) or [(tc, 0)]:
                if target not in result:
                    result.append(target)
        return result
