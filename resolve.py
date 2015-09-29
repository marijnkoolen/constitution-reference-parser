import re

def resolve_refs(sourceId, refList, document):
    for ref in refList.identified:
        ref.SourceId = sourceId
        # text sections are the body elements within the
        # section header elements, so use the parent of the
        # body section as the source
        if document.section[sourceId].Unit == 'body':
            ref.SourceId = document.section[sourceId].Parent
        #if ref.SourceId == 'section-0':
        #    ref.SourceId = sourceId
        ref.SourcePath = document.section[sourceId].Path
        ref.TargetId = find_target_section(sourceId, ref.TargetParts, document)

        # if there is no target id, the reference
        # remains unresolved, add target parts to
        # target name to show what we know about it
        if ref.TargetId == None:
            ref.TargetId = 'UNKNOWN'
            path = 'root'
            for partUnit, partNum in ref.TargetParts.iteritems():
                path = path + "/" + partUnit + "[" + partNum + "]"
            ref.TargetPath = path
        else:
            ref.status = 'resolved'
            ref.TargetPath = document.section[ref.TargetId].Path
        # Self-references have separate status
        if ref.TargetId == ref.SourceId:
            ref.status = 'self-reference'

def find_target_section(sourceId, TargetParts, document):
    leafUnit, leafNum = find_most_specific(TargetParts, document.ContainedBy)
    if not leafUnit:
        return None
    # Get initial candidate target sections
    # based on unit and number of leaf part
    candidates = find_candidate_targets(leafUnit, leafNum, document.section)
    candidates = filter_candidates(candidates, TargetParts, document)
    if candidates == []:
        print "ERROR *** no candidates found with target parts:", TargetParts, "in", document.DocName, sourceId
        return None
    targetId = find_common_ancestor(sourceId, candidates, document.section)
    return targetId

def filter_candidates(candidates, TargetParts, document):
    for TargetUnit, TargetNum in TargetParts.iteritems():
        targetPart = TargetUnit + "[" + TargetNum + "]"
        if targetPart not in document.partIndex:
            print "ERROR path chunk missing: {0} {1}".format(document.DocName.encode("utf8"), targetPart.encode("utf8"))
            return []
        # filter candidate target sections that
        # don't share all known target parts
        else:
            targetPartSections = document.PartInSection(targetPart)
            filtered = intersection(candidates, targetPartSections)
        if len(filtered) > 0:
            candidates = filtered
    return candidates

def find_most_specific(TargetParts, ContainedBy):
    targetUnits = TargetParts.keys()
    if len(targetUnits) == 0:
        return None, None
    if len(targetUnits) == 1:
        leafUnit = targetUnits[0]
        return [leafUnit, TargetParts[leafUnit]]
    firstUnit = targetUnits.pop()
    while firstUnit not in ContainedBy:
        if len(targetUnits) == 0:
            return None, None
        firstUnit = targetUnits.pop()

    mostSpecific = firstUnit
    for nextUnit in targetUnits:
        if nextUnit not in ContainedBy:
            continue
        if mostSpecific in ContainedBy[nextUnit]:
            mostSpecific = nextUnit
    return [mostSpecific, TargetParts[mostSpecific]]

def find_candidate_targets(leafUnit, leafNum, section):
    candidates = {}
    for sectionId in section:
        if section[sectionId].Unit == leafUnit:
            if section[sectionId].Number == leafNum:
                sectionPath = section[sectionId].Path
                # occasionally, multiple sections have the same
                # sectionPath name (e.g. two version of the same article)
                # in those cases, choose the first section in section
                # order.
                # See e.g. France article number 11
                if sectionPath in candidates:
                    if precedes(sectionId, candidates[sectionPath]):
                        candidates[sectionPath] = sectionId
                #print "candidate:", sectionPath
                candidates[sectionPath] = sectionId
    return candidates.values()

def find_common_ancestor(sourceId, candidates, section):
    sourceParts = section[sourceId].Path.split("/")
    selected = candidates
    for sourcePart in sourceParts:
        remaining = []
        for candidate in selected:
            if sourcePart in section[candidate].Path:
                remaining.append(candidate)
        if len(remaining) == 1:
            return remaining[0]
        if len(remaining) == 0:
            remaining = find_lowest_depth(selected, section)
            if len(remaining) == 1:
                return remaining[0]
            print "ERROR *** multiple best candidates, picking first in {0} {1}".format(section[sourceId].DocName, sourceId)
            firstNum = None
            firstSec = None
            for candidateId in remaining:
                pathDepth = len(section[candidateId].Path.split("/"))
                print "candidate:", section[candidateId].Path, "pathDepth", pathDepth, "depth", section[candidateId].Depth
                candidateNum = candidateId.replace('section-', '')
                if not firstNum:
                    firstNum = candidateNum
                    firstSec = candidateId
                if firstNum and int(firstNum) > int(candidateNum):
                    firstNum = candidateNum
                    firstSec = candidateId
            print
            # if there are multiple best candidates, pick first in document order
            return firstSec
            # if there are multiple best candidates, pick none
            return None
        selected = remaining

def find_lowest_depth(candidates, section):
    remaining = []
    depths = []
    for candidateId in candidates:
        depths.append(int(section[candidateId].Depth))
    lowest = min(depths)
    for candidateId in candidates:
        if int(section[candidateId].Depth) == lowest:
            remaining.append(candidateId)
    return remaining


def precedes(sectionId1, sectionId2):
    m1 = re.match('section-(\d+)', sectionId1)
    m2 = re.match('section-(\d+)', sectionId2)
    num1 = int(m1.group(1))
    num2 = int(m2.group(1))
    if num1 < num2:
        return True
    return False

def intersection(list1, list2):
    return list(set(list1) & set(list2))

