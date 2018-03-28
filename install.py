#!/usr/bin/python3

# 
# pyFvwm install script:
#   + Test python's version and for yaml.
#   + Asks for install location.
#   + Copies pyFvwm to install location and
#     creates a link to pyfvwm in /usr/local/bin.
#
# Basic Usage:
#   Interactive install:    python3 install.py
#   Update home to cwd:     python3 install.py --cwd
#   All install options:    python3 install.py --help
#

import os
import sys
import glob
import subprocess

# Test for Python 3. Abort otherwise.
if sys.version_info[0] < 3:
    sys.exit("Python 2 detected: pyFvwm requires python 3. . . .aborting!")
python = sys.executable

# Test for python yaml. Abort otherwise.
try:
    import yaml
except:
    sys.exit("YAML not found? pyFvwm requires python3-yaml. . . .aborting!")

#
# pyFvwm Installer functions
#

# Place binary link in binloc to pyfvwm
def copylink(loc, binloc):
    path = "{}/pyFvwm/pyfvwm".format(loc)
    link = "{}/pyfvwm".format(binloc)
    print("pyFvwm Installer: Creating binary link: {} -> {}".format(link,path))
    if not os.path.exists(path):
        sys.exit("Install error: Cannot find pyfvwm at {}".format(path))
    if os.path.isdir(binloc):
        if os.path.islink(link): os.unlink(link)
        if os.path.exists(link):
            print("Warning! {} exists and is not a link.")
            confirm = input("Delete file and replace with link anyways? (y/[N])? ")
            if confirm.lower() in ["y", "yes"]: os.remove(link)
            else: sys.exit("Aborting pyFvwm installer!")
        # Try to create a link
        try: os.symlink(path, link)
        except: sys.exit("Install error: Unable to create link: {}".format(link))
    else: sys.exit("Install error: Directory {} does not exist.".format(binloc))


# Update pyFvwm home location to loc.
# cwd is the directory the installer is in.
def updatehome(loc, cwd):
    print("pyFvwm Installer: Updating pyFvwm's home location: {}".format(loc))
    paths = ["{}/pyFvwm/pyfvwm".format(cwd), "{}/pyFvwm/Fvwm.py".format(cwd)]
    for path in paths:
        try: fin = open(path, "r")
        except: sys.exit("Install error: Unable to open {}".format(path))
        data = "#!{}\n".format(python)
        for line in fin.readlines()[1:]:
            if line.startswith("home"): data += 'home = "{}"\n'.format(loc)
            else: data += line
        fin.close()
        fout = open(path, "w")
        fout.write(data)


# Copy pyFvwm to location.
def copypyfvwm(loc):
    print("pyFvwm Installer: Copying pyFvwm to: {}".format(loc))
    if not os.path.exists(loc):
        # Try to create directory
        try: os.makedirs(loc)
        except: sys.exit("Install error: Unable to create directory: {}".format(loc))
    if not os.path.isdir(loc):
        sys.exit("Install error: Install location {} is not a directory.".format(loc))
    cpcmd = ["cp", "-r", "{}/fvwm2rc".format(cwd), "{}/gtk".format(cwd),
                         "{}/images".format(cwd), "{}/pyFvwm".format(cwd),
                         "{}/themes".format(cwd), "{}/utils".format(cwd), loc]
    # Copy pyFvwm components to loc.
    process = subprocess.Popen(cpcmd)
    process.wait()


# Write log of install variables as .yaml file
def loginst(cwd, loc, binloc):
    data = {'WorkingDirectory': cwd,
            'InstallLocation': loc,
            'BinaryLinkLocation': binloc}
    f = open("install.log.yaml", "w")
    yaml.dump(data, f, default_flow_style=False)
    f.close()

# Confirm install information.
def confirminst(cmd, loc, binloc, cwd):
    if cmd == "cwd":
        print("    Install actions:  Use current location. Only create link.")
        print("    pyFvwm home location:   {}".format(cwd))
        print("    Binary link location:   {}".format(binloc))
        print("    Python3 Interpreter:    {}".format(python))
        confirm = input("Install pyFvwm using above information ([Y]/n)? ")
        if confirm.lower() in ["", " ", "y", "yes"]:
            print("Installing...")
            updatehome(cwd, cwd)
            copylink(cwd, binloc)
            loginst(cwd, cwd, binloc)
        else: sys.exit("Aborting pyFvwm installer!")
    else:
        print("    Install actions:  Copy pyFvwm's files and create link.")
        print("    pyFvwm install location:   {}".format(loc))
        print("    Binary link location:      {}".format(binloc))
        print("    Python3 Interpreter:       {}".format(python))
        confirm = input("Install pyFvwm using above information ([Y]/n)? ")
        if confirm.lower() in ["", " ", "y", "yes"]:
            print("Installing...")
            updatehome(loc, cwd)
            copypyfvwm(loc)
            copylink(loc, binloc)
            loginst(cwd, loc, binloc)
        else: sys.exit("Aborting pyFvwm installer!")
    sys.exit() 


#
#   python3 install.py
#
# Interactive install.
def userinst(loc, binloc, cwd):
    print("pyFvwm Interactive Installer!\n")
    print("Do you want to use the current directory ({})?".format(cwd))
    answer = input("Enter N to copy pyFvwm to another location (optional): [Y]/n? ")

    if answer.lower() in ["", " ", "y", "yes"]:
        ans = input("\nEnter in location to place binary link [{}]: ".format(binloc))
        if len(ans) > 1: binloc = ans
        confirminst("cwd", loc, binloc, cwd)
    else:
        print("\nWhat directory do you want to copy pyFvwm to?")
        ans = input("Enter directory [{}]: ".format(loc))
        if len(ans) > 1: loc = ans
        print("\nWhere in your $PATH do you want to place a link?")
        ans = input("Enter directory [{}]: ".format(binloc))
        if len(ans) > 1: binloc = ans
        confirminst("install", loc, binloc, cwd)
        



#
#   python3 install.py uninstall
#
# Uninstall script. Right now only exports log info.
def uninstall(): pass




#
#   python3 install.py help
#
# Prints usage info for install and exits.
def help(*args):
    print("""pyFvwm install.py script:

    Usage: python3 install.py

Interactive install that prompts for install location and location of a
binary directory in $PATH to place a link to pyfvwm in.

    Usage: python3 install.py cwd [bin=path]

Updates pyFvwm's home directory to the current directory and places a link
in /usr/local/bin. Additional option bin=path sets the binary path. This
option only installs a link and leaves pyFvwm in its current location.

    Usage: python3 install.py loc=path [bin=path]

States the location and binary path to use. Location is required, binary path
is optional and defaults to /usr/local/bin if not set.""")
    sys.exit()

# Get command arguments
loc = "/usr/local/share/pyfvwm"
binloc = "/usr/local/bin"
cwd = os.getcwd()
if len(sys.argv) > 1:
    testcmd = sys.argv[1]
    if testcmd == "cwd":
        cmd = "cwd"
        if len(sys.argv) > 2 and sys.argv[2].startswith("bin="):
            binloc = sys.argv[2][4:]
    elif testcmd == "help": cmd = "help"
    elif testcmd == "uninstall": cmd = "uninstall"
    elif testcmd == "install": cmd="install"
    elif testcmd.startswith("loc="):
        cmd = "install"
        loc = testcmd[4:]
        if len(sys.argv) > 2 and sys.argv[2].startswith("bin="):
            binloc = sys.argv[2][4:]
    elif testcmd.startswith("bin="):
        cmd = "install"
        binloc = testcmd[4:]
        if len(sys.argv) > 2 and sys.argv[2].startswith("loc="):
            loc = sys.argv[2][4:]
        else: sys.exit("Input Error: bin={} option found but loc=path option missing.")
    else:
        sys.exit("Install Error: Invalid command: {}".format(testcmd))
else: userinst(loc, binloc, cwd)

if cmd == "help": help()
if cmd == "uninstall": uninstall()
confirminst(cmd, loc, binloc, cwd)
