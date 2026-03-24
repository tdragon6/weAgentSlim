FROM ubuntu:22.04

WORKDIR /root/workspace

RUN apt update && apt upgrade -y &&apt install -y --no-install-recommends \
    iputils-ping curl wget telnet iproute2 net-tools vim lsof unzip zip git jq python3-pip python3.10-venv ca-certificates gnupg ffmpeg \
    && pip3 install requests beautifulsoup4 scrapy openpyxl pandas python-docx pypdf numpy \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt update && apt upgrade -y \
    && apt install -y --no-install-recommends nodejs \
    && npm install -g npm@latest \
    && npm install -g agent-browser \
    && agent-browser install --with-deps \
    && wget https://github.com/anomalyco/opencode/releases/latest/download/opencode-linux-x64.tar.gz \
    && tar xzvf opencode-linux-x64.tar.gz && rm -r opencode-linux-x64.tar.gz \
    && chmod +x /root/workspace/opencode && mv /root/workspace/opencode /usr/local/bin/opencode \
    && npm install -g skills \
    && skills add -g -y https://github.com/vercel-labs/skills --skill find-skills \
    && skills add -g -y https://github.com/vercel-labs/agent-browser --skill agent-browser \
    # && apt clean && rm -rf /var/lib/apt/lists/* \
    && opencode stats

ENTRYPOINT ["opencode"]
