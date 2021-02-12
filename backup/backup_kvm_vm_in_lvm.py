#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 1.1с

Description: Скрипт позволяет делать автоматические бекапы виртуальных машин 
используя его в CRON для гипервизора KVM размещенных на блочном устройстве LVM.

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import sys as path_os
import time as time_os
import os as terminal_os
import subprocess as shell


dir_logs = "/var/log/"
kvm_vm_name, dev_lvm, size_snap, dir_backup = path_os.argv[1:]
folder_backup = kvm_vm_name + "_" + time_os.strftime("%d.%m.%Y")
touch_folder_src = dir_backup + folder_backup + "/" + kvm_vm_name


def main():
    performance_shell("mkdir -p {}{}/".format(dir_backup, folder_backup))
    logs_creation(["Start Process Backup Virtual Machine: {} {}{}".format(kvm_vm_name, dir_backup, folder_backup)])
    
    virsh_command()
    lvm_command("create", int(size_snap))
    virsh_restore()

    logs_creation(["#"*100])
    terminal_os._exit(0)


def logs_creation(messages):
    if terminal_os.path.isfile("{}{}.log".format(dir_logs, kvm_vm_name)):
        access_type = "a"
    else:
        access_type = "w"
    
    with open("{}{}.log".format(dir_logs, kvm_vm_name), access_type) as log:
        for message in messages:
            log.write("\n" + time_os.ctime() + " " + message)


def performance_shell(command, wait_shell = True):
    shell_os = shell.Popen(command, stdout=shell.PIPE, stderr=shell.PIPE, shell=True, executable="/bin/bash", universal_newlines=True)

    if wait_shell:
        shell_os.wait()
    
    output, errors = shell_os.communicate()
    if len(str(output)) != 0:
        logs_creation(str(output).splitlines())
    if len(str(errors)) != 0:
        logs_creation(str(errors).splitlines())


def virsh_command():
    """ Остонавливает виртуальную машину (VM) и собирает информацию
        для ее восстановления из Backup по надобности в будущем.
    """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["running"]:
        performance_shell("virsh save {} {}.vmstate --running".format(kvm_vm_name, touch_folder_src))
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["running"]:
        performance_shell("virsh dumpxml {} > {}.xml".format(kvm_vm_name, touch_folder_src))
        performance_shell("virsh domblkinfo {} {} > {}-raw_info && virsh vol-pool {} >> {}-raw_info && echo {} >> {}-raw_info".format(kvm_vm_name, dev_lvm, touch_folder_src, dev_lvm, touch_folder_src, dev_lvm, touch_folder_src))
    
    logs_creation(["Process Virsh Create: {}.vmstate --running and creation of auxiliary files VM!".format(kvm_vm_name)])


def lvm_command(command, ratio = 2):
    """ command: (create) Создать LVM_Snap. (remove) Удалить LVM_Snap.
        ratio: Размер таблицы(буфера), на каждые 8Gb LVM c VM нужно 256M.
        ratio=2 это 512M Snapshot для VM размером меньше чем 16Gb
    """
    if command == "create":
        performance_shell("sudo lvcreate -s -n {}_snap -L{}M {}".format(dev_lvm, str(ratio*256), dev_lvm))
        logs_creation(["LVM Snapshot Create: {}_snap Size: {}M Target: {}".format(dev_lvm, str(ratio*256), dev_lvm)])
    elif command == "remove":
        performance_shell("sudo lvremove -f {}_snap".format(dev_lvm))
        logs_creation(["LVM Snapshot Remove {}_snap".format(dev_lvm)])


def virsh_restore():
    """ Запускает виртуальную машину (VM) из сохраненного ранее состояния """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["running"]:
        logs_creation(["Start Process Restore Virtual Machine: {}.vmstate --running".format(kvm_vm_name)])
        performance_shell("virsh restore {}.vmstate".format(touch_folder_src))
        archive_creation()
    else:
        logs_creation(["Error Process Restore VM: The VM is not turned off, removing the folder with oriental information!"])
        performance_shell("rm -r {}{}/".format(dir_backup, folder_backup))
        lvm_command("remove")
        terminal_os._exit(1)


def archive_creation(compression = 3):
    """ compression: Степень сжатия .gz файла от 1 до 9. Чем выше степень,
        тем больше нужно мощностей процессора и времени на создание архива.
    """
    logs_creation(["Process GZIP LVM Snapshot: For disk recovery Virtual Machine " + kvm_vm_name])
    performance_shell("dd if={}_snap | gzip -ck -{} > {}.gz".format(dev_lvm, str(compression), touch_folder_src))

    logs_creation(["Allocated to LVM Snapshot: Allocated should be < 100% for performance Snapshot!"])
    performance_shell("sudo lvdisplay {}_snap".format(dev_lvm))

    lvm_command("remove")


if __name__ == '__main__':
    main()
