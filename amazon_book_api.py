import numpy as np
import os
import time
from amazon_paapi import AmazonApi
import mysql.connector

# 環境変数から認証情報を取得する
AMAZON_ACCESS_KEY = os.environ['AMAZON_ACCESS_KEY']
AMAZON_SECRET_KEY = os.environ['AMAZON_SECRET_KEY']
AMAZON_ASSOCIATE_TAG = os.environ['AMAZON_ASSOCIATE_TAG']
country = "JP"

# AmazonAPIオブジェクトを作成する
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, country)

# MySQLデータベースへの接続
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_DATABASE = os.environ['DB_DATABASE']

conn = mysql.connector.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_DATABASE,
    auth_plugin='rd',  # 任意
    charset='',        # 任意
)
c = conn.cursor()

# AmazonアソシエイトのアソシエイトID
AMAZON_ASSOCIATE_ID = os.environ['AMAZON_ASSOCIATE_ID']

# 検索キーワードのリスト
KEYWORDS = ['映画', '特撮', 'アニメ', 'フィギュア', '漫画', 'コミック', '模型', '聖地巡礼', 'ライトノベル', '特撮技術', 'サブカルチャー', 'SF小説', 'ゲーム情報', 'アート・建築・デザイン', 'デザイン', 'エンターテイメント', 'ムック', 'ぴあMOOK', 'デアゴスティーニ', 'アシェット・コレクションズ・ジャパン', 'モデル・カーズ', 'ワンテーマ']

for m in KEYWORDS:
    ASIN = []
    TITLE = []

    for n in range(5):  # 最大5ページまで取得
        time.sleep(2)  # API制限対策
        try:
            products = amazon.search_items(keywords=m, search_index='Books', sort_by='NewestArrivals', item_page=n + 1)

            # products.itemsがNoneの場合の処理を追加
            if products and products.items:
                for product in products.items:
                    try:
                        ASIN.append(product.asin)
                        TITLE.append(product.item_info.title.display_value)
                    except AttributeError:
                        print(f"商品情報が取得できませんでした。ページ: {n+1}  キーワード: {m}")
                    except TypeError:
                        print(f"キーワード '{m}' のページ {n+1} で商品が見つかりませんでした。")
                        # 次のページまたはキーワードに進む
                        continue
            else:
                print(f"キーワード '{m}' のページ {n+1} で商品が見つかりませんでした。")
                continue
        except Exception as e:
            print(f"キーワード '{m}' のページ {n+1} でエラーが発生しました: {e}")
            continue

    for title, asin in zip(TITLE, ASIN):
        sql = "SELECT * FROM `amazon_all_data` WHERE `key` = %s"
        c.execute(sql, (asin,))
        fig = c.fetchone()
        print(fig)
        if not fig:  # データベースに存在しない場合のみ処理
            c.execute('INSERT INTO `amazon_all_data` VALUES (%s, %s, %s)', (title, asin, asin))
            c.execute('INSERT INTO `amazon_update_data` VALUES (%s, %s, %s)', (title, asin, asin))
            print("挿入されたデータを確認:")

            sql_select = "SELECT * FROM `amazon_update_data` WHERE `key` = %s"
            c.execute(sql_select, (asin,))
            inserted_row = c.fetchone()

if inserted_row:
    print(f"  挿入されたデータ: {inserted_row}")
else:
    print("  データの取得に失敗しました。")

# アフィリエイトリンクの生成
c.execute('SELECT * FROM `amazon_update_data`')
rows = c.fetchall()

A_link = '<a href="https://www.amazon.co.jp/dp/{}?tag={AMAZON_ASSOCIATE_ID}&linkCode=osi&th=1&psc=1" target="_blank">{}</a><br>'
Affiliate_links = [A_link.format(asin, title) for title, asin, _ in rows]

html_1 = '<br>新着書籍<br>' + ''.join(Affiliate_links) + '<br>'

with open('affiliate_link_data.txt', 'w') as f:
    f.write(html_1)

conn.commit()
conn.close()  # データベース接続を閉じる
