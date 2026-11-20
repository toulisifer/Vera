# "Máy sạch" để kiểm tra tái lập: Ubuntu 24.04 trống + đúng các gói README yêu cầu.
# GCC của Ubuntu 24.04 là 13.3.0, cùng phiên bản dùng để build corpus chính thức.
# Dùng qua repro/run.sh (không chạy tay).
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 PYTHONIOENCODING=utf-8
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libc6-dev binutils make git python3 python3-venv ca-certificates docker.io \
    && rm -rf /var/lib/apt/lists/*
RUN git config --global --add safe.directory '*'
WORKDIR /src
