#!/usr/bin/env python3

"""
version: 0.5

Скрипт позволяет делать автоматические бекапы виртуальных машин 
(через cron) в гипервизоре KVM размещенных на блочном устройстве LVM

lvm_command (lvcreate): 256M на каждый Gb раздела LVM.
lvm_command (lvdisplay): Allocated должен быть < 100%
"""

import os as terminal
import time as time_os

dev_lvm = ""
kvm_vm_os = ""
kvm_vm_name = ""
dir_backup = ""
dir_logs = ""

folder_backup = kvm_vm_name + "_" + kvm_vm_os + "_" + time_os.strftime("%d.%m.%Y")
touch_folder_src = dir_backup + folder_backup + "/" + kvm_vm_name + "-" + kvm_vm_os
touch_lvm_src = dev_lvm + kvm_vm_name

def returning_command(command):
    return terminal.popen(command).read()


returning_command("mkdir -p " + dir_backup + folder_backup + "/")


def virsh_command(command):
    terminal.popen("virsh domstate " + kvm_vm_name)
    terminal.popen("virsh save " + kvm_vm_name + " " + touch_folder_src + ".vmstate" + " --running")
    terminal.popen("virsh dumpxml " + kvm_vm_name + " > " + touch_folder_src + ".xml")
    terminal.popen("virsh domblklist " + kvm_vm_name + " --details")
    terminal.popen("virsh domblkinfo " + kvm_vm_name + " " + touch_lvm_src + " > " + touch_folder_src + "-raw_info")
    terminal.popen("virsh vol-pool " + touch_lvm_src + " >> " + touch_folder_src + "-raw_info")
    terminal.popen("echo " + touch_lvm_src + " >> " + touch_folder_src + "-raw_info")


def archive_creation(compression):
    terminal.popen("dd if=" + touch_lvm_src + "_snap" + " | gzip -ck -" + compression + " > " + touch_folder_src + ".gz")


def logs_creation(message):
    if terminal.path.isfile(dir_logs + kvm_vm_name + ".log"):
        access_type = "a"
    else:
        access_type = "w"
    
    with open(dir_logs + kvm_vm_name + ".log", access_type) as log:
        log.write("\n" + time_os.ctime() + " " + message)


def lvm_command(ratio):
    terminal.popen("lvcreate -s -n " + touch_lvm_src + "_snap -L" + ratio + "G " + touch_lvm_src)
    terminal.popen("lvremove " + touch_lvm_src + "_snap")  
    terminal.popen("lvdisplay " + touch_lvm_src + "_snap")
