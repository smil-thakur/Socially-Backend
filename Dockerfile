# ------------------------
# Minimal FastAPI + LaTeX
# ------------------------
FROM python:3.12-slim

# Install core LaTeX via apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    perl \
    texlive-base \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-latex-recommended \
    texlive-xetex \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Set up tlmgr in user mode and install full recommended sets
RUN tlmgr init-usertree && \
    tlmgr install collection-fontsrecommended collection-latexrecommended collection-latexextra

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Cloud Run automatically sets the PORT environment variable.
# Your application should listen on this port.
# Remove the explicit ENV PORT 10000 line.

# Start FastAPI with Uvicorn, binding to the PORT environment variable
CMD hypercorn main:app --bind 0.0.0.0:$PORT