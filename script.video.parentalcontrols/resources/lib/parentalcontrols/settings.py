import codeui
import xbmcgui
import common
import xbmcaddon
import hook
import xbmc

__addon__       = xbmcaddon.Addon()
__addonpath__   = __addon__.getAddonInfo('path')

dialog = xbmcgui.Dialog()

def chooseAction():
    lines = ["Change Code" if common.getCode() else "Set Code",
             "TV:                "     + common.getTVRating()    + ("" if common.getTVRating().   startswith("All") else " and below"),
             "Movies:         " + common.getMovieRating() + ("" if common.getMovieRating().startswith("All") else " and below"),
             "Choose Plugins to Protect"
            ]
    return  dialog.select("Parental Controls", lines)

def setMovieRatingUI():
    choice = xbmcgui.Dialog().select("Choose Highest Allowed Movie Rating",common.movieRatings)
    if (choice < 0): return
    common.setMovieRating(common.movieRatings[choice])
    
def setTVRatingUI():
    choice = xbmcgui.Dialog().select("Choose Highest Allowed TV Rating",common.tvRatings)
    if (choice < 0): return
    common.setTVRating(common.tvRatings[choice])

def controlAddonsUI():
    while True:
        plugins = hook.getVideoPlugins()
        items = [p['name'] + ("  [Protected]" if p['hooked'] and p['uptodate'] else "  [Protected, Needs Update]" if p['hooked'] else "  [Unprotected]") for p in plugins]
        choice = dialog.select("Choose Plugins to Protect",items)
        if (choice < 0): return
        p = plugins[choice]
        if (p['hooked'] and p['uptodate']):
            common.removeProtectedPlugin(p['id'])
            hook.unhookPlugin(p['id'])
        else:
            hook.hookPlugin(p['id'])
            common.addProtectedPlugin(p['id'])

if (common.getCode()):
    allowed=codeui.unlockUI('Enter your code')
else:
    #prompt to choose code if first time
    allowed=codeui.setCodeUI("Choose a Code")
    #prompt to protect plugins
    if (allowed):
        controlAddonsUI()
    

#present main settings window
while (allowed):
    action = chooseAction()
    if (action == 0):
        codeui.setCodeUI()
    elif (action == 1):
        setTVRatingUI()
    elif (action == 2):
        setMovieRatingUI()
    elif (action == 3):
        controlAddonsUI()
    else:
        if ((not common.getCode()) and xbmcgui.Dialog().yesno("Set Code Now?","You haven't set a code yet.\nParental controls will not be enabled until you do")):
                codeui.setCodeUI()
        if (not common.getCode()):
            common.msg("Not enabled")
        break

