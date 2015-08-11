import re
romanPattern = re.compile("[mdclxvi]+")
numbers = "(\d+\.\d+|\d+\.[a-z]|\d+)"
rangeNumbers = numbers + "( ?- ?| to | up to | til )?" + numbers + "?"
numberPattern = re.compile(numbers)


def makePatterns(typeList):
	types = "(" + "|".join(typeList) + ")s? "
	conj = "( and |, and | or |, or )?"
	part = "( of | from | in )?"
	sep = "(, |; )?"
	refDummy= "<REF>"
	patterns = {}

	patterns['typeList'] = typeList
	patterns['refDummy'] = refDummy

	patterns['romanPattern'] = re.compile("[mdclxvi]+")
	numbers = "(\d+\.\d+|\d+\.[a-z]|\d+)"
	rangeNumbers = numbers + "( ?- ?| to | up to | til )?" + numbers + "?"

	# matching title units in section titles
	patterns['title_preamble'] = re.compile("preamble")
	patterns['title_unit_number'] = re.compile("(annex|art|article|chapter|division|part|schedule|sec|section|subdivision|title)[ \.](\d+[a-z]*)")
	patterns['title_unit_roman'] = re.compile("(annex|art|article|chapter|division|part|schedule|sec|section|subdivision|title)[ \.]([ivxlcdm]+)")
	patterns['title_number'] = re.compile("(\d+[a-z]*)[\.]*")

	# ref = type + number
	patterns['refStart'] = re.compile(types + rangeNumbers, re.IGNORECASE)
	# ref sep|conj number
	patterns['refSepConjNumber'] = re.compile(refDummy + sep + conj + rangeNumbers, re.IGNORECASE)
	# ref sep|conj|part type number
	patterns['refSepConjPartTypeNumber'] = re.compile(refDummy + sep + conj + part + types + rangeNumbers, re.IGNORECASE)
	# ref sep number
	patterns['refSepNumber'] = re.compile(refDummy + sep + rangeNumbers, re.IGNORECASE)
	# ref sep type number
	patterns['refSepTypeNumber'] = re.compile(refDummy + sep + types + rangeNumbers, re.IGNORECASE)
	# ref conj number
	patterns['refConjNumber'] = re.compile(refDummy + conj + rangeNumbers, re.IGNORECASE)
	# ref conj type number ref
	patterns['refConjTypeNumber'] = re.compile(refDummy + conj + types + rangeNumbers, re.IGNORECASE)
	# ref part type number
	patterns['refPartTypeNumber'] = re.compile(refDummy + part + types + rangeNumbers, re.IGNORECASE)

	return patterns
