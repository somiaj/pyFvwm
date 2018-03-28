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
from pyFvwmGtk import pyFvwmBasicBarGrid

notebook = pyFvwmNotebook("BasicBar Configuration")
bb = pyFvwmBasicBarGrid()
notebook.addpage(bb, "BasicBar")

# Launch Window
Gtk.main()



