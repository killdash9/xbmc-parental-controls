import xbmc
import xbmcaddon
import xbmcgui
import common

### get addon info
__addon__       = xbmcaddon.Addon('script.video.parentalcontrols')
__addonpath__   = __addon__.getAddonInfo('path')

class ComboWinXML(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath, default, message):
        self.code=""
        self.stars=""
        self.message = message
        self.ok=None
 
    def onInit(self):
        # Put your List Populating code/ and GUI startup stuff here
        xbmcgui.WindowXMLDialog.onInit(self)
        self.setTitle(self.message)
        
    def setTitle(self,title):
        self.getControl(1).setLabel(title)

    def updateStars(self,stars):
        self.stars = stars
        self.getControl(4).setLabel(stars)
 
    def onAction(self, action):
        id = action.getId()
        #common.msg("action is %s" % id)
        if (id == 1 or id == 2 or id == 3 or id == 4):
            self.code += str(id)
            self.updateStars(self.stars+"*")
        elif (id == 7):
            self.ok=1
            self.close()
        else:
            xbmcgui.WindowXMLDialog.onAction(self,action)


def showComboDialog(title):
    ui= ComboWinXML("DialogCode.xml", __addonpath__, "default", title)
    common.closeProgressDialogIfOpen()
    ui.doModal()
    if (ui.ok):
        code = ui.code
    else:
        code = None
    del ui
    return code

def setCodeUI(title="Enter New Code"):
    if (common.getCode()):
        if (not unlockUI("Enter Current Code")):
            return False
    while True:
        code1 = showComboDialog(title)
        if (code1 == None): return False
        code2 = showComboDialog("Re-enter Code")
        if (code2 == None): return False
        if (code1 == code2):
            if (len(code1)>0):
                common.setCode(code1)
                common.msg("Code has been set")
                return True
            else:
                common.msg("Code may not be empty")
        else:
            common.msg("Codes did not match")

def unlockUI(title = "Enter unlock code"):
    code = showComboDialog(title)
    while True:
        if (code == None): return False
        if (code == common.getCode()):
            return True
        code = showComboDialog("Incorrect, try again")
