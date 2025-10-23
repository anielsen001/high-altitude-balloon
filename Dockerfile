FROM ghcr.io/anielsen001/quarto-docker/quarto-16-texlive-python-julia:latest

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV JULIA_LOAD_PATH=".:$(JULIA_LOAD_PATH)"