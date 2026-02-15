import requests
import json

# 1. さっきコピーしたURLをここに貼る
webhook_url = "https://discord.com/api/webhooks/1471669700688744459/bW4WeVoe1McX-0dW6mBtv3fPTNbVwqva6QdNxbEqsOltNKKKOk5Xr2XLYpfBGho0_sCJ"

# 2. 送りたいメッセージ
content = {
    "content": "先生！PythonからDiscordへのテスト送信です！🎉\n改行もできますよ！"
}

# 3. 送信！（requests.post を使います）
# headers={'Content-Type': 'application/json'} は「JSON形式で送るよ」という合図
response = requests.post(
    webhook_url,
    json=content,
    headers={'Content-Type': 'application/json'}
)

# 4. 結果確認
if response.status_code == 204:
    print("送信成功！Discordを見てください！")
else:
    print(f"失敗... エラーコード: {response.status_code}")