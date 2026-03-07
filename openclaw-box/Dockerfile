FROM node:22-bookworm-slim

ARG OPENCLAW_VERSION=0.70.0
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN npm install -g openclaw@${OPENCLAW_VERSION}

USER node
WORKDIR /home/node
