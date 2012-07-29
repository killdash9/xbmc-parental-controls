import xbmcaddon
import xbmc
from os import path

__addon__       = xbmcaddon.Addon('script.video.parentalcontrols')
__icon__        = __addon__.getAddonInfo('icon')
__addonpath__   = __addon__.getAddonInfo('path')
globalSettingsFile = __addonpath__ + "/../parental-controls-settings.txt"

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
    
def getCode():
    return getGlobalSetting("code")

def setCode(code):
    return setGlobalSetting("code",code)

def getTVRating():
    return __addon__.getSetting("tv-rating") or "All TV"

def setTVRating(rating):
    return __addon__.setSetting("tv-rating",rating)

def getMovieRating():
    return __addon__.getSetting("movie-rating") or "All Movies"

def setMovieRating(rating):
    return __addon__.setSetting("movie-rating",rating)

def getProtectedPlugins():
    return eval(__addon__.getSetting("protected-plugins") or "set()")

def setProtectedPlugins(protectedPlugins):
    return __addon__.setSetting("protected-plugins",str(protectedPlugins))

def addProtectedPlugin(plugin):
    protectedPlugins = getProtectedPlugins()
    protectedPlugins.add(plugin)
    setProtectedPlugins(protectedPlugins)

def removeProtectedPlugin(plugin):
    protectedPlugins = getProtectedPlugins()
    protectedPlugins.remove(plugin)
    setProtectedPlugins(protectedPlugins)

movieRatings = ['All Movies','R','PG-13','PG','G']
tvRatings = ['All TV','TV-MA','TV-14','TV-PG','TV-G','TV-Y7-FV','TV-Y7','TV-Y']

def allowed(rating):
    rating = rating.upper()
    try:
        r = movieRatings.index(rating)
        #it's a movie rating
        try:
            a = movieRatings.index(getMovieRating())
            return a <= r
        except:
            #something's funny
            return False
    except:
        #it's not a movie rating
        try:
            r = tvRatings.index(rating)
            #it's a tv rating
            try:
                a = tvRatings.index(getTVRating())
                return a <= r
            except:
                return False
        except:
            #it's neither a TV rating nor a move rating.  Let's log this
            print "Unrecognized rating: " + rating
            return False

def msg(s):
    print s
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % ( "Parental Controls", s, 2000, __icon__) )
