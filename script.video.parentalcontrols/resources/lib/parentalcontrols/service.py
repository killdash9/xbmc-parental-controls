import time
import common
import hook
import traceback
import xbmcgui

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

common.msg("Started")
lastMessage = time.time()
counter=0
while (not xbmc.abortRequested):
    try:
        counter = counter+1
        if counter % 20 == 0:
            checkProtection()
            common.getXbmcAdultIds() #keep the cache up to date
        closeProgressDialogIfInterfering()
        
    except:
        traceback.print_exc()
        if (time.time() - lastMessage > 5*60): #we don't want to be too annoying with errors
            common.msg("Error checking plugin protection status")
            lastMessage = time.time()
    time.sleep(.5)
