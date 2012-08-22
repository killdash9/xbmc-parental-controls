from xbmcplugin import addDirectoryItem, addDirectoryItems, endOfDirectory, setResolvedUrl
from xbmcgui import ListItem
from xbmc import PlayList,Player
import xbmcaddon
import common
import sys
import codeui
import xbmc
import time
import re

allowedItems=0
total = 0
blockedRatings = set()

def getBlocked():
    global total, allowedItems
    return total - allowedItems

def getUnlockedTime():
    return int(common.getAddonSetting("unlocked-time",0))

def setUnlockedTime(i):
    return common.setAddonSetting("unlocked-time",str(i))

def addBlockedRating(rating):
    if len(rating)<=5:
        rating = rating.upper()
    if not rating:
        rating="Unrated"
    blockedRatings.add(rating)

def getBlockedRatingsString():
    retVal=""
    for rating in blockedRatings:
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
        rating=getMpaaRating(wrappeditem.infoLabels)
        if rating:
            if common.allowed(rating):
                return True
            else:
                addBlockedRating(rating)
                return False
        if not isFolder:
            addBlockedRating("Unknown Rating")
            return False
        return True #it's a folder, let it through
    print "shouldn't get here"
    return True #shouldn't happen
    
# returns None if no rating
def getMpaaRating(infoLabels):
    for k in infoLabels:
        if k.lower() == "mpaa":
            return infoLabels[k]
    return None

def unwrapTuple(t):
    if (len(t) == 2):
        return (t[0],t[1]._obj)
    else:
        return (t[0],t[1]._obj, t[2])

overridemarker = '?pc_override'
overridemarkerPattern = r'\?pc_override=(\w+)'

#xmbcplugin function overrides
def wrapper_addDirectoryItem(handle, url, listitem, isFolder=False, totalItems = 0):
    global total,allowedItems
    total=total+1
    if (not allowed(listitem, isFolder)):
        return False
    allowedItems = allowedItems + 1
    if listitem.getLabel() and re.sub(r'[\W]+','',listitem.getLabel().lower()) == "search":
        url = url + overridemarker + "=true"
        listitem.setLabel(listitem.getLabel() + " (Protected)")
    return addDirectoryItem(handle, url, listitem._obj, isFolder, totalItems-getBlocked())

def wrapper_addDirectoryItems(handle, items, totalItems = 0):
    global total,allowedItems
    total=total+len(items)
    items = [unwrapTuple(t) for t in items if allowed(t[1], t[2] if len(t) > 2 else False)]
    allowedItems = allowedItems + len(items)
    return addDirectoryItems(handle, items, totalItems-getBlocked())

def wrapper_endOfDirectory(handle, succeeded = True, updateListing = False, cacheToDisc = True):
    global allowedItems
    url = sys.argv[0] + sys.argv[2] + overridemarker + "=true"
    if (getBlocked() > 0):
        title="Blocked %s (%s)" % (getBlockedRatingsString(),getBlocked())
        item = ListItem(title,"",common.__icon__, common.__icon__)
        info={
            "Title":title,
            "Plot":"Some content has been blocked by the Parental Controls addon.  Click to unblock."
            }
        item.setInfo("video",info)
        addDirectoryItem(handle, url, item, False, allowedItems+1)
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

def wrapper_Player_play(self, item = None, listitem = None, windowed = False):
    
    if (listitem and hasattr(listitem,"_obj")):
        wrappeditem = listitem
        rating=getMpaaRating(wrappeditem.infoLabels)
        if not common.allowed(rating):
            blockedRating = rating or "Unknown Rating"
            if not codeui.unlockUI("Blocked (%s)" % blockedRating):
                return None
            setUnlockedTime(int(time.time()))
            common.msg("Unlocked for 5 minutes")
        #unwrap before delegating
        listitem=listitem._obj
    if (item and hasattr(item,"_obj")):
        #unwrap before delegating
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

#Determines whether to wrap the plugin.  Also shows unlock dialog
def check():

    showUnlockDialog = False
    
    # see if our marker is present
    match=re.search(overridemarkerPattern, sys.argv[2] if len(sys.argv) > 2 else None)
    if match:
        sys.argv[2] = re.sub(overridemarkerPattern,'',sys.argv[2]) #strip marker
        showUnlockDialog=True

    unlockWindow = 5*60
    if time.time() - getUnlockedTime() < unlockWindow:
        return #early return, we're in unlock window so we don't wrap

    # see if we're an adult plugin
    thisAddonId   = xbmcaddon.Addon().getAddonInfo('id')
    showUnlockDialog = showUnlockDialog or thisAddonId in common.getXbmcAdultIds() 

    if showUnlockDialog:
        if codeui.unlockUI():
            setUnlockedTime(int(time.time()))
            common.msg("Unlocked for 5 minutes")
            xbmc.executebuiltin('Container.Update(' + sys.argv[0] + sys.argv[2] + ')')
        #else incorrect code, abort navigation with exit()
        exit()

    __builtins__['__import__'] = wrapper_import

