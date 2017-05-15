import os
import re
import sys
import time
import Command
import threading

class CTS:
    workspace = None
    deviceIdList = None
    version = None
    romUrl = None
    forceAbi = None
    global deviceIdList

    def __init__(self, workspace, devices, version, url, abi):
        self.workspace = workspace
        self.deviceIdList = devices
        self.version = version
        self.romUrl = url
        self.forceAbi = abi

    def run(self):
        if self.romUrl != None:
            tmpromFolder = self.downloadRom()
            flashAllAndGuideSettingsThreads = []
            for deviceId in self.deviceIdList:
                flashAllAndGuideSettingsThread = threading.Thread(target = self.flashAllAndInitDevice, args = (deviceId, tmpromFolder))
                flashAllAndGuideSettingsThread.start()
                flashAllAndGuideSettingsThreads.append(flashAllAndGuideSettingsThread)
            for thread in flashAllAndGuideSettingsThreads:
                thread.join()
            Command.run("rm -rf " + tmpromFolder)
            os._exit(0)
            time.sleep(200)

        #First test

        threads = []
        runCasesThread = threading.Thread(target = self.runCases, args = (True,))
        runCasesThread.start()
        threads.append(runCasesThread)
        for thread in threads:
            thread.join()

        #Second test
        #Command.adbReboot(self.deviceIdList[0])
        time.sleep(10)
        runCasesThread = threading.Thread(target = self.runCases, args = (False,))
        runCasesThread.start()
        runCasesThread.join()

        #Third test
        #Command.adbReboot(self.deviceIdList[0])
        time.sleep(10)
        runCasesThread = threading.Thread(target = self.runCases, args = (False,))
        runCasesThread.start()
        runCasesThread.join()

        print "\n-------------DONE--------------\n"

    def downloadRom(self):
        tmpRomFolder = os.path.join(self.workspace, time.strftime("%H%M%S", time.localtime(time.time())))
        os.mkdir(tmpRomFolder)
        tmpRomFile = os.path.join(tmpRomFolder, "rom.tar.gz")
        os.system("curl " + self.romUrl + " -o " + tmpRomFile)
        os.system("tar -zxvf " + tmpRomFile + " -C " + tmpRomFolder)
        return tmpRomFolder

    def flashAllAndInitDevice(self, deviceId, romFolder):
        #Flash all
        flashAllScript = None
        for dirPath,dirNames,fileNames in os.walk(romFolder):
            for fileName in fileNames:
                if fileName == "flash_all_except_storage.sh":
                    flashAllScript = os.path.join(dirPath, fileName)
                    break;
        if flashAllScript == None:
            return None
        Command.adbRebootBootloader(deviceId)
        os.system("/bin/bash " + flashAllScript + " -s " + deviceId)
        Command.waitAndSetAdbDebugOn(deviceId)
        time.sleep(30)
        #Init device
        print "run guide settings by uiautomator, "
        #jar = os.path.join(self.workspace, "scripts/cts.jar")
        #Command.adbPush(deviceId, jar, "/data/local/tmp/")
        #Command.runUiautomatorCase(deviceId, "xxxxSettings")
        #--------------
        # doing
        #--------------

    def runCases(self, firstTime = True):
        qctsFolder = os.path.join(self.workspace, "qcts")
        scriptsFolder = os.path.join(self.workspace, "scripts")
        versionIndex = self.getCaseIndex(qctsFolder)

        #Run cts
        os.chdir(scriptsFolder)
        if firstTime is True:
            shardsValue = 0
            deviceIdsAndAbi = ""
            for deviceId in self.deviceIdList:
                deviceIdsAndAbi += "-s " + deviceId + " "
                shardsValue += 1
            deviceIdsAndAbi = deviceIdsAndAbi.strip()
            if self.forceAbi == "32":
                deviceIdsAndAbi += " --force-abi 32"
            elif self.forceAbi == "64":
                deviceIdsAndAbi += " --force-abi 64"
            #First loop
            print "./_expect.sh " + str(versionIndex) + " \""\
                 + deviceIdsAndAbi + "\" " + qctsFolder

            if self.version.startswith("6"):
             Command.run("./_expect6.sh " + str(versionIndex) + " \""\
                 + deviceIdsAndAbi + "\" " + qctsFolder + " " + str(shardsValue))
            elif self.version.startswith("7"):
             Command.run("./_expect7.sh " + str(versionIndex) + " \""\
                 + deviceIdsAndAbi + "\" " + qctsFolder + " " + str(shardsValue))
            else:
             Command.run("./_expect.sh " + str(versionIndex) + " \""\
                 + deviceIdsAndAbi + "\" " + qctsFolder + " " + str(shardsValue))
        else:
            shardsValue = 0
            deviceIdsAndAbi = ""
            for deviceId in self.deviceIdList:
                deviceIdsAndAbi += "-s " + deviceId + " "
                shardsValue += 1
            deviceIdsAndAbi = deviceIdList[0]
            if self.forceAbi == "32":
                deviceIdsAndAbi += " --force-abi 32"
            elif self.forceAbi == "64":
                deviceIdsAndAbi += " --force-abi 64"
            #Second Loop
            planName = self.getCtsTestPlanName()
            sessionId = self.getSessionId()
            if self.version.startswith("6"):
             Command.run("./__expect6.sh " + str(versionIndex) + " \""\
                 + deviceIdsAndAbi + "\" " + qctsFolder + " "  + planName + " " + str(sessionId))
            #elif self.version.startswith("7"):
            # Command.run("./__expect7.sh " + str(versionIndex) + " \"" \
            #     + deviceIdsAndAbi + "\" " + qctsFolder + " " + str(shardsValue))
            elif self.version.startswith("7"):
             Command.run("./__expect7.sh " + str(versionIndex) + " \"" \
                 + deviceIdsAndAbi + "\" " + qctsFolder + " " +  str(sessionId))
            else:
             Command.run("./__expect.sh " + str(versionIndex) + " \""\
                 + deviceIdsAndAbi + "\" " + qctsFolder + " " + planName + " " + str(sessionId))

    def getCaseIndex(self, qctsFolder):
        os.chdir(qctsFolder)
        Command.run("git pull .")
        envsetupScript = open(os.path.join(qctsFolder, "build/envsetup.sh"))
        deviceVersions = []
        AddLunchComboStartKeyword = "add_lunch_combo android-"
        try:
            envsetupScriptLines = envsetupScript.read()
            deviceVersions = re.findall(AddLunchComboStartKeyword + "\S*", envsetupScriptLines)
        finally:
            envsetupScript.close()
        versionIndex = 0
        while versionIndex < len(deviceVersions):
            if(deviceVersions[versionIndex].find(self.version) > -1):
                break
            versionIndex += 1
        return versionIndex + 1

    def getCtsTestPlanName(self):
        return "PN_" + time.strftime("%m%d%H%M%S", time.localtime(time.time()))

    def getSessionId(self):
        if self.version.startswith("7"):
         ctsReportsFolder = os.path.join(self.workspace, "qcts/google/cts", self.version, "android-cts/results")
        else:
         ctsReportsFolder = os.path.join(self.workspace, "qcts/google/cts", self.version,  "android-cts/repository/results")
        reportZipList = []
        for report in os.listdir(ctsReportsFolder):
            if report.endswith(".zip"):
                deviceId = Command.getDeviceIdFromResultZip(os.path.join(ctsReportsFolder, report))
                if deviceId != None:
                    reportZipList.append(report + "-" + deviceId)
        reportZipList.sort(cmp=lambda x,y: cmp(x.lower(), y.lower()), reverse = True)
        count = 0
        for rz in reportZipList:
            matchAllDeviceIds = True
            for deviceId in deviceIdList:
                if rz.find(deviceId) < 0:
                    matchAllDeviceIds = False
                    break
            if matchAllDeviceIds is True:
                break
            count += 1
        return len(reportZipList) - count - 1


#command line : python CTS.py --id deviceid1,deviceid2,,,deviceidn --version version --abi 32,64 --url rom_url
if __name__ == "__main__":
    #Command line arguments
    if len(sys.argv) == 1:
        print "Arguments format as follow:"
        print "    python CTS.py --id deviceid1,deviceid2,,,deviceidn --version version --abi 32,64 --url rom_url"
        os._exit(0)
    argvDict = {"devices" : None, "version" : None, "abi" : None, "romUrl" : None}
    commandLineArguments = "#".join(sys.argv[1:]).split("--")
    arguments = ""
    for argv in commandLineArguments:
        keyValue = argv.split("#")
        if len(keyValue) < 2:
            continue
        if keyValue[0] == "id":
            argvDict["devices"] = keyValue[1]
            arguments += "[deviceids] : " + argvDict["devices"] + "\n"
        elif keyValue[0] == "version":
            argvDict["version"] = keyValue[1]
            arguments += "[ version ] : " + argvDict["version"] + "\n"
        elif keyValue[0] == "abi" and (keyValue[1] == "32" or keyValue[1] == "64"):
            argvDict["abi"] = keyValue[1]
            arguments += "[force_abi] : " + argvDict["abi"] + "\n"
        elif keyValue[0] == "url":
            argvDict["romUrl"] = keyValue[1]
            arguments += "[ rom_url ] : " + argvDict["romUrl"] + "\n"
    print "-----------------\n" + arguments + "-----------------"
    if argvDict["devices"] == None:
        print "Error, missing parameter [device id], e.g. --id 3349dg2a"
        os._exit(0)
    if argvDict["romUrl"] == argvDict["version"] == None :
            print "Error, missing parameter [version], e.g. --version 4.4.4"
            os._exit(0)

    #Main body
    workspace = os.path.dirname(os.path.realpath(sys.path[0]))
    deviceIdList = []
    adbDevicesInfo = os.popen("adb devices").read()
    for deviceId in argvDict["devices"].split(","):
        if adbDevicesInfo.find(deviceId) < 0:
            print "Error, not found device [" + deviceId + "]"
            os._exit(0)
        deviceIdList.append(deviceId)
    CTS(workspace, deviceIdList, argvDict["version"], argvDict["romUrl"], argvDict["abi"]).run()
