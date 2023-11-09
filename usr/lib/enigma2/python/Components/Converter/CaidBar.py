# CaidBar Converter
# Copyright (c) 2boom 2014-22
# v.0.4-r2
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

from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.Poll import Poll
import os

class CaidBar(Poll, Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.caid_default = []
		self.type = type.split(',')
		self.maincolor = self.convert_color(self.type[0].strip())
		self.emmcolor = self.convert_color(self.type[1].strip())
		self.ecmcolor = self.convert_color(self.type[2].strip())
		if len(self.type) > 3:
			self.caid_default = self.type[-1].split()
		else:
			self.caid_default = ['B', 'D', 'I', 'S', 'V', 'N', 'PV', 'CW', 'ND', 'CO', 'BI']
		self.poll_interval = 1000
		self.poll_enabled = True
		self.txt_caids = {'26':'BI', '01':'S', '06':'I', '17':'B', '05':'V', '55':'BU', '18':'N', '09':'ND', '0B':'CO', '0D':'CW', '27':'EX',\
			'7B':'D', '0E':'PV', '22':'CC', '07':'DC', '56':'VM', 'A1':'RC', 'FF':'FF'}
		self.txt_dre_caids = {'E0':'D', 'E1':'D', 'EE':'BU', 'D0':'XC', 'D1':'XC', '70':'DM', 'EA':'CG', '20':'AC'}
	
	def convert_color(self, color_in):
		return '\c' + color_in.lower().replace('#','').replace('a',':').replace('b',';').replace('c','<').replace('d','=').replace('e','>').replace('f','?')

	def getCaidInEcmFile(self):
		caidvalue = return_line = ''
		ecm_files = ['/tmp/ecm.info', '/tmp/ecm1.info'] # Tuner A,B
		for ecm_file in ecm_files:
			if os.path.isfile(ecm_file):
				try:
					filedata = open(ecm_file)
				except:
					filedata = False
				if filedata:
					for line in filedata.readlines():
						if "caid:" in line:
							caidvalue = line.strip("\n").split()[-1][2:].zfill(4)
						elif "CaID" in line or "CAID" in line:
							caidvalue = line.split(',')[0].split()[-1][2:]
					if caidvalue.upper().startswith('4A'):
						return_line += ' %s ' % self.txt_dre_caids.get(caidvalue[2:].upper(), ' ')
					else:
						return_line += ' %s ' % self.txt_caids.get(caidvalue[:2].upper(), ' ')
					filedata.close()
		return return_line

	def getServiceInfoString(self, info, what):
		value = info.getInfo(what)
		if value == -3:
			line_caids = info.getInfoObject(what)
			if line_caids and len(line_caids) > 0:
				return_value = ''
				for caid in line_caids:
					return_value += '%.4X ' % caid
				return return_value[:-1]
			else:
				return ''
		return '%d' % value
		
	def addspaces(self, what):
		return ' %s ' % what

	@cached
	def getText(self):
		string = ecmcaid = line_caids = ''
		service = self.source.service
		info = service and service.info()
		if not info:
			for i in range(len(self.caid_default)):
				string += self.maincolor + self.caid_default[i] + '  '
			return string
		caidinfo = self.getServiceInfoString(info, iServiceInformation.sCAIDs)
		if caidinfo:
			ecmcaid = self.getCaidInEcmFile()
		for caid in caidinfo.split():
			if caid.upper().startswith('4A'):
				line_caids += self.addspaces(self.txt_dre_caids.get(caid[2:]))
			else:
				line_caids += self.addspaces(self.txt_caids.get(caid[:2]))
		for i in range(len(self.caid_default)):
			if self.addspaces(self.caid_default[i]) in ecmcaid:
				string += self.ecmcolor
			elif self.addspaces(self.caid_default[i]) in line_caids:
				string += self.emmcolor
			else:
				string += self.maincolor
			string += self.caid_default[i] + '  '
		return string.strip()

	text = property(getText)

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC:
			Converter.changed(self, what)
		elif what[0] == self.CHANGED_POLL:
			self.downstream_elements.changed(what)
