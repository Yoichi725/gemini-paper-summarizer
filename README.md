# Gemini と Google Cloud Functions を用いた自動論文収集 & Slack通知ツール

Gemini API は2024年初頭まで無料らしいので使い勝手を見るがてらお試しで作成。

## 使い方

1. SlackのIncoming Webhook URL と Gemini API Key を取得 
2. `summarize_papers(webhook_url, api_key, {search_term})` を実行

## 実行結果

![result](slack_notify.png)
