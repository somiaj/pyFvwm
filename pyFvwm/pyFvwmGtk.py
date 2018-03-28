#

#
# pyFvwm FvwmGtk Classes
#
# A collection of classes for the Gtk pyGObject.
#
# needs python3-gi + Gtk3 libaries.
#

import sys
from copy import deepcopy
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import glob
import os

import Fvwm


# FvwmNotebook: This sets up the main GtkWindow
# which consists of a GtkNotebook which can have
# different pages added to it, along with the
# event handlers for the three common buttons
# Apply, Reset, and Close.
class pyFvwmNotebook:
    def __init__(self, title="pyFvwm Configuration"):
        self.home = Fvwm.home
        self.fvwm = Fvwm.pyFvwm()
        self.pages = []

        # Get Notebook definition from Glade (XML) file.
        self.builder = Gtk.Builder()
        self.builder.add_from_file("{}/gtk/fvwmnotebook.glade".format(self.home))
        self.handlers = {
            "onDeleteWindow": Gtk.main_quit,
            "onDonePress": Gtk.main_quit,
            "onApplyPress": self.onApplyPress,
            "onResetPress": self.onResetPress,
        }
        self.builder.connect_signals(self.handlers)
        self.notebook = self.builder.get_object("fvwmnotebook")

        # Create Window
        self.window = self.builder.get_object("fvwmconfigwindow")
        self.window.set_border_width(11)
        self.window.set_title(title)
        self.window.set_wmclass("FvwmConfig", "FvwmConfig")
        self.window.show_all()

    # Each page must have an apply() and returnconf() function.
    # The apply() at a minimum must update the configuration values
    # from the users settings, then returnconf() needs to return both
    # the top level name of the configuration and the data.
    # The notebook then updates and saves the configuration. Pages should
    # not save their own configuration.
    def onApplyPress(self, button):
        for page in self.pages:
            page.apply()
            name, data, reloadlist = page.returnconf()
            self.fvwm.config.update({ name: data })
            for rcfile in reloadlist:
                fvwm2rc = self.fvwm.formatfvwm2rc(rcfile)
                self.fvwm.sendtofvwm(fvwm2rc, name=rcfile)
        self.fvwm.saveconfig()
        
    # Each page must have a reset() function to rest values.
    def onResetPress(self, button):
        for page in self.pages:
            page.reset()

    def addpage(self, page, pagetitle):
        self.pages.append(page)
        self.notebook.append_page(page.page, Gtk.Label(pagetitle))



# Gtk Configuration Grid for virtual Desktop settings.
class pyFvwmDesktopGrid:
    def __init__(self):
        self.home = Fvwm.home
        self.fvwm = Fvwm.pyFvwm()
        self.desktop = {}
        self.curdesk = 0
        self.initdesktop()

        # Get window definition from Glade (XML) file.
        self.builder = Gtk.Builder()
        self.builder.add_from_file("{}/gtk/desktopgrid.glade".format(self.home))
        self.handlers = {
            "onChangeDesk": self.onChangeDesk,
            "onFvwmBackerPress": self.onFvwmBackerPress,
            "onMaxDeskChange": self.onMaxDeskChange,
        }
        self.builder.connect_signals(self.handlers)

        # DesktopGrid Page
        self.page = self.builder.get_object("desktopgrid")

        # Max Number of desktops widget
        self.maxdeskct = self.builder.get_object('maxdeskct')

        # Build Desktop Selection List
        self.deskliststore = Gtk.ListStore(int,str)
        for i in range(0,self.desktop['maxdesks']):
            self.deskliststore.append([i,"Desktop {}".format(i)])
        self.desksel = self.builder.get_object('desksel')
        self.deskname = self.builder.get_object('deskname')
        self.desksel.set_model(self.deskliststore)
        self.deskcell = Gtk.CellRendererText()
        self.desksel.pack_start(self.deskcell, True)
        self.desksel.add_attribute(self.deskcell, 'text', 1)

        # FvwmBacker
        self.fvwmbacker = self.builder.get_object('fvwmbacker')

        # Build Wallpaper Selection List
        self.wallpaperstore = Gtk.ListStore(int,str)
        self.wallpaperlist = []
        self.wallpapers = glob.glob("{}/*.png".format(self.desktop['bgdir']))
        if not self.wallpapers:
            self.wallpapers = glob.glob("{}/images/wallpapers/*.png".format(self.home))
        for wallpaper in self.wallpapers:
            self.wallpaperlist.append(os.path.basename(wallpaper)[:-4])
        self.wallpaperlist.sort()
        for i, bg in enumerate(self.wallpaperlist):
            self.wallpaperstore.append([i,bg])

        # Wallpaper Selection ComboBox
        self.bgsel = self.builder.get_object('bgsel')
        self.bgsel.set_model(self.wallpaperstore)
        self.bgcell = Gtk.CellRendererText()
        self.bgsel.pack_start(self.bgcell, True)
        self.bgsel.add_attribute(self.bgcell, 'text', 1)

        # Setup rows and columns for pages
        self.colct = self.builder.get_object('colct')
        self.rowct = self.builder.get_object('rowct')

        # EdgeResistance
        self.edgeresistct = self.builder.get_object('edgeresistct')
        self.edgescroll = self.builder.get_object('edgescroll')

        # Wallpaper directory and command widget
        self.bgdir = self.builder.get_object('bgdir')
        self.bgcmd = self.builder.get_object('bgcmd')

        # Set initial widget values
        self.setvalues(self.desktop)
        self.makecopy()

    def apply(self):
        self.updatedesktop()

    def reset(self):
        self.restorecopy()
        self.setvalues(self.desktop)

    def returnconf(self):
        return ["desktop", self.desktop, ["Desktop"]]

    def updatedesktop(self):
        # Update desktop settings from Gtk widget
        self.desktop['maxdesks'] = int(self.maxdeskct.get_value())
        self.desktop['pagex'] = self.colct.get_value_as_int()
        self.desktop['pagey'] = self.rowct.get_value_as_int()
        if self.deskname.get_text() != '':
            self.desktop['desktops'][self.curdesk]['name'] = self.deskname.get_text()
        if self.bgsel.get_active() > -1:
            self.desktop['desktops'][self.curdesk]['wallpaper'] = self.wallpaperlist[self.bgsel.get_active()]
        self.desktop['fvwmbacker'] = self.fvwmbacker.get_active()
        if self.bgdir.get_text() != '':
            self.desktop['bgdir'] = self.bgdir.get_text()
        if self.bgcmd.get_text() != '':
            self.desktop['bgcmd'] = self.bgcmd.get_text()
        self.desktop['edgescroll'] = self.edgescroll.get_active()
        self.desktop['edgeresist'] = self.edgeresistct.get_value_as_int()

    def makecopy(self):
        self.desktopcopy = deepcopy(self.desktop)

    def restorecopy(self):
        self.desktop = deepcopy(self.desktopcopy)

    def setvalues(self, desktop):
        try: name = desktop['desktops'][self.curdesk]['name']
        except: name = desktop['desktops'][0]['name']
        self.fvwmbacker.set_active(desktop['fvwmbacker'])
        self.maxdeskct.set_value(desktop['maxdesks'])
        self.desksel.set_active(self.curdesk)
        self.deskname.set_text(name)
        if desktop['desktops'][self.curdesk]['wallpaper'] in self.wallpaperlist:
            self.bgsel.set_active(self.wallpaperlist.index(desktop['desktops'][self.curdesk]['wallpaper']))
        self.colct.set_value(int(desktop['pagex']))
        self.rowct.set_value(int(desktop['pagey']))
        self.bgdir.set_text(desktop['bgdir'])
        self.bgcmd.set_text(desktop['bgcmd'])
        self.edgescroll.set_active(desktop['edgescroll'])
        self.edgeresistct.set_value(int(desktop['edgeresist']))

    def initdesktop(self):
        try:
            self.desktop = deepcopy(self.fvwm.config['desktop'])
        except:
            self.desktop = {}
            self.fvwm.config.update({'desktop': {}})
        self.fvwm.checkgroupdefaults("desktop", self.desktop)

        # Build desktop list as needed
        i = 0
        for i, desk in enumerate(self.desktop['desktops']):
            if i >= self.desktop['maxdesks']: break
            if not ('name' in desk and desk['name'] is not None):
                desk.update({'name': "Desktop {}".format(i)})
            if 'wallpaper' not in desk: desk.update({'wallpaper': ''})
        for j in range(i,self.desktop['maxdesks']):
            self.desktop['desktops'].append( {'name': "Desktop {}".format(j+1), 'wallpaper': ''} )


    def onChangeDesk(self, desk):
        bgid = 0
        desk_iter = desk.get_active_iter()
        self.desktop['fvwmbacker'] = self.fvwmbacker.get_active()
        if desk_iter is not None:
            model = desk.get_model()
            row_id = model[desk_iter][0]
            if self.deskname.get_text() != '':
                self.desktop['desktops'][self.curdesk]['name'] = self.deskname.get_text()
            self.deskname.set_text(self.desktop['desktops'][row_id]['name'])
            if self.bgsel.get_active() > -1:
                if self.desktop['fvwmbacker']:
                    self.desktop['desktops'][self.curdesk]['wallpaper'] = self.wallpaperlist[self.bgsel.get_active()]
                    bgid = row_id
                else: self.desktop['desktops'][0]['wallpaper'] = self.wallpaperlist[self.bgsel.get_active()]
            if self.desktop['desktops'][bgid]['wallpaper'] in self.wallpaperlist:
                self.bgsel.set_active(self.wallpaperlist.index(self.desktop['desktops'][bgid]['wallpaper']))
            self.curdesk = row_id

    def onFvwmBackerPress(self, button):
        deskbg = 0
        if button.get_active(): deskbg = self.curdesk
        if self.desktop['desktops'][deskbg]['wallpaper'] in self.wallpaperlist:
            self.bgsel.set_active(self.wallpaperlist.index(self.desktop['desktops'][deskbg]['wallpaper']))

    # Update Desktop Name and Background on DeskChange
    def onMaxDeskChange(self, button):
        maxdesk = int(button.get_value())
        self.deskliststore = Gtk.ListStore(int,str)
        for i in range(0,maxdesk):
            self.deskliststore.append([i,"Desktop {}".format(i)])
        self.desksel.set_model(self.deskliststore)
        if self.curdesk >= maxdesk:
            self.curdesk = 0
            self.deskname.set_text(self.desktop['desktops'][0]['name'])
        self.desksel.set_active(self.curdesk)
        if maxdesk > len(self.desktop['desktops']):
            for j in range(len(self.desktop['desktops']), maxdesk):
                self.desktop['desktops'].append({'name': "Desktop {}".format(j), 'wallpaper': ''})



# GtkGrid for window manager settings.
class pyFvwmWMGrid:
    def __init__(self):
        self.home = Fvwm.home
        self.fvwm = Fvwm.pyFvwm()
        self.wm = {}
        self.initwm()

        # Get window definition from Glade (XML) file.
        self.builder = Gtk.Builder()
        self.builder.add_from_file("{}/gtk/windowsgrid.glade".format(self.home))

        # DesktopGrid Page
        self.page = self.builder.get_object("windowsgrid")

        self.focusdata = ['ClickToFocus', 'SloppyFocus', 'MouseFocus']
        self.focus = self.builder.get_object('focus')

        self.closedata = ['Menu', 'Close']
        self.closebutton = self.builder.get_object('closebutton')

        self.mousedata = ['Basic', 'Apps', 'XDG', 'Window', 'Fvwm', 'None']
        self.leftmouse = self.builder.get_object('leftmouse')
        self.rightmouse = self.builder.get_object('rightmouse')

        self.font = self.builder.get_object("font")
        self.fixedfont = self.builder.get_object("fixedfont")
        self.fontsizect = self.builder.get_object('fontsizect')
        self.raisedelayct = self.builder.get_object('raisect')
        self.fvwmauto = self.builder.get_object("fvwmauto")

        self.setvalues()
        self.makecopy()

    def apply(self):
        self.updatewm()

    def reset(self):
        self.restorecopy()
        self.setvalues()

    def returnconf(self):
        return ["wm", self.wm, ["Windows"]]

    def updatewm(self):
        self.wm['font'] = self.font.get_text()
        self.wm['fontsize'] = self.fontsizect.get_value_as_int()
        self.wm['fixedfont'] = self.fixedfont.get_text()
        self.wm['fvwmauto'] = self.fvwmauto.get_active()
        self.wm['raisedelay'] = self.raisedelayct.get_value_as_int()
        self.wm['focus'] = self.focusdata[self.focus.get_active()]
        self.wm['closebutton'] = self.closedata[self.closebutton.get_active()]
        self.wm['leftmouse'] = self.mousedata[self.leftmouse.get_active()]
        self.wm['rightmouse'] = self.mousedata[self.rightmouse.get_active()]

    def makecopy(self):
        self.wmcopy = deepcopy(self.wm)

    def restorecopy(self):
        self.wm = deepcopy(self.wmcopy)

    def setvalues(self):
        self.font.set_text(self.wm['font'])
        self.fixedfont.set_text(self.wm['fixedfont'])
        self.fontsizect.set_value(int(self.wm['fontsize']))
        self.raisedelayct.set_value(int(self.wm['raisedelay']))
        if self.wm['fvwmauto']: self.fvwmauto.set_active(True)
        else: self.fvwmauto.set_active(False)
        self.focus.set_active(self.focusdata.index(self.wm['focus']))
        self.closebutton.set_active(self.closedata.index(self.wm['closebutton']))
        self.leftmouse.set_active(self.mousedata.index(self.wm['leftmouse']))
        self.rightmouse.set_active(self.mousedata.index(self.wm['rightmouse']))

    def initwm(self):
        try: self.wm = deepcopy(self.fvwm.config['wm'])
        except:
            self.wm = {}
            self.fvwm.config.update({'wm':{}})
        self.fvwm.checkgroupdefaults("wm", self.wm)



# Gtk configuration Grid for default applications.
class pyFvwmAppsGrid:
    def __init__(self):
        self.home = Fvwm.home
        self.fvwm = Fvwm.pyFvwm()
        self.apps = {}
        self.initapps()

        # Get window definition from Glade (XML) file.
        self.builder = Gtk.Builder()
        self.builder.add_from_file("{}/gtk/appsgrid.glade".format(self.home))

        # DesktopGrid Page
        self.page = self.builder.get_object("appsgrid")

        self.termcmd = self.builder.get_object("termcmd")
        self.editorcmd = self.builder.get_object("editorcmd")
        self.editorterm = self.builder.get_object("editorterm")
        self.filemancmd = self.builder.get_object("filemancmd")
        self.filemanterm = self.builder.get_object("filemanterm")
        self.webcmd = self.builder.get_object("webcmd")
        self.webterm = self.builder.get_object("webterm")
        self.mediacmd = self.builder.get_object("mediacmd")
        self.mediaterm = self.builder.get_object("mediaterm")
        self.taskscmd = self.builder.get_object("taskscmd")
        self.tasksterm = self.builder.get_object("tasksterm")

        self.setvalues()
        self.makecopy()

    def apply(self):
        self.updateapps()
        self.fvwm.config['apps'] = deepcopy(self.apps)

    def reset(self):
        self.restorecopy()
        self.setvalues()

    def returnconf(self):
        return ["apps", self.apps, ["DefaultApps"]]

    def updateapps(self):
        self.apps['term'] = self.termcmd.get_text()
        self.apps['editor'] = self.editorcmd.get_text()
        self.apps['editorterm'] = self.editorterm.get_active()
        self.apps['fileman'] = self.filemancmd.get_text()
        self.apps['filemanterm'] = self.filemanterm.get_active()
        self.apps['web'] = self.webcmd.get_text()
        self.apps['webterm'] = self.webterm.get_active()
        self.apps['media'] = self.mediacmd.get_text()
        self.apps['mediaterm'] = self.mediaterm.get_active()
        self.apps['tasks'] = self.taskscmd.get_text()
        self.apps['tasksterm'] = self.tasksterm.get_active()

    def makecopy(self):
        self.appscopy = deepcopy(self.apps)

    def restorecopy(self):
        self.apps = deepcopy(self.appscopy)

    def setvalues(self):
        self.termcmd.set_text(self.apps['term'])
        self.editorcmd.set_text(self.apps['editor'])
        if self.apps['editorterm']: self.editorterm.set_active(True)
        else: self.editorterm.set_active(False)
        self.filemancmd.set_text(self.apps['fileman'])
        if self.apps['filemanterm']: self.filemanterm.set_active(True)
        else: self.filemanterm.set_active(False)
        self.webcmd.set_text(self.apps['web'])
        if self.apps['webterm']: self.webterm.set_active(True)
        else: self.webterm.set_active(False)
        self.mediacmd.set_text(self.apps['media'])
        if self.apps['mediaterm']: self.mediaterm.set_active(True)
        else: self.mediaterm.set_active(False)
        self.taskscmd.set_text(self.apps['tasks'])
        if self.apps['tasksterm']: self.tasksterm.set_active(True)
        else: self.tasksterm.set_active(False)

    def initapps(self):
        try: self.apps = deepcopy(self.fvwm.config['apps'])
        except: self.apps = {}
        self.fvwm.checkgroupdefaults("apps", self.apps)



# Gtk configuration Grid for BUE's BasicBar settings.
class pyFvwmBasicBarGrid:
    def __init__(self):
        self.home = Fvwm.home
        self.fvwm = Fvwm.pyFvwm()
        self.bb = {}

        # Get window definition from Glade (XML) file.
        self.builder = Gtk.Builder()
        self.builder.add_from_file("{}/gtk/basicbargrid.glade".format(self.home))

        # DesktopGrid Page
        self.page = self.builder.get_object("basicbargrid")

        self.sizedata = [35, 30, 25, 20, 15]
        self.size = self.builder.get_object("size")

        self.locdata = ["NW", "N", "NE", "SW", "S", "SE"]
        self.loc = self.builder.get_object("loc")

        self.layerdata = ["Top", "Same", "Bottom"]
        self.layer = self.builder.get_object("layer")

        self.basedata = [True, False]
        self.basestruts = self.builder.get_object("basestruts")

        self.timedata = [12, 24]
        self.time = self.builder.get_object("time")

        self.font = self.builder.get_object("font")
        self.fontsizedata = ["Large", "Regular", "Small"]
        self.fontsize = self.builder.get_object("fontsize")

        self.rightdata = ["Logout", "Desktop", "Terminal", "Home", "Nothing"]
        self.rightb = self.builder.get_object("rightb")
       
        self.initbb() 
        self.setvalues()
        self.makecopy()

    def apply(self):
        self.updatebb()

    def reset(self):
        self.restorecopy()
        self.setvalues()

    def returnconf(self):
        return ["basicbar", self.bb, ["BUE/BasicBar"]]

    def updatebb(self):
        self.bb['size'] = self.sizedata[self.size.get_active()]
        self.bb['loc'] = self.locdata[self.loc.get_active()]
        self.bb['layer'] = self.layerdata[self.layer.get_active()]
        self.bb['basestruts'] = self.basedata[self.basestruts.get_active()]
        self.bb['time'] = self.timedata[self.time.get_active()]
        self.bb['font'] = self.font.get_text()
        self.bb['fontsize'] = self.fontsizedata[self.fontsize.get_active()]
        self.bb['rightb'] = self.rightdata[self.rightb.get_active()]

    def makecopy(self):
        self.bbcopy = deepcopy(self.bb)

    def restorecopy(self):
        self.bb = deepcopy(self.bbcopy)

    def setvalues(self):
        self.size.set_active(self.sizedata.index(self.bb['size']))
        self.loc.set_active(self.locdata.index(self.bb['loc']))
        self.layer.set_active(self.layerdata.index(self.bb['layer']))
        self.basestruts.set_active(self.basedata.index(self.bb['basestruts']))
        self.time.set_active(self.timedata.index(self.bb['time']))
        self.font.set_text(self.bb['font'])
        self.fontsize.set_active(self.fontsizedata.index(self.bb['fontsize']))
        self.rightb.set_active(self.rightdata.index(self.bb['rightb']))

    def initbb(self):
        try: self.bb = deepcopy(self.fvwm.config['basicbar'])
        except:
            self.bb = {}
            self.fvwm.config.update({'basicbar':{}})
        self.fvwm.checkgroupdefaults("basicbar", self.bb)

