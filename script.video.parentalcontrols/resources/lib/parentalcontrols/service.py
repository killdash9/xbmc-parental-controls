import time
import traceback
import xbmcaddon
import os
import xbmc

import common
import serviceiter

__addonpath__   = xbmcaddon.Addon().getAddonInfo('path')
        
common.msg("Started")
lastMessage = time.time()
while (not xbmc.abortRequested):
    try:
        files = os.listdir(__addonpath__ + "/resources/lib/parentalcontrols")
        for file in files:
            if file.endswith(".py") and file != "service.py" and file != "settings.py":
                module=file[:-3]
                #reimport the module
                try:
                    reload(eval(module))
                except NameError:
                    exec("import " + module)
        serviceiter.iterate()
    except:
        traceback.print_exc()
        time.sleep(10)
        
