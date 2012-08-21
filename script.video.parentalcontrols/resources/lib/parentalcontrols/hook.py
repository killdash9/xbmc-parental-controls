from xml.dom.minidom import parse
import re
import os
import xbmcaddon
import traceback

__addon__       = xbmcaddon.Addon()
__addonpath__   = __addon__.getAddonInfo('path')

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

hookPattern = """(?is)#Begin parental controls hook.*?#End parental controls hook
"""
hookCode="""#Begin parental controls hook
try:
    import parentalcontrols.wrap
    parentalcontrols.wrap.check()
except (KeyboardInterrupt, SystemExit):raise
except:pass
#End parental controls hook
"""

def getPluginHookState(pluginid):
    plugindir=__addonpath__ + "/../" + pluginid
    dom=parse(plugindir + "/addon.xml")
    lib = None
    name=dom.documentElement.getAttribute('name')
    for extension in dom.getElementsByTagName("extension"):
        if (extension.getAttribute("point") == "xbmc.python.pluginsource"):
            for provides in extension.getElementsByTagName("provides"):
                if (getText(provides.childNodes).lower().find("video") >= 0):
                    lib = extension.getAttribute("library")
    if (lib):
        f = open(plugindir + "/" + lib)
        code = f.read()
        f.close()
        m = re.search(hookPattern,code,re.S)
        hooked=False
        uptodate=False
        if (m):
            hooked=True
            if (m.group() == hookCode):
                uptodate=True
        
        return {'id':pluginid,'name':name,'library':lib,'hooked':hooked,'uptodate':uptodate}
    else:
        return None


def getVideoPlugins():
    plugins=[]
    addondirs = os.listdir(__addonpath__ + "/..")
    for addondir in addondirs:
        if (addondir == __addonpath__): continue

        if (addondir =="packages"):
            continue

        if (os.path.isfile(__addonpath__+"/../"+addondir+"/addon.xml")):
            state = getPluginHookState(addondir)
        
        if (state):
            plugins.append(state)

    return plugins

def hookPlugin(pluginid):
    state = getPluginHookState(pluginid)
    if (state['hooked'] and state['uptodate']):
        return #it's done already
    pluginlibfile =__addonpath__ + "/../" + pluginid + "/" + state['library']
    f = open(pluginlibfile)
    code = f.read()
    f.close()
    code = re.sub(hookPattern,"",code) #remove old hook if present
    code = hookCode + code #add hook to top of file
    f = open(pluginlibfile,'w')
    f.write(code)
    f.close()
    return state

def unhookPlugin(pluginid):
    state = getPluginHookState(pluginid)
    if (not state['hooked']):
        return #it's done already
    pluginlibfile =__addonpath__ + "/../" + pluginid + "/" + state['library']
    f = open(pluginlibfile)
    code = f.read()
    f.close()
    code = re.sub(hookPattern,"",code) #remove old hook if present
    f = open(pluginlibfile,'w')
    f.write(code)
    f.close()

