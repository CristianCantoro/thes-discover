#!/usr/bin/env python
# -*- coding: utf-8  -*-

import matplotlib
import matplotlib.pyplot as plt
from unicodecsv import UnicodeReader

NEW_ANNOTATIONS = 'new_annotations.map'


def graph():
    readlist = []
    with open(NEW_ANNOTATIONS, 'r') as infile:
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
    graph()
