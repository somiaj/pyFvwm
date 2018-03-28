#

# ToDo: This is mostly just a test. This will correctly build
# a configuration widget for fvwm-menu-desktop, but at this
# time the widget does nothing.
#
#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import itertools
import subprocess
import sys
import os

import Fvwm


class XDGMenuConfig:
    def __init__(self):
        self.fvwm = Fvwm.pyFvwm()

        self.builder = Gtk.Builder()
        self.builder.add_from_file("{}/gtk/xdgconfig.glade".format(self.fvwm.home))
        self.handlers = {
            "onDeleteWindow": Gtk.main_quit,
            "onDonePress": Gtk.main_quit,
        }
        self.builder.connect_signals(self.handlers)

        self.menugrid = self.builder.get_object('menugrid')
        self.menuitem = []
        self.process = subprocess.Popen(['fvwm-menu-desktop', '--get-menus', 'all'],
                                        stdout=subprocess.PIPE, universal_newlines=True)
        out, err = self.process.communicate()

        self.menulist = []
        for menu in out.split():
            self.menulist.append( [os.path.dirname(menu), os.path.basename(menu)] )
            self.menulist.sort(key=lambda x: x[0])
        loc = 2
        path = ""
        for menu in self.menulist:
            if menu[0] != path:
                path = menu[0]
                pathlabel = Gtk.Label()
                pathlabel.set_text(path)
                pathlabel.set_property("margin_left", 10)
                pathlabel.set_property("margin_top", 5)
                pathlabel.set_property("margin_bottom", 5)
                pathlabel.set_property("halign", Gtk.Align.START)
                #pathlabel.set_justify(Gtk.Justification.LEFT)
                if loc%2 == 1: loc += 1
                self.menugrid.attach(pathlabel, 0, int(loc/2), 1, 1)
                loc += 2
            self.menuitem.append(Gtk.CheckButton(menu[1][:-5]))
            self.menuitem[-1].set_property("margin_left", 25)
            self.menuitem[-1].set_property("margin_top", 3)
            self.menuitem[-1].set_property("margin_bottom", 3)
            self.menuitem[-1].set_property("margin_right", 5)
            self.menugrid.attach(self.menuitem[-1], loc%2, int(loc/2), 1, 1)
            loc += 1

        # Create Window
        self.window = self.builder.get_object("xdgmenu")
        self.window.set_border_width(10)
        self.window.set_wmclass("FvwmConfig", "FvwmConfig")
        self.window.show_all()




