#!/bin/bash
set -e

CONFIG_PATH="/etc/krr"

echo "Step0: install packages"
add-apt-repository main
apt-get install -y make gcc libncurses5-dev dpkg-dev build-essential bison flex libssl-dev libelf-dev build-essential meson ninja-build pkg-config libglib2.0-dev libusb-1.0-0-dev libncursesw5-dev libpixman-1-dev libepoxy-dev libv4l-dev libpng-dev  libsdl2-dev libsdl2-image-dev libgtk-3-dev libgdk-pixbuf2.0-dev libasound2-dev libpulse-dev  libx11-dev python3-pyelftools linux-tools-common linux-tools-generic linux-tools-`uname -r` python3-pip
python3 -m pip install pandas psutil qemu.qmp matplotlib seaborn gdown

echo "Step1: compile KRR QEMU"
git submodule update --init --recursive
cd qemu-tcg-kvm;git checkout main;mkdir -p build;cd build;../configure --target-list=x86_64-softmmu; make -j$(nproc);./qemu-img create nkbypass.img 5G;mkfs.ext4 nkbypass.img;cd ../..

echo "Step2: compile KRR Kernel"
cp scripts/kernel_rr_config kernel-rr-linux/.config
cd kernel-rr-linux/;git checkout rr-para;make -j$(nproc);make modules_install;make install;cd ..

echo "Step3: configure environment"
sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="[^"]*/& intel_idle.max_cstate=0 intel_pstate=no_turbo=1 intel_iommu=on/' /etc/default/grub && sudo update-grub

mkdir -p ${CONFIG_PATH}

cp scripts/init.sh ${CONFIG_PATH}

INIT_PATH="${CONFIG_PATH}/init.sh"
sed "s|{init_path}|${INIT_PATH}|g" scripts/kernel-rr.service.tmpl > kernel-rr.service

cp kernel-rr.service /lib/systemd/system/
systemctl enable kernel-rr
cp scripts/rr_set_cpu_aff /usr/bin/

echo "Downloading disk and kernel image file"
gdown --id 1AZS0GGAnhfdZ8HSqpo0XlZBV-pI_VQkk
gzip -d rootfs-bypass.qcow2.gz

gdown --id 1cO0qMsqkReSKdHDZ1XC8r3-lT-ixJqfW
gdown --id 1q5MEQ1g7dSJAQQlV7hrMFv9ff6DHVWhN

echo "Setup finished, please reboot your machine to launch KRR kernel"
