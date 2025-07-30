# Minecraft Bot

## CHAT BREAKING TEMP FIX
Can be found in the mineflayer repo
> A temporary fix i made is to replace the line at `minecraft-protocol\src\client\chat.js:61:114` with
> `const acknowledgements = previousMessages.length > 0 ? ['i32', previousMessages.length, 'buffer', Buffer.concat(previousMessages.map(msg => msg.signature || client._signatureCache[msg.id]).> filter(buf => Buffer.isBuffer(buf)))] : ['i32', 0]`

# Prerequisites
## Linux
1. First you will need nodejs 

`sudo apt install nodejs`

2. Now you need to install js module for python

`pip install javascript`

3. you'll also need the node package manager

`sudo apt install npm`

4. and you'll need the mineflayer package

`npm install mineflayer`

## macOS
1. Install homebrew if you haven't already

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

2. Install python modules

`pip install javascript`
`pip install discord`
`pip install discord.py[voice]`
`pip install python-dotenv`

3. Install nodejs and npm

`brew install node`

4. Install mineflayer package

`npm install mineflayer` 

