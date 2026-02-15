import requests
from bs4 import BeautifulSoup
import csv  # ★追加！CSV（Excel用ファイル）を扱う道具
import datetime # ★追加！今日の日付を入れるため

# 1. 準備
url = "https://news.yahoo.co.jp/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

seen_urls = [] 
all_links = soup.find_all("a")

# 2. ファイルを開く準備（ファイル名は 'yahoo_news.csv'）
# mode="w" は「書き込み(Write)」、encoding="utf_8_sig" は「文字化け防止（Excel用）」
with open("yahoo_news.csv", mode="w", encoding="utf_8_sig", newline="") as f:
    
    writer = csv.writer(f) # ペンを用意する
    
    # 3. 最初の行（見出し）を書く
    writer.writerow(["取得日時", "タイトル", "URL"]) # A1, B1, C1セルになる

    print("--- CSVファイルへの書き込みを開始します ---")

    for link in all_links:
        title = link.text
        url = link.get("href")

        if title and len(title) > 10 and url:
            if "news.yahoo.co.jp/pickup" in url:
                if url in seen_urls:
                    continue 

                # 4. データをファイルに書き込む
                # 今の時間も一緒に記録しちゃいましょう
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                
                writer.writerow([now, title, url]) # 1行書き込む！
                
                print(f"書き込み中... {title}")
                seen_urls.append(url)

print("--- 完了！フォルダを見てみてください！ ---")