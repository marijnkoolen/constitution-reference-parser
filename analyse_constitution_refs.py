import json, nltk, re, os
from constitution import Constitution, Section
import extract, rewrite, resolve

def read_constitution_data(config):
	for fname in next(os.walk(config['inputDir']))[2]:
		with open(os.path.join(config['inputDir'], fname), 'rb') as reader:
			data = json.loads(reader.read())
		country = fname.replace(".json","")
		print "Reading constitution", country
		if 'Sweden_' in country:
			fix_Sweden(data)
		constitution = make_constitution(country, data, config)
		process_constitution(constitution)
		write_identifiers(constitution, config)
		write_references(constitution, config)


def make_constitution(country, sections, config):
	constitution = Constitution(country)
	constitution.SetUnits(config['subUnitRefs'], config['nonRefUnits'], config['skipUnitRefs'])
	for sectionId in sections:
		section = Section(sections[sectionId])
		constitution.IndexUnit(section.Unit)
		constitution.IndexSection(section)
		if section.Unit not in constitution.SkipUnits:
			parse_name(section, constitution)
	return constitution

def clean_text(section, refUnits):
	rewriter = rewrite.RewritePatterns(refUnits)
	updatedText = rewriter.rewrite_text(section.AnalyseText)
	section.UpdateText(updatedText)

def process_constitutions(constitutions):
	for constitution in constitutions:
		print "parsing constitution of {0}".format(constitution.CountryName)
		process_constitution(constitution)

def process_constitution(constitution):
	for section in constitution.Sections():
		clean_text(section, constitution.RefUnits())
		process_section(section, constitution)

def process_section(section, constitution):
	sentences = nltk.sent_tokenize(section.AnalyseText)
	typePattern = re.compile("("+"|".join(constitution.RefUnits())+")s?", re.IGNORECASE)
	for sentence in sentences:
		if re.search(typePattern, sentence):
			#print sentence
			refList = extract.extract_refs(constitution, sentence);
			resolve.resolve_refs(section.Id, refList, constitution)
			constitution.references += refList.identified

def fix_Sweden(sections):
	rewriter = rewrite.RewritePatterns()
	for secId in sections:
		section = sections[secId]
		section['text'] = rewriter.rewrite_sweden(section['text'])

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

def write_identifiers(constitution, config):
	identifierFile = os.path.join(config['identifierDir'], constitution.CountryName) + ".json"
	identifier = open(identifierFile, 'wb')
	for section in constitution.Sections():
		if section.Unit == 'body' and section.Unit == 'UNKNOWN':
			continue
		constitutionName = section.Constitution.encode('utf-8')
		sectionId = section.Id.encode('utf-8')
		sectionName = section.Name.encode('utf-8')
		identifier.write("{0}\t{1}\t{2}\n".format(constitutionName, sectionId, sectionName))
	identifier.close()

def write_references(constitution, config):
	referenceFile = os.path.join(config['referenceDir'], constitution.CountryName) + ".json"
	missingRefFile = os.path.join(config['missingRefDir'], constitution.CountryName) + ".json"
	referencer = open(referenceFile, 'wb')
	misser = open(missingRefFile, 'wb')
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
		elif reference.status == 'unresolved':
			misser.write(refString)
	referencer.close()
	misser.close()

def main(script, inputDir, idDir, refDir, missDir):
	config = {}
	config["nonRefUnits"] =  ['body','list_item','UNKNOWN']
	config["subUnitRefs"] =  ['subsection', 'subarticle', 'paragraph', 'sentence', 'point']
	config["skipUnitRefs"] =  ['subsection','subarticle', 'paragraph', 'sentence', 'point']
	try:
		config["inputDir"] = inputDir
		config["identifierDir"] = idDir
		config["referenceDir"] = refDir
		config["missingRefDir"] = missDir
	except IndexError:
		print "\nRequires 4 arguments: \n<input file> <identifier file> <reference file> <missing reference file>\n\n"
		sys.exit()


	read_constitution_data(config)

if __name__ == "__main__":
	import sys
	main(*sys.argv)
