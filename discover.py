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

import os
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

INFILE_DIR = '/home/cristian/Wikimedia/bot/soggettario/thes'

CONFIG_DIR = os.path.join(INFILE_DIR, 'config')

CACHE_DIR = os.path.join(INFILE_DIR, '.cache_dir')

STOPWORDS_FILE = os.path.join('stop.txt')

NEW_ANNOTATIONS = 'new_annotations.map'

DIFFERENT_ANNOTATIONS = 'different_annotations.map'


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

# ----- main -----
if __name__ == '__main__':

    infile_name = 'NS-SKOS-Cose-Oggetti.xml'
    infile = os.path.join(INFILE_DIR, infile_name)

    config_name = 'settings.cfg'
    config_file = os.path.join(CONFIG_DIR, config_name)

    config = configparser.ConfigParser()
    config.read(config_file)

    stopwords = read_stopword(STOPWORDS_FILE)

    stemmer = Stemmer('italian')

    app_id = config.get('keys', 'app_id')
    app_key = config.get('keys', 'app_key')

    datatxt = DataTXT(app_id=app_id,
                      app_key=app_key,
                      cache=FileCache(CACHE_DIR)
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
        with open(NEW_ANNOTATIONS, 'r') as infile:
            reader = UnicodeReader(infile)
            readlist += [int(re[0].split('/')[-1]) for re in reader]

        with open(DIFFERENT_ANNOTATIONS, 'r') as infile:
            reader = UnicodeReader(infile)
            readlist += [int(re[0].split('/')[-1]) for re in reader]

        subject_id = int(subject_url.split('/')[-1])
        if subject_id in readlist:
            print name, 'già nella lista: continuo'
            continue

        narrower = g.query_skos('narrower', subject_url)

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
                import pdb
                pdb.set_trace()

            try:
                annlist = annotations['annotations']
                for ann in annlist:
                    start = ann['start']
                    end = ann['end']
                    if start == 0:
                        if end == len(name):
                            wiki_match = ann['uri']
                            confidence = ann['confidence']
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
                                wiki_match = ann['uri']

            except Exception as e:
                import pdb
                pdb.set_trace()

            if wiki_match:
                outfile_name = NEW_ANNOTATIONS
                if close_match:
                    close_match_obj = close_match.split('/')[-1]
                    wiki_match_obj = wiki_match.split('/')[-1]

                    if close_match_obj != wiki_match_obj:
                        outfile_name = DIFFERENT_ANNOTATIONS
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
