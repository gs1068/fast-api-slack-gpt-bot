# Slack GPT Bot

## ディレクトリ構成

```
├── Dockerfile
├── Makefile
├── README.md
├── config
│   └── load_env.py
├── domain
│   ├── model
│   │   ├── gpt.py
│   │   ├── slack.py
│   │   └── spreadsheet.py
│   └── repository
│       ├── gpt.py
│       ├── slack.py
│       └── spreadsheet.py
├── infrastructure
│   ├── __init__.py
│   ├── gpt
│   │   └── gpt.py
│   ├── slack
│   │   └── slack.py
│   └── spreadsheet
│       └── spreadsheet.py
├── interfaces
│   ├── __init__.py
│   ├── gpt.py
│   └── slack.py
├── main.py
├── requirements.txt
├── router
│   ├── __init__.py
│   ├── gpt.py
│   ├── ping.py
│   └── slack.py
└── usecase
    ├── __init__.py
    ├── gpt.py
    └── slack.py
```

## インフラ構成

![インフラ構成](./images/001.jpg)

### 使用技術

- **言語**: Python(FastAPI)
- **API**:
  - Slack API
  - OpenAI GPT API
  - Google Spreadsheet API
- **インフラ**:
  - Docker
  - ECR
  - AWS App Runner
 

## Slack APP
OAuth & Permissions
- app_mentions:read
- channels:history
- channels:read
- chat:write
- groups:history
- groups:read
- im:history
- im:read
- im:write

Event Subscription
- app_mention
- message.im

## スプレッドシート
GCPでこのプロジェクトを作成し、credential.jsonを取得
プレッドシートの作成とActivityタブを作る

最終利用日時が変わると「一日のトークン使用量」がリセットされる。

![スプレッドシート](./images/002.jpg)

## 環境設定

### `.env` ファイル

以下の環境変数を設定してください。

```plaintext
SLACK_BOT_TOKEN="xoxb-xxxx-xxxx-xxxx-xxxx"
OPENAI_API_KEY="sk-xxxx-xxxx-xxxx-xxxx"
SPREADSHEET_ID="xxxx-xxxx-xxxx-xxxx-xxxx"
GOOGLE_CREDENTIALS_PATH="./credential.json"
```

GCP から取得した `credentials.json` ファイルを `./` ディレクトリに配置してください。
