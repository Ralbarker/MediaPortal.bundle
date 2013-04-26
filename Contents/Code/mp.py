from base64 import encodestring
from urllib import urlencode

class MediaPortal:

####################################### User Info ##########################################

	ip = None
	port = None
	username = None
	password = None
	token = None
	base = None
	channels_detailed = None
	finish_stream = None
	streaming_sessions = None
	profiles = None

####################################### Class Methods #######################################

	def setupUser(self):
		self.ip = Prefs['address']
		self.port = Prefs['port']
		self.username = Prefs['username']
		self.password = Prefs['password']
		self.token = encodestring("%s:%s" % (self.username, self.password))[:-1]
		self.base = "http://%s:%s/MPExtended" % (self.ip, self.port)
		self.channels_detailed = self.base + "/TVAccessService/json/GetChannelsDetailed"
		self.finish_stream = self.base + "/StreamingService/json/FinishStream"
		self.streaming_sessions = self.base + "/StreamingService/json/GetStreamingSessions"
		self.profiles = [["Direct Stream", "Direct"],["HD", "HTTP Live Streaming HD"],["Ultra HQ", "HTTP Live Streaming ultra HQ"],["HQ", "HTTP Live Streaming HQ"],["Medium", "HTTP Live Streaming medium"],["Low Quality", "HTTP Live Streaming LQ"],["Ultra LQ", "HTTP Live Streaming ultra LQ"]]

	def isLoggedIn(self):
		if self.ip != None and self.port != None and self.username != None and self.password != None:
			return True
		else:
			return False

	def request_url(self, url, values = None):
		HTTP.Headers['Cache-Control'] = 'no-cache'
		qs = ''
		if values != None:
			qs = '?' + urlencode(values)
		headers = {'Authorization': "Basic %s" % (self.token)}
		return JSON.ObjectFromString(HTTP.Request(url + qs, headers=headers).content)

	def close_streams(self):
		streams = self.request_url(self.streaming_sessions)
		for s in streams:
			data = self.request_url(self.finish_stream, values = {"identifier": s["Identifier"]})
		return True

####################################### END #################################################

mp = MediaPortal()