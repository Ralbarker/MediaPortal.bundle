from base64 import encodestring
from urllib import urlencode

TITLE = 'MediaPortal'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'

BASE_URL = 'http://localhost:4322/MPExtended'
CHANNELS_URL = BASE_URL + '/TVAccessService/json/GetChannelsDetailed'
ACTIVESTREAMS_URL = BASE_URL + '/StreamingService/json/GetStreamingSessions'
FINISHSTREAM_URL = BASE_URL + '/StreamingService/json/FinishStream'

####################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
  	VideoClipObject.art = R(ART)
  	MessageContainer.thumb = R(ICON)
  	MessageContainer.art = R(ART)

####################################################################################################
@handler('/video/mediaportal', TITLE, art = ART, thumb = ICON)
def MainMenu():

	oc = ObjectContainer()
	oc.add(DirectoryObject(key = Callback(GetChannels), title = 'Channels'))
	oc.add(DirectoryObject(key = Callback(CloseStreams), title = 'Close Streams'))
	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	return oc

####################################################################################################
@route('/video/mediaportal/getchannels')
def GetChannels():

	oc = ObjectContainer()

	channels = Request(CHANNELS_URL)
	for channel in channels:
		if channel['VisibleInGuide'] == True:
				oc.add(VideoClipObject(
					url = "%s?id=%s&token=%s" % (BASE_URL, str(channel['Id']), Dict['token']),
					title = channel['Title']
				))

	return oc

####################################################################################################
@route('/video/mediaportal/request')
def Request(url, values = {}):

	username = Prefs['username']
	password = Prefs['password']

	if (username != None) and (password != None):

		if 'token' not in Dict:
			Dict['token'] = encodestring("%s:%s" % (username, password))[:-1]

		headers = {'Authorization': "Basic %s" % (Dict['token'])}
		qs = urlencode(values)

		return JSON.ObjectFromURL(url + '?' + qs, headers = headers, cacheTime = 0)

	return {}

####################################################################################################
@route('/video/mediaportal/closestreams')
def CloseStreams():

	streams = Request(ACTIVESTREAMS_URL)
	for s in streams:
		data = Request(FINISHSTREAM_URL, values = {"identifier": s["Identifier"]})

	return MessageContainer("All streams have been closed", "Press OK to continue")

####################################################################################################