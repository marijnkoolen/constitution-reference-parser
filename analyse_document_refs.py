import json, nltk, re, os
from document import Document, Section
import extract, rewrite, resolve

def read_document_data(config):
	for fname in next(os.walk(config['inputDir']))[2]:
		with open(os.path.join(config['inputDir'], fname), 'rb') as reader:
			data = json.loads(reader.read())
		docType, docName = fname.split(".")[0:2]
		print "Reading document", fname
		if 'Sweden_' in docName:
			fix_Sweden(data)
		document = make_document(docType, docName, data, config)
		process_document(document)
		write_identifiers(document, config)
		write_references(document, config)


def make_document(docType, docName, sections, config):
	document = Document(docType, docName)
	document.SetUnits(config['subUnitRefs'], config['nonRefUnits'], config['skipUnitRefs'])
	for sectionId in sections:
		section = Section(sections[sectionId])
		document.IndexUnit(section.Unit)
		document.IndexSection(section)
		if section.Unit not in document.SkipUnits:
			parse_name(section, document)
	return document

def clean_text(section, refUnits):
	rewriter = rewrite.RewritePatterns(refUnits)
	updatedText = rewriter.rewrite_text(section.AnalyseText)
	section.UpdateText(updatedText)

def process_documents(documents):
	for document in documents:
		print "parsing document of {0}".format(document.CountryName)
		process_document(document)

def process_document(document):
	for section in document.Sections():
		clean_text(section, document.RefUnits())
		process_section(section, document)

def process_section(section, document):
	if not section.AnalyseText:
		return 1
	sentences = nltk.sent_tokenize(section.AnalyseText)
	typePattern = re.compile("("+"|".join(document.RefUnits())+")s?", re.IGNORECASE)
	for sentence in sentences:
		if re.search(typePattern, sentence):
			#print sentence
			refList = extract.extract_refs(document, sentence);
			resolve.resolve_refs(section.Id, refList, document)
			document.references += refList.identified

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

def parse_name(section, document):
	parts = section.Path.split("/")
	document.IndexParts(parts, section.Id)
	units = [re.sub("\[.*\]","", part) for part in parts]
	for unit in units:
		if unit == '':
			continue
		document.IndexUnit(unit)
	unitPairs = get_pairs(units)
	document.IndexUnitRelations(unitPairs)

def write_identifiers(document, config):
	identifierFile = os.path.join(config['identifierDir'], document.DocType + "." + document.DocName) + ".json"
	identifier = open(identifierFile, 'wb')
	for section in document.Sections():
		if section.Unit == 'body' and section.Unit == 'UNKNOWN':
			continue
		documentName = section.DocName.encode('utf-8')
		sectionId = section.Id.encode('utf-8')
		sectionPath = section.Path.encode('utf-8')
		identifier.write("{0}\t{1}\t{2}\n".format(documentName, sectionId, sectionPath))
	identifier.close()

def write_references(document, config):
	referenceFile = os.path.join(config['referenceDir'], document.DocType + "." + document.DocName) + ".json"
	missingRefFile = os.path.join(config['missingRefDir'], document.DocType + "." + document.DocName) + ".json"
	referencer = open(referenceFile, 'wb')
	misser = open(missingRefFile, 'wb')
	for reference in document.references:
		sourceId = reference.SourceId.encode('utf-8')
		sourcePath = reference.SourcePath.encode('utf-8')
		sourceStart = document.section[sourceId].StartOffset
		targetId = reference.TargetId.encode('utf-8')
		targetPath = reference.TargetPath.encode('utf-8')
		if targetId == 'UNKNOWN':
			targetStart = '-1'
		else:
			targetStart = document.section[targetId].StartOffset
		refString = "{0} {1} {2} {3} {4} {5} {6} {7}\n".format(document.DocType, document.DocName, sourceId, sourcePath, sourceStart, targetId, targetPath, targetStart)
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


	read_document_data(config)

if __name__ == "__main__":
	import sys
	if len(sys.argv) != 5:
		print "\n\tUsage: input-dir, identifier-dir, reference-dir, missing-ref-dir\n\n"
		sys.exit()
	main(*sys.argv)
