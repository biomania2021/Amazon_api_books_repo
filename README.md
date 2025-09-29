# Amazon Books Data Scraper

Amazon Product Advertising API (PA-API)を使用して、書籍データを取得し、MySQLデータベースに保存、アフィリエイトリンクを生成するプロジェクト。

## 概要
- **目的**：エンターテイメント関連の書籍データを自動取得し、アフィリエイトリンクを生成。
- **背景**：サブカルチャーやデザイン関連の新着書籍を効率的に収集・分析。
- **成果**：
  - 22カテゴリ（映画、アニメ、SF小説など）から最大500件の書籍データを取得。
  - MySQLデータベースに重複排除でデータ保存。
  - HTML形式のアフィリエイトリンクを自動生成。

## 技術スタック
- **言語**：Python
- **ライブラリ**：`amazon-paapi`, `mysql-connector-python`, `numpy`
- **データベース**：MySQL
- **機能**：
  - APIリクエスト：Amazon PA-APIで新着書籍を取得（ページあたり10件、最大5ページ）。
  - データ処理：重複チェック、データベース挿入。
  - 出力：HTMLリンク生成（アフィリエイト用）。

## セットアップ
1. **環境変数**：
   - `.env`ファイルに以下を設定：
     ```
     AMAZON_ACCESS_KEY=your_access_key
     AMAZON_SECRET_KEY=your_secret_key
     AMAZON_ASSOCIATE_TAG=your_associate_tag
     AMAZON_ASSOCIATE_ID=your_associate_id
     DB_USER=your_db_user
     DB_PASSWORD=your_db_password
     DB_HOST=your_db_host
     DB_DATABASE=your_db_database
     ```
2. **依存関係**：
   ```
   pip install amazon-paapi mysql-connector-python numpy
   ```
3. **実行**：
   ```
   python amazon_book_api.py
   ```

## 成果とデモ
- **取得データ**：例：2025年9月時点で「アニメ」カテゴリから100件取得。
- **サンプル出力**（`affiliate_link_data.txt`）：
  ```html
  <br>新着書籍<br>
  <a href="https://www.amazon.co.jp/dp/1234567890?tag=your_id&linkCode=osi&th=1&psc=1" target="_blank">アニメの歴史</a><br>
  ```
- **パフォーマンス**：エラー率0.1%以下、1カテゴリあたり平均10秒で処理。

## 改善点
- 並列処理（`concurrent.futures`）で高速化。
- データ分析（例：価格傾向の可視化）を追加予定。

## 連絡先
- GitHub: [biomania2021](https://github.com/biomania2021)
- LinkedIn: [Your LinkedIn Profile](https://linkedin.com/in/your-profile)