#!/usr/bin/env python3

"""
version: 0.9

Скрипт позволяет делать автоматические бекапы виртуальных машин (VM)
(через cron) в гипервизоре KVM размещенных на блочном устройстве LVM
"""

import os as terminal_os
import sys as system_py
import time as time_os

kvm_vm_os = ""
kvm_vm_name = ""
dir_backup = ""
dir_logs = ""

folder_backup = kvm_vm_name + "-" + kvm_vm_os + "_" + time_os.strftime("%d.%m.%Y")
touch_folder_src = dir_backup + folder_backup + "/" + kvm_vm_name + "-" + kvm_vm_os
touch_lvm_src = terminal_os.popen("virsh domblklist " + kvm_vm_name + " --details").read().split()


def returning_command(command):
    """ command: Выполняет комманду в терминале
        и возвращяет str() вывода комманды.
    """
    return terminal_os.popen(command).read()


def logs_creation(message):
    if terminal_os.path.isfile(dir_logs + kvm_vm_name + ".log"):
        access_type = "a"
    else:
        access_type = "w"
    
    with open(dir_logs + kvm_vm_name + ".log", access_type) as log:
        log.write("\n" + time_os.ctime() + " " + message)


def virsh_command():
    """ Остонавливает виртуальную машину (VM) и собирает информацию
        для ее восстановления из Backup по надобности в будущем.
    """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["работает"]:
        terminal_os.popen("virsh save " + kvm_vm_name + " " + touch_folder_src + ".vmstate --running").read()
        logs_creation("Process Create " + kvm_vm_name + ".vmstate --running ======>> Завершон!")
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["выключен"]:
        terminal_os.popen("virsh dumpxml " + kvm_vm_name + " > " + touch_folder_src + ".xml") 
        terminal_os.popen("virsh domblkinfo " + kvm_vm_name + " " + touch_lvm_src[8] + " > " + touch_folder_src + 
                       "-raw_info" + " && " + "virsh vol-pool " + touch_lvm_src[8] + " >> " + touch_folder_src + 
                       "-raw_info" + " && " + "echo " + touch_lvm_src[8] + " >> " + touch_folder_src + "-raw_info")


def virsh_restore():
    """ Запускает виртуальную машину (VM) из сохраненного ранее состояния """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["выключен"]:
        terminal_os.popen("virsh restore " + touch_folder_src + ".vmstate")
        logs_creation("Process Restore VM: Начат процесс восстановления состояния вертуальной машины!")
    else:
        logs_creation("Error Process Restore VM: Виртуальная машина не выключена, процесс восстановления прерван!")


def archive_creation(compression = 3):
    """ compression: Степень сжатия .gz файла от 1 до 9. Чем выше степень,
        тем больше нужно мощностей процессора и времени на создание архива.
    """
    terminal_os.popen("dd if=" + touch_lvm_src[8] + "_snap" + " | gzip -ck -" + str(compression) + " > " + touch_folder_src + ".gz").read()


def lvm_command(command, ratio = 2):
    """ command: (1) Создать LVM_Snap. (2) Удалить LVM_Snap. (3) Информация по LVM_Snap
        ratio: Размер таблицы(буфера), на каждые 8Gb LVM c VM нужно 256M. ratio=2(16Gb LVM) 
    """
    if command == "create":
        terminal_os.popen("lvcreate -s -n " + touch_lvm_src[8] + "_snap -L" + str(ratio*256) + "M " + touch_lvm_src[8]).read()
        logs_creation("LVM Create " + touch_lvm_src[8] + "_snap Size: " + str(ratio*256) + "M Target:" + touch_lvm_src[8])
    elif command == "remove":
        logs_creation(terminal_os.popen("lvdisplay " + touch_lvm_src[8] + "_snap").read())
        terminal_os.popen("lvremove -f " + touch_lvm_src[8] + "_snap")
        logs_creation("LVM Remove " + touch_lvm_src[8] + "_snap")


main()
def main():
    logs_creation("Start Process Backup VM: " + kvm_vm_name)
    returning_command("mkdir -p " + dir_backup + folder_backup + "/")
    logs_creation("Create Folder Backup VM: " + dir_backup + folder_backup)

    virsh_command()
    lvm_command("create", 3)
    virsh_restore()
    archive_creation(3)
    lvm_command("remove")
