# Pull the Node.js Docker image:
FROM node:22-alpine

# Verify the Node.js version:
RUN node -v # Should print "v22.18.0".

# Verify npm version:
RUN npm -v # Should print "10.9.3".

# install python
RUN apk add --no-cache python3 py3-pip espeak-ng git

# Create a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# set working directory
WORKDIR /app

# copy npm files and install
COPY package*.json ./
RUN npm install --no-cache

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY patches/chat.js node_modules/minecraft_protocol/src/client/
COPY . .

CMD ["python3", "main.py"]
