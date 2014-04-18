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
  graph.py <csv>

Options:
  -h --help                                     Show this screen.
  --version                                     Show version.
"""

from docopt import docopt
import matplotlib.pyplot as plt

import sys
sys.path.append('..')

from unicodecsv import UnicodeReader


def graph(infile_name):
    readlist = []
    with open(infile_name, 'r') as infile:
        reader = UnicodeReader(infile)
        readlist += [re for re in reader]

    labels = []
    values = []
    wikipages = []
    for row in readlist:
        labels.append(row[1])
        wikipages.append(row[2])
        values.append(float(row[3]))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, axisbg='white')

    line, = ax.plot(values, 'ro', picker=5)

    plt.title('Punteggi di confidenza dei match Thesauro-Wikipedia')
    plt.xlabel('no.')
    plt.ylabel('Punteggio di confidenza')

    def onpick(event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind

        n = int(xdata[ind])
        v = ydata[ind]

        try:
            ax.texts.pop()
        except IndexError:
            pass

        # text = matplotlib.text.Annotation(labels[n], xy=(n, v+0.005))

        # # ax.texts.remove(text)
        # ax.add_artist(text)

        text = labels[n] + '\n' + wikipages[n]
        ax.annotate(text, xy=(n+0.005, v+0.005))

        print 'onpick points:', zip(xdata[ind], ydata[ind])
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)

    plt.show()

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.2.0')

    infile_name = arguments['<csv>']
    graph(infile_name)
