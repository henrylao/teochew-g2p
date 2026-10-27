from . import utils
from . import romanization
from .accent import AccentConverter
import jieba
import types
import yaml
import os

from . import DATA_DIR


def _data(*parts):
    """Absolute path to a data file inside the package; independent of CWD."""
    return os.path.join(DATA_DIR, *parts)


with open(_data('word_dict', 'jieba_userdict.txt'), 'rb') as _fr:
    jieba.load_userdict(_fr)

class pyPengIm():
    def __init__(self, history=False) -> None:
        self._dict_paths = {
            "char_main": _data('char_dict', 'char_main.txt'),
            "char_extension": _data('char_dict', 'char_extension.txt'),
            "word_common": _data('word_dict', 'word_common.txt'),
            "word_teochew": _data('word_dict', 'word_teochew.txt'),
            "mandarin_to_teochew": _data('word_dict', 'mandarin_to_teochew.txt'),
            "word_surname": _data('word_dict', 'word_surname.txt'),
            "syllable_to_ipa": _data('phonology', 'syllable_to_ipa.txt'),
            # "syllable_to_phone": _data('phonology', 'syllable_to_phone.txt'),
            "char_low_frequency": _data('char_dict', 'char_low_frequency.txt')
        }

        self.accent_dict = self._load_accent()
        self._accent_converter = AccentConverter()

        self._loaded_dicts = {}
        
        # Whether to load the Chinese history dictionary (reign titles, regimes, offices, names, ethnic groups, …)
        if history:
            self.word_common.update(utils.load_dict(_data('word_dict', 'word_history.txt')))
            self.word_common.update(utils.load_dict(_data('word_dict', 'word_reign_title.txt')))

        jieba.cut('')# warm-up

    # Legacy attribute name -> new name, for backward compatibility with external code
    _LEGACY_NAMES = {
        'vocab': 'char_main',
        'vocab_extension': 'char_extension',
        'low_fre_dict': 'char_low_frequency',
        'word_dict': 'word_common',
        'teochew_word_dict': 'word_teochew',
        'translation_dict': 'mandarin_to_teochew',
        'surname_dict': 'word_surname',
        'IPA_dict': 'syllable_to_ipa',
    }

    def __getattr__(self, name):
        name = self._LEGACY_NAMES.get(name, name)
        if name in self._dict_paths:
            if name not in self._loaded_dicts:
                self._loaded_dicts[name] = utils.load_dict(self._dict_paths[name])
            return self._loaded_dicts[name]

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _load_accent(self, accent_config_path=None):
        accent_config_path = accent_config_path or _data('accent_convert', 'accent.yaml')
        with open(accent_config_path, 'r', encoding='utf-8') as file:
            accent_config = yaml.safe_load(file)
            accent_dict = {}
            for k,v in accent_config.items():
                accent_dict[k] = (
                        utils.load_dict(_data('accent_convert', v['path'])),
                        v['name']
                    )

        return accent_dict
    
    def pinyin(self, text, heteronym=False, accent='', auto_split=True, scheme='pengim'):
        """Convert hanzi to pinyin.

        scheme: output romanization scheme, default 'pengim' (Teochew pinyin).
                See romanization.available_schemes() for options.
                The 'result' field always stays Teochew pinyin; only 'pinyin_seq' follows scheme.
        """
        if scheme not in romanization.SCHEMES:
            raise ValueError("未知拼音方案: {}，可选: {}".format(scheme, ', '.join(romanization.SCHEMES)))
        text = text.upper()
        if heteronym:
            pinyin_list = self._pinyin_heteronym(text)
        else:
            if auto_split:
                pinyin_list = self.pinyin_optimize(utils.preprocess_generator(self.sentence_cut(text)))
            else:
                pinyin_list = self.pinyin_optimize(text.split(' '))

        if accent in self.accent_dict:
            pinyin_list = self.convert_accent(pinyin_list, accent)

        surname_list = self._surname_notice(text)

        return {
            'result': pinyin_list,
            'pinyin_seq': self.to_scheme(self._to_pinyin_sequence(pinyin_list), scheme),
            'surname_notice': surname_list
        }

    def to_scheme(self, pinyin_seq, scheme='pengim', from_scheme='pengim'):
        """Convert between romanization schemes: take a pinyin sequence written in from_scheme
        (space-separated; polyphone candidates joined with |) and rewrite it in scheme.

        If from_scheme is omitted, input is treated as Teochew pinyin. Any pair of schemes
        can convert; internally everything passes through Teochew pinyin.
        scheme / from_scheme options: pengim (Teochew), dieghv, fielde, puj (Pe̍h-ūe-jī, diacritic),
        pujn (digit), pujs (superscript), ggn (Gaginang), ggns (Gaginang superscript), chen (Chen Enquan).
        On reverse parsing, unrecognized syllables pass through unchanged.
        """
        for name in (scheme, from_scheme):
            if name not in romanization.SCHEMES:
                raise ValueError("未知拼音方案: {}，可选: {}".format(name, ', '.join(romanization.SCHEMES)))
        return romanization.convert_between(pinyin_seq, from_scheme, scheme)

    def convert_accent_between(self, word, pinyin_seq, from_accent, to_accent):
        """Accent-to-accent conversion: rewrite the readings of word under from_accent into to_accent.

        word is a hanzi string; pinyin_seq is a Teochew-pinyin sequence aligned one-to-one with
        the characters (space-separated; polyphone candidates joined with |). It may use any
        accent's readings as long as they are consistent with from_accent. Returns the same format.
        Accent codes: see accent_converter().accents() — tc Fucheng, ky Jieyang, st Shantou,
        th Chenghai, gz_c / gz_g Gimzieh, ap Ampou.
        With known hanzi the restore is exact (99.9% of (char, reading) pairs in the dictionary
        restore uniquely); raises ValueError when word and reading counts do not match.
        """
        syllables = [token.split('|') for token in pinyin_seq.split(' ')]
        if len(word) != len(syllables):
            raise ValueError("汉字数 {} 与读音数 {} 不一致".format(len(word), len(syllables)))
        converted = self._accent_converter.convert_word(word, syllables, from_accent, to_accent)
        return ' '.join('|'.join(item) if item else syl for item, syl in zip(converted, pinyin_seq.split(' ')))

    def accent_converter(self):
        """Return the accent converter; call convert_char / convert_syllable / candidates etc. directly."""
        return self._accent_converter

    def sentence_cut(self, text):
        new_text_list = []
        for ch in text:
            if ch not in self.char_main and ch not in self.char_extension:
                new_text_list.append(' {} '.format(ch))
            else:
                new_text_list.append(ch)
        
        return jieba.cut("".join(new_text_list))


    def _to_pinyin_sequence(self, pinyin_list):
        result = []
        for item in pinyin_list:
            for pinyin in item[1:]:
                if pinyin != ['None']:
                    result.append('|'.join([py.replace('*', '') for py in pinyin]))
                else:
                    result.append(item[0]) ## invalid character: pass through unchanged

        return ' '.join(result)

    def _surname_notice(self, text):
        """Find surnames in the text and their readings. Compound surnames take priority
        (longest match), e.g. 「诸葛亮」 only reports 「诸葛」.

        Return format matches pinyin()'s result: [surname, [reading of char 1...], [reading of char 2...]].
        """
        surnames = self.word_surname
        max_len = max((len(k) for k in surnames), default=1)
        result = []
        i = 0
        while i < len(text):
            for length in range(min(max_len, len(text) - i), 0, -1):
                word = text[i:i + length]
                if word in surnames:
                    result.append([word] + [self._to_pinyin_list(s) for s in surnames[word].split(' ')])
                    i += length
                    break
            else:
                i += 1
        return result

    def _pinyin_heteronym(self, text):
        result = []
        text = text.replace('#', '')
        for zh_char in text:
            item = []
            if zh_char in self.char_main.keys():
                item.extend(self._to_pinyin_list(self.char_main[zh_char]))
            if zh_char in self.char_extension.keys():
                item.extend(self._to_pinyin_list(self.char_extension[zh_char]))
            if zh_char in self.char_low_frequency.keys():
                item.extend(self._to_pinyin_list(self.char_low_frequency[zh_char]))
            result.append([zh_char, item])

        return result

    def _to_pinyin_list(self, pinyin_item):
        return pinyin_item.split('|') if '|' in pinyin_item else [pinyin_item]

    def _word_to_pinyin(self, item_word):
        if ' ' in item_word:
            return [self._to_pinyin_list(pinyin) for pinyin in item_word.split(' ')]
        return [[item_word]]

    def pinyin_optimize(self, word_list):
        result = []
        for word in word_list:
            if not word.strip():
                continue

            word_translate_flag = word.endswith('#')
            word = word.rstrip('#')
            word_found_flag = False

            item = [word]
            if word in self.word_teochew.keys():
                item.extend(self._word_to_pinyin(self.word_teochew[word]))
                word_found_flag = True

            if not word_translate_flag and word in self.word_common:
                item = [word]
                item.extend(self._word_to_pinyin(self.word_common[word]))  # in non-translation mode, clear previous pinyin and keep only word_common (Mandarin sense)
                word_found_flag = True

            elif not word_translate_flag or not word_found_flag:
                if word in self.word_common:
                    item.extend(self._word_to_pinyin(self.word_common[word]))
                    word_found_flag = True


            if not word_found_flag:
                for zh_char in word:
                    if zh_char in self.char_main.keys():
                        item.append(self._to_pinyin_list(self.char_main[zh_char]))
                    elif zh_char in self.char_extension.keys():
                        item.append(self._to_pinyin_list(self.char_extension[zh_char]))
                    else:
                        item.append(self._to_pinyin_list('None'))

            result.append(item)
        return result

    def convert_accent(self, pinyin_list, accent):
        """Fucheng -> target accent. Within each segmented word, try word-level mappings first
        (e.g. Jieyang 「家己」), then convert character by character."""
        result = []
        for one_pair in pinyin_list:
            word, pinyins = one_pair[0], list(one_pair[1:])
            if len(word) != len(pinyins):      # char/reading count mismatch (e.g. bad dictionary data): keep as-is
                result.append([word] + pinyins)
                continue
            converted = self._accent_converter.convert_from_base(word, pinyins, accent)
            result.append([word] + converted)
        return result

    def to_IPA(self, pinyin_seq, blank=True):
        if blank:
            split_char = ' '
        else:
            split_char = ''

        result = []
        for pinyin in pinyin_seq.split(' '):
            if '|' in pinyin:
                ipa_item = []
                for py in pinyin.split('|'):
                    ph_list = utils.pinyin_to_phoneme_list(py)
                    ipa_item.append(split_char.join([self.syllable_to_ipa[ph] if ph in self.syllable_to_ipa else ph for ph in ph_list]))
                result.append("|".join(ipa_item))
            else:
                ph_list = utils.pinyin_to_phoneme_list(pinyin)
                result.append(split_char.join(self.syllable_to_ipa[ph] if ph in self.syllable_to_ipa else ph for ph in ph_list))

        return result

    def to_phoneme(self, pinyin_seq):
        return ['|'.join([utils.pinyin_to_phoneme(py) for py in pinyin.split('|')]) if '|' in pinyin else utils.pinyin_to_phoneme(pinyin) for pinyin in pinyin_seq.split(' ')]

    def to_oral(self, text, auto_split=True):
        if isinstance(text, list) or isinstance(text, types.GeneratorType):
            word_list = text
        elif isinstance(text, str):
            word_list = jieba.cut(text) if auto_split else text.split(' ')
        else:
            return None

        return ' '.join([self.mandarin_to_teochew.get(word, word) + '#' if word in self.mandarin_to_teochew else word for word in word_list])

    def add_word_mapping(self, user_mapping: dict):
        self.mandarin_to_teochew.update(user_mapping)

    # Query a single character's readings across regions
    def single_query(self, single_char):
        if single_char not in self.char_main and single_char not in self.char_extension:
            return None

        if len(single_char) > 1:
            return None

        result_dict = {}
        pinyin_list = self._pinyin_heteronym(single_char)
        result_dict['府城'] = pinyin_list[0]

        for k,v in self.accent_dict.items():
            result_dict[v[1]] = self.convert_accent(pinyin_list, accent=k)[0]

        return result_dict