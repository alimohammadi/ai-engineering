FROM ghcr.io/astral-sh/uv:python3.9.6-bookworm-slim

WORKDIR /app


# Enable bytecode compilation and Python optimization
ENV PYTHONOPTIMIZE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONPATH="/app/apps/chatbot_ui/src:$PYTHONPATH"

# Copy workspace root files for dependency resolution
COPY pyproject.toml uv.lock ./

# Install dependencies including workspace packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev 

COPY src ./src/

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Create non-root user and set permissions
RUN addgroup --system app && \
    adduser --system --ingroup app app && \
    chown -R app:app /app && \
    mkdir -p /home/app && \
    chown -R app:app /home/app && \
    mkdir -p /home/app/.streamlit && \
    mkdir -p /home/app/.streamlit/data && \
    mkdir -p /home/app/.streamlit/cache && \
    chown -R app:app /home/app/.streamlit

# Set home directory for the user
ENV HOME=/home/app

# Switch to non-root user
USER app

# Expose the Streamlit port
EXPOSE 8501

# WORKDIR /app/apps/chatbot_ui/src

# Command to run the application
CMD ["streamlit", "run", "chatbot_ui/app.py", "--server.address=0.0.0.0"]