# RouteInfo
# Copyright (c) 2boom 2012-22
# v.0.2
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
# <widget source="session.CurrentService" render="Label" position="189,397" zPosition="4" size="50,20" valign="center" halign="center" font="Regular;14" foregroundColor="foreground" transparent="1"  backgroundColor="background">
#	<convert type="RouteInfo"/>
# </widget>
#<widget source="session.CurrentService" render="Pixmap" pixmap="750HD/icons/ico_lan_on.png" position="1103,35" zPosition="1" size="28,15" transparent="1" alphatest="blend">
#    <convert type="RouteInfo">Lan  | Wifi | Modem</convert>
#    <convert type="ConditionalShowHide"/>
#  </widget>

from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.Directories import fileExists

class RouteInfo(Converter, object):
	Info = 0
	Lan = 1
	Wifi = 2
	Modem = 3

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "Lan":
			self.type = self.Lan
		elif type == "Wifi":
			self.type = self.Wifi
		elif type == "Modem":
			self.type = self.Modem
		else:
			self.type = self.Info
		self.actdev = self.devlist()	
	
	@cached
	def getBoolean(self):
		if self.type == self.Lan and self.actdev.startswith('et'):
			return True
		elif self.type == self.Wifi and (self.actdev.startswith('wl') or self.actdev.startswith('ra')):
			return True
		elif self.type == self.Modem and self.actdev.startswith('pp'):
			return True
		else:
			return False

	boolean = property(getBoolean)

	@cached
	def getText(self):
		if self.type == self.Lan and self.actdev.startswith('et'):
			return "Lan"
		elif self.type == self.Wifi and (self.actdev.startswith('wl') or self.actdev.startswith('ra')):
			return "WiFi"
		elif self.type == self.Modem and self.actdev.startswith('pp'):
			return "Lte"
		else:
			return ""

	text = property(getText)
	
	def devlist(self):
		devname = []
		devtype = ['et', 'wl', 'ra', 'pp']
		if fileExists('/proc/net/dev'):
			for line in open('/proc/net/dev'):
				for i in range(len(devtype)):
					if line.strip().startswith(devtype[i]):
						devname.append(line.split(':')[0].strip())
			if fileExists("/proc/net/route"):
				for line in open("/proc/net/route"):
					for i in range(len(devname)):
						if line.startswith(devname[i]) and '\t0003\t' in line:
							return devname[i]
		return ''

	def changed(self, what):
		Converter.changed(self, what)
