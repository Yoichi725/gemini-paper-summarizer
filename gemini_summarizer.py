import os
import arxiv
from datetime import datetime, timedelta
import requests
import json
import pytz
import google.generativeai as genai

def load_config():
    # gemini-api と slack-webhook の呼び出し
    slack_webhook_url = os.getenv("SLACK_WEB_HOOK_URL")
    gemini_pro_api_key = os.getenv("GEMINI_PRO_API_KEY")
    return slack_webhook_url, gemini_pro_api_key

def search_arxiv(weeks, search_terms, max_results=10):
    # {weeks}週間分の論文を検索
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    past_date = now - timedelta(weeks=weeks)
    now_str = now.strftime("%Y%m%d%H%M%S")
    past_date_str = past_date.strftime("%Y%m%d%H%M%S")

    search = arxiv.Search(
        query=f"{search_terms} AND submittedDate:[{past_date_str} TO {now_str}]",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    return search.results()

def slack_notify(webhook_url, text):
    requests.post(webhook_url, data=json.dumps({
        'text': f'{text}',
        'username': u'GeminiSummarizerBot',
        'icon_emoji': u':bookmark_tabs:',
        'link_names': 1,
    }))

def summarize_papers(webhook_url, api_key, search_terms="%22Additive Manufacturing%22"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    template = """
    # 命令文
        以下の論文を30字程度の5つの要点に要約し、日本語に直してください。また、解答形式に則って回答してください。
            
    # 論文タイトル
        {title}

    # 論文概要
        {summary}

    # 解答形式
    ============================================================
    日本語タイトル：「{title} (Translate to Japanese)」
    URL: {url}
    Published Date: {date}
    ============================================================
    要点1: 「要点1」
    要点2: 「要点2」
    要点3: 「要点3」
    要点4: 「要点4」
    要点5: 「要点5」
    """

    results = search_arxiv(1, search_terms) # arxivで論文検索

    if not results:
        print("No results found")
        slack_notify(webhook_url, "No results found")

    for text in results:
        title = text.title
        summary = text.summary.replace('\n', ' ')
        url = text.entry_id
        date = text.published

        response = model.generate_content(
            template.format(title=title, summary=summary, url=url, date=date)
            )

        slack_notify(webhook_url, f'```{response.text}```')
        print("Slack notification sent...")

def main():
    webhook_url, api_key = load_config()
    summarize_papers(webhook_url, api_key, "%22Additive Manufacturing%22")
