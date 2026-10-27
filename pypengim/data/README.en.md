> English | [中文](./README.cn.md)

# Dictionary and Lexicon Files

Naming convention: single-character tables start with `char_`, word tables start with `word_`, and syllable-level mappings live in `phonology/`. All files are UTF-8, one `key#value` per line, and lines starting with `%` are comments.

```
pypengim/data/        (formerly dict_data/)
├── char_dict/        single-character pronunciations
├── word_dict/        word pronunciations, Mandarin→Teochew mappings, segmentation lexicon
├── phonology/        syllable → phoneme / IPA
├── accent_convert/   Fucheng accent → regional accents
└── romanization/     Peng'im → other romanization schemes
```

In code, locate this directory via `pypengim.DATA_DIR`; do not hard-code relative paths.

## accent_convert directory

As the name suggests, this directory holds accent-conversion dictionaries. The txt files map the Fucheng accent to the accents of Shantou (Swatow), Jieyang (Kityall), Chenghai (Tenhigh), Jinshi, Ampou, and others.

Each line has one of two forms:
- Character-to-character: `char_Fucheng-syllable#target-syllable`, e.g. `反_huêng2#huang2`.
- Word-to-word: `word_Fucheng-reading#target-reading`. Readings are space-separated per character, with multiple candidates for a character separated by `|`, e.g. `家己_ga1 gi7#ga1 di7|li7`. This only takes effect when the whole word appears and the Fucheng reading matches, and is used for accent changes that occur only in specific words.

## char_dict directory

This folder stores several core dictionary files, including:

#### 1. char_main.txt
The main character table. Derived from the raw data of the Chaozhou pronunciation dictionary, with relatively low-frequency pronunciations or those used only in specific words removed, and some readings modified and refined.

#### 2. char_low_frequency.txt
Records the relatively low-frequency readings removed from char_main.txt; those marked with an asterisk (*) are extremely low-frequency.

#### 3. char_extension.txt
Records Chinese characters not found in the original dictionary, as well as new or adapted characters introduced for the problem of "sound but no word". Also includes some English letters.

#### 4. char_nasal_variants.txt
Pairs of readings of the same character that can be read either as nasalized or non-nasalized (same initial and tone), e.g. `底#doi2|doin2`. Grouped by final: i-in, iu-iun, ua-uan, ui-uin, oi-oin, etc.

#### 5. char_mispronunciation.txt

Because today's compulsory education strongly promotes Mandarin, traditional cultural forms (such as dialect sketch comedy and storytelling) are declining, and electronic Teochew materials are relatively scarce, many Teochew speakers' pronunciation habits are influenced by Mandarin, for example:

```
趁: read as cêng3
奔: read as bung1
荐: read as giang3
标: read as biou1
宠: read as cong2
揣: read as cuai2
蹭: read as cêng3
```
Such mispronunciations have become a de facto reality, so I added the file `char_mispronunciation.txt` to record them.

This file will continue to be updated.

#### 6. char_traditional.txt
Readings of traditional characters (where they differ from simplified), e.g. 臟, 髒.

## word_dict directory

This folder stores several core dictionary files, including:

#### 1. word_common.txt
Readings of common words, used for polyphone disambiguation. Mostly Mandarin vocabulary; because the project did not make a special distinction early on, some Teochew dialect words are mixed in as well, to be checked and improved later.

#### 2. word_teochew.txt
Readings of dialect words. For example, 【生理】 is `sên1 li2` in word_common.txt, meaning "the life activity of the biological organism and the functions of its organs"; in word_teochew.txt it is `sêng1 li2`, meaning "business, trade".

#### 3.word_surname.txt
Organizes the Teochew readings of common surnames (including compound surnames).

#### 4. word_place.txt
Organizes place names from ancient and modern times, China and abroad, and the Teochew region itself; basically covers most countries and regions of the world, as well as major cities.
Local place names follow customary readings and colloquial (bai) readings as much as possible.
Place names in other parts of China and abroad prioritize customary readings; if the place name is rarely used, literary (wen) readings are preferred.

#### 5. word_history.txt
Stores history-related vocabulary (dynasties, regime names, ethnic groups, personal names, official titles).

#### 6. word_reign_title.txt
Records terms specific to ancient emperors' reign titles.

#### 7. mandarin_to_teochew.txt
Used to map Mandarin words to more idiomatic Teochew words.

#### 8. homophone_substitution.txt
Homophone character substitution. Records the homophone characters Teochew people like to use on platforms such as WeChat and Douyin.

#### 9. jieba_userdict.txt
jieba user dictionary. Compiled from the dictionary files above to assist the jieba library's word segmentation, making it better suited to Teochew segmentation.

## phonology directory

#### 1. syllable_to_phone.txt / syllable_to_phone_nasalized.txt
Maps pinyin to smaller phonemes, i.e. the `initial + final` pattern. There are two versions:
- `syllable_to_phone.txt`: the original; vowels after m/n/ng initials are not marked nasalized, e.g. `ma#m a`.
- `syllable_to_phone_nasalized.txt`: the nasalized version; vowels after m/n/ng initials always carry nasalization, e.g. `man#m an`, `muênh#m uênh`, consistent with the annotation convention of the current dictionaries and corpora.

#### 2. syllable_to_ipa.txt
Maps pinyin to the International Phonetic Alphabet (IPA), facilitating integration with existing multilingual speech large models.

## File Renaming Reference

| Old path (under dict_data/) | New path (under pypengim/data/) |
|---|---|
| vocab/origin_vocab.txt | char_dict/char_main.txt |
| vocab/low_fre.txt | char_dict/char_low_frequency.txt |
| vocab/vocab_extension.txt | char_dict/char_extension.txt |
| vocab/鼻音.txt | char_dict/char_nasal_variants.txt |
| vocab/error_pronunciation.txt | char_dict/char_mispronunciation.txt |
| vocab/traditional_chinese.txt | char_dict/char_traditional.txt |
| vocab/Surname.txt | word_dict/word_surname.txt |
| vocab/phone.txt | phonology/syllable_to_phone.txt |
| vocab/IPA_lexicon.txt | phonology/syllable_to_ipa.txt |
| word_dict/dict.txt | word_dict/word_common.txt |
| word_dict/teochew_local_dict.txt | word_dict/word_teochew.txt |
| word_dict/place.txt | word_dict/word_place.txt |
| word_dict/history.txt | word_dict/word_history.txt |
| word_dict/reign_title.txt | word_dict/word_reign_title.txt |
| word_dict/madr_to_tch.txt | word_dict/mandarin_to_teochew.txt |
| word_dict/homophonic_substitution.txt | word_dict/homophone_substitution.txt |
| word_dict/jieba_cut.txt | word_dict/jieba_userdict.txt |
