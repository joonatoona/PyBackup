#Import required libraries
from sys import exit, argv, path;

#Compensate for running from different directory
addir = '/'.join(argv[0].split('/')[:-1])+"/";
if addir == "/":
	addir = "";

path.append(addir+"libs/")
from guilib import *;
from time import time, strftime;
from os import system as cmd;

lBrTime = 0;
dbm = False;

#Checks if debug argument is passed
if len(argv) > 1 and argv[1] == "debug=true":
	dbm = True;

#Function for logging messages
def logMsg(msg, mType="INFO"):
	if mType == "DEBUG" and not dbm:
		return;
	print strftime("[%b %d|%H:%M:%S]["+mType+"] "+msg);

#Backup function
def backup(fPath, buPath="~/.PyBackups/"):
	buPath += fPath.replace("/", "").replace("~", "")+strftime("/%b-%d-%H-%M")+"/"; #Gets path to put backup in
	logMsg("Backing up "+fPath+" to "+buPath, "DEBUG"); #Debugging
	logMsg("Running command "+"mkdir -p "+buPath, "DEBUG"); #Debugging
	cmd("mkdir -p "+buPath) #Creates the directory if it doesn't already exists
	logMsg("Running command "+"cp -r "+fPath+" "+buPath, "DEBUG"); #Debugging
	cmd("cp -r "+fPath+" "+buPath) #Copies the files
	cmd("touch "+addir+"budata"); #Creates the backup data file if it doesn't already exist
	open(addir+"budata", "a").write("\n"+fPath+strftime(",%a-%b-%d-%H-%M")); #Appends the backup info to the data file

cmd("touch "+addir+"data"); #Creates the data file if it doesn't already exist

data = [i.split(',') for i in open(addir+"data").read().split('\n')]; #Reads the data file

print open(addir+"title").read(); #Reads the title file and prints it

logMsg("Daemon Started"); #Logging

#Config steps
if data[0][0] != "true":
	logMsg("Starting Configuration");
	msgbox("""
		It appears you haven't configured PyBackup yet!
		Follow these instructions to get started!
		(Keep in mind you can re-configure PyBackup using the config command)
	""", "PyBackup Config");
	path = diropenbox("""
		Select the directory you wish to keep backed up:
	""", "PyBackup Config");
	freq = integerbox("""
		How often do you wish to back up the file?
		(In minutes)
	""", "PyBackup Config")*60;
	logMsg("Configuration Completed");
	logMsg("Starting Config File Write");
	logMsg("Writing \"true\\n"+path+","+str(freq)+"\" to file", "DEBUG");
	open(addir+"data", "w").write("true\n"+path+","+str(freq));
	logMsg("Config File Writing Complete");
else:
	path = data[1][0];
	freq = int(data[1][1]);

while True:
	if int(time())%freq == 0 and int(time()) != lBrTime: #More efficient than time.sleep()
		lBrTime = int(time());
		logMsg("Starting Backup");
		backup(path);
		logMsg("Backup Completed");