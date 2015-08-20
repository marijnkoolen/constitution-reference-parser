import re
romanPattern = re.compile("[mdclxvi]+")
numbers = "(\d+\.\d+|\d+\.[a-z]|\d+)"
rangeNumbers = numbers + "( ?- ?| to | up to | til )?" + numbers + "?"
numberPattern = re.compile(numbers)


def makeTitlePatterns():
	# matching title units in section titles
	titlePatterns = {}
	titlePatterns['title_preamble'] = re.compile("(preamble)")
	titlePatterns['title_unit_number'] = re.compile("(annex|art|article|chapter|division|part|schedule|section|sec|subdivision|title)[ \.](\d+[a-z]*)")
	titlePatterns['title_unit_roman'] = re.compile("(annex|art|article|chapter|division|part|schedule|section|sec|subdivision|title)[ \.]([ivxlcdm]+)")
	titlePatterns['title_number'] = re.compile("(\d+[a-z]*)[\.]*")
	return titlePatterns

def makeRefPatterns(typeList):
	types = "\\b(" + "|".join(typeList) + ")s? "
	conj = "( and |, and | or |, or )?"
	part = "( of | from | in )?"
	sep = "(, |; )?"
	refDummy= "<REF>"
	refPatterns = {}

	refPatterns['typeList'] = typeList
	refPatterns['refDummy'] = refDummy

	refPatterns['romanPattern'] = re.compile("[mdclxvi]+")
	numbers = "(\d+\.\d+|\d+\.[a-z]|\d+)"
	rangeNumbers = numbers + "( ?- ?| to | up to | til )?" + numbers + "?"

	# ref = type + number
	refPatterns['refStart'] = re.compile(types + rangeNumbers, re.IGNORECASE)
	# ref sep|conj number
	refPatterns['refSepConjNumber'] = re.compile(refDummy + sep + conj + rangeNumbers, re.IGNORECASE)
	# ref sep|conj|part type number
	refPatterns['refSepConjPartTypeNumber'] = re.compile(refDummy + sep + conj + part + types + rangeNumbers, re.IGNORECASE)
	# ref sep number
	refPatterns['refSepNumber'] = re.compile(refDummy + sep + rangeNumbers, re.IGNORECASE)
	# ref sep type number
	refPatterns['refSepTypeNumber'] = re.compile(refDummy + sep + types + rangeNumbers, re.IGNORECASE)
	# ref conj number
	refPatterns['refConjNumber'] = re.compile(refDummy + conj + rangeNumbers, re.IGNORECASE)
	# ref conj type number ref
	refPatterns['refConjTypeNumber'] = re.compile(refDummy + conj + types + rangeNumbers, re.IGNORECASE)
	# ref part type number
	refPatterns['refPartTypeNumber'] = re.compile(refDummy + part + types + rangeNumbers, re.IGNORECASE)

	return refPatterns
