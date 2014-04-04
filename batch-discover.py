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
  discover.py <input_xml>... [ -c CONFIG | --config CONFIG ] [--dry] [ --radix ( name | number ) ]
  discover.py --dir <input_dir> [ -c CONFIG | --config CONFIG ]  [--dry] [ --radix ( name | number ) ]


Options:
  -h --help                                     Show this screen.
  --version                                     Show version.
  -c CONFIG, --config CONFIG                    Config file path [default: ./config/settings.cfg].
  --dir <input_dir>                             Process all files in input_dir.
"""

import os
from docopt import docopt
from subprocess import check_call
from subprocess import CalledProcessError

# ----- main -----
if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.2.0')

    if not arguments['--radix'] or \
        (arguments['--radix'] and not
            (arguments['name'] or arguments['number'])):

        arguments['name'] = True

    config_file = arguments['--config']

    input_files = arguments['<input_xml>']
    if not input_files:
        path = arguments['--dir']
        try:
            input_files = [os.path.join(path, fn)
                           for fn in next(os.walk(path))[2]
                           if fn.endswith('.xml')
                           ]
        except StopIteration:
            raise IOError('No such directory: {}'.format(path))

    i = 0
    for input_xlm in input_files:
        basename = os.path.basename(input_xlm)

        if arguments['name']:
            radix = basename.replace('NS-SKOS-', '').replace('.xml', '')
        else:
            i = i + 1
            radix = i

        new_annotations = 'new_annotations-{}.map'.format(radix)
        different_annotations = 'different_annotations-{}.map'.format(radix)

        command = ['./discover.py',
                   input_xlm,
                   '-n', new_annotations,
                   '-d', different_annotations,
                   '-c', config_file
                   ]

        print ' '.join(command)

        try:
            if not arguments['--dry']:
                check_call(command)
                print '... done'
        except CalledProcessError as e:
            print e
