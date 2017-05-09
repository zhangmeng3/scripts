#!/usr/bin/expect
set versionIndex [lindex $argv 0]
set deviceId [lindex $argv 1]
set normalWorkspace [lindex $argv 2]
set planName [lindex $argv 3]
set sessionId [lindex $argv 4]
spawn bash _normal.sh $normalWorkspace
expect "]"
send "${versionIndex}\n"
expect ">"
send "add subplan --name ${planName} -s ${sessionId} --result-type failed\n"
expect ">"
send "run cts -s ${deviceId} --subplan  ${planName} --disable-reboot  --skip-preconditions\n"
expect "Time:"
send "exit\n"
interact
