FROM ubuntu:latest

ENV PYTHON=python3
ENV YCMS_PORT=8086
ENV YCMS_DEBUG=1

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

# Clone git repository (patient-to-room_assignment)
RUN mkdir -p /bed-management/ycms
RUN git clone https://github.com/TabeaBrandt/patient-to-room_assignment.git /bed-management/patient-to-room_assignment

# Setup patient-to-room-assignment algorithm
WORKDIR /bed-management/patient-to-room_assignment
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip install gurobipy

# Change ownership of patient-to-room-assignment repository
RUN chown -R 1000:1000 /bed-management/patient-to-room_assignment

# Copy entrypoint
WORKDIR /bed-management
COPY docker/dev/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

# Switch to a non-root user
USER ubuntu

ENTRYPOINT ["/bed-management/entrypoint.sh"]
