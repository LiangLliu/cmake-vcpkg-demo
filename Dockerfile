FROM amd64/ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
            build-essential \
            curl \
            git \
            zip \
            wget \
            unzip \
            ca-certificates \
            gpg \
            gnupg \
            lsb-release \
            autoconf \
            python3 \
            patchelf \
            pkg-config \
            libtool && \
    apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN curl https://bootstrap.pypa.io/get-pip.py | python3 && \
    pip install pyelftools

# install camke https://apt.kitware.com/
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - \
          | tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main" \
            | tee /etc/apt/sources.list.d/kitware.list >/dev/null && \
    apt-get update && \
    apt-get install -y cmake && \
    apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-linux.zip  -O /tmp/ninja-linux.zip && \
    unzip /tmp/ninja-linux.zip -d /usr/local/bin/ && \
    update-alternatives --install /usr/bin/ninja ninja /usr/local/bin/ninja 1 --force && \
    rm /tmp/ninja-linux.zip

