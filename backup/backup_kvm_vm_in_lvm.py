#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 1.2

Description: Скрипт позволяет делать автоматические бекапы виртуальных машин 
используя его в CRON для гипервизора KVM размещенных на блочном устройстве LVM.

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import time as time_os
import os as terminal_os
import argparse as parser
import subprocess as shell


help_parser = parser.ArgumentParser(description="KVM backup of Virtual Machines on the LVM block device")

help_parser.add_argument("vm_name", type=str, help="Example: srv4prod-vm")
help_parser.add_argument("lvm_dev", type=str,  help="Example: /dev/vg0/prod-vm")
help_parser.add_argument("-size_snap", type=int, default=2, help="Example: default=2 is 512M Snapshot for VMs less than 16Gb")
help_parser.add_argument("bakup_folder", type=str, help="Example: /var/backup/prod-vm/")

args_parser = help_parser.parse_args()
print(args_parser)

dir_logs = "/var/log/"
kvm_vm_name = args_parser.vm_name
dev_lvm = args_parser.lvm_dev
size_snap = args_parser.size_snap
dir_backup = args_parser.bakup_folder

folder_backup = kvm_vm_name + "_" + time_os.strftime("%d.%m.%Y")
touch_folder_src = dir_backup + folder_backup + "/" + kvm_vm_name


def main():
    performance_shell("mkdir -p {0}{1}/".format(dir_backup, folder_backup))
    logs_creation(["Start Process Backup Virtual Machine: {0} {1}{2}".format(kvm_vm_name, dir_backup, folder_backup)])
    
    virsh_command()
    lvm_command("create", int(size_snap))
    virsh_restore()

    logs_creation(["#"*120])
    terminal_os._exit(0)


def logs_creation(messages):
    if terminal_os.path.isfile("{0}{1}.log".format(dir_logs, kvm_vm_name)):
        access_type = "a"
    else:
        access_type = "w"
    
    with open("{0}{1}.log".format(dir_logs, kvm_vm_name), access_type) as log:
        for message in messages:
            log.write("\n" + time_os.ctime() + " " + message)


def performance_shell(command, wait_shell = True):
    shell_os = shell.Popen(command, stdout=shell.PIPE, stderr=shell.PIPE, shell=True, executable="/bin/bash", universal_newlines=True)

    if wait_shell:
        shell_os.wait()
    
    output, errors = shell_os.communicate()
    if len(str(output)) != 0:
        logs_creation(str(output.strip()).splitlines())
    if len(str(errors)) != 0:
        logs_creation(str(errors.strip()).splitlines())


def virsh_command():
    """ Остонавливает виртуальную машину (VM) и собирает информацию
        для ее восстановления из Backup по надобности в будущем.
    """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["работает"] :
        performance_shell("virsh save {0} {1}.vmstate --running".format(kvm_vm_name, touch_folder_src))
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["работает"]:
        performance_shell("virsh dumpxml {0} > {1}.xml".format(kvm_vm_name, touch_folder_src))
        performance_shell("virsh domblkinfo {0} {1} > {2}-raw_info && virsh vol-pool {1} >> {2}-raw_info && echo {1} >> {2}-raw_info".format(kvm_vm_name, dev_lvm, touch_folder_src))
    
    logs_creation(["Process Virsh Create: {0}.vmstate --running and creation of auxiliary files VM!".format(kvm_vm_name)])


def lvm_command(command, ratio = 2):
    """ command: (create) Создать LVM_Snap. (remove) Удалить LVM_Snap.
        ratio: Размер таблицы(буфера), на каждые 8Gb LVM c VM нужно 256M.
        ratio=2 это 512M Snapshot для VM размером меньше чем 16Gb
    """
    if command == "create":
        performance_shell("sudo lvcreate -s -n {0}_snap -L{1}M {0}".format(dev_lvm, str(ratio*256)))
        logs_creation(["LVM Snapshot Create: {0}_snap Size: {1}M Target: {0}".format(dev_lvm, str(ratio*256))])
    elif command == "remove":
        performance_shell("sudo lvremove -f {0}_snap".format(dev_lvm))
        logs_creation(["LVM Snapshot Remove {0}_snap".format(dev_lvm)])


def virsh_restore():
    """ Запускает виртуальную машину (VM) из сохраненного ранее состояния """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["работает"]:
        logs_creation(["Start Process Restore Virtual Machine: {0}.vmstate --running".format(kvm_vm_name)])
        performance_shell("virsh restore {0}.vmstate".format(touch_folder_src))
        archive_creation()
    else:
        logs_creation(["Error Process Restore VM: The VM is not turned off, removing the folder with oriental information!"])
        performance_shell("rm -r {0}{1}/".format(dir_backup, folder_backup))
        lvm_command("remove")
        terminal_os._exit(1)


def archive_creation(compression = 3):
    """ compression: Степень сжатия .gz файла от 1 до 9. Чем выше степень,
        тем больше нужно мощностей процессора и времени на создание архива.
    """
    logs_creation(["Process GZIP LVM Snapshot: For disk recovery Virtual Machine " + kvm_vm_name])
    performance_shell("dd if={0}_snap | gzip -ck -{1} > {2}.gz".format(dev_lvm, str(compression), touch_folder_src))

    logs_creation(["Allocated to LVM Snapshot: Allocated should be < 100% for performance Snapshot!"])
    performance_shell("sudo lvdisplay {0}_snap".format(dev_lvm))

    lvm_command("remove")


if __name__ == '__main__':
    main()
