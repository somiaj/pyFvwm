#!/usr/bin/python3

# 
# This contains the main pyFvwm class which handles creation
# and management of the pyFvwm configuration database. In
# addition it handles formatting fvwm2rc files and building
# themes.
#
# Ensure that the home directory below is set to the location
# of pyFvwm's data files.
#

import os
import sys
import glob
import subprocess
import yaml


# Set this to the location of pyfvwm's install directory.
global home
home = "/home/jaimos/pyfvwm-0.1"
version = 0.2

#
# Main pyFvwm class
#
class pyFvwm:
    def __init__(self):
        self.home = home
        self.version = version
        self.userdir = "{}/.pyfvwm".format(os.environ['HOME'])
        self.yaml = "config.yaml"
        self.config = {}
        self.loadconfig()
        self.loadfvwm2rc()

    # Loads configuration from YAML file. Creates a blank file if none is found.
    def loadconfig(self):
        try:
            f = open('{}/{}'.format(self.userdir, self.yaml), 'r')
            self.config = yaml.safe_load(f)
            f.close()
        except:
            try:
                self.config = {}
                self.saveconfig()
            except:
                print("pyFvwmError: Unable to access configuration file: {}/{}".format(self.userdir, self.yaml))

    # Saves the configuration. Errors out if unable to write to file.
    def saveconfig(self):
        # Check if pyFvwm.userdir exists, if not create it.
        if not os.path.exists(self.userdir):
            os.makedirs(self.userdir)

        # Try to open configuration file for writing.
        try:
            f = open('{}/{}'.format(self.userdir, self.yaml), 'w')
            yaml.dump(self.config, f, default_flow_style=False)
            f.close()
        except:
            print("pyFvwmError: Unable to write to configuration file: {}/{}".format(self.userdir, self.yaml))
            sys.exit(1)

    # Loads and default configuration file. This file contains
    # the definitions needed of all configuration variables.
    def loaddefaults(self):
        f = open('{}/pyFvwm/defaults.yaml'.format(self.home), 'r')
        self.defaults = yaml.safe_load(f)
        f.close()

    # Checks to see if a given configuration group is in the
    # configuration file, and then compares the configuration
    # group to the defaults.
    def checkdefaults(self, group, config):
        if not isinstance(config, dict): config = {}
        if group not in config: config.update({group:{}})
        self.checkgroupdefaults(group, config[group])
        return config
        
    # Uses the defaults file to check and/or define any
    # variables needed in the configuration group.
    def checkgroupdefaults(self, group, config):
        self.loaddefaults()
        if not group in self.defaults: return
        defaults = self.defaults[group]
        if group in self.defaults['defaulttests']:
            defaulttests = self.defaults['defaulttests'][group]
        else: defaulttests = {}
        for key, value in defaults.items():
            try:
                data = config[key]
                if key in defaulttests:
                    test = defaulttests[key]
                    if test['type'] == "bool":
                        if not isinstance(data, bool): raise
                    elif test['type'] == "int":
                        if not isinstance(data, int): raise
                        if 'values' in test:
                            if not (test['values'][0] <= int(data) <= test['values'][1]): raise
                    elif test['type'] == "inlist" and 'values' in test:
                        if data not in test['values']: raise
                    elif test['type'] == "list":
                        if not isinstance(data, list): raise
            except: config.update({key:value})

    # Sets viewport width and height.
    def updatevpsize(self, width, height):
        self.config['vpwidth'] = int(width)
        self.config['vpheight'] = int(height)
        self.saveconfig()

    # Builds a list of both system and user fvwm2rc files available.
    def loadfvwm2rc(self):
        # Build list of system fvwm2rc files
        self.fvwm2rcsystem = []
        for root, dirs, files, in os.walk("{}/fvwm2rc/".format(self.home)):
            start = len(self.home) + 9
            for name in files:
                if name.endswith(".fvwm2rc"):
                    self.fvwm2rcsystem.append(os.path.join(root,name)[start:-8])
        self.fvwm2rcsystem.sort()

        # Build list of user fvwm2rc files
        self.fvwm2rcuser = []
        for root, dirs, files, in os.walk("{}/fvwm2rc/".format(self.userdir)):
            start = len(self.userdir) + 9
            for name in files:
                if name.endswith(".fvwm2rc"):
                    self.fvwm2rcuser.append(os.path.join(root,name)[start:-8])
        self.fvwm2rcuser.sort()
 

    # Builds a fvwm configuration file from a theme,
    # which is just a list of fvwm2rc files to format.
    def buildfvwm2rc(self, theme="default"):
        tmpfname = "{}/themes/{}".format(self.home, theme)
        try: tmpf = open(tmpfname, "r")
        except: return "FileNotFound: {}".format(tmpfname)
        data = tmpf.readlines()
        tmpf.close()

        fvwm2rc = "### pyFvwm generating theme {}\n".format(theme)
        for line in data:
            fvwm2rc += self.formatfvwm2rc(line.rstrip('\n'))
        # Add Local configuration to end
        fvwm2rc += self.formatfvwm2rc('Local')
        return fvwm2rc

    # Formats an fvwm2rc file by using a Python header which
    # defines the function FvwmFormatter that returns the
    # dictionary to use to format the remaining file using
    # Python string formatting.
    def formatfvwm2rc(self, rcfile):
        if rcfile in self.fvwm2rcuser:
            tmpfname = "{}/fvwm2rc/{}.fvwm2rc".format(self.userdir, rcfile)
        elif rcfile in self.fvwm2rcsystem:
            tmpfname = "{}/fvwm2rc/{}.fvwm2rc".format(self.home, rcfile)
        else: return "\n#pyFvwmError: Unknown fvwm2rc file: {}\n".format(rcfile)

        fvwm2rc = '\n#\n# pyFvwm formatting {}\n#\n'.format(tmpfname)
        header = ''
        pyFvwmBlock = False
        try: tmpf = open(tmpfname, "r")
        except: return "\n#pyFvwmError: FileNotFound: {}\n".format(tmpfname)
        data = tmpf.readlines()
        tmpf.close()

        # Separate pyFvwmBlock 
        for line in data:
            if line.startswith("#pyFvwmStart"):
                pyFvwmBlock = True
                continue
            if line.startswith("#pyFvwmEnd"):
                pyFvwmBlock = False
                continue
            if pyFvwmBlock: header += line
            else: fvwm2rc += line
        # Run pyFvwmBlock code if found
        if len(header) > 5:
            try:
                global fvwm
                fvwm=self
                exec(header, globals())
                formatter = FvwmFormatter(self.config)
            except Exception as err:
                return "#pyFvwmBlockError: {}".format(err)
            try:
                fmt = Fvwm2rcFormatter()
                fvwm2rc = fmt.format(fvwm2rc, **formatter)
            except: return "#PyFvwmError: FvwmFormatterError"
        return fvwm2rc

    # Sends commands to a running fvwm instance.
    # Currently only sends commands to fvwm via the shell
    # command FvwmCommand using the corresponding fvwm
    # module. ToDo: Add the ability to communicate via
    # the fvwm module api.
    def sendtofvwm(self, fvwm2rc, name="fvwm2rc", method="FvwmCommand"):
        if method == "FvwmCommand":
            self.FvwmCmd(fvwm2rc, name=name)

    # Write a temporary file then tell fvwm to Read
    # it via FvwmCommand.
    def FvwmCmd(self, fvwm2rc, name="fvwm2rc"):
        name = name.replace("/","-")
        tmpfname = "{}/.{}.tmp".format(self.userdir, name)
        try: tmpf = open(tmpfname, "w")
        except: return
        tmpf.write(fvwm2rc)
        tmpf.write("\n# This message will self destruct in 30 seconds.\n")
        tmpf.write("\nSchedule 30000 Exec exec rm {}\n".format(tmpfname))
        tmpf.close()
        cmd = "Read {}".format(tmpfname)
        subprocess.Popen(["FvwmCommand", cmd])


# Fvwm2rcFormatter is a custom formatter to ignore key errors
# from unmatched keys in the fvwm2rc file.
#from __future__ import print_function
import string
class Fvwm2rcFormatter(string.Formatter):
    def __init__(self, default='{{{0}}}'):
        self.default=default

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default.format(key))
        else:
            string.Formatter.get_value(self, key, args, kwds)
