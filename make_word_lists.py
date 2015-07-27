# Make word lists for materials etc.

# Loading the synsets and recursing them takes several seconds, so do it once
# then cache the results

import pickle
from nltk.corpus import wordnet as wn

def recurse_hyponyms(synset, all_hyponyms):
    """Get all the hyponyms for each hyponym for the synset"""
    synset_hyponyms = synset.hyponyms()
    if synset_hyponyms:
        for hyponym in synset_hyponyms:
            all_hyponyms.append(hyponym.name().split('.')[0].replace('_', ' '))
            recurse_hyponyms(hyponym, all_hyponyms)
    return all_hyponyms

# celestial bodies?

# All chemical, biological, etc substances. Matter contains more noise eg glop
# inludes metal elements and alloys
substance = recurse_hyponyms(wn.synset('substance.n.01'), [])

# chemical, geological, organic and physical phenomena including radiation
natural_phenomenon = recurse_hyponyms(wn.synset('natural_phenomenon.n.01'), [])

attribute = recurse_hyponyms(wn.synset('attribute.n.02'), [])

# Includes physical, abstract and thing entities., pretty much everything
entity = recurse_hyponyms(wn.synset('attribute.n.02'), [])

# Psychology

# rational, irrational, ethical motices, urges and impulses, libido, some noise
motivation = recurse_hyponyms(wn.synset('motivation.n.01'), [])

# personality traits, nature
trait = recurse_hyponyms(wn.synset('trait.n.01'), [])

# all kinds of unfortunate people
unfortunate = recurse_hyponyms(wn.synset('unfortunate.n.01'), [])


# Extent

# All kinds of properties, including duration and extent
# among more abstract/personal ones
wn_property = recurse_hyponyms(wn.synset('property.n.02'), [])

# Includes computers etc.
machine = recurse_hyponyms(wn.synset('machine.n.01'), [])

# All kinds of beasts
animal = recurse_hyponyms(wn.synset('animal.n.01'), [])

# Some noise (bilocation), here, there, deserts, regions down to specific cities
location = recurse_hyponyms(wn.synset('location.n.01'), [])


# More abstract

quality = recurse_hyponyms(wn.synset('quality.n.01'), [])
psychic_communication = recurse_hyponyms(wn.synset('psychic_communication.n.01'), [])
system = recurse_hyponyms(wn.synset('system.n.01'), [])


# Write it out

with open('word_lists.pickle', 'w') as outfile:
    pickle.dump({
        'substance': substance,
        'phenomenon': natural_phenomenon,
        'attribute': attribute,
        'entity': entity,
        'motivation': motivation,
        'trait': trait,
        'unfortunate': unfortunate,
        'property': wn_property,
        'machine': machine,
        'animal': animal,
        'location': location,
        'quality': quality,
        'psychic': psychic_communication,
        'system' : system
    }, outfile)
