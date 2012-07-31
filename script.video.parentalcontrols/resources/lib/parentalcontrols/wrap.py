from xbmcplugin import addDirectoryItem, addDirectoryItems, endOfDirectory, setResolvedUrl
from xbmcgui import ListItem
from xbmc import PlayList,Player
import xbmcaddon
import common
import sys
import codeui
import xbmc
import time

__addon__ = xbmcaddon.Addon('script.video.parentalcontrols')

def resetCounts():
    __addon__.setSetting("total","0")
    __addon__.setSetting("allowed","0")
    __addon__.setSetting("blocked-ratings","set()")
    
def incrementAllowed(i):
    __addon__.setSetting("allowed",str(getAllowed()+i))

def incrementTotal(i):
    __addon__.setSetting("total",str(getTotal()+i))

def getTotal():
    return int(__addon__.getSetting("total") or 0)

def getAllowed():
    return int(__addon__.getSetting("allowed") or 0)

def getBlocked():
    return getTotal() - getAllowed()

def getUnlockedTime():
    return int(__addon__.getSetting("unlocked-time") or 0)

def setUnlockedTime(i):
    return __addon__.setSetting("unlocked-time",str(i))

def getBlockedRatings():
    return eval(__addon__.getSetting("blocked-ratings") or "set()")

def setBlockedRatings(blockedRatings):
    return __addon__.setSetting("blocked-ratings",str(blockedRatings))

def addBlockedRating(rating):
    if len(rating)<=5:
        rating = rating.upper()
    if not rating:
        rating="Unrated"
    blockedRatings = getBlockedRatings()
    blockedRatings.add(rating)
    setBlockedRatings(blockedRatings)

def getBlockedRatingsString():
    s=getBlockedRatings()
    retVal=""
    for rating in s:
        if len(retVal)>0:
            retVal +=","
        retVal +=rating
    if retVal:
        return " [%s]" % retVal
    return ""

class Proxy(object):
    """Pulled this from http://code.activestate.com/recipes/252151-generalized-delegates-and-proxies/"""
    def __init__(self, obj):
        super(Proxy, self).__init__()
        #Set attribute.
        self._obj = obj
        
    def __getattr__(self, attrib):
        return getattr(self._obj, attrib)

def allowed(wrappeditem, isFolder):
    #get rating
    if (hasattr(wrappeditem,"type")
        and wrappeditem.type.lower() == 'video'
        and hasattr(wrappeditem, "infoLabels")
        ):
        print wrappeditem.infoLabels
        for k in wrappeditem.infoLabels:
            if (k.lower() == "mpaa"):
                mpaa = wrappeditem.infoLabels[k]
                print "Current settings: " + common.getMovieRating() + " " + common.getTVRating()
                if (not common.allowed(mpaa)):
                    print "Blocking rating " + mpaa
                    addBlockedRating(mpaa)
                    return False
                else:
                    print "Allowing rating " + mpaa
                    return True
        print "Couldn't find rating, returning isFolder: %s" % isFolder
        if not isFolder:
            addBlockedRating("Unknown Rating")
        return isFolder #allow folders
    return True #shouldn't happen
    
def unwrapTuple(t):
    if (len(t) == 2):
        return (t[0],t[1]._obj)
    else:
        return (t[0],t[1]._obj, t[2])

overridemarker = '?pc_override=true'

#xmbcplugin function overrides
def wrapper_addDirectoryItem(handle, url, listitem, isFolder=False, totalItems = 0):
    incrementTotal(1)
    if (not allowed(listitem, isFolder)):
        return False
    incrementAllowed(1)
    return addDirectoryItem(handle, url, listitem._obj, isFolder, totalItems-getBlocked())

def wrapper_addDirectoryItems(handle, items, totalItems = 0):
    incrementTotal(len(items))
    items = [unwrapTuple(t) for t in items if allowed(t[1], t[2] if len(t) > 2 else False)]
    incrementAllowed(len(items))
    return addDirectoryItems(handle, items, totalItems-getBlocked())

def wrapper_endOfDirectory(handle, succeeded = True, updateListing = False, cacheToDisc = True):
    url = sys.argv[0] + sys.argv[2] + overridemarker
    if (getBlocked() > 0):
        item = ListItem("Blocked %s (%s)" % (getBlockedRatingsString(),getBlocked()),"",common.__icon__, common.__icon__)
        info={
            "Title":"Blocked by Parenal Controls",
            "Plot":"Some content has been blocked by the Parental Controls plugin.  Click to unblock."
            }
        item.setInfo("video",info)
        addDirectoryItem(handle, url, item, False, getAllowed()+1)
    return endOfDirectory(handle,succeeded,updateListing,cacheToDisc)

def wrapper_setResolvedUrl(handle, succeeded, listitem):
    return setResolvedUrl(handle, succeeded, listitem._obj)
    
#ListItem method overrides
def wrapper_ListItem(*args,**kwargs):
    rv= ListItem(*args,**kwargs)
    cls=type("ListItemProxy",(Proxy,),{"setInfo":wrapper_ListItem_setInfo})
    return cls(rv)

def wrapper_ListItem_setInfo(self,type, infoLabels):
    self.type = type 
    self.infoLabels = infoLabels
    return self._obj.setInfo(type,infoLabels)

#PlayList method overrides
def wrapper_PlayList(*args,**kwargs):
    rv = PlayList(*args,**kwargs)
    cls=type("PlayListProxy",(Proxy,),{"add":wrapper_PlayList_add})
    return cls(rv)

def wrapper_PlayList_add(self, url, listitem = None, index = -1):
    if (listitem and hasattr(listitem,"_obj")):
        listitem=listitem._obj
    return self._obj.add(url,listitem,index)

#Player method overrides
def wrapper_Player(*args,**kwargs):
    rv = Player(*args,**kwargs)
    cls=type("PlayerProxy",(Proxy,),{"play":wrapper_Player_play})
    return cls(rv)

def wrapper_Player_play(item = None, listitem = None, windowed = False):
    if (listitem and hasattr(listitem,"_obj")):
        listitem=listitem._obj
    if (item and hasattr(item,"_obj")):
        item = item._obj
    return self._obj.play(item, listitem, windowed)

#Hook in on import
origimport = __builtins__['__import__']

def wrapper_import(*args,**kwargs):
    rv= origimport(*args,**kwargs)
    if (args[0] == "xbmcplugin"):
        rv.addDirectoryItem = wrapper_addDirectoryItem
        rv.addDirectoryItems = wrapper_addDirectoryItems
        rv.endOfDirectory = wrapper_endOfDirectory
        rv.setResolvedUrl = wrapper_setResolvedUrl
    elif (args[0] == "xbmcgui"):
        rv.ListItem = wrapper_ListItem
    elif (args[0] == "xbmc"):
        rv.PlayList = wrapper_PlayList
        rv.Player = wrapper_Player
    return rv


#don't hook if override marker is present and they have the code
hook=True
unlockWindow = 5 * 60 
print "ARGV is ", sys.argv
if (len(sys.argv) > 2 and sys.argv[2].find(overridemarker)>=0):
    sys.argv[2] = sys.argv[2].replace(overridemarker,"") #strip marker
    if (codeui.unlockUI()):
        setUnlockedTime(int(time.time()))
        common.msg("Unlocked for 5 minutes")
        xbmc.executebuiltin('Container.Update(' + sys.argv[0] + sys.argv[2] + ')')
    exit() #we don't want the plugin to execute
elif (time.time() - getUnlockedTime() < unlockWindow):
    hook = False
    
if (hook):
    __builtins__['__import__'] = wrapper_import
    resetCounts()
