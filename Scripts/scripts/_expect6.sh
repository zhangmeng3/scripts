#!/usr/bin/expect
set versionIndex [lindex $argv 0]
set deviceIdList [lindex $argv 1]
set normalWorkspace [lindex $argv 2]
set shardsValue [lindex $argv 3]
spawn bash _normal.sh $normalWorkspace
expect "]"
send "${versionIndex}\n"
expect ">"
send "run cts ${deviceIdList} --plan 6.0CTS --shards ${shardsValue} --disable-reboot --skip-preconditions\n"
expect "Time:"
send "exit\n"
interact



