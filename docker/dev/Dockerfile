FROM ubuntu:latest

ENV PYTHON=python3
ENV YCMS_PORT=8086
ENV YCMS_DEBUG=1

# Patient to room assignement algorithm
ARG USER=TabeaBrandt
ARG REPO=patient-to-room_assignment
ARG BRANCH=main

# Install packages
RUN apt-get update && apt-get install -y \
    npm \
    nodejs \
    python3 \
    python3-pip \
    python3-venv \
    git \
    netcat-traditional \
    gettext \
    pcregrep \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /bed-management/ycms /opt/gurobi

# Clone git repository (patient-to-room_assignment)
ADD https://api.github.com/repos/$USER/$REPO/git/refs/heads/$BRANCH version.json
RUN git clone -b $BRANCH https://github.com/$USER/$REPO.git /bed-management/patient-to-room_assignment

# Setup patient-to-room-assignment algorithm
WORKDIR /bed-management/patient-to-room_assignment
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip install gurobipy

# Change ownership of patient-to-room-assignment repository and gurobi folder
RUN chown -R 1000:1000 /bed-management/patient-to-room_assignment /opt/gurobi

# Copy scripts
WORKDIR /bed-management
COPY docker/dev/entrypoint.sh docker/dev/install_dependencies.sh docker/dev/translate.sh docker/dev/test.sh .
RUN chmod +x entrypoint.sh install_dependencies.sh translate.sh test.sh

# Switch to a non-root user
USER ubuntu

ENTRYPOINT ["/bed-management/entrypoint.sh"]
