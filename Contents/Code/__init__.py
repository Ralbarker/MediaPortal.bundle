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

	# Getting our transcoder profiles based on our client
	mp.set_transcoder_profiles(Client.Platform)

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
				oc.add(DirectoryObject(
					key = Callback(GetChannelSubMenu, id=str(channel['Id'])),
					title = channel['Title']
				))
	return oc

####################################################################################################
@route('/video/mediaportal/closestreams')
def CloseStreams():

	close = mp.close_streams()
	return MessageContainer("All streams have been closed", "Press OK to continue")

####################################################################################################
@route('/video/mediaportal/getchannelsubmenu')
def GetChannelSubMenu(id):

	oc = ObjectContainer()

	for key, val in mp.profiles.iteritems():
		oc.add(CreateStreamObject(
			id = id,
			title = mp.friendly_name(key),
			profile = key,
			index = val['index']
		))
		oc.objects.sort(key=lambda obj: obj.rating_key)
	return oc

####################################################################################################
@route('/video/mediaportal/CreateStreamObject')
def CreateStreamObject(id, title, profile, index, include_container=False):

	data = mp.profiles[profile]
	stream_obj = VideoClipObject(
		key = Callback(CreateStreamObject, id=id, title=title, profile=profile, index=index, include_container=True),
		rating_key = index,
		title = title,
		items = [
			MediaObject(
				parts = [PartObject(key=Callback(PlayStream, id=id, profile=profile))],
				height = data['height'],
				width = data['width'],
				protocol = data['protocol'],
				container = data['container'],
				video_codec = data['video_codec'],
				audio_codec = data['audio_codec'],
				audio_channels = data['audio_channels']
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

		if profile.startswith('HTTP Live'):
			return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url=playlist_url))
		else:
			return IndirectResponse(VideoClipObject, key=playlist_url)
	except:
		raise Ex.MediaNotAvailable

####################################################################################################