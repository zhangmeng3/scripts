#!/usr/bin/expect
#/bin/bash
workspace=$1
cd $workspace
pwd
. build/envsetup.sh
expect "yes/no"
send "yes\n"
normal
