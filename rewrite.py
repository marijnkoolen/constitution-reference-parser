import re
import roman

class RewritePatterns:

	def __init__(self, refUnits=None):
		self.rankWordPattern = re.compile("(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirtheenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth)")

		self.countWordPattern = re.compile("(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eightteen|nineteen|twenty)")

		self.romanPattern = "([ivxlcdm]+)"

		if refUnits == None:
			refUnits = []
		self.refUnits = refUnits
		self.refPattern = re.compile(r"\b(" + "|".join(refUnits) + ")\b")

		self.relativeWords = [
			"previous",
			"next",
			"preceding",
			"following",
		]

		self.rankMap = {
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
			"twelfth": '12',
			"thirteenth": '13',
			"fourteenth": '14',
			"fifteenth": '15',
			"sixteenth": '16',
			"seventeenth": '17',
			"eighteenth": '18',
			"nineteenth": '19',
			"twentieth": '20',
			"twenty-first": '21',
			"twenty-second": '22',
			"twenty-third": '23',
			"twenty-fourth": '24',
			"twenty-fifth": '25',
			"twenty-sixth": '26',
		}

		self.countMap = {
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

	def rewrite_roman_numerals(self, text):
		if self.refUnits == []:
			return text
		romanRef = re.compile(r"\b(" + "|".join(self.refUnits) + ") " + self.romanPattern + r"\b")
		matches = romanRef.findall(text)
		for unit, romanNumeral in matches:
			try:
				transform = roman.fromRoman(romanNumeral.upper())
				number = str(transform)
				text = re.sub(r"\b" + romanNumeral + r"\b", number, text)
				#print "unit:", unit, "Roman Numeral:", romanNumeral, "number:", number, "context:", text
			except roman.InvalidRomanNumeralError:
				pass
		return text


	def rewrite_rank_words(self, text):
		rankWords = "\\b(" + "|".join(self.rankMap.keys()) + ")\\b"
		rankPattern = re.compile("([tT]he )?" + rankWords + " (\w+)")
		done = 0
		while not done:
			m = re.search(rankPattern, text)
			if m:
				number = self.rankMap[m.group(2)]
				nextWord = m.group(3)
				text = re.sub(m.group(0), nextWord + " " + number, text)
			else:
				done = 1
		return text


	def rewrite_count_words(self, text):
		countWords = "\\b(" + "|".join(self.countMap.keys()) + ")\\b"
		countPattern = re.compile("(\w+) " + countWords )
		done = 0
		while not done:
			m = re.search(countPattern, text)
			if m:
				number = self.countMap[m.group(2)]
				text = re.sub(m.group(0), m.group(1) + " " + number, text)
			else:
				done = 1
		return text


	def rewrite_text(self, text):
		if not text:
			return text
		text = self.rewrite_rank_words(text)
		text = self.rewrite_count_words(text)
		text = self.rewrite_roman_numerals(text)
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
			numDotChar = "(\d+)(\.[0-9a-zA-Z]+)"
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
		text = re.sub("(\W)[aA]rt[.]? ([0-9])", "\g<1>article \g<2>", text, re.IGNORECASE)
		text = re.sub("(\W)[sS]ec[.]? ([0-9])", "\g<1>section \g<2>", text, re.IGNORECASE)
		return text

	def rewrite_sweden(self, text):
		mapName = {}
		mapName['the instrument of government'] = "the_instrument_of_goverment 1"
		mapName['the act of succession'] = 'the_act_of_succession 1'
		mapName['the freedom of the press act'] = 'the_freedom_of_the_press_act 1'
		mapName['the fundamental law on freedom of expression'] = 'the_fundamental_law_on_freedom_of_expression 1'
		mapName['the riksdag act'] = 'the_riksdag_act 1'
		for name in mapName:
			text = re.sub(name, mapName[name], text, flags=re.IGNORECASE)

		#text = re.sub(chunk1, 'Chunk 1', text, flags=re.IGNORECASE)
		#text = re.sub(chunk2, 'Chunk 2', text, flags=re.IGNORECASE)
		#text = re.sub(chunk3, 'Chunk 3', text, flags=re.IGNORECASE)
		#text = re.sub(chunk4, 'Chunk 4', text, flags=re.IGNORECASE)
		#text = re.sub(chunk5, 'Chunk 5', text, flags=re.IGNORECASE)
		return text

def main():
	inputText = u"This is civil indpendence for ii"
	rewriter = RewritePatterns()
	rewriter.rewrite_text(inputText)

if __name__ == "__main__":
	main()

