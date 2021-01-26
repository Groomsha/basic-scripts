#!/usr/bin/env python3

"""
version: 0.6

Скрипт позволяет делать автоматические бекапы виртуальных машин 
(через cron) в гипервизоре KVM размещенных на блочном устройстве LVM

lvm_command (lvcreate): 256M на каждый Gb раздела LVM.
lvm_command (lvdisplay): Allocated должен быть < 100%
"""

import os as terminal
import time as time_os

touch_lvm_src = []
dev_lvm = ""
kvm_vm_os = ""
kvm_vm_name = ""
dir_backup = ""
dir_logs = ""

check_creation = True
folder_backup = kvm_vm_name + "_" + kvm_vm_os + "_" + time_os.strftime("%d.%m.%Y")
touch_folder_src = dir_backup + folder_backup + "/" + kvm_vm_name + "-" + kvm_vm_os


def returning_command(command):
    return terminal.popen(command).read()


def logs_creation(message):
    if terminal.path.isfile(dir_logs + kvm_vm_name + ".log"):
        access_type = "a"
    else:
        access_type = "w"
    
    with open(dir_logs + kvm_vm_name + ".log", access_type) as log:
        log.write("\n" + time_os.ctime() + " " + message)


def virsh_command():
    touch_lvm_src = terminal.popen("sudo virsh domblklist " + kvm_vm_name + " --details").read().split()

    if terminal.popen("sudo virsh domstate " + kvm_vm_name).read().split() == ["работает"]:
        terminal.popen("sudo virsh save " + kvm_vm_name + " " + touch_folder_src + ".vmstate" + " --running")
    elif terminal.popen("sudo virsh domstate " + kvm_vm_name).read().split() == ["выключен"]:
        terminal.popen("sudo virsh dumpxml " + kvm_vm_name + " > " + touch_folder_src + ".xml") 
        terminal.popen("sudo virsh domblkinfo " + kvm_vm_name + " " + touch_lvm_src[8] + " > " + touch_folder_src + 
                       "-raw_info" + " && " + "sudo virsh vol-pool " + touch_lvm_src[8] + " >> " + touch_folder_src + 
                       "-raw_info" + " && " + "echo " + touch_lvm_src[8] + " >> " + touch_folder_src + "-raw_info")
    

def archive_creation(compression):
    return terminal.popen("sudo dd if=" + touch_lvm_src + "_snap" + " | gzip -ck -" + str(compression) + " > " + touch_folder_src + ".gz").read()


def lvm_command(ratio):
    terminal.popen("sudo lvcreate -s -n " + touch_lvm_src + "_snap -L" + str(ratio) + "G " + touch_lvm_src)
    #terminal.popen("sudo lvremove " + touch_lvm_src + "_snap")  
    return terminal.popen("sudo lvdisplay " + touch_lvm_src + "_snap").read()


returning_command("mkdir -p " + dir_backup + folder_backup + "/")
#virsh_command()
lvm_command(4)
#print(archive_creation(3))
#print(lvm_command(4))

