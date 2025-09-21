FROM debian:bullseye-slim

# Install TeX Live minimal + manager
RUN apt-get update && apt-get install -y \
    texlive-base \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    texlive-xetex \
    texlive-science \
    && rm -rf /var/lib/apt/lists/*

# Optionally install extra packages via tlmgr
RUN tlmgr install latex-bin xcolor geometry amsmath hyperref fontspec preprint enumitem titlesec marvosym