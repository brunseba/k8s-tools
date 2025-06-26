FROM python:3.11-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-install-project --no-group dev --no-group test --no-group docs

FROM python:3.11-slim

# OCI-compliant labels
LABEL org.opencontainers.image.title="k8s-reporter" \
      org.opencontainers.image.version="0.7.3" \
      org.opencontainers.image.description="Kubernetes resource analyzer with relationship mapping" \
      org.opencontainers.image.authors="K8s Analyzer Team <team@example.com>" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.url="https://github.com/brunseba/k8s-analyzer" \
      org.opencontainers.image.documentation="https://your-org.github.io/k8s-analyzer" \
      org.opencontainers.image.source="https://github.com/brunseba/k8s-analyzer" \
      org.opencontainers.image.vendor="K8s Analyzer Team" \
      org.opencontainers.image.ref.name="k8s-analyzer:0.7.3"

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY src ./src
COPY README.md .
COPY LICENSE .

RUN uv pip install --no-deps .

# Need to be update with port parameters
ENTRYPOINT ["k8s-reporter"]

