import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time # ★追加：サーバーに優しくするための道具

# 1. 狙うURLを「リスト」にする（複数ページを巡回！）
target_urls = [
    "https://news.yahoo.co.jp/categories/domestic", # 国内
    "https://news.yahoo.co.jp/categories/world",    # 国際
    "https://news.yahoo.co.jp/categories/business"  # 経済
]

# 2. キーワードを強化（動詞や抽象的な言葉を追加）
target_keywords = [
    # 政治・行政
    "政治", "政府", "首相", "国会", "内閣", "政党", "選挙", "知事", "市長",
    # 国際・外交
    "外交", "米軍", "中国", "韓国", "北朝鮮", "ロシア", "ウクライナ", "台湾",
    # 経済・社会
    "経済", "円安", "株価", "物価", "増税", "賃上げ", "予算", "補助金",
    # 教育・小論文頻出テーマ
    "教育", "少子化", "子育て", "環境", "脱炭素", "エネルギー", "AI", 
    "デジタル", "医療", "介護", "年金", "差別", "ジェンダー",
    # ★ここがポイント！ニュースによく出る「動き」を表す言葉
    "方針", "検討", "決定", "改正", "案", "批判", "問題", "逮捕", "容疑"
]

filename = "politics_news_v2.csv"
seen_urls = [] 

with open(filename, mode="w", encoding="utf_8_sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["取得日時", "ジャンル", "タイトル", "URL", "キーワード"]) 

    print("--- ニュース収集ツアーを開始します ---")

    # ★URLリストをループで回す（ページをめくるイメージ）
    for target_url in target_urls:
        print(f"\nアクセス中... {target_url}")
        
        # サーバーへの負荷を減らすため、ページ移動のたびに1秒休む（マナー）
        time.sleep(1)
        
        try:
            response = requests.get(target_url)
            soup = BeautifulSoup(response.text, "html.parser")
            all_links = soup.find_all("a")

            # ジャンル名をURLから推測（表示用）
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
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        writer.writerow([now, genre, title, url, found_keyword])
                        print(f"  ★採用（{found_keyword}）: {title}")
                        seen_urls.append(url)
        
        except Exception as e:
            print(f"エラーが発生しました: {e}")

print(f"\n--- ツアー終了！ {filename} を確認してください ---")