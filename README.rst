A simple system for indexing and subsequently searching MusicBrainz chat logs.

Installation
------------
To install the required dependencies:

    pip install -r requirements.txt

Running
-------
First, index some logs. For example:

    ./index.py musicbrainz-devel

Then, another example, to search the indexed logs for "Brainz":

    ./search.py musicbrainz-devel Brainz
