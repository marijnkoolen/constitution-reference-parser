
class Document:


    def __init__(self, docType, docName):
        self.DocType = docType
        self.DocName = docName
        self.section = {}
        self.hasRefUnit = {}
        self.hasNonRefUnit = {}
        self.SkipUnits = []
        self.Contains = {}
        self.ContainedBy = {}
        self.partIndex = {}
        self.references = []

    def IndexSection(self, section):
        self.section[section.Id] = section

    def Sections(self):
        return self.section.values()

    def Section(self, sectionId):
        return self.section[sectionId]

    def SetUnits(self, refUnits, nonRefUnits, skipUnitRefs):
        for refUnit in refUnits:
            self.hasRefUnit[refUnit] = 1
        for nonRefUnit in nonRefUnits:
            self.hasNonRefUnit[nonRefUnit] = 1
        self.SkipUnits = skipUnitRefs

    def IndexUnit(self, unit):
        if unit not in self.hasNonRefUnit:
            self.hasRefUnit[unit] = 1

    def RefUnits(self):
        return self.hasRefUnit.keys()

    def NonRefUnits(self):
        return self.nonRefUnits.leys

    def IndexUnitRelations(self, unitRelations):
        for ancestor, descendant in unitRelations:

            if ancestor not in self.Contains:
                self.Contains[ancestor] = {}
            if descendant not in self.ContainedBy:
                self.ContainedBy[descendant] = {}
            self.Contains[ancestor][descendant] = 1
            self.ContainedBy[descendant][ancestor] = 1

    def IndexParts(self, parts, sectionId):
        for part in parts:
            if part not in self.partIndex:
                self.partIndex[part] = {}
            self.partIndex[part][sectionId] = 1

    def PartInSection(self, part):
        try:
            return self.partIndex[part].keys()
        except KeyError:
            return []

class Section:

    def __init__(self, sectionData):
        self.Id = sectionData['id']
        self.DocName = sectionData['doc_name']
        self.DocType = sectionData['doc_type']
        self.Path = sectionData['path']
        self.Unit = sectionData['unit']
        self.OriginalText = sectionData['text']
        self.AnalyseText = sectionData['text_clean']
        self.StartOffset = sectionData['start_offset']
        self.EndOffset = sectionData['end_offset']
        self.Depth = sectionData['depth']
        self.Parent = sectionData['parent']
        self.Number = sectionData['number']

    def UpdateText(self, text):
        self.AnalyseText = text

class ReferenceList:

    def __init__(self, sentence, pattern):
        self.identified = []
        self.current = []
        self.prevUnit = ''
        self.sentence = sentence
        self.pattern = pattern

    def UpdatePrev(self, prevUnit):
        self.prevUnit = prevUnit

    def Last(self):
        return self.current[-1]

    def RemoveLast(self):
        self.current.pop()

    def AddCurrent(self, reference):
        self.current.append(reference)

    def ResetCurrent(self):
        self.current = []

    def FinishCurrent(self):
        for reference in self.current:
            self.identified.append(reference)
        self.current = []
        # replace refDummy with reference element
        # with reference order numbers


class Reference:
    def __init__(self):
        self.SourceId = ''
        self.SourcePath = ''
        self.TargetId = ''
        self.TargetPath = ''
        self.TargetParts = {}
        self.status = 'unresolved'

    def AddPart(self, targetPartUnit, targetPartNum):
        self.TargetParts[targetPartUnit] = targetPartNum

    def CopyFrom(self, reference):
        self.SourceId = reference.SourceId
        self.SourcePath = reference.SourcePath
        self.TargetId = reference.TargetId
        self.TargetPath = reference.TargetPath
        for partUnit in reference.TargetParts:
            partNum = reference.TargetParts[partUnit]
            self.TargetParts[partUnit] = partNum
