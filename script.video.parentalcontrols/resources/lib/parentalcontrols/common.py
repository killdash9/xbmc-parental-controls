import xbmcaddon
import xbmc
import xbmcgui
from os import path
import urllib2
from xml.dom.minidom import parse
import time
import traceback

__addon__       = xbmcaddon.Addon('script.video.parentalcontrols')
__icon__        = __addon__.getAddonInfo('icon')
__addonpath__   = __addon__.getAddonInfo('path')
globalSettingsFile = __addonpath__ + "/../parental-controls-settings.txt"
addonSettingsCache={}
lastAddonSettingsCacheFlush=time.time()

def readGlobalSettings():
    if (path.exists(globalSettingsFile)):
        f = open(globalSettingsFile)
        settings=eval(f.read())
        f.close()
    else:
        settings={}
    return settings

def writeSettings(settings):
    f = open(globalSettingsFile,"w")
    f.write(str(settings))
    f.close()

def getGlobalSetting(name, default=None):
    settings = readGlobalSettings()
    return settings[name] if name in settings else default

def setGlobalSetting(name, value):
    settings = readGlobalSettings()
    settings[name]=value
    writeSettings(settings)

def setAddonSetting(name, value):
    global addonSettingsCache
    __addon__.setSetting(name,value)
    addonSettingsCache[name]=value

def getAddonSetting(name, default=None):
    global addonSettingsCache
    if time.time() - lastAddonSettingsCacheFlush > 5: #5 second cache expiration
        addonSettingsCache={}
    if name in addonSettingsCache:
        return addonSettingsCache[name]
    value = __addon__.getSetting(name) or default
    addonSettingsCache[name]=value
    return value
    
def getCode():
    return getGlobalSetting("code")

def setCode(code):
    return setGlobalSetting("code",code)

def getTVRating():
    rating=getAddonSetting("tv-rating","Allow All TV")
    if rating == "All TV":
        rating = "Allow All TV"
    return rating

def setTVRating(rating):
    return setAddonSetting("tv-rating",rating)

def getMovieRating():
    rating = getAddonSetting("movie-rating","Allow All Movies")
    if rating == "All Movies":
        rating = "Allow All Movies"
    return rating

def setMovieRating(rating):
    return setAddonSetting("movie-rating",rating)

def getProtectedPlugins():
    return eval(getAddonSetting("protected-plugins","set()"))

def setProtectedPlugins(protectedPlugins):
    return setAddonSetting("protected-plugins",str(protectedPlugins))

def addProtectedPlugin(plugin):
    protectedPlugins = getProtectedPlugins()
    protectedPlugins.add(plugin)
    setProtectedPlugins(protectedPlugins)

def removeProtectedPlugin(plugin):
    protectedPlugins = getProtectedPlugins()
    protectedPlugins.remove(plugin)
    setProtectedPlugins(protectedPlugins)

movieRatings = ['Allow All Movies', 'NC-17', 'R','PG-13','PG','G','Block All Movies']
tvRatings = ['Allow All TV', 'TV-MA','TV-14','TV-PG','TV-G','TV-Y7-FV','TV-Y7','TV-Y','Block All TV']

def allowed(rating):
    if not rating:
        return False
    rating = rating.upper()
    allowedMovie = getMovieRating()
    allowedTV = getTVRating()
    try:
        if rating in movieRatings:
            #it's a movie rating
            r = movieRatings.index(rating)
            a = movieRatings.index(allowedMovie)
            return a <= r
        elif rating in tvRatings:
            #it's a tv rating
            r = tvRatings.index(rating)
            a = tvRatings.index(allowedTV)
            return a <= r
        else:
            # it's neither a TV rating nor a movie rating.  We don't know whether it's TV or movie,
            # but let it through if they're allowing everything, otherwise block it.
            return (allowedMovie == "Allow All Movies" or allowedMovie == "NC-17")  and (allowedTV == "Allow All TV" or allowedTV == "TV-MA")
    except ValueError:
        #something's funny
        traceback.print_exc()
        return False

def closeProgressDialogIfOpen():
    progressDialog= None
    progressDialogWindowId=10101
    try:
        progressDialog = xbmcgui.Window(progressDialogWindowId)
    except:
        #window not found
        pass
    if progressDialog:
        #close progress dialog so it doesn't interfere
        xbmc.executebuiltin( "Dialog.Close(%s,true)" % progressDialogWindowId )


def msg(s):
    print s
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % ( "Parental Controls", s, 2000, __icon__) )

def getXbmcAdultIds():
    cacheDuration=60*60 #1 hour
    lastUpdate = getGlobalSetting("xbmc-adult-addon-update-time",0)
    if time.time()>lastUpdate + cacheDuration:
        try:
            refreshXbmcAdultAddonRepoXML()
        except:
            traceback.print_exc()
    return getGlobalSetting("xbmc-adult-addon-ids", [u'metadata.movie.adultdvdempire.com', u'metadata.movie.aebn.gay.net', u'metadata.movie.aebn.net', u'metadata.movie.cduniverse.com', u'metadata.movie.excaliburfilms.com', u'metadata.movie.xonair.com', u'plugin.video.empflix', u'plugin.video.fantasticc', u'plugin.video.lubetube', u'plugin.video.tube8', u'plugin.video.videodevil', u'plugin.video.you.jizz', u'repository.xbmcadult'])

def refreshXbmcAdultAddonRepoXML():
    response = urllib2.urlopen('http://xbmc-adult.googlecode.com/svn/trunk/addons.xml')
    xml=parse(response)
    adultIds=[]
    for addon in xml.getElementsByTagName("addon"):
        id=addon.getAttribute("id")
        if id:
            adultIds.append(id)
    setGlobalSetting("xbmc-adult-addon-ids",adultIds)
    setGlobalSetting("xbmc-adult-addon-update-time", int(time.time()))
