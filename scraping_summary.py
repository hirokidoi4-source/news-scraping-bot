import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time

# ★重要：私はロボットではありません（ブラウザのふりをする設定）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ==========================================
#  【決定版】記事の要約を「Metaタグ」から取る関数
# ==========================================
def get_article_summary(article_url):
    """
    ニュースの詳細ページから、SEO用の「説明文（description）」を抜き出す
    """
    try:
        # headers（身分証）を提示してアクセス！
        res = requests.get(article_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # ★作戦変更：「クラス名」ではなく「Metaタグ」を探す
        # <meta name="description" content="ここに要約が入っている"> を狙い撃ち
        meta_desc = soup.find("meta", attrs={"name": "description"})
        
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]
        else:
            # 万が一Metaタグがない場合の保険（本文の最初のpタグ）
            p_tag = soup.select_one("article p") or soup.select_one("div p")
            if p_tag:
                return p_tag.text[:50] + "..." # 長すぎるので50文字で切る
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
    "政治", "政府", "首相", "国会", "内閣", "政党", "選挙", "知事", 
    "外交", "米軍", "中国", "韓国", "北朝鮮", "ロシア", "ウクライナ", "台湾",
    "経済", "円安", "株価", "物価", "増税", "賃上げ", "予算", 
    "教育", "少子化", "子育て", "環境", "エネルギー", "AI", "デジタル",
    "方針", "検討", "決定", "改正", "案", "批判", "問題", "逮捕", "容疑"
]

filename = "news_final_summary.csv" # ファイル名も新しくしました
seen_urls = [] 

with open(filename, mode="w", encoding="utf_8_sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["取得日時", "ジャンル", "タイトル", "URL", "キーワード", "要約"]) 

    print("--- ニュース収集ツアー（Metaタグ版）を開始します ---")

    for target_url in target_urls:
        print(f"\nジャンルページ移動中... {target_url}")
        time.sleep(1)
        
        try:
            # ここでも headers を使う
            response = requests.get(target_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            all_links = soup.find_all("a")

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

                    found_keyword = ""
                    for key in target_keywords:
                        if key in title:
                            found_keyword = key
                            break 

                    if found_keyword:
                        print(f"  Fetching... {title[:15]}...")
                        time.sleep(1) 
                        summary_text = get_article_summary(url)

                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        writer.writerow([now, genre, title, url, found_keyword, summary_text])
                        
                        print(f"  ★保存完了（{found_keyword}）")
                        seen_urls.append(url)
        
        except Exception as e:
            print(f"エラー: {e}")

print(f"\n--- 完了！ {filename} を確認してください ---")