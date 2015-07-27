# -*- coding: utf-8 -*-
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

import datetime, hashlib, json, math, pickle, random
import pytumblr

with open('./config.json') as credentials_file:
    config = json.load(credentials_file)

with open('word_lists.pickle') as infile:
    words = pickle.load(infile)

# https://cmloegcmluin.wordpress.com/2012/11/10/relative-frequencies-of-english-phonemes/
# Out of 100

PHONEMS = (("ə", 11.49), ("n", 7.11), ("r", 6.94), ("t", 6.91), ("ɪ", 6.32),
           ("s", 4.75), ("d", 4.21), ("l", 3.96), ("i", 3.61), ("k", 3.18),
           ("ð", 2.95), ("ɛ", 2.86), ("m", 2.76), ("z", 2.76), ("p", 2.15),
           ("æ", 2.10), ("v", 2.01), ("w", 1.95), ("u", 1.93), ("b", 1.80),
           ("e", 1.79), ("ʌ", 1.74), ("f", 1.71), ("aɪ", 1.50), ("ɑ", 1.45),
           ("h", 1.40), ("o", 1.25), ("ɒ", 1.18), ("ŋ", 0.99), ("ʃ", 0.97),
           ("y", 0.81), ("g", 0.80), ("dʒ", 0.59), ("tʃ", 0.56), ("aʊ", 0.50),
           ("ʊ", 0.43), ("θ", 0.41), ("ɔɪ", 0.10), ("ʒ", 0.07))

PHONEM_SCALE = 100.0 / 255

def numToPhonem(num):
    """Convert a byte to a phonem, scaling as necessary"""
    result = ''
    target = num * PHONEM_SCALE
    total = 0
    for phonem in PHONEMS:
        total += phonem[1]
        if total >= target:
            result = phonem[0]
            break
    return result

def hashToPhonems(source):
    """Convert an even-length hex string to a series of phonem characters"""
    return ''.join([numToPhonem(byte) for byte in bytearray.fromhex(source)])

PROPERTIES = {
    "Substance": words['substance'],
    "Natural Phenomenon": words['phenomenon'],
    "Attribute": words['attribute'],
    "Entity": words['entity'],
    "Motivation": words['motivation'],
    "Trait": words['trait'],
    "Unfortunate": words['unfortunate'],
    "Property": words['property'],
    "Machine": words['machine'],
    "Animal": words['animal'],
    "Location": words['location']
}

MULTI_PROPERTIES = {
    "Extent": [words['location'], words['property']],
    "Presence": [words['substance'], words['phenomenon'], words['attribute']],
    "Fields": [words['quality'], words['psychic'], words['system']]
}

MIN_ENTITIES = 1
MAX_ENTITIES = 13
MIN_PROPERTIES = 1
MAX_PROPERTIES = len(PROPERTIES)
MIN_MULTI_PROPERTIES = 1
MAX_MULTI_PROPERTIES = len(MULTI_PROPERTIES)

def choose(population):
    maxchoice = len(population)
    # FIXME: shuffles in-place
    random.shuffle(population)
    choices = random.sample(population,
                            random.randint(math.ceil(maxchoice / 2), maxchoice))
    return ', '.join([random.choice(options) for options in choices])


def genDescription(property_keys, multi_property_keys):
    """Generate a description for a single entity"""
    description = ""
    description += '<br>'.join(['<b>' + key + ':</b> '
                                + random.choice(PROPERTIES[key])
                                for key in property_keys])
    description += '<br>'
    description += '<br>'.join(['<b>' + key + ':</b> '
                                + choose(MULTI_PROPERTIES[key])
                                for key in multi_property_keys])
    return description

def postDescription(description, pantheon):
    name_hash = hashlib.new('ripemd160')
    name_hash.update(description)
    name = hashToPhonems(name_hash.hexdigest()) + " (%s)" % pantheon
    client = pytumblr.TumblrRestClient(
        config['consumer_key'],
        config['consumer_secret'],
        config['oauth_token'],
        config['oauth_token_secret'])
    client.create_text(config['blog'], state='published', title=name,
                       body=description)

def postSeveral(property_keys, multi_property_keys, pantheon):
    for i in xrange(random.randrange(MIN_ENTITIES, MAX_ENTITIES)):
        description = genDescription(property_keys, multi_property_keys)
        postDescription(description, pantheon)

if __name__ == '__main__':
    pantheon_hash = hashlib.new('ripemd160')
    pantheon_hash.update(datetime.datetime.now().isoformat())
    pantheon = hashToPhonems(pantheon_hash.hexdigest())
    property_keys = random.sample(PROPERTIES,
                                  random.randrange(MIN_PROPERTIES,
                                                   MAX_PROPERTIES))
    random.shuffle(property_keys)
    multi_property_keys = random.sample(MULTI_PROPERTIES,
                                  random.randrange(MIN_MULTI_PROPERTIES,
                                                   MAX_MULTI_PROPERTIES))
    random.shuffle(multi_property_keys)
    postSeveral(property_keys, multi_property_keys, pantheon)
