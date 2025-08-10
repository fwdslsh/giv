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
    python3.11 \
    python3.11-dev \
    python3-pip \
    pipx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the local source code into a more appropriate location
COPY . /opt/giv

# Install Giv globally from the local source
RUN pip install /opt/giv

# Add the Giv binary directory to the PATH
ENV PATH="$PATH:/root/.local/bin"

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
