# ブログ

## 公開
GitHub Pagesを使って，
https://e235221.github.io/Blog/
で公開しています。

## ディレクトリ構成

- `index.html` — トップページ。各セクションの本文をここで管理します。
- `styles/main.css` — サイト全体のスタイル。カラー、レイアウト、レスポンシブ設定を含みます。
- `styles/article.css` — 記事ページ固有のタイポグラフィや余白を定義します。
- `scripts/main.js` — モバイルナビゲーション、タブ切り替え、記事一覧の読み込みを担当します。
- `scripts/article.js` — Markdown 記事を HTML に変換して表示します。
- `posts/` — Markdown で書いた記事と `posts.json`（記事一覧のマニフェスト）を管理します。
- `article.html` — 単一記事を表示するためのテンプレート。クエリパラメータ `?post=スラッグ` で表示する記事を切り替えます。
- `assets/` — 背景テクスチャなどの静的アセットを配置しています。
- `.nojekyll` — GitHub Pages で Jekyll の自動ビルドを無効にするためのフラグ。

## run in local
```bash
cd MY_ORIGINAL_SITE
python3 -m http.server 4000
```

- ブラウザで `http://localhost:4000` にアクセスすると内容を確認できます。別のポートを使いたい場合は `4000` を適宜変更してください。
- index.htmlを直で開いても記事を表示できません。

## GitHub Pages 公開手順

1. GitHub に新しいリポジトリを作成し、このディレクトリの内容をコミット・プッシュします。
2. GitHub リポジトリの **Settings → Pages** を開き、**Branch** を公開したいブランチに設定、フォルダーは `/ (root)` を選択します。
3. 保存後、数分ほどでhttps://e235221.github.io/Blog/ でサイトが公開されます。
- 既定で Jekyll が無効化されるよう `.nojekyll` を同梱しています。追加のビルド設定は不要です。

## Markdown 記事の追加方法

1. `posts/` ディレクトリに `slug.md` 形式で記事を追加します。見出しや本文は通常の Markdown で記述します。
2. `posts/posts.json` に以下のようなエントリを追加します。
   ```json
   {
     "title": "記事タイトル",
     "date": "2024-06-01",
     "tags": ["カテゴリ"],
     "summary": "トップページに表示する概要。",
     "slug": "記事のスラッグ",
     "contentPath": "posts/記事のスラッグ.md"
   }
   ```
3. トップページ（`index.html`）の「記事」セクションに自動的に反映され、リンクを開くと `article.html?post=スラッグ` で内容が表示されます。
