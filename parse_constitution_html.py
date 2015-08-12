from bs4 import BeautifulSoup
import json, re, sys, os
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
	if currType == 'title':
		try:
			sectionData['text'] = htmlSection.find(class_='float-left').text
			cleanText = rewrite.rewrite_text(sectionData['text'].lower())
			sectionData['text_clean'] = cleanText
			sectionData['unit'], sectionData['number'] = get_unit(cleanText)
		except AttributeError:
			sectionData['text'] = "untitled section " + htmlSection['id']
			sectionData['unit'] = "untitled_section"
			sectionData['number'] = htmlSection['id']
	else:
		sectionData['unit'] = 'body'
		sectionData['number'] = '1'
		sectionData['text'] = htmlSection.text
		sectionData['text_clean'] = rewrite.rewrite_text(sectionData['text'].lower())
	return sectionData

def parse_constitution(constitution):
	with open(constitution, 'rb') as fh:
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

def parse_constitutions(constitutions, outputFile):
	constitutionSections = {}
	for constitution in constitutions:
		print "Parsing constitution", constitution, "..."
		constitutionSections[constitution] = parse_constitution(constitution)
	with open(outputFile, 'wb') as writer:
		json.dump(constitutionSections, writer, indent=4)

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
		if 'unspecified' in section[sectionId]['name']:
			section[sectionId]['name'] = section[sectionId]['name'].replace('unspecified', secUnit)
		if 'unspecified' in section[sectionId]['unit']:
			section[sectionId]['unit'] = section[sectionId]['unit'].replace('unspecified', secUnit)



def main():
	# my code here
	constitutionDir = sys.argv[1]
	outputFile = sys.argv[2]
	_, _, constitutions = next(os.walk(constitutionDir), (None, None, []))
	constitutions = [os.path.join(constitutionDir,fn) for fn in next(os.walk(constitutionDir))[2]]
	parse_constitutions(constitutions, outputFile)

if __name__ == "__main__":
	main()

