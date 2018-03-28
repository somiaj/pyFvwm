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
from pyFvwmGtk import pyFvwmAppsGrid
from pyFvwmGtk import pyFvwmWMGrid
from pyFvwmGtk import pyFvwmBasicBarGrid

notebook = pyFvwmNotebook("Basic User Environment Configuration")

notebook.addpage(pyFvwmWMGrid(), "Windows")
notebook.addpage(pyFvwmAppsGrid(), "Applications")
notebook.addpage(pyFvwmDesktopGrid(), "Workspaces")
notebook.addpage(pyFvwmBasicBarGrid(), "BasicBar")

# Launch Window
Gtk.main()



