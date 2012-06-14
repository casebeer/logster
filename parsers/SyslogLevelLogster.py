# vim: expandtab ts=4 sw=4:
###  A logster parser that can be used to count the number
###  of each syslog error level found in an syslog file.
###
###  For example:
###  sudo ./logster --dry-run --output=ganglia SyslogLevelLogster /var/log/messages
###
###
###  Copyright 2011, Etsy, Inc.
###
###  This file is part of Logster.
###
###  Logster is free software: you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation, either version 3 of the License, or
###  (at your option) any later version.
###
###  Logster is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
###  GNU General Public License for more details.
###
###  You should have received a copy of the GNU General Public License
###  along with Logster. If not, see <http://www.gnu.org/licenses/>.
###

import time
import re

from logster_helper import MetricObject, LogsterParser
from logster_helper import LogsterParsingException

class SyslogLevelLogster(LogsterParser):
    def __init__(self, option_string=None):
        level_strings = [ 'EMERG', 'ALERT', 'CRIT', 'ERR', 'WARNING', 'NOTICE', 'INFO', 'DEBUG' ]
        self.levels = dict([(level,0) for level in level_strings])

        self.reg = re.compile('.* (?P<level>{levels}):.*'.format(levels="|".join(level_strings)), re.IGNORECASE)
    def parse_line(self, line):
        '''Parse a single line and update counter states accordingly.'''
        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
                level = linebits['level']

                if level in self.levels:
                    self.levels[level] += 1
            # n.b. not all syslog lines will have a standard level string, so don't worry if the pattern misses
        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e
    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = duration

        # Return a list of metrics objects
        return [ MetricObject("syslog_{level}".format(level=level), self.levels[level], "Total errors") for level in self.levels ]

        # todo: allow per second output via options
        #MetricObject("syslog_{level}_per_second".format(level=level), (self.levels[level] / self.duration), "Errors per second")
