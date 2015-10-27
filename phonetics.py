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

import re

# https://cmloegcmluin.wordpress.com/2012/11/10/relative-frequencies-of-english-phonemes/
# Out of 100

PHONEMS = ((u"ə", 11.49), (u"n", 7.11), (u"r", 6.94), (u"t", 6.91), (u"ɪ", 6.32),
           (u"s", 4.75), (u"d", 4.21), (u"l", 3.96), (u"i", 3.61), (u"k", 3.18),
           (u"ð", 2.95), (u"ɛ", 2.86), (u"m", 2.76), (u"z", 2.76), (u"p", 2.15),
           (u"æ", 2.10), (u"v", 2.01), (u"w", 1.95), (u"u", 1.93), (u"b", 1.80),
           (u"e", 1.79), (u"ʌ", 1.74), (u"f", 1.71), (u"aɪ", 1.50), (u"ɑ", 1.45),
           (u"h", 1.40), (u"o", 1.25), (u"ɒ", 1.18), (u"ŋ", 0.99), (u"ʃ", 0.97),
           (u"y", 0.81), (u"g", 0.80), (u"dʒ", 0.59), (u"tʃ", 0.56), (u"aʊ", 0.50),
           (u"ʊ", 0.43), (u"θ", 0.41), (u"ɔɪ", 0.10), (u"ʒ", 0.07))

PHONEM_SCALE = 100.0 / 255

# "ɒ", "ou" needs a better replacement

PHONEM_ASCII = {u"ə": "uh", u"n": "n", u"r": "r", u"t": "t", u"ɪ": "i",
                u"s": "s", u"d": "d", u"l": "l", u"i": "i", u"k": "k",
                u"ð": "th", u"ɛ": "ay", u"m": "m", u"z": "z", u"p": "p",
                u"æ": "a", u"v": "v", u"w": "w", u"u": "u", u"b": "b",
                u"e": "e", u"ʌ": "u", u"f": "f", u"aɪ": "ii", u"ɑ": "ah",
                u"h": "h", u"o": "o", u"ɒ": "ou", u"ŋ": "ng", u"ʃ": "sh",
                u"y": "y", u"g": "g", u"dʒ": "j", u"tʃ": "ch", u"aʊ": "ow",
                u"ʊ": "oo", u"θ": "th", u"ɔɪ": "oy", u"ʒ": "z"}

def phonemsToASCII(string):
    """Convert from IPA to a plain ASCII approximation."""
    for key in PHONEM_ASCII.keys():
        string = re.sub(key, PHONEM_ASCII[key], string)
    return string

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
    return ''.join([numToPhonem(byte)
                    for byte in bytearray.fromhex(source)])

#p = hashToPhonems('07a765fcd0a35e9a00ab4319')
#print phonemsToASCII(p)
