from base64 import encodestring
from urllib import urlencode

class MediaPortal:

####################################### User Info ##########################################

	ip = None
	port = None
	username = None
	password = None
	token = None

####################################### REST URLs ###########################################

	base = None
	channels_detailed = None
	finish_stream = None
	init_stream = None
	start_stream = None
	custom_transcoder_data = None
	streaming_sessions = None

####################################### Class Methods #######################################

	def __init__(self):
		self.ip = Prefs['address']
		self.port = Prefs['port']
		self.username = Prefs['username']
		self.password = Prefs['password']
		self.token = encodestring("%s:%s" % (self.username, self.password))[:-1]
		self.base = "http://%s:%s/MPExtended" % (self.ip, self.port)
		self.channels_detailed = self.base + "/TVAccessService/json/GetChannelsDetailed"
		self.finish_stream = self.base + "/StreamingService/json/FinishStream"
		self.init_stream = self.base + "/StreamingService/json/InitStream"
		self.start_stream = self.base + "/StreamingService/json/StartStream"
		self.custom_transcoder_data = self.base + "/StreamingService/stream/CustomTranscoderData?identifier=%s&action=playlist&parameters=index.m3u8"
		self.streaming_sessions = self.base + "/StreamingService/json/GetStreamingSessions"

	def request_url(self, url, values = None):
		qs = ''
		if values != None:
			qs = '?' + urlencode(values)
		headers = {'Authorization': "Basic %s" % (self.token)}
		return JSON.ObjectFromURL(url + qs, headers = headers, cacheTime = 0, timeout=60)

	def close_streams(self):
		streams = self.request_url(self.streaming_sessions)
		for s in streams:
			data = self.request_url(self.finish_stream, values = {"identifier": s["Identifier"]})
		return True

####################################### END #################################################

mp = MediaPortal()