> English | [中文](./README.cn.md)

### Introduction to the Teochew Text Processing Tool (pyPengIm)

This project is foundational work for Teochew (Chaoshan) speech synthesis (text-to-speech, TTS), covering text-side processing of Teochew. TTS systems typically consist of three modules: text frontend, acoustic model, and vocoder. For Chinese-family TTS, the text frontend (especially the hanzi-to-pinyin conversion module) has a huge impact on synthesis quality. Currently, because Teochew has extremely few online resources — mostly hobbyist-built websites rather than authoritative institutions or universities — there is a blank slate for Teochew orthography, hanzi-to-pinyin conversion, pinyin-to-phoneme conversion, regional accent conversion, pinyin-to-IPA tools, and more.

To fill this gap, this project builds a text processing tool based on the 1960 Teochew romanization scheme and materials from [Chaozhou Yin Dictionary](http://www.czyzd.com/), [Chaozhou Native Language Network (Chao Dian)](https://www.mogher.com/baike), and [Learn Teochew](https://learnteochew.com/), with the following features:

- 1. Input hanzi and output the corresponding Teochew pinyin; common high-frequency readings as well as all readings are available.

- 2. Word segmentation and polyphone disambiguation.

- 3. Defaults to the Fucheng (prefectural city) accent of Chaozhou urban area, and supports conversion to Shantou urban, Jieyang urban, Chenghai, and other accents; more accents (e.g. Raoping, Shantou suburbs) are planned.

- 4. Translate Mandarin vocabulary into more authentic colloquial Teochew expressions.

- 5. Convert Teochew pinyin to IPA.

- 6. GUI support.

- **7. Online UI demo: [Hugging Face](https://huggingface.co/spaces/panlr/teochew_pyPengIm) | [ModelScope](https://www.modelscope.cn/studios/zzhway/teochew_pyPengIm/)**

### Known limitations

- 1. All materials were scraped, organized, and structured by a single person; omissions and errors are inevitable.

- 2. The author is not a linguistics major; understanding of historical phonology may be incomplete.

- 3. Tone sandhi in connected speech is not yet supported; all pinyin output keeps citation tones. Reasons:

    - Sandhi rules may differ across regions
    - Specific sandhi often depends on the speaker's subjective phrasing or context
    - Sandhi tones frequently fall outside the 8 base tones of Teochew; a finer tone-value system would greatly increase effort and hinder data scaling

- 4. The Lianjiang variety of the Chaopu group is excluded, as it differs greatly from the Hanjiang and Rongjiang varieties and is treated as an outlier.
- 5. All conversion mappings use brute-force dictionary lookup; initial load efficiency is low and needs optimization.
- 6. No intelligent part-of-speech judgment; surnames, personal names, numbers, and special place names require semi-manual handling.

### Recent changes
* [2026/10/27]
  - **English docs and comments**: added [README.en.md](./README.en.md) (full English readme); the old `readme.md` was renamed to `README.cn.md`; `pyproject.toml`'s `readme` and `description` now use English. Code comments and docstrings have been translated to English; GUI labels, error messages, dictionary data, and romanization scheme display names remain Chinese.
  - Dev environment switched to uv: `uv venv` + `uv pip install -e .`.

* [2026/10/13]
  - **Project restructured as a standard Python package `pypengim`**: code moved from `script/` to `pypengim/`, dictionary data from `dict_data/` to `pypengim/data/`, with renames (char tables `char_*`, word tables `word_*`). Now installable via `pip install .` and runnable from any directory. Import as `from pypengim import pyPengIm`; the old `from script.pyPengIm import pyPengIm` still works temporarily (with a deprecation warning).
  - **Accent conversion supports word-level pairs**: some readings only change in specific words, e.g. 「家己」 (oneself) is `ga1 di7|li7` in Jieyang, but 「己」 alone is unchanged. Accent tables can write `word_fucheng_reading#target_reading`.
  - Surname list adjusted: single surnames rarely used as such in daily life (e.g. 乜, 只, 还, 区) are commented out.
  - **Accent mappings corrected**: against the Native Language Network, PUJdict, and the basic character/word dictionary, 20+ Jieyang/Shantou -oin and -iou mappings were checked and fixed (e.g. 閒 ain5, 苋 hain7, 佻 tiao2, 哟 iao1); Jieyang 门, 们, 扪, 钔, 问, 晚 change from mung to meng; Chenghai hng1 unified to heng1 (方, 荒, 昏, etc.).
  - **Character table cleanup**: merged 34 duplicate entries in the low-frequency char table (later entries used to overwrite earlier ones, losing readings); added `char_nasal_variants.txt` for characters with both nasalized and non-nasalized reading pairs (e.g. 底 doi2/doin2, 非 hui1/huin1).

* [2026/10/07]
  - Fixed various vocabulary and character-reading errors (initial/final/tone errors, mismatched reading counts, duplicate entries, etc.).
  - Unified convention: when the initial is m, n, or ng, vowels always carry nasalization — add -n at the end of vowel-final finals, and insert -n before h in -h finals (-nh). E.g. ni5 → nin5, ê2 → ên2, noi5 → noin5, muêh8 → muênh8, moh4 → monh4. Finals ending in consonants (-ng, -m, -b, -g, -d), already-nasalized finals, and syllabic nasals (m, ng, hm, hng, ngh, hngh) are unaffected. Dictionaries, accent conversion tables, IPA dictionary, romanization scheme mappings, and annotated datasets were synced; finals anh, aonh, oinh, onh, uênh were added.
  - Added accent-to-accent conversion (any pair, e.g. Shantou→Jieyang) and scheme-to-scheme conversion (any pair, e.g. Pe̍h-ūe-jī→Gaginang Peng'im). See 【Usage → 7. Other romanization schemes】 and 【8. Accent conversion】.
  - Added multiple romanization scheme outputs: Teochew pinyin, Fielde, Pe̍h-ūe-jī (diacritic / digit / superscript tones), Gaginang Peng'im, Chen Enquan; default remains Teochew pinyin. See 【Usage → 7. Other romanization schemes】; the GUI also gained a “romanization scheme” dropdown.

* [2025/12/04]
  - Added the Tencent Channel “AI 潮汕话” community for交流/experience without a VPN.

    PC web: https://pd.qq.com/s/13fb621f2

    Mobile QQ / WeChat mini-program:
            <div align="center">
                <img src="./image/tencent_discord.jpg" width="200" />
            </div>

* [2025/04/23]
  - Added [reference readings for country names](./doc/country_list.md)
* [2025/04/23]
  - Removed from the surname file the **parts that do not need alternate readings**;
  - Added support for Chinese historical **reign titles** (prefer literary readings), mainly for disambiguating polyphones such as 【咸】【天】【安】【元】【大】
  - Added a pinyin dictionary of ancient Chinese nouns (dynasties, regimes, ethnic groups, personal names, official titles) (history.txt)
  - Added three Han–Rong mixed accents: **Gimzieh-general (gz-g)**, **Gimzieh-classical (gz-c)**, **Ampou (ap)**
    - Gimzieh-general: widely used in Jinshi, Shaxi, and parts of Caitang and Longhu (town); features no closed finals and Rongjiang assimilation ([ing][ig] merge into [êng][êg]; [iêng][iêg][uêng][uêg] merge into [iang][iag][uang][uag]). Also 【乞】 (give/by) reads 【koih4】, 【橄榄】 reads [gai1 nai2], 【每】 reads [mui2], 【某(人)】 reads [mung2]; **the three initial–final groups [boi][bhoi][poi] (and their nasalized counterparts) conventionally merge into [buê][bhuê][puê]**, e.g. 【买】 [bhuê2], 【批】 [puê1], 【畔】 [buên5].
    - Gimzieh-classical: in Jinshi, Shaxi, and parts of Longhu (town); on top of gimzieh-general, some finals with [o] become unrounded, reading [ɤ], written here as [er]. E.g. 【坐】 【zer6】 (IPA [tsɤ25]), 袋 【der7】 (IPA [tɤ21]).
    - Ampou: similar to gimzieh-general — no closed finals, Rongjiang assimilation, 【乞】 reads 【koih4】 — but keeps [boi][bhoi][poi] and their nasalized counterparts. 森, 鲇, 参, 糁 change from [siam1] to [sing1]. Finals [iê][iên][iêh] become [io][ion][ioh], though actual pronunciation differs slightly from Jieyang/Shantou [io][ion][ioh].
    - **These three accent mappings may contain errors; locals are welcome to point them out**
  - Custom accents supported
  - Fixed some errors in the Chaozhou dictionary
  - Split 【𠶧】 into 【昣@diang1】 and 【倎@diang5】 meaning “time/when” and “who” respectively
  - Added GUI


### Usage / Examples

#### 0. Installation
```
pip install .          # run at the repo root; for development use pip install -e .
```
Dependencies: jieba, cn2an, pyyaml. Dictionary data ships with the package; no need to run from the repo root.


#### 1. Default mode
Create an instance and call class methods. Default is optimized mode (Fucheng accent standard), automatic jieba word segmentation, and best-match readings.

```
from pypengim import pyPengIm

pinyin_tool = pyPengIm()
print(pinyin_tool.pinyin('中心 企业'))

Output:
{'result': [['中心', ['dong1'], ['sim1']], ['企业', ['gi6'], ['ngiab8']]], 'pinyin_seq': 'dong1 sim1 gi6 ngiab8', 'surname_notice': []}

print(pinyin_tool.pinyin('方耀 翁万达')) 

Output:
{'result': [['方耀', ['bung1'], ['iou6']], ['翁万达', ['êng1'], ['bhuêng7'], ['dag8']]], 'pinyin_seq': 'bung1 iou6 êng1 bhuêng7 dag8', 'surname_notice': [['方', ['bung1']], ['翁', ['êng1']]]}
```

By default, `.pinyin()` returns a dict with three keys:
```
'result': a list whose items are [segmented word – pinyin] pairs (also lists).
The first element of each item is the current word segment; if the segment has n characters,
the next n elements are the reading lists for character i.

By default, polyphones are disambiguated via dictionary rule matching against the segmentation;
in the examples above 【中】 and 【企】 are polyphones resolved this way.

'pinyin_seq': because the 'result' hierarchy is somewhat complex, a flat pinyin sequence is provided.

'surname_notice': Teochew surname readings are special and complex; the tool is not yet smart enough
to decide whether a word should use a dedicated surname alternate reading, so surname_notice is a hint.
In the examples, 【方】 and 【翁】 are surnames and need special surname readings.

```

#### 2. Heteronym (all readings) mode
Set `heteronym=True` to enable heteronym mode. Outputs every potential reading of each character; an asterisk (*) marks a less common reading or one that exists only in a few specific words, such as 【家己】, 【目的】, etc.

```
pinyin_tool.pinyin('家中',heteronym=True)

Output:
{'result': [['家', ['gê1', 'gia1*', 'ga1*', 'kia1*']], ['中', ['dong1', 'dang1', 'dong3', 'dêng3']]], 'pinyin_seq': 'gê1|gia1|ga1|kia1 dong1|dang1|dong3|dêng3', 'surname_notice': []}
```
Above, 【家】 has 4 readings but only 【gê1】 is common; 【ga1】 is only used in 【家己】, 【gia1】 in classical texts/poetry, 【kia1】 in dialect words 【私@sai1 家@kia1】, 【私家钱】, etc., meaning private/personal (though that word seems rare now).

【中】 also has 4 readings: Mandarin zhōng/zhòng each have literary and colloquial readings, so Teochew has 4: zhōng → 【'dang1' (colloquial), 'dong1' (literary)】, zhòng → 【'dong3' (literary), 'dêng3' (colloquial)】.


#### 3. Accent conversion
Default output is Fucheng (tc). With the `accent` parameter, convert to Shantou (st), Chenghai (th), or Jieyang (ky):
```
pinyin_tool.pinyin('恁揭阳')['result'] # Chaozhou Fucheng accent
pinyin_tool.pinyin('恁揭阳',accent='st')['result'] # convert to Shantou
pinyin_tool.pinyin('恁揭阳',accent='th')['result'] # convert to Chenghai
pinyin_tool.pinyin('恁揭阳',accent='ky')['result'] # convert to Jieyang

Outputs respectively:
[['恁', ['ning2']], ['揭阳', ['gig4'], ['iên5']]]
[['恁', ['ning2']], ['揭阳', ['gig4'], ['ion5']]]
[['恁', ['neng2']], ['揭阳', ['gig4'], ['iên5']]]
[['恁', ['nêng2']], ['揭阳', ['gêg4'], ['ion5']]]

```
#### 4. Segmentation modes
Chinese context is special; different segmentations may yield different readings. `auto_split` provides two modes:

- 4.1 jieba automatic segmentation: segment with jieba and substitute

- 4.2 manual space-separated segmentation: use when jieba is not smart enough; also lets you pick candidate words for the next step (colloquial conversion). Example in section 5.


#### 5. Colloquial conversion
To make Teochew text closer to real speech, use `.to_oral` to replace some vocabulary with Chaozhou dialect words, then feed the result to `.pinyin`. Words marked with '#' are phonetic conversions using local dialect pronunciations.

```

oral_text=pinyin_tool.to_oral('你要去哪里玩',auto_split=True)# automatic segmentation
print(oral_text)
# pinyin_tool.pinyin(oral_text) ## to pinyin

oral_text=pinyin_tool.to_oral('我 要 去 做生意',auto_split=False)# segmentation inaccurate; manual spaces
print(oral_text)

Output:
你 欲# 去 底块# 𨑨迌#
我 欲# 去 做生理#
```
- Candidate word mode
  Some Mandarin words map to multiple Teochew words, or need not be converted. In the [mapping dictionary](./pypengim/data/word_dict/mandarin_to_teochew.txt), digits 1, 2, 3, 4 select alternatives.
  ```
    print(pinyin_tool.to_oral('晚上 晚上1 晚上2 晚上3',auto_split=False))# digits enable alternatives

    Output:
    暝囝# 夜旰# 一夜# 夜昏囝#
  ```


- '#' controls local-vocabulary mode: some words differ between local and Mandarin usage and thus in reading.
  ```
    print(pinyin_tool.pinyin('生理')['pinyin_seq'])# Mandarin sense: organic activity of organisms
    print(pinyin_tool.pinyin('生理#')['pinyin_seq'])# Teochew sense: business/trade 
    
    Output:
        sên1 li2
        sêng1 li2

    print(pinyin_tool.pinyin('倚赖')['pinyin_seq'])# Mandarin sense: rely on
    print(pinyin_tool.pinyin('倚赖#')['pinyin_seq'])# Teochew sense: frame/slander 

    Output:
      i2|in2 nai6
      ua2 lua7

  ```

#### 6. Single-character mode
Query all readings of one character across all accents
```
print(pinyin_tool.single_query('生'))

{'潮州': ['生', ['sên1', 'cên1', 'sêng1']], '汕头': ['生', ['sên1', 'cên1', 'sêng1']], '澄海': ['生', ['sên1', 'cên1', 'sêng1']], '揭阳': ['生', ['sên1', 'cên1', 'sêng1']]}

```

#### 7. Other romanization schemes
Default is Teochew pinyin (Pêng'im). With `scheme`, output other schemes directly; `to_scheme` converts existing Teochew pinyin sequences.

| scheme | Scheme | Example (`水` zui2) |
|---|---|---|
| `pengim` | Teochew pinyin (default) | `zui2` |
| `dieghv` | Dieghv | `zui2` (ṳ written as v, e.g. `e`→`v`) |
| `fielde` | Fielde (diacritic tones) | `cúi` |
| `puj` | Pe̍h-ūe-jī, diacritic tones | `tsúi` |
| `pujn` | Pe̍h-ūe-jī, digit tones | `tsui2` |
| `pujs` | Pe̍h-ūe-jī, superscript tones | `tsui²` |
| `ggn` / `ggns` | Gaginang Peng'im, digit / superscript | `jui2` / `jui²` |
| `chen` | Chen Enquan's Teochew scheme | `zui2` |

```
print(pinyin_tool.pinyin('我吃蘑菇中毒了', scheme='puj')['pinyin_seq'])
Output: úa ngṳk mô kou tong ta̍k liòu

print(pinyin_tool.pinyin('我吃蘑菇中毒了', scheme='chen')['pinyin_seq'])
Output: ua2 jwg4 mo5 gou1 doj1 dak8 liou3

# When you already have a Teochew pinyin sequence
print(pinyin_tool.to_scheme('ua2 ng eg4', 'ggns'))
```

Notes:
- The `result` field is always Teochew pinyin; only `pinyin_seq` is converted by `scheme`, so it composes with accent conversion (`accent`).
- Initial/final tables for each scheme live in `pypengim/data/romanization/` (`puj.txt`, `fielde.txt`, `dieghv.txt`, `ggn.txt`, `chen_enquan.txt`), same format as `pypengim/data/phonology/syllable_to_ipa.txt`; edit freely.
- Pe̍h-ūe-jī, Fielde, Dieghv, and Gaginang mappings were compiled from [pengim-js](https://github.com/learn-teochew/pengim-js) (MIT); Fielde finals absent from the original dictionary (Fucheng/Gimzieh finals such as `eng`, `iêng`, `ung`) were extrapolated from Pe̍h-ūe-jī.
- Chen Enquan pinyin is aligned IPA-by-IPA via `chen_enquan_ipa.txt`: of 100 finals, 83 match the original IPA exactly; the other 17 (Fucheng-specific finals like `iêng`, `iou`, `êi`, plus Gimzieh finals) follow its spelling rules by analogy.
- Gimzieh finals `er`, `erh`, `ern` ([ɤ]) have no standard spelling in the original schemes; this repo defines: Pe̍h-ūe-jī `or`, `orh`, `orⁿ`; other schemes `er`, `erh`, `ern`.
- Front nasals (alveolar endings [n]/[t̚]): most areas including the three urban centers have merged them into velar [ŋ]/[k̚]; a few areas still retain them. In Teochew pinyin `-n` already marks nasalization, so this pair is written `-nd`/`-d`; Pe̍h-ūe-jī uses `-n`/`-t`. Currently 14 finals: `and ad iênd iêd ind id und ud end ed uênd uêd uand uad`, e.g. `zind1`→`tsin1`, `zad4`→`tsat4`. The dictionaries do not yet annotate these readings; other schemes and IPA do not include them either.
- Chen Enquan's scheme is Jieyang-based; syllabic nasals `ng`, `ngh`, `hng`, `hngh` are written `wn`, `wq`, `hwn`, `hwq` per the original.
- Schemes convert among themselves: `to_scheme(sequence, target, from_scheme=source)`; source defaults to Teochew pinyin. Internally everything is restored to Teochew pinyin first, so any pair works; unrecognized syllables pass through unchanged.
- Reverse-parsing limits: Fielde writes both tone 5 and tone 8 as `^`, distinguished only by entering-tone endings; Chen Enquan writes both `en` and `ng` as `wn`, reverse always yields `ng` (the dictionary has no `-en` final). All 2700+ syllables in the dictionary round-trip correctly in every scheme.


#### 8. Accent-to-accent conversion
Accent tables (`pypengim/data/accent_convert/to_*.txt`) only record “Fucheng → other”; now any pair works: restore the source accent's readings to Fucheng syllables, then convert to the target. Accent codes: `tc` Fucheng, `ky` Jieyang, `st` Shantou, `th` Chenghai, `gz_c` / `gz_g` Gimzieh, `ap` Ampou.

```
st = pinyin_tool.pinyin('冤家', accent='st', auto_split=False)['pinyin_seq']   # uang1 gê1 (Shantou)
print(pinyin_tool.convert_accent_between('冤家', st, 'st', 'ky'))              # uang1 gê1 (Jieyang)
print(pinyin_tool.convert_accent_between('冤家', st, 'st', 'tc'))              # uêng1 gê1 (Fucheng)
```

Some readings only change inside specific words — e.g. 「家己」 (oneself) is `ga1 di7|li7` in Jieyang, but 「己」 alone is unchanged. Word-level mappings are written as described in 【13. Custom accents】:

```
pinyin_tool.pinyin('我家己去', accent='ky')['pinyin_seq']                  # ua2 ga1 di7|li7 ke3
pinyin_tool.pinyin('己', accent='ky')['pinyin_seq']                        # gi2 (unchanged)
print(pinyin_tool.convert_accent_between('家己', 'ga1 di7', 'ky', 'st'))  # ga1 gi7
```

- Readings must correspond one-to-one with hanzi; a count mismatch raises `ValueError`. Characters missing from the dictionary or readings not belonging to the character pass through unchanged.
- The GUI gained an “accent / scheme conversion” section with source/target accent and scheme selectors.

#### 9. Convert to IPA
Input a Teochew pinyin sequence, output an IPA sequence (list), each item's initial/final/tone space-separated
```
pinyin_seq=pinyin_tool.pinyin('我吃蘑菇中毒了')['pinyin_seq']
print(pinyin_tool.to_IPA(pinyin_seq))

Output: ['ua ˥˧', 'ŋ ɯk ˨', 'm o ˥', 'k ou ˧', 't oŋ ˨˩˧', 't ak ˥', 'l iou ˨˩˧'] 
```

#### 10. Phoneme mode
Output smaller phoneme units ([initial final+tone]), mainly for training with MFA (Montreal Forced Aligner) and similar tools

```
pinyin_seq=pinyin_tool.pinyin('我吃蘑菇中毒了')['pinyin_seq']
print(pinyin_tool.to_phoneme(pinyin_seq))

Output: ['ua2', 'ng eg4', 'm o5', 'g ou1', 'd ong3', 'd ag8', 'l iou3']
```

#### 11. Arabic numerals: convert to hanzi manually before input

Chinese has flexible numeral readings — sometimes digit-by-digit (phone numbers, ID numbers, student numbers, class numbers, years, postal codes), with 【一】 sometimes read as 【幺】; sometimes as a value. Check these yourself.
```
from pypengim.utils import num_to_chinese,num_to_chinese_smart
print(num_to_chinese('15')) #【一 幺】五
print(num_to_chinese('120')) # 【一 幺】二零

print(num_to_chinese_smart('15')) # 十五
print(num_to_chinese_smart('120')) # 一百二十

```


#### 12. Characters not in the dictionary output 'None'
```
print(pinyin_tool.pinyin('*',accent='ky')['result']) # convert to Jieyang
[['*', ['None']]]
```

#### 13. Custom accents
Add your own accent mapping file under `pypengim/data/accent_convert`, then register it in `accent.yaml`:
```accent.yaml
ky: 
  path: to_Kityall.txt
  name: "揭阳"
st: 
  path: to_Swatow.txt
  name: "汕头"
th: 
  path: to_Tenhigh.txt
  name: "澄海"
new_accent: 
  path: to_new_accent.txt
  name: accent_name
```
`to_new_accent.txt` format:
```
{char}_{fucheng}#{target}
反_huêng2#huang2
爿_puêng5#puang5
畔_puêng3#puang3
扮_buêng6#buang6
```

Besides char-to-char, word-to-word is supported: `{word}_{fucheng_readings}#{target_readings}`, readings space-separated per character, multiple candidates per character separated by `|`.
Only applies when the whole word appears (possibly inside a longer segment, e.g. 「家己人」) and the Fucheng readings match; otherwise char-level conversion is used:
```
家己_ga1 gi7#ga1 di7|li7
```

For Gimzieh-general, Gimzieh-classical, and Ampou, write in `accent.yaml`:
```accent.yaml
ky: 
  path: to_Kityall.txt
  name: "揭阳"
st: 
  path: to_Swatow.txt
  name: "汕头"
th: 
  path: to_Tenhigh.txt
  name: "澄海"
gz_c: 
  path: to_Gimzieh_c.txt
  name: "金石-经典"
gz_g: 
  path: to_Gimzieh_g.txt
  name: "金石-泛"
ap: 
  path: to_Ampou.txt
  name: "庵埠"
```



#### 14. Homophone lookup of the standard character [TBD]
Look up 【沤】 from 【奥】, 【喝誧】 from 【华普】, 【喇誧】 from 【拉普】. [TODO]

### Graphical interface
Interactively adjust segmentation, accent, colloquial translation, Arabic-numeral-to-hanzi, and pinyin annotation.

```
Run:
python gui_server.py

Open in browser:
http://127.0.0.1:7860
```

![GUI](./image/gui.jpg)


### [Teochew romanization scheme](http://www.czyzd.com/data/chaopin) and the standard accent
Among written/web materials for Teochew, the most widely used is the Teochew romanization scheme (Pêng'im) published by the Guangdong education authorities in September 1960. Based on the Shantou accent, it writes sounds in Latin letters with numbered tones: 17 initials (excluding zero initial), 59 finals, 8 base tones.

However, the scheme omits finals that exist in speech but have few or no example characters — e.g. aon (好), uên (横), uin (畏), oun (虎), iun (幼), uain (县), aoh (乐), eg (乞) — as well as finals specific to other regions, e.g. Chaozhou urban iêng (焉), uêng (冤), iêg (噎), uêg (越). Counting these, Teochew has over 80 finals.

Teochew also has more than 8 tones. In connected speech there is very complex tone sandhi; some sandhi tones are derivatives outside the 8 base tones. Including derivatives and regional variation, Teochew has 10+ tones.

Southern dialects often vary every ten li; Teochew, being primarily spoken, naturally has many varieties. Broadly by river: Hanjiang, Rongjiang, Lianjiang, and Huanggang River. Even within Shantou urban (Jinping, Longhu) one can split four or five accents. Text processing must pick one standard. This project follows the Chaozhou Yin Dictionary and uses Chaozhou's Fucheng accent as standard.


#### Why Fucheng as the standard?
Fucheng is mainly used in Chaozhou prefectural city, Beiguan, Yixi, Guihu, Wenci, etc. It has clear closed finals and pseudo-front nasals (iêng, uêng), and is among the richest in finals — with high character-reading distinctiveness. From 19th-century missionary documents through post-1949 dialect scholarship, Fucheng has been the most fully recorded and studied; the 19th-century “old Fucheng” can be seen as a superset of today's accents. Compared with lowland areas with heavy population mobility, Fucheng in hill country evolves more slowly and is therefore more stable.


### Pain-Kuan Orthography (PKO)

Teochew is not an official language, so there is no appointed norm or standard written form. In film/TV subtitles, online articles and comments, and even some experts' folklore/dialect papers, Teochew is usually written with homophone characters.

In rare cases this works: 自己人 as “胶己人”, 男人 as "打埠", 姘头/奸夫 as “老衍” (source character “嫪毐”, the Qin-era paramour), 迎老爷 as "营老爷" — harmless and sometimes clearer.


But in most cases homophone spelling is neither consistent nor accurate; and experts' reconstructed characters or orthography proposals also have clear gaps — too many polyphones, meanings clashing with modern Mandarin, persistent grapheme-less words, contracted syllables, phonetic loans, popular or variant forms causing inconsistent writing, etc.

In summary, I want to improve existing expert proposals — reduce polyphone counts, reduce vocabulary conflicts and ambiguity, reduce overloading of single characters, unify writing — to build a standard that aids Teochew hanzi-to-pinyin conversion. See [Pain-Kuan Orthography](./doc/readme.md) (Chinese) for more.
