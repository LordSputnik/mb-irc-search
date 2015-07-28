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

#import cPickle as pickle
import requests
import datetime
import re
import hashlib
import time
from bs4 import BeautifulSoup

def get_log(channel, date):
    """ Fetch the raw HTML for a log from MusicBrainz's IRC log archives, for
    the chatroom channel on the provided date.
    """

    year = date.strftime('%Y')
    month = date.strftime('%Y-%m')
    day = date.strftime('%Y-%m-%d')

    url = 'http://chatlogs.musicbrainz.org/{}/{}/{}/{}.html'.format(
        channel, year, month, day
    )

    return requests.get(url)

def parse_log(html):
    """ Parse an HTML chat log to extract message times, users and content. """

    soup = BeautifulSoup(html)

    times = [child.a.get_text() for child in soup.dl.children if child.name == 'dt']
    users = [child.contents[1].strip(' []') for child in soup.dl.children if child.name == 'dt']
    msgs = [child.get_text() for child in soup.dl.children if child.name == 'dd']

    return zip(times, users, msgs)

def clean_log(log):
    """ Remove some fluff from the log - eg. join and leave messages which
    shouldn't be included in the search index.
    """

    def is_clean(log_entry):
        dirty_matches = [
            re.search(r'has joined #', log_entry[2]),
            re.search(r'has left #', log_entry[2]),
            re.search(r'has changed the topic to:', log_entry[2]),
            re.search(r'Users on #', log_entry[2])
        ]
        if all(m is None for m in dirty_matches):
            return True
        else:
            return False

    return [log_entry for log_entry in log if is_clean(log_entry)]

def load_database(filename):
    """ Load a saved database containing channel messages and the index of
    searchable words.
    """

    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except IOError:
        return ({}, {})


def save_database(filename, messages, index):
    """ Save a database of channel messages and the corresponding index of
    searchable words.
    """
    combined = (messages, index)
    with open(filename, 'wb') as file:
        pickle.dump(combined, file)

def update_messages_with_log(messages, url, log):
    """ Append new messages to the a dictionary of messages from a database, by
    calculating the hash of some message data and storing the message
    information using this hash as the key in a dictionary.
    """

    for log_entry in log:
        time = log_entry[0]
        user = log_entry[1]
        msg = log_entry[2]
        msg_id = hashlib.sha1((time+user+msg).encode('utf8')).hexdigest()

        messages[msg_id] = (url, time, user, msg)

def update_index_with_log(index, log):
    """ Calculate the hash for each message. For each word in the message, use
    the word as the key for the index dictionary, and append the message hash
    to the list stored as the corresponding values.
    """

    for log_entry in log:
        time = log_entry[0]
        user = log_entry[1]
        msg = log_entry[2]
        msg_id = hashlib.sha1((time+user+msg).encode('utf8')).hexdigest()

        words = re.sub("\W", " ",  msg).split()
        for word in words:
            index.setdefault(word.lower(), set()).add(msg_id)


def main(args):
    """ Parse the logs for a channel (argv[1]), starting at the current date
    and going backwards in time to the earliest log to be found.
    """

    channel = args[1]

    current_date = datetime.date.today()
    messages, index = load_database(channel + '.db')

    misses = 0
    while 1:
        current_date = current_date - datetime.timedelta(days=1)
        print current_date
        r = get_log(channel, current_date)
        if r.status_code == 404:
            if misses != 100:
                misses += 1
            else:
                return
        else:
            log = clean_log(parse_log(r.text))

            # Store as:
            # messages[id] = [date, name, message]
            # index[word] = [id, id, id, id]
            update_messages_with_log(messages, r.url, log)
            update_index_with_log(index, log)

            time.sleep(1)

            save_database(channel + '.db', messages, index)


if __name__ == '__main__':
    import sys
    main(sys.argv)
