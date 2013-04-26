from mp import *

TITLE = 'MediaPortal'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'
SERVICE_URL = "%s:%s/video/mediaportal/playstream?token=%s&id=%s&profile=%s"

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
  	PopupDirectoryObject.thumb = R(ICON)
  	PopupDirectoryObject.art = R(ART)

####################################################################################################
@handler('/video/mediaportal', TITLE, art = ART, thumb = ICON)
def MainMenu():

	mp.setupUser()
	oc = ObjectContainer()

	if mp.isLoggedIn():
		oc.add(DirectoryObject(key = Callback(GetChannels), title = 'Channels'))
		oc.add(DirectoryObject(key = Callback(CloseStreams), title = 'Close Streams'))

	oc.add(PopupDirectoryObject(key = Callback(QualitiesMenu), title = 'Set Default Quality'))
	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	return oc

####################################################################################################
@route('/video/mediaportal/getchannels')
def GetChannels():

	oc = ObjectContainer()

	channels = mp.request_url(mp.channels_detailed)
	for channel in channels:
		if channel['VisibleInGuide'] == True:
				oc.add(VideoClipObject(
					url = SERVICE_URL % (mp.ip, mp.port, mp.token, str(channel['Id']), Data.Load("Profile")),
					title = channel['Title']
				))
	return oc

####################################################################################################
@route('/video/mediaportal/qualitiesmenu')
def QualitiesMenu():

	oc = ObjectContainer()

	for idx, profile in enumerate(mp.profiles):
		if idx == 0 and Client.Platform != "Windows":
			continue

		oc.add(DirectoryObject(
			key = Callback(SetQuality, quality=profile[1], friendly_name=profile[0]),
			title = profile[0]
		))

	return oc

####################################################################################################
@route('/video/mediaportal/setquality')
def SetQuality(quality, friendly_name):

	Data.Save("Profile", quality)
	return MessageContainer("The default quality has been set to " + friendly_name, "Press OK to continue")

####################################################################################################
@route('/video/mediaportal/closestreams')
def CloseStreams():

	close = mp.close_streams()
	return MessageContainer("All streams have been closed", "Press OK to continue")

####################################################################################################