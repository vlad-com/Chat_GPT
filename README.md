# Chat_GPT
Can respond to text and voice https://t.me/gpt_chat_5bot
## Install
### Clone repo:
```bash
git clone github.com/vlad-com/Chat_GPT/
cd Chat_GPT
```
### Install requirements:
```bash
pip install -r requirements.txt
```
### Set in environment: telegram api token [get here](https://t.me/BotFather), OpenAI api key [get here](https://platform.openai.com/account/api-keys), and if you need set webhook:
### Example in linux:
```bash
export TOKEN=53535:dgssdgASGgsasgagsasgasgg
export OPENAI_API_KEY=key12345
```
### Example in windows:
```bash
set TOKEN=53535:dgssdgASGgsasgagsasgasgg
set OPENAI_API_KEY=key12345
```
### If you need set webhook in windows:
```bash
set USE_WEBHOOK=1 #1==True
set BASE_WEBHOOK_URL=https://mywebhook.com
set WEBHOOK_PATH=/somebot/
set WEB_SERVER_HOST=0.0.0.0 #For ipv4 server
set WEB_SERVER_HOST=:: #For ipv6 server
set WEB_SERVER_PORT=8080 #Any usable port
```
### Run script
```bash
python main.py
```
### Generate images
To generate images you need subscription to ChatGPT Plus and set in evironment GPT-4 model `set MODEL=gpt-4`
