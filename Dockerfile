# syntax=docker.io/docker/dockerfile:1.4
FROM --platform=linux/riscv64 cartesi/python:3.10-slim-jammy

LABEL io.sunodo.sdk_version=0.2.0
LABEL io.cartesi.rollups.ram_size=128Mi

ARG MACHINE_EMULATOR_TOOLS_VERSION=0.12.0
RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends busybox-static=1:1.30.1-7ubuntu3 ca-certificates=20230311ubuntu0.22.04.1 curl=7.81.0-1ubuntu1.15
curl -fsSL https://github.com/cartesi/machine-emulator-tools/releases/download/v${MACHINE_EMULATOR_TOOLS_VERSION}/machine-emulator-tools-v${MACHINE_EMULATOR_TOOLS_VERSION}.tar.gz \
  | tar -C / --overwrite -xvzf -
rm -rf /var/lib/apt/lists/*
EOF

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libhdf5-dev libc-ares-dev libeigen3-dev \
    libatlas-base-dev libatlas3-base gfortran \
    libhdf5-serial-dev libopenblas-dev libblas-dev \
    liblapack-dev liblapacke-dev

ENV PATH="/opt/cartesi/bin:${PATH}"

WORKDIR /opt/cartesi/dapp
COPY ./requirements.txt .

# RUN docker pull tensorflow/tensorflow

# RUN pip install tensorflow


RUN <<EOF
pip install -r requirements.txt --no-cache-dir
find /usr/local/lib -type d -name __pycache__ -exec rm -r {} +
EOF

# RUN  docker run -it --rm tensorflow/tensorflow:2.3.0

COPY . .


ENV ROLLUP_HTTP_SERVER_URL="http://127.0.0.1:5004"

ENTRYPOINT ["rollup-init"]
CMD ["python3", "dapp.py"]
