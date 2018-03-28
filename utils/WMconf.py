#

#
# pyFvwm desktop Configuration module.
#
#
#
#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import Fvwm
from pyFvwmGtk import pyFvwmNotebook
from pyFvwmGtk import pyFvwmWMGrid

notebook = pyFvwmNotebook("Window Manager Configuration")
wm = pyFvwmWMGrid()
notebook.addpage(wm, "Windows")

# Launch Window
Gtk.main()



