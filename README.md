# openai_gpt_proxy telegram bot
Telegram bot with ChatGPT model by OpenAI 

How to run:

Clone repository:

```
TODO
git clone https://github.com/Flaeros/openai_gpt_proxy.git
cd openai_gpt_proxy
```

Create and activate environment:

```
python3 -m venv env
or
py -3.10 -m venv env
```

If you have Linux/macOS

```
source env/bin/activate
```

If you have windows

```
source env/scripts/activate
python -m pip install --upgrade pip
```

Install requirements in requirements.txt:

```
pip install -r requirements.txt
```

Create file 'tokens.env' in main repository then provide CHAT_GPT_API_KEY and TELEGRAM_BOT_TOKEN:

```
# in tokens.env file
TELEGRAM_BOT_TOKEN=
CHAT_GPT_API_KEY=
```

Run project:

```
python main.py
```
