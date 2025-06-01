#!/usr/bin/env python3
# selenium_note_draft.py

import os
import time
import datetime
import yaml
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ────────── 環境変数読み込み ──────────
load_dotenv()

NOTE_EMAIL = os.getenv("NOTE_EMAIL")
NOTE_PASSWORD = os.getenv("NOTE_PASSWORD")
PROJECTS_YAML_PATH = os.getenv("PROJECTS_YAML_PATH", "projects.yaml")
CACHE_FILE = os.getenv("CACHE_FILE", "yaml_note_cache.txt")

def load_yaml(path):
    """
    projects.yaml を読み込んで Python dict に変換する関数
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"YAML ファイルが見つかりません: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def format_markdown_from_yaml(data):
    """
    読み込んだ dict （YAML パース結果）を Markdown に変換する関数
    """
    today = datetime.date.today().isoformat()
    lines = [f"# プロジェクト一覧\n", f"_更新日: {today}_\n"]
    for block in data.get("projects", []):
        cat_name = block.get("category", "無名カテゴリ")
        items = block.get("items", [])
        lines.append(f"## {cat_name}\n")
        lines.append("| ID | プロジェクト名 | 状況 | 次のステップ |")
        lines.append("|----|--------------|------|-------------|")
        for p in items:
            pid = p.get("id", "")
            title = p.get("title", "")
            status = p.get("status", "")
            next_steps = p.get("next_steps", [])
            ns = "<br>".join(f"- {step}" for step in next_steps) if next_steps else ""
            lines.append(f"| {pid} | {title} | {status} | {ns} |")
        lines.append("")
    return "\n".join(lines)

def already_drafted(title):
    """
    重複投稿を防ぐチェック
    """
    if not os.path.exists(CACHE_FILE):
        return False
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == title:
                return True
    return False

def update_cache(title):
    """
    キャッシュファイルにタイトルを書き込む
    """
    with open(CACHE_FILE, 'a', encoding='utf-8') as f:
        f.write(title + "\n")

def main():
    # 1. YAML を読み込んで Markdown に変換
    print("[DEBUG] YAML 読み込み開始")
    try:
        data = load_yaml(PROJECTS_YAML_PATH)
        md_body = format_markdown_from_yaml(data)
        print("[DEBUG] YAML 読み込み＆Markdown 変換完了")
    except Exception as e:
        print(f"[ERROR] YAML の読み込みに失敗: {e}")
        return

    # 2. 下書きタイトルを生成 (例: "2025-06-02 プロジェクト一覧（下書き）")
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    title = f"{today_str} プロジェクト一覧（下書き）"
    print(f"[DEBUG] タイトルを生成: {title}")

    # 3. 重複チェック
    if already_drafted(title):
        print(f"[INFO] タイトル「{title}」はすでに投稿済みです。スキップします。")
        return
    print("[DEBUG] 重複チェック OK")

    # 4. Selenium の設定（headless Chrome）
    print("[DEBUG] Selenium オプション設定中")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # コメントアウトするとブラウザが表示されます
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    print("[DEBUG] ChromeDriverService 生成完了")

    driver = webdriver.Chrome(service=service, options=options)
    print("[DEBUG] Chrome を起動しました")

    try:
        # 5. note.com のログインページにアクセス
        print("[DEBUG] note.com ログインページにアクセス中...")
        driver.get("https://note.com/login")
        time.sleep(3)
        print("[DEBUG] ログインページ読み込み完了")

        # 6. メールアドレス入力 (id="email")
        email_xpath = "//input[@id='email']"
        print(f"[DEBUG] メール入力欄を探します: {email_xpath}")
        email_input = driver.find_element(By.XPATH, email_xpath)
        print("[DEBUG] メール入力欄 発見")
        email_input.clear()
        email_input.send_keys(NOTE_EMAIL)
        print("[DEBUG] メールアドレス入力完了")

        # 7. パスワード入力 (id="password")
        password_xpath = "//input[@id='password']"
        print(f"[DEBUG] パスワード入力欄を探します: {password_xpath}")
        pw_input = driver.find_element(By.XPATH, password_xpath)
        print("[DEBUG] パスワード入力欄 発見")
        pw_input.clear()
        pw_input.send_keys(NOTE_PASSWORD)
        print("[DEBUG] パスワード入力完了")

        # 8. ログインボタンをクリック (div.a-button__inner を使用)
        login_xpath = "//div[contains(@class,'a-button__inner') and (contains(text(),'ログイン') or contains(text(),'Log in'))]"
        print(f"[DEBUG] ログインボタンを探します: {login_xpath}")
        login_button = driver.find_element(By.XPATH, login_xpath)
        print("[DEBUG] ログインボタン 発見 → クリックします")
        login_button.click()
        time.sleep(5)  # ログイン後の遷移待機
        print("[DEBUG] ログイン後ページ読み込み完了")

        # 9. ログイン失敗チェック
        if "ログイン" in driver.title or "Log in" in driver.title:
            print("[ERROR] ログインに失敗しました。メールアドレス／パスワードを確認してください。")
            return
        print("[DEBUG] ログイン 成功")

        # 10. 「投稿」メニューを開き、「新しく記事を書く」をクリックして下書きページに移動
        print("[DEBUG] 「投稿」メニューを探しています")
        post_menu_xpath = "//button[@aria-label='投稿']"
        print(f"[DEBUG] 投稿メニューボタンXPath: {post_menu_xpath}")
        post_menu_button = driver.find_element(By.XPATH, post_menu_xpath)
        print("[DEBUG] 「投稿」メニュー 発見 → クリックします")
        post_menu_button.click()
        time.sleep(2)  # メニュー展開待機

        print("[DEBUG] 「新しく記事を書く」リンクを探しています")
        new_note_xpath = "//a[@href='/notes/new' and .//div[contains(text(),'新しく記事を書く')]]"
        new_note_link = driver.find_element(By.XPATH, new_note_xpath)
        print("[DEBUG] 「新しく記事を書く」リンク 発見 → クリックします")
        new_note_link.click()
        time.sleep(5)  # 下書き作成ページ読み込み待機
        print("[DEBUG] 下書き作成ページ読み込み完了")

        # 11. 下書きタイトルを入力 (textarea に変更)
        print("[DEBUG] タイトル入力欄を探します")
        title_field = driver.find_element(By.XPATH, "//textarea[@placeholder='記事タイトル' or @placeholder='Enter title']")
        print("[DEBUG] タイトル入力欄 発見 → 文字を入力")
        title_field.clear()
        title_field.send_keys(title)
        print("[DEBUG] タイトル入力完了")

        # 12. 本文（Markdown）を ProseMirror エディタに入力
        print("[DEBUG] ProseMirror エディタを探しています")
        editor_div = driver.find_element(By.XPATH, "//div[contains(@class,'ProseMirror')]")
        print("[DEBUG] エディタ 発見 → フォーカス＆Markdown を送信")
        editor_div.click()
        editor_div.send_keys(md_body)
        time.sleep(2)
        print("[DEBUG] Markdown の入力完了")

        # 13. 下書き保存ボタンをクリック
        print("[DEBUG] 下書き保存ボタンを探しています")
        save_xpath = "//button[.//span[contains(text(),'下書き保存')]]"
        save_button = driver.find_element(By.XPATH, save_xpath)
        print("[DEBUG] 下書き保存ボタン 発見 → クリックします")
        save_button.click()
        time.sleep(3)  # 保存完了待機
        print("[DEBUG] 下書き保存完了")

        # 14. キャッシュ更新
        print(f"[SUCCESS] note.com 上で下書き（{title}）を作成しました。")
        update_cache(title)

    except Exception as e:
        print(f"[ERROR] Selenium 処理中にエラーが発生しました: {e}")

    finally:
        driver.quit()
        print("[DEBUG] ブラウザを閉じました")

if __name__ == "__main__":
    main()
