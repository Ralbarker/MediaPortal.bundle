
import datetime

TITLE 			= 'MediaPortal'
ART_DEFAULT 	= 'art-default.jpg'
ICON_DEFAULT 	= 'icon-default.png'
ICON_PREFS 		= 'icon-prefs.png'

####################################################################################################

def ServiceRequest(url, id=None, title=None, start=None, end=None, type=None):		
	data = [url]
	if id:		
		data.append(id)	
	if title:
		data.append(title)
	if start:
		data.append(str(start))
	if end:
		data.append(str(end))
	if type:
		data.append(type)	

	mp_url = 'mediaportal://%s' % ('/'.join(data))
	data = URLService.NormalizeURL(mp_url)
	if data:
		return JSON.ObjectFromString(String.Decode(data))
	else:
		return 

def IsConnected():
	status = ServiceRequest('status')
	if status:
		return status['HasConnectionToTVServer']
	else:
		return False

def NoData():
	return ""
	
def FormatDate(date, format=None):
	ms = int(date.split('/Date(')[1].split('-')[0])
	date = datetime.datetime.fromtimestamp(ms/1000.0)
	
	if format:
		return datetime.datetime.strftime(date, format)
	else:
		return date

####################################################################################################

def ValidatePrefs():
  pass

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
	connected = IsConnected()
	oc = ObjectContainer(title2='MediaPortal')

	if connected:		
		oc.add(DirectoryObject(key = Callback(GetEPG, title='EPG'), title='EPG'))
		oc.add(DirectoryObject(key = Callback(GetSchedules), title='Schedules'))
		oc.add(DirectoryObject(key = Callback(GetRecordings), title='Recordings'))
	else:
		oc.add(DirectoryObject(key = Callback(NoData), title='MediaPortal [OFFLINE]'))

	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))

	return oc

@route('/video/mediaportal/getepg')
def GetEPG(title):
	sub_title = 'EPG for '
	oc = ObjectContainer(title2=title)

	groups = ServiceRequest('groups')
	for group in groups:
		oc.add(DirectoryObject(key = Callback(GetChannels, title=sub_title + group['GroupName'], id=group['Id']), title=sub_title + group['GroupName']))			

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
		oc.add(DirectoryObject(key = Callback(GetEPGList, title=channel['Title'], id=channel['Id']), title=channel['Title']))			

	return oc
	
@route('/video/mediaportal/getepglist')
def GetEPGList(title, id):
	oc = ObjectContainer(title2='EPG for ' + title)
	start = datetime.datetime.now()
	end = start + datetime.timedelta(days=1)
	
	channels = ServiceRequest('epg', id=id, start=start, end=end)
	for idx,channel in enumerate(channels):
		start = FormatDate(channel['StartTime'], '%I:%M %p')
		end = FormatDate(channel['EndTime'], '%I:%M %p')
		oc.add(DirectoryObject(key = Callback(PlayAndRecordMenu, id=channel['ChannelId'], title=channel['Title'], start=channel['StartTime'], end=channel['EndTime'], index=idx), title=start + ' - ' + end + ' ' + channel['Title']))

	return oc

@route('/video/mediaportal/playandrecordmenu')	
def PlayAndRecordMenu(id, title, start, end, index):
	oc = ObjectContainer(title2='Play/Record: ' + title)
	Log(index)
	if int(index) == 0:
		oc.add(URLService.MetadataObjectForURL('mediaportal://show/%s/%s' % ('12', id)))
	
	oc.add(DirectoryObject(key = Callback(AddSchedule, id=id, title=title, start=start, end=end, type=0), title='Record ' + title + ' once'))
	oc.add(DirectoryObject(key = Callback(AddSchedule, id=id, title=title, start=start, end=end, type=3), title='Record ' + title + ' every time'))
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

@route('/video/mediaportal/addschedule')
def AddSchedule(id, title, start, end, type):
	ServiceRequest('add_schedule', id, title, FormatDate(start), FormatDate(end), type)
	return MessageContainer('Press OK to continue', 'Show Recorded')

####################################################################################################