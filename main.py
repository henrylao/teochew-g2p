from pypengim import pyPengIm 

pinyin_tool = pyPengIm()

# default mode
print(pinyin_tool.pinyin('中心 企业'))
print(pinyin_tool.pinyin('方耀 翁万达')) 

# exit()
# heteronym mode (all readings)
print(pinyin_tool.pinyin('家中',heteronym=True)) 

## accent conversion
print(pinyin_tool.pinyin('恁揭阳')['result'])# Chaozhou Fucheng accent
print(pinyin_tool.pinyin('恁揭阳',accent='st')['result']) # convert to Shantou urban
print(pinyin_tool.pinyin('恁揭阳',accent='th')['result']) # convert to Chenghai
print(pinyin_tool.pinyin('恁揭阳',accent='ky')['result']) # convert to Jieyang

# print(pinyin_tool.pinyin('橄榄',accent='gz_c')['result']) # convert to Gimzieh-classical
# print(pinyin_tool.pinyin('人参',accent='ap')['result']) # convert to Ampou

#
print(pinyin_tool.pinyin('我吃蘑菇中毒了')) 

# colloquial conversion
print(pinyin_tool.to_oral('你要去哪里玩',auto_split=True))
print(pinyin_tool.to_oral('我 要 去 做生意',auto_split=False))
print(pinyin_tool.to_oral('晚上 晚上1 晚上2 晚上3',auto_split=False))# digits 1/2/3 enable alternative words


# '#' toggles local-vocabulary reading mode.
print(pinyin_tool.pinyin('生理')['pinyin_seq'])# Mandarin sense: organic activity of living organisms
print(pinyin_tool.pinyin('生理#')['pinyin_seq'])# Teochew sense: business/trade

print(pinyin_tool.pinyin('倚赖')['pinyin_seq'])# Mandarin sense: rely on / depend on
print(pinyin_tool.pinyin('倚赖#')['pinyin_seq'])# Teochew sense: frame / slander


# query all readings and accents of a single character
print(pinyin_tool.single_query('生'))


# pinyin sequence -> IPA and phonemes
pinyin_seq=pinyin_tool.pinyin('我吃蘑菇中毒了')['pinyin_seq']
print(pinyin_tool.to_IPA(pinyin_seq))
print(pinyin_tool.to_phoneme(pinyin_seq))

# Other schemes: default pengim; also dieghv, fielde, puj/pujn/pujs (Pe̍h-ūe-jī diacritic/digit/superscript),
# ggn/ggns (Gaginang digit/superscript), chen (Chen Enquan)
for scheme in ['dieghv', 'fielde', 'puj', 'pujn', 'pujs', 'ggn', 'chen']:
    print(scheme, pinyin_tool.pinyin('我吃蘑菇中毒了', scheme=scheme)['pinyin_seq'])
print(pinyin_tool.to_scheme(pinyin_seq, 'pujs'))# can also convert an existing Teochew pinyin sequence directly

# scheme conversion: from_scheme sets the input scheme (default Teochew pinyin); any pair works
print(pinyin_tool.to_scheme('úa ngṳk mô', 'ggns', from_scheme='puj'))
print(pinyin_tool.to_scheme('ua2 jwg4 mo5', 'puj', from_scheme='chen'))

# accent conversion: any -> any. Provide hanzi plus that accent's readings (one per char)
st = pinyin_tool.pinyin('冤家', accent='st', auto_split=False)['pinyin_seq']  # Shantou readings
print(pinyin_tool.convert_accent_between('冤家', st, 'st', 'ky'))   # Shantou -> Jieyang
print(pinyin_tool.convert_accent_between('冤家', st, 'st', 'tc'))   # Shantou -> Fucheng
# syllable-only (no hanzi): rough conversion (one syllable may map to several Fucheng syllables)
print(pinyin_tool.accent_converter().convert_syllable('uang1', 'st', 'ky'))



print(pinyin_tool.pinyin('*',accent='ky')['result'])



## Arabic numerals
from pypengim.utils import num_to_chinese,num_to_chinese_smart

print(num_to_chinese('15'))
print(num_to_chinese('120'))

print(num_to_chinese_smart('15'))
print(num_to_chinese_smart('120'))
