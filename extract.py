import re
import patterns
from document import ReferenceList, Reference

def extract_refs(document, sentence):
	sentenceDone = 0

	# returns a dictionary of document specific patterns
	pattern = patterns.makeRefPatterns(document.RefUnits())
	refList = ReferenceList(sentence, pattern)

	while not sentenceDone:
		# Start of a reference
		matchStart = re.search(refList.pattern['refStart'], refList.sentence)
		if matchStart:
			extract_start_ref(matchStart, refList, document)
			while pattern['refDummy'] in refList.sentence:
				extract_sequence_refs(refList, document)
		else:
			# assumption: there is no reference in this sentence
			# action: signal extraction is done
			refList.FinishCurrent()
			sentenceDone = 1
		# check if this is a complex reference sequence
	return refList

def extract_start_ref(matchStart, refList, document):
	refList.sentence = re.sub(matchStart.group(0), refList.pattern['refDummy'], refList.sentence, 1)
	refType, num1, rangeSymbol, num2 = matchStart.groups()
	refType = refType.lower()
	refNums = makeRange(num1, rangeSymbol, num2)
	if refType in document.SkipUnits:
		refList.sentence = re.sub(refList.pattern['refDummy'], "", refList.sentence, 1)
		return 0
	addToRefList(refType, refNums, refList)
	refList.UpdatePrev(refType)
	return 0

def extract_sequence_refs(refList, document):
	refNums = []
	refType = None
	sep, conj, part, refType, refNums = findSequenceType(refList, document)
	if refNums == []:
		# assumption: if there is no next pattern, the sequence is done
		# action: remove the reference dummy
		refList.sentence = re.sub(refList.pattern['refDummy'], "", refList.sentence, 1)
		refList.FinishCurrent()
		refList.UpdatePrev('')
		return 0
	elif refType:
		refType = refType.lower()
		# if found type is too deep in hierarchy, ignore it
		# e.g. we don't consider paragraphs and refList.sentences as part of the reference
		if refType in document.SkipUnits:
			refList.UpdatePrev(refType)
			return 0
	elif refType == None:
		# if previous type is too deep in hierarchy, ignore it
		# e.g. we don't consider paragraphs and refList.sentences as part of the reference
		if refList.prevUnit in document.SkipUnits:
			refNums = []
	if sep:
		parse_separator_ref(refType, refNums, refList, document)
	elif conj:
		parse_conjunction_ref(refType, refNums, refList, document)
	elif part:
		parse_part_of_ref(refType, refNums, refList)
	if refType != None:
		refList.UpdatePrev(refType)


def findSequenceType(refList, document):
	mSepConjNumber = re.search(refList.pattern['refSepConjNumber'], refList.sentence)
	mSepConjPartTypeNumber = re.search(refList.pattern['refSepConjPartTypeNumber'], refList.sentence)
	sep = None
	conj = None
	part = None
	refType = None
	refNums = []
	if mSepConjNumber:
		refList.sentence = re.sub(mSepConjNumber.group(0), refList.pattern['refDummy'], refList.sentence, 1)
		sep, conj, num1, rangeSymbol, num2 = mSepConjNumber.groups()
		refNums = makeRange(num1, rangeSymbol, num2)
	elif mSepConjPartTypeNumber:
		refList.sentence = re.sub(mSepConjPartTypeNumber.group(0), refList.pattern['refDummy'], refList.sentence, 1)
		sep, conj, part, refType, num1, rangeSymbol, num2 = mSepConjPartTypeNumber.groups()
		refNums = makeRange(num1, rangeSymbol, num2)

	return (sep, conj, part, refType, refNums)

def parse_separator_ref(refType, refNums, refList, document):
	# 1. ref sep number -> new ref of same type
	# assumption: type of new ref is implicit
	# action: add refs similar to previous type
	if refType == None:
		addToRefList(None, refNums, refList)
	# 2. ref sep type number -> new ref of same type
	# assumption: type of new ref is explicit and of same type
	elif refType == refList.prevUnit:
		addToRefList(None, refNums, refList)
	# 3. ref sep type number -> specification of existing ref
	# assumption: hierarchical relations are written from high to low
	# action: replace previous reference with hierarchical reference
	elif refType in document.ContainedBy and refList.prevUnit in document.ContainedBy[refType]:
		prevRef = refList.Last()
		refList.RemoveLast()
		for refNum in refNums:
			reference = Reference()
			reference.CopyFrom(prevRef)
			reference.AddPart(refType, refNum)
			refList.AddCurrent(reference)
	# 4. ref sep type number -> new ref of different type
	# assumption: previous ref was hierarchical, new ref is higher in hierarchy
	# action: add refType as new reference
	else:
		addToRefList(refType, refNums, refList)

def parse_conjunction_ref(refType, refNums, refList, document):
	# ref conj number -> ref
	# assumptions:
	# 1. no mention of type suggests these are
	#    references of the same type as the
	#    previous reference
	if refType == None:
		addToRefList(None, refNums, refList)
	# ref conj type number -> ref
	# previous reference has same type and higher
	# level type
	# assumptions:
	# 2. explicit mention of type suggest this is a
	#    separate reference, but share higher level
	#    type
	elif refType == refList.prevUnit:
		prevRef = refList.Last()
		for container in document.ContainedBy[refType]:
			if container in prevRef.TargetParts:
				for refNum in refNums:
					reference = Reference()
					reference.CopyFrom(prevRef)
					reference.AddPart(refType, refNum)
					refList.AddCurrent(reference)
				break
	# ref conj type number -> ref
	# assumptions:
	# 3. explicit mention of type suggests these are
	#    separate references
	else:
		addToRefList(refType, refNums, refList)

def parse_part_of_ref(refType, refNums, refList):
	# ref part type number -> ref
	# assumptions:
	# 1. part of signals end of sequence
	# 2. new type is container of all refs in sequence
	for refNum in refNums:
		for reference in refList.current:
			reference.AddPart(refType, refNum)
	refList.prevUnit = ''
	refList.FinishCurrent()
	# remove dummy reference
	refList.sentence = re.sub(refList.pattern['refDummy'], "", refList.sentence, 1)

def addToRefList(refType, refNums, refList):
	#print "DEBUG: addToRefList"
	for refNum in refNums:
		reference = Reference()
		#print "adding reference of type {0} with number {1}".format(refType, refNum)
		if refType == None:
			reference.CopyFrom(refList.Last())
			refType = refList.prevUnit
		reference.AddPart(refType, refNum)
		refList.AddCurrent(reference)

def makeRange(num1, rangeSymbol, num2):
	if rangeSymbol and num2:
		if int(num2) < int(num1):
			return [num1]
		return [unicode(num) for num in range(int(num1), int(num2)+1)]
	return [num1]

