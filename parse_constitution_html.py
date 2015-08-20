from bs4 import BeautifulSoup
import roman
import json, re, os
import patterns, rewrite

def get_unit(title):
	pattern = patterns.makeTitlePatterns()
	title = title.lower()
	unit = title.replace(" ", "_")
	unit = re.sub("[ \[\]\(\)]", "_", title)
	number = "1"
	for unitForm, unitPattern in pattern.iteritems():
		m = unitPattern.match(title)
		if m:
			if unitForm == 'title_preamble':
				unit = m.group(1)
				number = "1"
			elif unitForm == 'title_number':
				unit = "unspecified"
				number = m.group(1)
			elif unitForm == 'title_unit_roman':
				unit = m.group(1)
				try:
					number = str(roman.fromRoman(m.group(2).upper()))
				except roman.InvalidRomanNumeralError:
					print "Invalid Roman title number:", title, "unit:", unit, "number:", number
					number = m.group(2)
			else:
				unit = m.group(1)
				number = m.group(2)
				if unit == 'art':
					unit = 'article'
	return unit, number

def update_stacks(sectionData, idStack, partStack):
	currPart = sectionData['unit'] + "[" + sectionData['number'] + "]"
	prevLevel = len(idStack) - 2
	if sectionData['level'] == prevLevel:
		idStack[-1] = sectionData['id']
		partStack[-1] = currPart
	elif sectionData['level'] > prevLevel:
		idStack.append(sectionData['id'])
		partStack.append(currPart)
	elif sectionData['level'] < prevLevel:
		for i in range(0, prevLevel - sectionData['level']):
			idStack.pop()
			partStack.pop()
		partStack[-1] = currPart
		idStack[-1] = sectionData['id']

def parse_section(htmlSection):
	sectionData = {}
	sectionData['id'] = 'section-' + str(htmlSection['id'])
	classAttrs = htmlSection['class']
	sectionData['level'] = int(classAttrs[1].replace("level",""))
	currType = classAttrs[2].replace("article-","")
	rewriter = rewrite.RewritePatterns()
	if currType == 'title':
		try:
			sectionData['text'] = htmlSection.find(class_='float-left').text
			cleanText = rewriter.rewrite_text(sectionData['text'].lower())
			sectionData['text_clean'] = cleanText
			sectionData['unit'], sectionData['number'] = get_unit(cleanText)
		except AttributeError:
			try:
				firstParagraph = htmlSection.section.p.text
				sectionData['unit'], sectionData['number'] = get_unit(firstParagraph)
			except AttributeError:
				sectionData['unit'] = "untitled_section"
				sectionData['number'] = htmlSection['id']
			sectionData['text'] = ""
			sectionData['text_clean'] = ""
	else:
		sectionData['unit'] = 'body'
		sectionData['number'] = '1'
		sectionData['text'] = htmlSection.text
		sectionData['text_clean'] = rewriter.rewrite_text(sectionData['text'].lower())
	return sectionData

def parse_constitution(constitution, inputFile):
	with open(inputFile, 'rb') as fh:
		soup = BeautifulSoup(fh, "lxml")
	textOffset = 0
	section = {}
	idStack = ['section-0']
	partStack = ['root[0]']
	htmlSections = soup.find_all('section')
	hasUnspecified = False
	for htmlSection in htmlSections:
		sectionData = parse_section(htmlSection)
		update_stacks(sectionData, idStack, partStack)
		sectionData['constitution'] = constitution
		sectionData['name'] = "/".join(partStack)
		sectionData['parent'] = idStack[-2]
		sectionData['start_offset'] = textOffset
		textOffset += len(sectionData['text'])
		sectionData['end_offset'] = textOffset
		section[sectionData['id']] = sectionData
		if sectionData['unit'] == 'unspecified':
			hasUnspecified = True
	if hasUnspecified:
		specify_units(section)
	return section

def parse_constitutions(inputDir, outputDir):
	for constitution in next(os.walk(inputDir))[2]:
		inputFile = os.path.join(inputDir, constitution)
		outputFile = os.path.join(outputDir, constitution) + ".json"
		print "Parsing constitution", constitution, "..."
		sections = parse_constitution(constitution, inputFile)
		with open(outputFile, 'wb') as writer:
			json.dump(sections, writer, indent=4)

def specify_units(section):
	secCount = 0
	artCount = 0
	for sectionId in section:
		text = section[sectionId]['text']
		secList = re.findall(r'\bsection \d', text, re.IGNORECASE)
		artList = re.findall(r'\barticle \d', text, re.IGNORECASE)
		artCount += len(artList)
		secCount += len(secList)
	if artCount < secCount:
		resolve_unspecified('section', section)
	else:
		resolve_unspecified('article', section)

def resolve_unspecified(secUnit, section):
	for sectionId in section:
		replaceUnit = secUnit
		if replaceUnit in section[sectionId]['name']:
			replaceUnit = "sub" + replaceUnit
		while 'unspecified' in section[sectionId]['name']:
			section[sectionId]['name'] = section[sectionId]['name'].replace('unspecified', replaceUnit, 1)
			replaceUnit = "sub" + replaceUnit
		replaceUnit = replaceUnit.replace("sub", "", 1)
		if 'unspecified' in section[sectionId]['unit']:
			section[sectionId]['unit'] = section[sectionId]['unit'].replace('unspecified', replaceUnit, 1)



def main(script, constitutionDir, outputDir):
	parse_constitutions(constitutionDir, outputDir)

if __name__ == "__main__":
	import sys
	main(*sys.argv)

