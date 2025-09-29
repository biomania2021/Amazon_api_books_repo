import numpy as np
import os
import time
import logging
from amazon_paapi import AmazonApi
import mysql.connector

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_env_vars():
    """環境変数から認証情報を取得"""
    try:
        return {
            'AMAZON_ACCESS_KEY': os.environ['AMAZON_ACCESS_KEY'],
            'AMAZON_SECRET_KEY': os.environ['AMAZON_SECRET_KEY'],
            'AMAZON_ASSOCIATE_TAG': os.environ['AMAZON_ASSOCIATE_TAG'],
            'AMAZON_ASSOCIATE_ID': os.environ['AMAZON_ASSOCIATE_ID'],
            'DB_USER': os.environ['DB_USER'],
            'DB_PASSWORD': os.environ['DB_PASSWORD'],
            'DB_HOST': os.environ['DB_HOST'],
            'DB_DATABASE': os.environ['DB_DATABASE']
        }
    except KeyError as e:
        logger.error(f"環境変数 {e} が設定されていません")
        raise

def connect_db(db_config):
    """MySQLデータベースに接続"""
    try:
        conn = mysql.connector.connect(
            user=db_config['DB_USER'],
            password=db_config['DB_PASSWORD'],
            host=db_config['DB_HOST'],
            database=db_config['DB_DATABASE']
        )
        logger.info("データベース接続成功")
        return conn
    except mysql.connector.Error as e:
        logger.error(f"データベース接続エラー: {e}")
        raise

def search_amazon_products(amazon, keyword, max_pages=5):
    """Amazon APIで書籍データを検索"""
    asins, titles = [], []
    for page in range(1, max_pages + 1):
        time.sleep(2)  # API制限対策
        try:
            products = amazon.search_items(
                keywords=keyword,
                search_index='Books',
                sort_by='NewestArrivals',
                item_page=page
            )
            if products and products.items:
                for product in products.items:
                    try:
                        asins.append(product.asin)
                        titles.append(product.item_info.title.display_value)
                        logger.info(f"取得成功: {product.item_info.title.display_value} (ASIN: {product.asin})")
                    except (AttributeError, TypeError):
                        logger.warning(f"商品情報取得失敗 (キーワード: {keyword}, ページ: {page})")
            else:
                logger.info(f"キーワード '{keyword}' のページ {page} で商品なし")
        except Exception as e:
            logger.error(f"検索エラー (キーワード: {keyword}, ページ: {page}): {e}")
    return asins, titles

def store_to_db(conn, titles, asins):
    """データベースにデータを保存"""
    cursor = conn.cursor()
    inserted_count = 0
    for title, asin in zip(titles, asins):
        try:
            cursor.execute("SELECT * FROM `amazon_all_data` WHERE `key` = %s", (asin,))
            if not cursor.fetchone():
                cursor.execute(
                    'INSERT INTO `amazon_all_data` VALUES (%s, %s, %s)',
                    (title, asin, asin)
                )
                cursor.execute(
                    'INSERT INTO `amazon_update_data` VALUES (%s, %s, %s)',
                    (title, asin, asin)
                )
                inserted_count += 1
                logger.info(f"データ挿入: {title} (ASIN: {asin})")
        except mysql.connector.Error as e:
            logger.error(f"データベース挿入エラー (ASIN: {asin}): {e}")
    conn.commit()
    logger.info(f"挿入件数: {inserted_count}")
    return inserted_count

def generate_affiliate_links(conn, associate_id):
    """アフィリエイトリンクを生成"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM `amazon_update_data`')
    rows = cursor.fetchall()
    link_template = '<a href="https://www.amazon.co.jp/dp/{}?tag={}&linkCode=osi&th=1&psc=1" target="_blank">{}</a><br>'
    affiliate_links = [link_template.format(asin, associate_id, title) for title, asin, _ in rows]
    return ''.join(affiliate_links)

def save_to_file(html_content, filename='affiliate_link_data.txt'):
    """HTMLリンクをファイルに保存"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'<br>新着書籍<br>{html_content}<br>')
        logger.info(f"リンクを {filename} に保存")
    except IOError as e:
        logger.error(f"ファイル保存エラー: {e}")
        raise

def main():
    """メイン処理"""
    # 環境変数
    env_vars = load_env_vars()
    
    # Amazon API初期化
    amazon = AmazonApi(
        env_vars['AMAZON_ACCESS_KEY'],
        env_vars['AMAZON_SECRET_KEY'],
        env_vars['AMAZON_ASSOCIATE_TAG'],
        country="JP"
    )
    
    # データベース接続
    conn = connect_db(env_vars)
    
    # 検索キーワード
    keywords = [
        '映画'
    ] # そのほかジャンル適宜追加
    
    # 書籍データ取得
    total_inserted = 0
    for keyword in keywords:
        asins, titles = search_amazon_products(amazon, keyword)
        inserted = store_to_db(conn, titles, asins)
        total_inserted += inserted
    
    # アフィリエイトリンク生成
    affiliate_links = generate_affiliate_links(conn, env_vars['AMAZON_ASSOCIATE_ID'])
    
    # ファイル保存
    save_to_file(affiliate_links)
    
    # 終了処理
    conn.close()
    logger.info(f"処理完了: {total_inserted} 件のデータを挿入")

if __name__ == "__main__":
    main()
