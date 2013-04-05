from mp import *

TITLE = 'MediaPortal'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'

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

	channels = mp.request_url(mp.channels_detailed)
	for channel in channels:
		if channel['VisibleInGuide'] == True:
				oc.add(CreateStreamObject(
					url = "%s?id=%s&token=%s" % (mp.base, str(channel['Id']), mp.token),
					id = str(channel['Id']),
					title = channel['Title']
				))

	return oc

####################################################################################################
@route('/video/mediaportal/closestreams')
def CloseStreams():

	close = mp.close_streams()
	return MessageContainer("All streams have been closed", "Press OK to continue")

####################################################################################################
@route('/video/mediaportal/CreateStreamObject')
def CreateStreamObject(url, id, title, include_container=False):

	if Client.Platform in [ClientPlatform.Windows, ClientPlatform.MacOSX, ClientPlatform.Linux]:
		profile = "Direct"
	else:
		profile = "HTTP Live Streaming HQ"

	stream_obj = VideoClipObject(
		key = Callback(CreateStreamObject, url=url, id=id, title=title, include_container=True),
		rating_key = url,
		title = title,
		items = [
			MediaObject(
				parts = [PartObject(key=Callback(PlayStream, id=id, profile=profile))],
				video_codec = VideoCodec.H264,
				audio_codec = AudioCodec.AAC
			)
		]
	)

	if include_container:
		return ObjectContainer(objects=[stream_obj])
	else:
		return stream_obj

####################################################################################################
@indirect
@route('/video/mediaportal/playstream')
def PlayStream(id, profile):

	playlist_url = None
	active = False

	try:
		sessions = mp.request_url(mp.streaming_sessions)
		for s in sessions:
			if id == str(s["Identifier"]) and profile == s["Profile"]:
				active = True
				break

		if active == True:
			playlist_url = mp.custom_transcoder_data % (id)

		else:
			init = mp.request_url(mp.init_stream, values = {"identifier": id, "itemId": id, "type": "12"})
			start = mp.request_url(mp.start_stream, values = {"identifier": id, "profileName": profile})
			playlist_url = start["Result"]

		if profile == "Direct":
			return IndirectResponse(VideoClipObject, key=playlist_url)
		else:
			return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url=playlist_url))
	except:
		raise Ex.MediaNotAvailable

####################################################################################################