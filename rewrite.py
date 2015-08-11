import re

rankWordPattern = re.compile("(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirtheenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth)")

countWordPattern = re.compile("(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eightteen|nineteen|twenty)")

relativeWords = [
	"previous",
	"next",
]

rankMap = {
	"first": '1',
	"second": '2',
        "third": '3',
        "fourth": '4',
        "fifth": '5',
        "sixth": '6',
        "seventh": '7',
        "eight": '8',
        "ninth": '9',
        "tenth": '10',
        "eleventh": '11',
        "twelth": '12',
        "thirteenth": '13',
        "fourteenth": '14',
        "fifteenth": '15',
        "sixteenth": '16',
        "seventeenth": '17',
        "eighteenth": '18',
        "nineteenth": '19',
        "twentieth": '20',
        "twenty-sixth": '26',
}

countMap = {
	"one": '1',
	"two": '2',
        "three": '3',
        "four": '4',
        "five": '5',
        "six": '6',
        "seven": '7',
        "eight": '8',
        "nine": '9',
        "ten": '10',
        "eleven": '11',
        "twelve": '12',
        "thirteen": '13',
        "fourteen": '14',
        "fifteen": '15',
        "sixteen": '16',
        "seventeen": '17',
        "eighteen": '18',
        "nineteen": '19',
        "twenty": '20',
}


def rewrite_rank_words(text):
	rankWords = "\\b(" + "|".join(rankMap.keys()) + ")\\b"
	rankPattern = re.compile(rankWords + " (\w+)")
	done = 0
	while not done:
		m = re.search(rankPattern, text)
		if m:
			number = rankMap[m.group(1)]
			text = re.sub(m.group(0), m.group(2) + " " + number, text)
		else:
			done = 1
	return text


def rewrite_count_words(text):
	countWords = "\\b(" + "|".join(countMap.keys()) + ")\\b"
	countPattern = re.compile("(\w+) " + countWords )
	done = 0
	while not done:
		m = re.search(countPattern, text)
		if m:
			number = countMap[m.group(2)]
			text = re.sub(m.group(0), m.group(1) + " " + number, text)
		else:
			done = 1
	return text


def rewrite_text(text):
	text = rewrite_rank_words(text)
	text = rewrite_count_words(text)
	done = 0
	while done == 0:
		done = 1
		# Section 116A -> Section 116
		numChar = "(\d+)([a-zA-Z]+)"
		mNumChar = re.search(numChar, text)
		if mNumChar:
			text = re.sub(numChar, mNumChar.group(1), text, 1, re.IGNORECASE)
			done = 0
		# Section 116.A -> Section 116
		# Section 116.1 -> Section 116
		numDotChar = "(\d+)(\.[a-zA-Z]+)"
		mNumDotChar = re.search(numDotChar, text)
		if mNumDotChar:
			text = re.sub(numDotChar, mNumDotChar.group(1), text, 1, re.IGNORECASE)
			done = 0
		# Article 117(3) -> Article 117
		# Article 117(3)(b) -> Article 117
		numSubChar = "(\d+)(\(\w+\))"
		mNumSubChar = re.search(numSubChar, text)
		if mNumSubChar:
			text = re.sub(numSubChar, mNumSubChar.group(1), text, 1, re.IGNORECASE)
			done = 0
		# Subsection (2) -> Subsection 2
		subNum = " \((\d+)\)"
		mSubNum = re.search(subNum, text)
		if mSubNum:
			text = re.sub(subNum, " {0}".format(mSubNum.group(1)), text, 1, re.IGNORECASE)
			done = 0
	return text

def rewrite_sweden(text):
	chunk1 = 'the instrument of government'
	chunk2 = 'the act of succession'
	chunk3 = 'the freedom of the press act'
	chunk4 = 'the fundamental law on freedom of expression'
	chunk5 = 'the riksdag act'
	text = re.sub(chunk1, 'Chunk 1', text, flags=re.IGNORECASE)
	text = re.sub(chunk2, 'Chunk 2', text, flags=re.IGNORECASE)
	text = re.sub(chunk3, 'Chunk 3', text, flags=re.IGNORECASE)
	text = re.sub(chunk4, 'Chunk 4', text, flags=re.IGNORECASE)
	text = re.sub(chunk5, 'Chunk 5', text, flags=re.IGNORECASE)
	return text
