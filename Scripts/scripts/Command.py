import os
import re
import sys
import time
import zipfile

def adbInstallApk(deviceId, apkPath):
    run("adb -s " + deviceId + " install -r " + apkPath)

def adbPush(deviceId, srcPath, targetPath):
    run("adb -s " + deviceId + " push " + srcPath + " " + targetPath)

def adbReboot(deviceId):
    time.sleep(3)
    run("adb -s " + deviceId + " reboot")
    time.sleep(30)
    while os.popen("adb -s " + deviceId + " get-state").read().find("device") < 0:
        time.sleep(5)
        print "wait for " + deviceId + "..."

def adbRebootBootloader(deviceId):
    run("adb -s " + deviceId + " reboot-bootloader")
    time.sleep(10)
    while os.popen("fastboot devices").read().find(deviceId) < 0:
        time.sleep(5)
        print "wait for " + deviceId + " bootloader..."

def waitAndSetAdbDebugOn(deviceId):
    print "wait device, set 'debug mode' on by mdb"
    #--------------
    # doing
    #--------------

def runUiautomatorCase(deviceId, className):
    run("adb -s " + deviceId + " shell uiautomator runtest cts.jar -c com.miui.test." + className)

def run(command):
    os.system(command)

def getDeviceIdFromResultZip(zipPath):
    resultZip = zipfile.ZipFile(zipPath, "r")
    testResultXml = None
    for filename in resultZip.namelist():
        if filename.endswith("test_result.xml"):
            testResultXml = filename
            break
    if testResultXml is not None:
        returns = re.findall('deviceID="[\w,]+"', resultZip.read(testResultXml))
        if len(returns) > 0:
            return returns[0].split('"')[1]
        else:
            return "unknown"
    return None

def getVersionAndRegion(deviceId):
    returnInfo = os.popen("adb -s " + deviceId + " shell getprop ro.miui.ui.version.name").read()
    return returnInfo.strip().upper()

def getDeviceDpi(deviceId):
    returnInfo = os.popen("adb -s " + deviceId + " shell dumpsys window windows").read()
    returns = re.findall('mScreenRect=\[0,0\]\[\d+,\d+\]', returnInfo)
    try:
        Dpis = returns[0].replace("mScreenRect=[0,0][", "").replace("]", "").split(",")
        Dpi = Dpis[1] + "x"+ Dpis[0]
    except:
        Dpi = "1920x1080"
    return Dpi