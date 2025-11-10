# 山脇大貴の記録

生成AIやプロダクトづくりの学びをまとめた日本語ブログです。  
公開URL: <https://e235221.github.io/Blog/>

Obsidian の Vault をソースとして使い、`python3 scripts/build_posts.py` を実行するだけで GitHub Pages へ公開できる静的サイトになっています。

---

## ディレクトリ構成

- `index.html` / `article.html` — 公開用の HTML ファイル。
- `styles/` — レイアウト・タイポグラフィを定義するスタイルシート。
- `scripts/main.js` — ナビゲーションや記事一覧の読み込み処理。
- `scripts/article.js` — Markdown を HTML に変換して記事ページに表示。
- `scripts/build_posts.py` — Vault から公開用 Markdown (`posts/`) とマニフェスト (`posts/posts.json`) を生成。
- `vault/posts/` — Obsidian から同期する元記事（Markdown）。
- `vault/assets/` — 記事で使用する画像・メディア。
- `posts/` — 公開用に生成された Markdown と `posts.json`。
- `assets/blog/` — 記事用の画像など（`build_posts.py` が `vault/assets` からコピー）。
- `.nojekyll` — GitHub Pages で Jekyll の自動ビルドを無効化するフラグ。

---

## ローカルでの確認方法

```bash
cd MY_ORIGINAL_SITE
python3 scripts/build_posts.py   # Vault 内容から公開ファイルを生成
python3 -m http.server 4000      # サーバーを起動
```

ブラウザで <http://localhost:4000> を開くとサイトを確認できます。  
`file://` では `fetch` が失敗するため、必ずローカルサーバー経由で閲覧してください。

---

## Obsidian Vault との同期フロー

1. **Vault をコピー（または rsync）**
   ```bash
   rsync -av --delete ~/Obsidian/Blog/ vault/
   ```
   - `vault/posts` に Markdown、`vault/assets` に画像を配置します。
   - 直接このリポジトリを Obsidian Vault として開いてもOKです。

2. **公開用ファイルを生成**
   ```bash
   python3 scripts/build_posts.py
   ```
   これにより以下が自動で更新されます。
   - `posts/*.md`（フロントマターを除去した公開用 Markdown）
   - `posts/posts.json`（トップページで使う記事リスト）
   - `assets/blog/`（Vault の画像をコピー）

3. **コミット & プッシュ**
   ```bash
   git status
   git add .
   git commit -m "Update blog posts"
   git push
   ```

---

## 記事ファイルの書き方

- `vault/posts/` に Markdown を保存し、冒頭に YAML フロントマターを付けます。

  ```markdown
  ---
  title: "GASを用いた欠席連絡自動化"
  date: "2025-06-10"
  tags: ["GAS", "Googleフォーム"]
  summary: "Googleフォームの回答をトリガーに欠席予定をカレンダー登録し、Discord通知まで自動化した手順の記録。"
  slug: "gas-google-forms-calendar"
  ---

  本文はここから始めます。Obsidian の `![[images/sample.png]]` 記法も利用できます。
  ```

- `slug` を省略した場合はファイル名から自動生成されます。
- `summary` が無いと本文の冒頭段落から抜粋されます。

### 画像の扱い

- `vault/assets/` に画像を配置します（例: `vault/assets/images/diagram.png`）。
- Markdown 内では以下のいずれかで参照できます。
  - Obsidian 記法 `![[images/diagram.png]]`
  - あるいは標準 Markdown `![説明](assets/blog/images/diagram.png)`  
    ※ビルド時に `assets/blog/` へコピーされます。

---

## GitHub Pages で公開する手順

1. このディレクトリをコミットして GitHub にプッシュ。
2. リポジトリの **Settings → Pages** を開き、`Branch: main`、`Folder: /(root)` を選択して保存。
3. 数分後に `https://<ユーザー名>.github.io/<リポジトリ名>/` で公開されます。
4. 公開後に 404 になる場合は、`index.html` がリポジトリ直下に存在するか、デプロイ (Deployments) のステータスを確認してください。

---

## よくある質問

### Q. `記事の読み込み中にエラーが発生しました` と表示される
`file://` で開いていると `fetch` が失敗します。`python3 -m http.server 4000` などでサーバーを起動し、`http://localhost:4000` からアクセスしてください。

### Q. Vault とリポジトリを完全に同期したい
`rsync`, `git subtree`, GitHub Actions など好みの方法で `vault/` を同期してください。ビルド済みの `posts/` と `assets/blog/` は GitHub Pages が必要とする公開ファイルなので、そのままコミットして問題ありません。

---

質問や改善アイデアがあれば Issue や Pull Request でお知らせください。
