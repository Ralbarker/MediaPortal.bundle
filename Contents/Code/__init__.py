
TITLE 				= 'MediaPortal'
ART_DEFAULT 	= 'art-default.jpg'
ICON_DEFAULT 	= 'icon-default.png'
ICON_PREFS 		= 'icon-prefs.png'

####################################################################################################

def ServiceRequest(url, id=None):
	mp_url = 'mediaportal://%s' % url
	if id:
		mp_url = 'mediaportal://%s/%s' % (url, id)

	return JSON.ObjectFromString(String.Decode(URLService.NormalizeURL(mp_url)))

def isConnected():
	status = ServiceRequest('status')
	if status:
		return status['HasConnectionToTVServer']
	else:
		return False

####################################################################################################

def Start():
	HTTP.CacheTime = 0
	HTTP.Headers['Cache-Control'] = 'no-cache'

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART_DEFAULT)

	DirectoryObject.thumb = R(ICON_DEFAULT)
	DirectoryObject.art = R(ART_DEFAULT)

	VideoClipObject.thumb = R(ICON_DEFAULT)
	VideoClipObject.art = R(ART_DEFAULT)

@handler('/video/mediaportal', TITLE, art=ART_DEFAULT, thumb=ICON_DEFAULT)
def MainMenu():
	connected = isConnected()

	if connected:
		title = "MediaPortal"
	else:
		title = "MediaPortal [offline]"

	oc = ObjectContainer(title2="MediaPortal")

	if connected:
		#oc.add(DirectoryObject(key = Callback(GetEPG), title = 'EPG'))
		oc.add(DirectoryObject(key = Callback(GetGroups), title='Channels'))
		oc.add(DirectoryObject(key = Callback(GetSchedules), title='Schedules'))
		oc.add(DirectoryObject(key = Callback(GetRecordings), title='Recordings'))

	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))

	return oc

@route('/video/mediaportal/getgroups')
def GetGroups():
	oc = ObjectContainer(title2='Groups')

	groups = ServiceRequest('groups')
	for group in groups:
		oc.add(DirectoryObject(key = Callback(GetChannels, title=group['GroupName'], id=group['Id']), title=group['GroupName']))

	return oc

@route('/video/mediaportal/getschedules')
def GetSchedules():
	oc = ObjectContainer(title2='Schedules')

	schedules = ServiceRequest('schedules')
	for schedule in schedules:
		oc.add(DirectoryObject(key = Callback(DeleteSchedules, title=schedule['Title'], id=schedule['Id']), title=schedule['Title']))

	return oc

@route('/video/mediaportal/getrecordings')
def GetRecordings():
	oc = ObjectContainer(title2='Recordings')

	recordings = ServiceRequest('recordings')
	for recording in recordings:
		vo = URLService.MetadataObjectForURL('mediaportal://show/%s/%s' % ('13', recording['Id']))
		oc.add(vo)

	return oc

@route('/video/mediaportal/getchannels')
def GetChannels(title, id):
	oc = ObjectContainer(title2=title)

	channels = ServiceRequest('channels', id)
	for channel in channels:
		vo = URLService.MetadataObjectForURL('mediaportal://show/%s/%s' % ('12', channel['Id']))
		oc.add(vo)

	return oc

@route('/video/mediaportal/deleteschedules')
def DeleteSchedules(title, id):
	oc = ObjectContainer(title2='Delete ' + title)
	oc.add(DirectoryObject(key = Callback(DeleteSchedule, id=id), title='Delete'))
	return oc

@route('/video/mediaportal/deleteschedule')
def DeleteSchedule(id):
	ServiceRequest('delete_schedule', id)
	return MessageContainer('Press OK to continue', 'Item Deleted')

####################################################################################################