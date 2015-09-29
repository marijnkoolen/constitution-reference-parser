from bs4 import BeautifulSoup
import json, os

def parse_xml_files(inputDir, outputDir):
    for document in next(os.walk(inputDir))[2]:
        inputFile = os.path.join(inputDir, document)
        print "Parsing document", document, "..."
        structure, doc_type, doc_name = parse_xml(inputFile)
        clean_text(structure)
        structureFile = "{}/{}.{}.json".format(outputDir, doc_type, doc_name)
        with open(structureFile, 'wb') as fh:
            json.dump(structure, fh, indent=4)

def parse_xml(xmlfile):
    with open(xmlfile, 'rb') as fh:
        soup = BeautifulSoup(fh, "lxml")
    structure = {}
    sectionElement = soup.find('document')
    sectionId = "section-0"
    structure[sectionId] = {"id": sectionId, "parent": None}
    structure[sectionId]["doc_name"] = sectionElement['country'] + "_" + sectionElement['code_date']
    structure[sectionId]["doc_type"] = "civil_code"
    structure[sectionId]["path"] = "root[0]"
    structure[sectionId]["unit"] = "root"
    structure[sectionId]["number"] = 0
    structure[sectionId]["text"] = None
    structure[sectionId]["depth"] = 0
    structure[sectionId]["start_offset"] = 0
    structure[sectionId]["end_offset"] = 0
    for childElement in sectionElement.contents:
        structure[sectionId]["end_offset"] = parse_section(childElement, sectionId, structure)
    return structure, structure[sectionId]["doc_type"], structure[sectionId]["doc_name"]

def get_section_metadata(sectionElement, section, parent):
    section["doc_name"] = parent["doc_name"]
    section["doc_type"] = parent["doc_type"]
    section["unit"] = sectionElement['class'][0].lower()
    section["depth"] = sectionElement['depth']
    section["text"] = None
    if 'number' not in sectionElement.attrs:
        section["number"] = 1
    else:
        section["number"] = sectionElement['number']
    section["start_offset"] = parent["end_offset"]
    section["end_offset"] = parent["end_offset"]
    section["path"] = unicode(parent["path"]) + u"/{}[{}]".format(unicode(section["unit"]), unicode(section["number"]))

def parse_section(sectionElement, parentId, structure):
    sectionId = "section-{}".format(len(structure.keys()))
    structure[sectionId] = {"id": sectionId, "parent": parentId}
    get_section_metadata(sectionElement, structure[sectionId], structure[parentId])
    parse_children(sectionElement, sectionId, structure)
    #print sectionId, structure[sectionId]["path"].encode('utf8')
    return structure[sectionId]["end_offset"]

def parse_children(sectionElement, sectionId, structure):
    for child in sectionElement.contents:
        if child.name == None:
            structure[sectionId]["text"] = sectionElement.text
            structure[sectionId]["end_offset"] += len(sectionElement.text)
        elif child.name == 'header':
            structure[sectionId]["text"] = child.text
            structure[sectionId]["end_offset"] += len(child.text)
        elif child.name == 'section':
            structure[sectionId]["end_offset"] = parse_section(child, sectionId, structure)

def clean_text(structure):
    for sectionId in structure:
        if structure[sectionId]["text"]:
            structure[sectionId]["text_clean"] = structure[sectionId]["text"].lower()
        else:
            structure[sectionId]["text_clean"] = None

def main(script, xmlDir, structureDir, *args):
    parse_xml_files(xmlDir, structureDir)

if __name__ == "__main__":
    import sys
    main(*sys.argv)
