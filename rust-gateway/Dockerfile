# --- build stage ---
FROM rust:1.82-slim-bookworm AS builder

WORKDIR /app

# rdkafka links against librdkafka; cmake-build feature compiles it from
# source, so we need a C toolchain + cmake, not just the Rust toolchain.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY Cargo.toml ./
COPY src/ ./src/

RUN cargo build --release

# --- runtime stage ---
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 gatewayuser
COPY --from=builder /app/target/release/rust-gateway /usr/local/bin/rust-gateway
USER gatewayuser

ENV RUST_LOG=info

CMD ["/usr/local/bin/rust-gateway"]
