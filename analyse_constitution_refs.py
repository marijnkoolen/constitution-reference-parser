import json, nltk, re, sys
from constitution import Constitution, Section
import extract, rewrite, resolve

def read_constitution_data(fname, config):
	with open(fname, 'rb') as reader:
		data = json.loads(reader.read())

	constitutions = []
	for country in data:
		if country == 'Sweden_2012':
			fix_Sweden(data[country])
		constitution = make_constitution(country, data[country], config)
		constitutions.append(constitution)
	return constitutions


def make_constitution(country, sections, config):
	constitution = Constitution(country)
	constitution.SetUnits(config['subUnitRefs'], config['nonRefUnits'], config['skipUnitRefs'])
	for sectionId in sections:
		section = Section(sections[sectionId])
		clean_text(section)
		constitution.IndexUnit(section.Unit)
		constitution.IndexSection(section)
		if section.Unit not in constitution.SkipUnits:
			parse_name(section, constitution)
	return constitution

def clean_text(section):
	updatedText = rewrite.rewrite_text(section.Text)
	section.UpdateText(updatedText)

def process_constitutions(constitutions):
	for constitution in constitutions:
		process_constitution(constitution)
		print "parsing constitution of {0}".format(constitution.CountryName)

def process_constitution(constitution):
	for section in constitution.Sections():
		process_section(section, constitution)

def process_section(section, constitution):
	sentences = nltk.sent_tokenize(section.Text)
	typePattern = re.compile("("+"|".join(constitution.RefUnits())+")s?", re.IGNORECASE)
	for sentence in sentences:
		if re.search(typePattern, sentence):
			if len(sentence) < 40:
				continue
			refList = extract.extract_refs(constitution, sentence);
			resolve.resolve_refs(section.Id, refList, constitution)
			constitution.references += refList.identified

def fix_Sweden(sections):
	for secId in sections:
		section = sections[secId]
		#secName = section['name'].replace("_"," ")
		section['text'] = rewrite.rewrite_sweden(section['text'])
		#secName = rewrite.rewrite_sweden(secName)
		#section['name'] = secName.replace(" ","_").lower().replace("chunk_","chunk.")

def get_pairs(items):
	if items == []:
		return []
	head = items.pop(0)
	headPairs = [(head, item) for item in items]
	restPairs = get_pairs(items)
	return headPairs + restPairs

def parse_name(section, constitution):
	parts = section.Name.split("/")
	constitution.IndexParts(parts, section.Id)
	units = [re.sub("\[.*\]","", part) for part in parts]
	for unit in units:
		if unit == '':
			continue
		constitution.IndexUnit(unit)
	unitPairs = get_pairs(units)
	constitution.IndexUnitRelations(unitPairs)

def write_identifiers(constitutions, identityFile):
	identifier = open(identityFile, 'wb')
	for constitution in constitutions:
		for section in constitution.Sections():
			if section.Unit == 'body' and section.Unit == 'UNKNOWN':
				continue
			constitutionName = section.Constitution.encode('utf-8')
			sectionId = section.Id.encode('utf-8')
			sectionName = section.Name.encode('utf-8')
			identifier.write("{0}\t{1}\t{2}\n".format(constitutionName, sectionId, sectionName))
	identifier.close()

def write_references(constitutions, referenceFile, missingRefFile):
	referencer = open(referenceFile, 'wb')
	misser = open(missingRefFile, 'wb')
	for constitution in constitutions:
		for reference in constitution.references:
			sourceId = reference.SourceId.encode('utf-8')
			sourceName = reference.SourceName.encode('utf-8')
			sourceStart = constitution.section[sourceId].StartOffset
			targetId = reference.TargetId.encode('utf-8')
			targetName = reference.TargetName.encode('utf-8')
			if targetId == 'UNKNOWN':
				targetStart = '-1'
			else:
				targetStart = constitution.section[targetId].StartOffset
			refString = "{0} {1} {2} {3} {4} {5} {6}\n".format(constitution.CountryName, sourceId, sourceName, sourceStart, targetId, targetName, targetStart)
			if reference.status == 'resolved':
				referencer.write(refString)
			else:
				misser.write(refString)
	referencer.close()
	misser.close()

def main():
	try:
		inputfile = sys.argv[1]
		identityFile = sys.argv[2]
		referenceFile = sys.argv[3]
		missingRefFile = sys.argv[4]
	except IndexError:
		print "\nRequires 4 arguments: \n<input file> <identity file> <reference file> <missing reference file>\n\n"
		sys.exit()

	config = {}
	config["nonRefUnits"] =  ['body','list_item','UNKNOWN']
	config["subUnitRefs"] =  ['paragraph', 'sentence', 'point']
	config["skipUnitRefs"] =  ['paragraph', 'sentence', 'point']

	constitutions = read_constitution_data(inputfile, config)
	write_identifiers(constitutions, identityFile)
	process_constitutions(constitutions)
	write_references(constitutions, referenceFile, missingRefFile)

if __name__ == "__main__":
	main()
