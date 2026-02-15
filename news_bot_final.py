import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time
import json
import os
from dotenv import load_dotenv

# ==========================================
#  【修正】 .envファイルを強制的に読み込む
# ==========================================

# 1. このPythonファイル（news_bot_final.py）がある場所を特定する
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. その場所にある ".env" ファイルのパスを作る
env_path = os.path.join(script_dir, '.env')

# 3. 指定したパスから読み込む！
load_dotenv(env_path)

# 4. URLを取り出す
discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

# デバッグ用：読み込めたか確認（URLの一部だけ表示する）
if discord_webhook_url:
    print(f"✅ .env読み込み成功！ URL: {discord_webhook_url[:10]}...")
else:
    print(f"❌ エラー： '{env_path}' に .envファイルが見つかりません！")
    print("ヒント：ファイル名が '.env.txt' になっていませんか？")
    exit()

# 私はロボットではありません（User-Agent）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
# ==========================================
#  関数1：Discordにメッセージを送る
# ==========================================
def send_to_discord(text):
    """
    Discordにメッセージを送信する関数
    """
    try:
        content = {"content": text}
        requests.post(
            discord_webhook_url,
            json=content,
            headers={'Content-Type': 'application/json'}
        )
        print("  📲 Discordに通知しました")
    except Exception as e:
        print(f"  ❌ 送信エラー: {e}")

# ==========================================
#  関数2：記事の要約を取ってくる
# ==========================================
def get_article_summary(article_url):
    try:
        res = requests.get(article_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Metaタグから要約を取得
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]
        
        # 保険：本文の最初のpタグ
        p_tag = soup.select_one("article p") or soup.select_one("div p")
        if p_tag:
            return p_tag.text[:50] + "..."
        return "要約なし"
    except Exception as e:
        return f"エラー: {e}"

# ==========================================
#  メイン処理
# ==========================================
target_urls = [
    "https://news.yahoo.co.jp/categories/domestic", 
    "https://news.yahoo.co.jp/categories/world",    
    "https://news.yahoo.co.jp/categories/business"  
]

target_keywords = [
    "政治", "政府", "首相", "国会", "選挙", "外交", "中国", "米国", "韓国", "北朝鮮",
    "ウクライナ", "経済", "株価", "円安", "増税", "賃上げ", "教育", "少子化", "AI",
    "事件", "逮捕", "方針", "検討", "決定"
]

filename = "news_discord.csv"
seen_urls = [] 

# ★最初に「開始の合図」をDiscordに送る
send_to_discord("🤖 **ニュース収集を開始します...**")

with open(filename, mode="w", encoding="utf_8_sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["取得日時", "ジャンル", "タイトル", "URL", "キーワード", "要約"]) 

    for target_url in target_urls:
        print(f"\n巡回中... {target_url}")
        time.sleep(1)
        
        try:
            response = requests.get(target_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            all_links = soup.find_all("a")

            # ジャンル判定
            genre = "その他"
            if "domestic" in target_url: genre = "国内"
            elif "world" in target_url: genre = "国際"
            elif "business" in target_url: genre = "経済"

            for link in all_links:
                title = link.text
                url = link.get("href")

                if title and len(title) > 10 and url and "pickup" in url:
                    if url in seen_urls:
                        continue

                    # キーワードチェック
                    found_keyword = ""
                    for key in target_keywords:
                        if key in title:
                            found_keyword = key
                            break 

                    if found_keyword:
                        print(f"  発見！ {title[:10]}...")
                        time.sleep(1) 
                        summary_text = get_article_summary(url)

                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        writer.writerow([now, genre, title, url, found_keyword, summary_text])
                        seen_urls.append(url)

                        # ★ここでDiscordにニュースを投稿！
                        # 見やすいようにフォーマットを整えます
                        message = (
                            f"**【{found_keyword}】 {title}**\n"
                            f"{summary_text}\n"
                            f"{url}\n"
                            f"----------------"
                        )
                        send_to_discord(message)
        
        except Exception as e:
            print(f"エラー: {e}")

# ★最後に「終了の合図」を送る
send_to_discord("🏁 **収集完了！お疲れ様でした。**")
print(f"\n--- 完了！Discordを確認してください ---")