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

# Expose port (Render sets $PORT automatically)
ENV PORT 10000

# Start FastAPI with Uvicorn
CMD ["hypercorn", "main:app", "--bind", "::"]

