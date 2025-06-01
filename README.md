# cursor_note_pipeline

## 概要
YAMLで管理されたプロジェクト一覧を、PythonスクリプトとSeleniumを用いてnote.comへ自動下書き投稿するパイプラインです。

- プロジェクト管理をYAMLで一元化
- Markdown変換・note.comへの自動投稿
- Seleniumによるブラウザ自動操作

---

## セットアップ
1. **Python 3.8以上**をインストール
2. 必要なパッケージをインストール

```sh
pip install selenium python-dotenv pyyaml webdriver-manager
```

3. **chromedriver.exeの手動ダウンロード・配置は不要です**
   - `webdriver_manager`が自動で適切なバージョンのchromedriverをダウンロード・セットアップします。
   - インターネット接続が必要です。

4. `.env` ファイルを作成し、以下を記載

```
NOTE_EMAIL=あなたのメールアドレス
NOTE_PASSWORD=あなたのパスワード
PROJECTS_YAML_PATH=./projects.yaml
CACHE_FILE=./yaml_note_cache.txt
```

---

## 使い方
1. `projects.yaml` を編集し、管理したいプロジェクト情報を記載
2. ターミナルで以下を実行

```sh
python selenium_note_draft.py
```

- note.comに自動でログインし、下書き記事が作成されます
- 重複投稿防止のため、キャッシュファイルで管理しています

---

## 依存パッケージ
- selenium
- python-dotenv
- pyyaml
- webdriver-manager

---

## ライセンス
MIT License

---

## 作者
- nyattoh
- GitHub: [nyattoh/cursor_note_pipeline](https://github.com/nyattoh/cursor_note_pipeline)
