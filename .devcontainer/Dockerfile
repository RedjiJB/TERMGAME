ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Switch to non-root user
USER $USERNAME

# Set working directory
WORKDIR /workspaces/termgame

# Copy Python version file
COPY .python-version .python-version

# Default command
CMD ["/bin/bash"]
