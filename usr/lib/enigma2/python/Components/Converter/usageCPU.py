# usageCPU Converter
# Copyright (c) 2boom 2022
# v.0.1-r0
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#average idle percentage X % = ( idle * 100 ) / ( user + nice + system + idle + iowait + irq + softirq )

from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.Poll import Poll
from Tools.Directories import fileExists

class usageCPU(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 1000
		self.poll_enabled = True
		
	@cached
	def getText(self):
		cpunum = []
		corecount = cpusumm = 0
		if fileExists('/proc/stat'):
			for line in open('/proc/stat'):
				if line.startswith('cpu'):
					tmp = 0
					for i in range(1,8):
						tmp += int(line.split()[i])
					cpunum.append(100 - (int(line.split()[4]) * 100)/ tmp)
			for i in range(len(cpunum)):
				cpusumm = cpusumm + cpunum[i]
				corecount += 1
			return '%d%%' % round(cpusumm / corecount)
		else:
			return 'N/A'

	text = property(getText)
	
	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC:
			Converter.changed(self, what)
		elif what[0] == self.CHANGED_POLL:
			self.downstream_elements.changed(what)