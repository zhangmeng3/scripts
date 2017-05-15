#!/usr/bin/expect
set versionIndex [lindex $argv 0]
set deviceId [lindex $argv 1]
set normalWorkspace [lindex $argv 2]
set sessionId [lindex $argv 3]
spawn bash _normal.sh $normalWorkspace
expect "]"
send "${versionIndex}\n"
expect ">"
send "run cts -s ${deviceId} --retry  ${sessionId} --disable-reboot  --skip-preconditions\n"
expect "Time:"
send "exit\n"
interact