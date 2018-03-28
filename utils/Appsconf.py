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
from pyFvwmGtk import pyFvwmAppsGrid
from pyFvwmGtk import pyFvwmNotebook

notebook = pyFvwmNotebook("Default Applications")
apps = pyFvwmAppsGrid()
notebook.addpage(apps, "Applications")

# Launch Window
Gtk.main()



