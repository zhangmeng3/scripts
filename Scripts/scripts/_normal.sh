#!/usr/bin/expect
#/bin/bash
export LANG="en_US.UTF-8"
workspace=$1
cd $workspace
pwd
. build/envsetup.sh
normal
