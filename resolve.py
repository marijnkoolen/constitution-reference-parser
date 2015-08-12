import re

def resolve_refs(sourceId, refList, constitution):
    for ref in refList.identified:
        # text sections are the body elements within the
        # section header elements, so use the parent of the
        # body section as the source
        ref.SourceId = constitution.section[sourceId].Parent
        if ref.SourceId == 'section-0':
            ref.SourceId = sourceId
        ref.SourceName = constitution.section[sourceId].Name
        ref.TargetId = find_target_section(sourceId, ref.TargetParts, constitution)

        # if there is no target id, the reference
        # remains unresolved, add target parts to
        # target name to show what we know about it
        if ref.TargetId == None:
            ref.TargetId = 'UNKNOWN'
            path = 'root'
            for partUnit, partNum in ref.TargetParts.iteritems():
                path = path + "/" + partUnit + "[" + partNum + "]"
            ref.TargetName = path
        else:
            ref.status = 'resolved'
            ref.TargetName = constitution.section[ref.TargetId].Name
        # Self-references have separate status
        if ref.TargetId == ref.SourceId:
            ref.status = 'self-reference'

def find_target_section(sourceId, TargetParts, constitution):
    leafUnit, leafNum = find_most_specific(TargetParts, constitution.ContainedBy)
    if not leafUnit:
        return None
    # Get initial candidate target sections
    # based on unit and number of leaf part
    candidates = find_candidate_targets(leafUnit, leafNum, constitution.section)
    candidates = filter_candidates(candidates, TargetParts, constitution)
    targetId = find_common_ancestor(sourceId, candidates, constitution.section)
    return targetId

def filter_candidates(candidates, TargetParts, constitution):
    for TargetUnit, TargetNum in TargetParts.iteritems():
        targetPart = TargetUnit + "[" + TargetNum + "]"
        if targetPart not in constitution.partIndex:
            print "ERROR path chunk missing: {0}".format(targetPart)
            return []
        # filter candidate target sections that
        # don't share all known target parts
        else:
            targetPartSections = constitution.PartInSection(targetPart)
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
            if type(section[sectionId].Number) != type(leafNum):
                print "ERROR *** different data types"
            if section[sectionId].Number == leafNum:
                sectionName = section[sectionId].Name
                # occasionally, multiple sections have the same
                # sectionName name (e.g. two version of the same article)
                # in those cases, choose the first section in section
                # order.
                # See e.g. France article number 11
                if sectionName in candidates:
                    if precedes(sectionId, candidates[sectionName]):
                        candidates[sectionName] = sectionId
                #print "candidate:", sectionName
                candidates[sectionName] = sectionId
    return candidates.values()

def find_common_ancestor(sourceId, candidates, section):
    sourceParts = section[sourceId].Name.split("/")
    selected = candidates
    for sourcePart in sourceParts:
        remaining = []
        for candidate in selected:
            if sourcePart in section[candidate].Name:
                remaining.append(candidate)
                #print "PARTIAL MATCH: sourcePart: {0}\tcandidate path: {1}".format(sourcePart, section[candidate].Name)
        if (len(remaining) == 1):
            #print "FINAL MATCH: {0} {1}".format(section[sourceId].Name, section[candidate].Name)
            return remaining[0]
        if (len(remaining) == 0):
            print "ERROR *** multiple best candidates, picking first"
            #print "current path: {0}".format(section[sourceId].Name)
            #print "candidates: {0}".format(selected)
            firstNum = None
            firstSec = None
            for candidateId in selected:
                candidateNum = candidateId.replace('section-', '')
                if not firstNum:
                    firstNum = candidateNum
                    firstSec = candidateId
                if firstNum and int(firstNum) > int(candidateNum):
                    firstNum = candidateNum
                    firstSec = candidateId
            # use first sec if need to pick one from multiple
            # best candidates
            selected = [firstSec]
            # if there are multiple best candidates, pick none
            return None
        selected = remaining

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

