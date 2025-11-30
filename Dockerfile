# -------------------------
# Stage 1: builder
# -------------------------
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build tools needed for some Python packages (kept in builder only)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency list and build wheels to speed up runtime image installs
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir -r requirements.txt -w /wheels


# -------------------------
# Stage 2: runtime
# -------------------------
FROM python:3.11-slim
ENV TZ=UTC
WORKDIR /app

# Install runtime system packages (cron, tzdata) and clean apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone to UTC explicitly
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone

# Copy prebuilt wheels and install Python packages from them (no network)
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Copy application code into image
COPY . /app

# Ensure required directories exist and set permissions
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Ensure cron file is readable and will be installed on container start
# (cron/2fa-cron should exist in repository root)
RUN chmod 0644 /app/cron/2fa-cron || true

# Expose the API port
EXPOSE 8080

# Start cron and uvicorn. We install crontab at container start and then run uvicorn.
# Use a simple shell invocation so both services start in foreground (cron runs as daemon).
CMD service cron start && crontab /app/cron/2fa-cron && uvicorn app.main:app --host 0.0.0.0 --port 8080
