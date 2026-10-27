
# initials
INITIALS = [
    'b','bh','c','d','g',
    'gh','h','k','l','m',
    'n','ng','p','r','s',
    't','z'
]

# labial-ending finals (closed finals)
__rhyme_with_a_labial_ending__ = [
    "am","iam","im","om","uam",
    "ab","iab","ib","uab",
]

# nasalized finals, nasalized vowels
__nasal_vowel__  = [
    "ain","an","en","ian",
    "in","iaon","iaonh","inh",
    "ioun","ion","oin","on","iun",
    "iounh","oun","uain","uan","uin","ên","ênh",
    "uên","aon","uanh",
    # vowels after nasal initials (m n ng) always carry nasalization; the finals below derive from that
    "anh","aonh","iên","oinh","onh","uênh",
]

# finals
FINALS = [
    "a","ag","ah","ai",
    "aih","ang",
    "ao","aoh","e","eg",
    "eh","eng","i","ia",
    "iag","iah",
    "iang","iao","iaoh",
    "ig","ih",
    "ing","io","iog","ioh",
    "iong","iou","iouh",
    "iu","iê","iêg",
    "iêh","iêng",
    "o","og","oh","oi","oih",
    "ong","ou",
    "u","ua","uag",
    "uah","uai",
    "uang","ug","uh","ui",
    "ung","uê","uêg","uêh",
    "uêi","uêng","ê","êg",
    "êh","êi","êng",
]



# Gimzieh, Shaxi, Longhu
__gimzieh__ = [
    'er','erh','ern'
]
FINALS = FINALS + __nasal_vowel__ + __rhyme_with_a_labial_ending__ + __gimzieh__

# syllabic nasals
NASALS = [
    'hm','hng','hngh','ngh','ng','m'
]
