#!/bin/bash
set -o errexit -o nounset -o pipefail

export DEBIAN_FRONTEND=noninteractive

# 基础系统更新
apt-get update -y

# 安装基本构建工具 - 使用Ubuntu 20.04自带的版本，避免PPA问题
apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    python3 \
    wget \
    curl \
    zip \
    ninja-build \
    fontconfig \
    libfontconfig1-dev \
    libglu1-mesa-dev

# 安装clang（用于可能的交叉编译）
apt-get install -y clang

# 验证安装
echo "=== 构建环境信息 ==="
gcc --version
g++ --version
python3 --version
ninja --version
echo "=== 准备完成 ==="