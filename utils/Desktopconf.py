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
from pyFvwmGtk import pyFvwmDesktopGrid

notebook = pyFvwmNotebook("Workspace Configuration")
desk = pyFvwmDesktopGrid()
notebook.addpage(desk, "Workspaces")

# Launch Window
Gtk.main()



