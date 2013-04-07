from base64 import encodestring
from urllib import urlencode

class MediaPortal:

####################################### User Info ##########################################

	ip = None
	port = None
	username = None
	password = None
	token = None
	profiles = {}

####################################### REST URLs ###########################################

	base = None
	channels_detailed = None
	finish_stream = None
	init_stream = None
	start_stream = None
	custom_transcoder_data = None
	streaming_sessions = None
	client = None

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
		self.transcoder_profiles = self.base + "/StreamingService/json/GetTranscoderProfiles"

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

	def set_transcoder_profiles(self, platform):
		targets = self.active_targets(platform)
		group_profiles = self.request_url(self.transcoder_profiles)
		for idx, p in enumerate(group_profiles):

			#checking this once instead of each time thru the inner loop
			add_single = p['Name'] in targets['single']

			for t in p['Targets']:
				if t in targets['group'] or add_single:
					current = {
						"index": idx,
						"height": p['MaxOutputHeight'],
						"width": p['MaxOutputWidth'],
						"video_codec": 'h264',
						"audio_codec": 'aac',
						"audio_channels": 6,
						"container": 'mp4'
					}
					if p['Transport'] == 'httplive':
						current['protocol'] = 'hls'
					else:
						current['protocol'] = 'http'

					self.profiles[p['Name']] = current
					break;

		return True

	def active_targets(self, p):
	    return {
	        'Roku'		: {'group': ['mobile-hls-video'], 	'single': []},
	        'Android'	: {'group': ['mobile-hls-video'], 	'single': []},
	        'iOS'		: {'group': ['mobile-hls-video'], 	'single': []},
	        'Windows'	: {'group': ['pc-vlc-video'], 		'single': ['Android VLC direct']},
	        'MacOSX'	: {'group': ['pc-vlc-video'], 		'single': ['Android VLC direct']},
	        'Linux'		: {'group': ['pc-vlc-video'], 		'single': ['Android VLC direct']}
        }.get(p, {'group': ['mobile-hls-video'], 'single': []})

	def friendly_name(self, t):
		return {
			'Direct'						: 'Direct Stream',
			'Android FFmpeg HD'				: 'HD',
			'Android FFmpeg ultra HQ'		: 'Ultra High',
			'Android FFmpeg HQ'				: 'High',
			'Android FFmpeg medium'			: 'Medium',
			'Android FFmpeg LQ'				: 'Low',
			'Android FFmpeg ultra LQ'		: 'Ultra Low',
			'Android VLC direct'			: 'VLC Direct Stream',
			'Android VLC HD'				: 'VLC HD',
			'Android VLC ultra HQ'			: 'VLC Ultra High',
			'Android VLC HQ'				: 'VLC High',
			'Android VLC medium'			: 'VLC Medium',
			'Android VLC LQ'				: 'VLC Low',
			'Android VLC ultra LQ'			: 'VLC Ultra Low',
			'HTTP Live Streaming HD'		: 'HD',
			'HTTP Live Streaming ultra HQ'	: 'Ultra High',
			'HTTP Live Streaming HQ'		: 'High',
			'HTTP Live Streaming medium'	: 'Medium',
			'HTTP Live Streaming LQ'		: 'Low',
			'HTTP Live Streaming ultra LQ'	: 'Ultra Low',
			'Flash HD'						: 'HD',
			'Flash HQ'						: 'High',
			'Flash medium'					: 'Medium',
			'Flash LQ' 						: 'Low',
			'Flash Ultra LQ'				: 'Ultra Low'
		}[t]

####################################### END #################################################

mp = MediaPortal()