#!/bin/bash
echo off > /sys/devices/system/cpu/smt/control
echo core >/proc/sys/kernel/core_pattern
