#!/usr/bin/env python
# -*- coding: utf-8  -*-
#########################################################################
# Copyright (C) 2012 Cristian Consonni <cristian.consonni@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (see COPYING).
# If not, see <http://www.gnu.org/licenses/>.
#########################################################################
"""Usage:
  discover.py <input_xml> [ -c CONFIG | --config CONFIG ]
                          [ -s STOPWORDS | --stopwords STOPWORDS ]
                          [ -n NEW | --new-annotations NEW ]
                          [ -d DIFF | --different-annotations DIFF ]
                          [ -p PROC | --processed-items PROC ]

  discover.py -h | --help | --version


Options:
  -h --help                                     Show this screen.
  --version                                     Show version.
  -c CONFIG, --config CONFIG                    Config file path [default: ./config/settings.cfg].
  -s STOPWORDS, --stopwords STOPWORDS           Stopwords file path [default: ./utils/stop.txt].
  -n NEW, --new-annotations NEW                 File to store the new annotations [default: ./new_annotations.map].
  -d STOPWORDS, --different-annotations DIFF    File to store the annotations which are different from the ones in the BNCF Thesaurus
                                                [default: ./different_annotations.map].
  -p PROC, --processed-items PROC               File to store the processed items
                                                [default: ./processed-items.dat].

"""

import os
from docopt import docopt
from rdflib import Namespace
from rdflib import Graph
from Stemmer import Stemmer
import ConfigParser as configparser
import dandelion
from dandelion import DataTXT
from dandelion.cache import FileCache

from unicodecsv import UnicodeWriter, UnicodeReader

SKOSNS = Namespace('http://www.w3.org/2004/02/skos/core#')
NS = {'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      'skos': "http://www.w3.org/2004/02/skos/core#",
      'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
      'dc': "http://purl.org/dc/elements/1.1/",
      'nsogi': "http://prefix.cc/nsogi"
      }


class SKOSGraph(Graph):

    def __init__(self):
        super(SKOSGraph, self).__init__()

    def query_skos(self, skos, subject):
        query = u'''SELECT DISTINCT ?o
                    WHERE {{
                            <{subject}> skos:{predicate} ?o .
                            }}'''.format(subject=subject,
                                         predicate=skos)

        qres = g.query(query, initNs=dict(skos=SKOSNS))

        return [o for o in qres]


def pref(prefix):
    def add_prefix(tag):
        return '{' + NS[prefix] + '}' + tag

    return add_prefix


def read_stopword(stopwords_file):
    stopwords = []
    with open(stopwords_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if not line.startswith("#") and len(line) > 0:
                stopwords.append(line)

    return stopwords


def touchopen(filename, *args, **kwargs):
    ''' Open the file in R/W and create if it doesn't exist.
        From:
            http://stackoverflow.com/questions/10349781/
            how-to-open-read-write-or-create-a-file-with-truncation-possible
    '''

    fd = os.open(filename, os.O_RDWR | os.O_CREAT)

    # Encapsulate the low-level file descriptor in a python file object
    return os.fdopen(fd, *args, **kwargs)


def wikipedia_match(annotation):
    wiki_match = ann['uri']
    confidence = ann['confidence']
    return wiki_match, confidence


# ----- main -----
if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.2.0')
    print(arguments)

    infile = arguments['<input_xml>']

    config_file = arguments['--config']
    config = configparser.ConfigParser()
    config.read(config_file)

    stopwords_file = arguments['--stopwords']
    stopwords = read_stopword(stopwords_file)

    new_annotations = arguments['--new-annotations']
    different_annotations = arguments['--different-annotations']

    processed_items = arguments['--processed-items']

    stemmer = Stemmer('italian')

    app_id = config.get('keys', 'app_id')
    app_key = config.get('keys', 'app_key')
    cache_dir = config.get('cache', 'cache_dir')

    datatxt = DataTXT(app_id=app_id,
                      app_key=app_key,
                      cache=FileCache(cache_dir)
                      )

    g = SKOSGraph()
    g.parse(infile, format='xml')

    query = u'SELECT DISTINCT ?a ?b WHERE { ?a skos:prefLabel ?b .}'
    qres = g.query(query, initNs=dict(skos=SKOSNS))

    i = 0
    tot = len(qres)
    print tot
    for subject_url, name in qres:
        i = i + 1
        name = unicode(name)

        print 'processing: {name} ({num}/{tot})'.format(
            name=name.encode('utf-8'),
            num=i,
            tot=tot)

        readlist = []
        with touchopen(new_annotations, 'r') as infile:
            reader = UnicodeReader(infile)
            readlist += [int(re[0].split('/')[-1]) for re in reader]

        with touchopen(different_annotations, 'r') as infile:
            reader = UnicodeReader(infile)
            readlist += [int(re[0].split('/')[-1]) for re in reader]

        subject_id = int(subject_url.split('/')[-1])
        if subject_id in readlist:
            print name, 'già nella lista: continuo'
            continue

        proclist = []
        with touchopen(processed_items, 'r') as infile:
            proclist += [int(tid) for tid in infile.readlines()]

        if subject_id in proclist:
            print name, 'già processato: continuo'
            continue

        with open(processed_items, 'a+') as outfile:
            outfile.write(str(subject_id)+'\n')

        definition = g.query_skos('definition', subject_url)
        definition = definition and definition[0][0].value or u''

        scopeNote = g.query_skos('scopeNote', subject_url)
        scopeNote = scopeNote and scopeNote[0][0].value or u''

        closeMatch = g.query_skos('closeMatch', subject_url)

        close_match = ''
        if closeMatch:
            for cl in closeMatch[0]:
                if 'it.dbpedia.org' in cl:
                    close_match = cl

        text = u''
        if definition or scopeNote:
            wiki_match = ''
            text = u'{name} {definition} {scopeNote}'.format(
                name=name,
                definition=definition,
                scopeNote=scopeNote)

            try:
                annotations = datatxt.nex(text, lang='it')
            except dandelion.base.DandelionException as e:
                if e.message == u'usage limits are exceeded':
                    print 'DataTXT daily usage limits met, exiting.'
                    exit(0)
                else:
                    import pdb
                    pdb.set_trace()

            try:
                annlist = annotations['annotations']
                for ann in annlist:
                    start = ann['start']
                    end = ann['end']
                    if start == 0:
                        if end == len(name):
                            wiki_match, confidence = wikipedia_match(ann)
                        else:
                            title = ann['title']
                            name_words = set([stemmer.stemWord(word.lower())
                                              for word in title.split()
                                              if word not in stopwords
                                              ])
                            title_words = set([stemmer.stemWord(word.lower())
                                               for word in title.split()
                                               if word not in stopwords
                                               ])
                            if name_words == title_words:
                                wiki_match, confidence = wikipedia_match(ann)

            except Exception as e:
                import pdb
                pdb.set_trace()

            if wiki_match:
                outfile_name = new_annotations
                if close_match:
                    close_match_obj = close_match.split('/')[-1]
                    wiki_match_obj = wiki_match.split('/')[-1]

                    if close_match_obj != wiki_match_obj:
                        outfile_name = different_annotations
                    else:
                        print name, 'già matchato con: ', close_match
                        continue

                with open(outfile_name, 'a+') as outfile:
                    writer = UnicodeWriter(outfile)
                    writer.writerow([subject_url,
                                     name,
                                     wiki_match,
                                     unicode(confidence)
                                     ])
