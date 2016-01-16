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

dbm = False;
bupath = "~/.PyBackups/";
cmds = ["Add Directory", "Change Frequency", "Take Backup", "Restore Backup", "About", "Quit"];

def backup(buPath):
	fPath = diropenbox("""
		Select the directory you wish to back up:
	""", "PyBackup Client");
	buPath += fPath.replace("/", "").replace("~", "")+strftime("/%b-%d-%H-%M")+"/";
	logMsg("Backing up "+fPath+" to "+buPath, "DEBUG");
	logMsg("Running command "+"mkdir -p "+buPath, "DEBUG");
	cmd("mkdir -p "+buPath)
	logMsg("Running command "+"cp -r "+fPath+" "+buPath, "DEBUG");
	cmd("cp -r "+fPath+" "+buPath)
	cmd("touch "+addir+"budata");
	open(addir+"budata", "a").write("\n"+fPath+strftime(",%a-%b-%d-%H-%M"));

def resBackup(buPath):
	logMsg("Re-reading Backup Data")
	budata = [i.split(',') for i in open(addir+"budata").read().split('\n')][1:];
	butr = choicebox("Select A Backup to restore:", "PyBackup Client", [i[0]+" on "+' '.join(i[1].split('-')[:3])+" at "+':'.join(i[1].split('-')[3:]) for i in budata]);
	ptrb = "";
	for i in budata:
		if i[0]+" on "+' '.join(i[1].split('-')[:3])+" at "+':'.join(i[1].split('-')[3:]) == butr:
			ptrb = i[0]+"/";
			buPath += ptrb.replace("/", "").replace("~", "")+"/"+'-'.join(i[1].split('-')[1:])+"/"+i[0].split('/')[-1]+"/";
			break;
	logMsg("Running command cp -r "+buPath+" "+ptrb, "DEBUG");

def logMsg(msg, mType="INFO"):
	if mType == "DEBUG" and not dbm:
		return;
	print strftime("[%b %d|%H:%M:%S]["+mType+"] "+msg);

argvl = [];

if len(argv) > 1:
	argvl = [i.replace("-", "").split("=") for i in argv[1:]];

for i in argvl:
	if i[0] == "debug" and i[1] == "true":
		dbm = True;
	if i[0] == "bupath":
		bupath = i[1];

cmd("touch "+addir+"data");
cmd("touch "+addir+"budata");
data = [i.split(',') for i in open(addir+"data").read().split('\n')];
budata = [i.split(',') for i in open(addir+"budata").read().split('\n')];

print open(addir+"title").read();

logMsg("Client Started");

if data[0][0] != "true":
	logMsg("Config File Not Present, exiting", "ERROR");
	exit();

if len(budata) < 2:
	logMsg("Backup Data Not Present, Exiting", "ERROR");
	exit();

budata = budata[1:];

while True:
	cho = choicebox("Select A Command:", "PyBackup Client", cmds);
	if not cho or cho == "Quit":
		logMsg("Quitting Client");
		exit();
	elif cho == "About":
		msgbox("""
			PyBackup V1.0 by @joonatoona
			Automatically back up / restore any directory on your computer!
		""", "PyBackup Client");
	elif cho == "Restore Backup":
		logMsg("Selecting Backup To Restore");
		resBackup(bupath);
	elif cho == "Take Backup":
		if bupath:
			backup(bupath);
		else:
			backup();
	else:
		msgbox("""
			That feature is not currently implemented.
			Maybe next update?
		""", "PyBackup Client");