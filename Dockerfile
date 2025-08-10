# Use the stable version of Debian as the base image
FROM debian:stable

# Set the working directory inside the container
WORKDIR /workspace


# Install necessary packages and dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    sudo \
    build-essential \
    libssl-dev \
    pkg-config \
    python3 \
    python3-dev \
    python3-pip \
    pipx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the source code into the container
COPY . /opt/giv

# Create a virtual environment and install Giv
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install /opt/giv

# Add the virtual environment's bin directory to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user and grant sudo privileges
RUN useradd -m -s /bin/bash nonroot \
    && echo "nonroot ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to the non-root user
USER nonroot

# Set the working directory for the non-root user
WORKDIR /workspace

# Set the default command to `giv`
ENTRYPOINT ["giv"]

# Allow interactive sessions to provide a shell
CMD ["/bin/bash"]
