#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright (C) 2015  Ben Ockmore
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import cPickle as pickle

def load_database(filename):
    """ Load a saved database containing channel messages and the index of
    searchable words.
    """

    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except IOError:
        return ({}, {})


def main(args):
    """ Load the database for the provided channel (argv[1]), and look up the
    provided search term in the index of searchable words, to find relevant
    message hashes. Get the messages corresponding to these hashes from the
    messages dictionary.
    """

    channel = args[1]
    term = args[2]

    messages, index = load_database(channel + '.db')

    words = term.split()
    results = index[words[0]]
    for word in words[1:]:
        results = results.intersection(index[word])

    for msg in results:
        print messages[msg]

if __name__ == '__main__':
    import sys
    main(sys.argv)
