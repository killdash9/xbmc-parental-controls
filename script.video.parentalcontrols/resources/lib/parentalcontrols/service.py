import time
import common
import hook
import traceback

def checkProtection():
    plugins = common.getProtectedPlugins()
    for plugin in plugins:
        state = hook.getPluginHookState(plugin)
        if (not state['hooked']) or not (state['uptodate']):
            p=hook.hookPlugin(plugin)
            common.msg("Re-protecting plugin " + p['name'])
        

common.msg("Started")
lastMessage = time.time()
while (not xbmc.abortRequested):
    try:
        checkProtection()
        time.sleep(10) 
    except:
        traceback.print_exc()
        if (time.time() - lastMessage > 5*60): #we don't want to be too annoying with errors
            common.msg("Error checking plugin protection status")
            lastMessage = time.time()
        time.sleep(10)
