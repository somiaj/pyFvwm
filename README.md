pyFvwm: Python 3 Configuration System for Fvwm
==============================================

pyFvwm is a configuration system for [fvwm](http://www.fvwm.org) written
in Python. This configuration system consists of:

+ A configuration database which tracks and stores configuration variables
  in key + value pairs. The database uses a [python dictionary](
  https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
  written as a [YAML](http://yaml.org/) file to be human friendly.

+ Configuration files, called fvwm2rc files, which are fvwm configuration
  files plus an optional pyFvwm header. The header is a python function
  that describes how to use the pyFvwm configuration to generate values
  of variables in the configuration.

+ A fvwm2rc builder, which takes an .fvwm2rc configuration file and
  builds it into a configuration for fvwm using the pyFvwm variables.
  This builder can either build a single .fvwm2rc file, or it can
  build a collection of files, called a theme.

+ Utilities are additional tools that can be used to configure,
  or help manage the configuration database and fvwm2rc files. So far
  there is the main shell script pyfvwm and a collection of Gtk 3
  configuration utilities using pyGObjects.


Installation
============

pyFvwm is a collection of Python 3 scripts and needs to have
Python 3 and some additional Python libraries installed.
See INSTALL.md for details and install instructions.

Usage
=====

The main configuration script is `pyfvwm`. The script can be used to build
a fvwm configuration as follows.

```
pyfvwm build
```

This will output "Read $HOME/.pyfvwm/.fvwm2rc". The configuration file
was built and saved at $HOME/.pyfvwm/.fvwm2rc, then the script told
fvwm to Read that file (if fvwm was listening).

The commands issued to pyfvwm will try to match based off the command
__starting with__ the command issued. For example you could also build
the configuration file with `pyfvwm b` or `pyfvwm buil`.

Besides being able to build a full theme you can build and list
individual fvwm2rc files. To list all fvwm2rc files run

```
pyfvwm fvwm2rc list
```

or just `pyfvwm f l` or even `pyfvwm f` for short. This will list all
available configuration files both system and user. Any system files
with a * are overridden by a user file of the same name.

pyfvwm can also format one of the configuration files. For example
to format the configuration file BUE/Decor.fvwm2rc the full command
would be

```
pyfvwm fvwm2rc BUE/Decor
```

This could be shortened to `pyfvwm fvwm bue/decor` (matching is not
case sensitive) or even `pyfvwm f bue/d`. You can't reduce this further
because bue would match multiple configurations for the Basic Use
Environment (BUE) configurations.

To see a full list of commands run `pyfvwm help`

Using pyFvwm with Fvwm
======================

Once pyfvwm is working above, add the following to your Fvwm configuration
file, $HOME/.fvwm/config, to import the configuration to Fvwm. To do this,
you only need to add the following

```
PipeRead `pyfvwm init $[vp.width] $[vp.height]`
```

That will be all you need in your fvwm configuration file. The init option
provides the width and height so pyFvwm can use this to build configurations
based on the size of the screen.


Basic User Environment
======================









