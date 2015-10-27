#!/usr/bin/env python
# -*- language: python; coding: utf-8 -*-
# autoloa.py - Automatic pantheon generation.
# Copyright 2014 - 2015 Rob Myers <rob@robmyers.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import hashlib, itertools, math, random, sys

from nltk.corpus import wordnet as wn

import phonetics

# Missing: unfortunate, psychic, machine, animal

PROPERTY_ROOTS = ['attribute.n.02', 'entity.n.01', 'location.n.01',
                  'motivation.n.01', 'natural_phenomenon.n.01',
                  'property.n.02', 'quality.n.01', 'substance.n.01',
                  'system.n.01', 'trait.n.01']

# Should permanently cache these....
RELATIONSHIP_ROOTS = ['relation.n.01']
EVENT_ROOTS = ['event.n.01']

MIN_ENTITIES = 1
MAX_ENTITIES = 13
MIN_DEPTH = 1
MAX_DEPTH = 2
MIN_PROPERTIES = 1
MAX_PROPERTIES = len(PROPERTY_ROOTS)
MIN_EVENTS = 0
MAX_EVENTS = 5
MIN_RELATIONSHIPS = 0
MAX_RELATIONSHIPS = 4

CONCEPT_CACHE = {}

def cleanWordNetName(name):
    """Strip '.n.01' and change underscores to spaces"""
    return name.split('.')[0].replace('_', ' ')

def cleanWordNetList(names):
    """Strip '.n.01' and change underscores to spaces"""
    return [cleanWordNetName(name) for name in names]

def recurse_hyponyms(synset, all_hyponyms, max_depth=sys.maxint):
    """Get all the hyponyms for each hyponym for the synset"""
    if max_depth > 0:
        synset_hyponyms = synset.hyponyms()
        if synset_hyponyms:
            for hyponym in synset_hyponyms:
                all_hyponyms.append(hyponym.name())
                recurse_hyponyms(hyponym, all_hyponyms, max_depth - 1)
    return all_hyponyms

def loadConceptList(concept_root, depth=sys.maxint):
    """Fetch all leaf concepts under concept_root into the cache"""
    CONCEPT_CACHE[concept_root] = recurse_hyponyms(wn.synset(concept_root),
                                                   [],
                                                   depth)

def getOrCacheConceptList(concept_root, depth=sys.maxint):
    """Get the leaf concept list for the concept, caching it if needed"""
    if not concept_root in CONCEPT_CACHE:
        loadConceptList(concept_root, depth)
    return CONCEPT_CACHE[concept_root]

def removeAlreadyUsed(a, b):
    """Remove items in a from b"""
    return list(set(b) - set(a))

#FIXME: These aren't leaves, and we want a version that avoids leaves as well
def chooseLeafConcepts(concepts, count, depth=sys.maxint):
    """Choose at most count leaf concepts under concept, less if too specific,
    the original(s) if concept(s) is a leaf"""
    leaves = [getOrCacheConceptList(concept, depth) for concept in concepts]
    merged = list(itertools.chain.from_iterable(leaves))
    if len(merged) == 0:
        merged = concepts
    return random.sample(merged, count)

def chooseEvents():
    """Choose some events"""
    events = chooseLeafConcepts(EVENT_ROOTS,
                                random.randint(MIN_EVENTS, MAX_EVENTS))
    return cleanWordNetList(events)

def choosePastAndFutureEvents():
    """Choose past and future (history/prophecy) events, with no overlap"""
    past = chooseEvents()
    future = chooseEvents()
    return (past, removeAlreadyUsed(past, future))

def chooseRelationships(entity, entities):
    """Relate the entity to the other entities"""
    # This doesn't handle reflexive or contradictory relationships,
    # although this does allow for more interesting stories
    others = removeAlreadyUsed([entity], entities)
    relationships = chooseLeafConcepts(RELATIONSHIP_ROOTS,
                                       random.randint(MIN_RELATIONSHIPS,
                                                      min(len(others),
                                                          MAX_RELATIONSHIPS)))
    return zip(cleanWordNetList(relationships),
               random.sample(others, len(relationships)))

def choosePropertyValues(property_roots):
    """Choose the entity's properties"""
    properties = [chooseLeafConcepts([root], 1)
                  for root in property_roots]
    properties_list = list(itertools.chain.from_iterable(properties))
    return zip(cleanWordNetList(property_roots),
               cleanWordNetList(properties_list))

def choosePropertyRoots():
    """Choose the property roots, not too high or low."""
    return chooseLeafConcepts(PROPERTY_ROOTS,
                              random.randint(MIN_PROPERTIES, MAX_PROPERTIES),
                              random.randint(MIN_DEPTH, MAX_DEPTH))
    #return random.sample(PROPERTY_ROOTS, random.randint(MIN_PROPERTIES,
    #                                                    MAX_PROPERTIES))

def describeEntity(entity_name, entities, property_roots):
    """Generate a description for a single entity"""
    random.seed(entity_name)
    properties = choosePropertyValues(property_roots)
    (past, future) = choosePastAndFutureEvents()
    relationships = chooseRelationships(entity_name, entities)
    description = "<b>Pronounced: </b> %s<br>\n" \
                  % phonetics.phonemsToASCII(entity_name)
    for attribute in properties:
        description += "<b>%s</b>: %s.<br>\n" % (attribute[0].title(),
                                                 attribute[1])
    if past:
        description += "<b>Legends:</b> %s.<br>\n" % ", ".join(past)
    if future:
        description += "<b>Prophecies:</b> %s.<br>\n" % ", ".join(future)
    if relationships:
        description += "<b>Relations</b>: "
        # Because Python doesn't do Unicode.
        description += ", ".join(["%s (%s)" %
                                  ((relationship[1]),
                                   relationship[0])
                                  for relationship in relationships])
        description += ".\n"
    return description

def pantheonSeed(seed):
    """Generate a random hex string to use as the seed for the pantheon"""
    pantheon_hash = hashlib.new('ripemd160')
    pantheon_hash.update(seed)
    return pantheon_hash

def entityName(pantheon_hash, entity_index):
    """Name the entity"""
    entity_hash = pantheon_hash.copy()
    entity_hash.update(str(entity_index))
    return phonetics.hashToPhonems(entity_hash.hexdigest())

def describePantheon(seed):
    """Name a pantheon and its entities, describe those entities"""
    pantheon = pantheonSeed(seed)
    pantheon_name = phonetics.hashToPhonems(pantheon.hexdigest())
    # Make choices deterministic based on pantheon
    # Each entity sets its own seed as well, so don't rely on this after them
    random.seed(pantheon_name)
    descriptionsRange = xrange(random.randrange(MIN_ENTITIES, MAX_ENTITIES))
    names = [entityName(pantheon, i) for i in descriptionsRange]
    property_roots = choosePropertyRoots()
    random.shuffle(property_roots)
    descriptions = [("%s (%s)" % (names[i], pantheon_name),
                     describeEntity(names[i], names, property_roots))
                    for i in descriptionsRange]
    return descriptions

if __name__ == "__main__":
    descriptions = describePantheon(str(random.random()))#"testing")
    #pantheon_name = phonetics.hashToPhonems(pantheon.hexdigest())
    #print pantheon_name
    #random.seed(pantheon_name)
    #descriptionsRange = xrange(6)
    #names = [entityName(pantheon, i) for i in descriptionsRange]
    #print "  ".join(names)
    #print choosePastAndFutureEvents()
    #print chooseRelationships(names[0], names[1:])
    #random.seed(pantheon_name)
    #property_roots = choosePropertyRoots()
    #random.shuffle(property_roots)
    #print property_roots
    #descriptions = [describeEntity(names[i], names, property_roots)
    #                for i in descriptionsRange]
    #print descriptions
    for description in descriptions:
        print "%s\n" % description[1]
