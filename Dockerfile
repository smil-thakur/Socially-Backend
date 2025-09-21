# ------------------------
# Minimal FastAPI + LaTeX
# ------------------------
FROM python:3.12-slim

# Install minimal TeX Live + dependencies for tlmgr
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

# Set up tlmgr in user mode and install extra LaTeX packages
RUN tlmgr init-usertree && \
    tlmgr install latex-bin xcolor geometry amsmath hyperref fontspec preprint enumitem titlesec marvosym

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port (Render sets $PORT automatically)
ENV PORT 10000

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]