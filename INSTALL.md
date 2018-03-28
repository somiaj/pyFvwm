Install
-------

## Python 3 Dependencies

pyFvwm is written for Python 3. Besides needing python 3, the base
module needs the python YAML library.

pyFvwmGtk utilities require python GObject Introspection (python-gi)
with Gtk support and the Gtk libs installed on your system.

To install the required python 3 libraries on Debian run

```
apt install python3-yaml python3-gi gir1.2-gtk-3.0
```

Adjust the instructions for installing Python 3 and Gtk 3
libraries on other systems.

## pyFvwm

pyFvwm is a collection of python scripts and fvwm configurations.
You can run the scripts from any location, and only provide a link
to the main binary `pyfvwm`. To configure the scripts to run in
the current working directory, use the installer

```
python3 install.py cwd
```

If you want to copy the pyFvwm files to another location
during the install, you can use the interactive installer:

```
python3 install.py
```

For additional install options, see

```
python3 install.py help
```

To see if pyFvwm was installed correctly or to check its
configuration run

```
pyfvwm conf
```
