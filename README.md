# Fridge Manager

A Django web app to manage your refrigerator contents and get AI-powered recipe suggestions (Gemini, English & Japanese).

## Features

- Add, edit, and delete fridge items
- Suggest recipes using Gemini (English and Japanese)
- Save favorite recipes
- Temporary Gemini API key support at login

## Usage

1. **Install requirements:**
   ```
   pip install -r requirements.txt
   ```

2. **Set your Gemini API key:**
   - Option 1: Set `GEMINI_API_KEY` as an environment variable.
   - Option 2: Enter a temporary API key at login.

3. **Run migrations and start the server:**
   ```
   python manage.py migrate
   python manage.py runserver
   ```

4. **Access the app:**
   - Go to [http://localhost:8000](http://localhost:8000)

## Project Structure

- `fridge_manager/` (project root)
  - `refrigerator/` (main app: models, views, templates, static)
  - `requirements.txt`
  - `README.md`

---

# Fridge Manager（日本語）

冷蔵庫の中身を管理し、AI（Gemini）によるレシピ提案を受けられるDjango製Webアプリです。

## 主な機能

- 冷蔵庫アイテムの追加・編集・削除
- Geminiを使ったレシピ提案（日本語・英語対応）
- お気に入りレシピの保存
- レスポンシブUI・一時Gemini APIキー対応

## 使い方

1. **必要なパッケージをインストール：**
   ```
   pip install -r requirements.txt
   ```

2. **Gemini APIキーの設定：**
   - 環境変数 `GEMINI_API_KEY` を設定する
   - または、ログイン時に一時的なAPIキーを入力する

3. **マイグレーションとサーバー起動：**
   ```
   python manage.py migrate
   python manage.py runserver
   ```

4. **アプリにアクセス：**
   - [http://localhost:8000](http://localhost:8000) にアクセス

## 必要環境

詳細は `requirements.txt` を参照してください。