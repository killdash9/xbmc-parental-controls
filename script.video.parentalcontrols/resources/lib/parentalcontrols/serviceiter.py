import time
import xbmcgui
import xbmcaddon
import xbmc
import inspect

import common
import hook

__addon__       = xbmcaddon.Addon()
__addonpath__   = __addon__.getAddonInfo('path')

def checkProtection():
    plugins = common.getProtectedPlugins()
    for plugin in plugins:
        state = hook.getPluginHookState(plugin)
        if (not state['hooked']) or not (state['uptodate']):
            p=hook.hookPlugin(plugin)
            common.msg("Re-protecting plugin " + p['name'])
            
def closeProgressDialogIfInterfering():
    pythonWindow = None
    pythonWindowId=13000
    try:
        pythonWindow=xbmcgui.Window(pythonWindowId)
    except:
        pass
        #window not found
    if pythonWindow:
        xmlfile = pythonWindow.getProperty('xmlfile')
        codeDialogIsUp = xmlfile and xmlfile.find('DialogCode.xml')>=0
        if codeDialogIsUp:
            #close any other open dialogs so they don't interfere
            common.closeProgressDialogIfOpen()


def iterate():
    counter=0
    while (not xbmc.abortRequested and counter < 20):
        if counter % 20 == 0:
            checkProtection()
            common.getXbmcAdultIds() #keep the cache up to date
        closeProgressDialogIfInterfering()
        time.sleep(.5)
        counter = counter+1

