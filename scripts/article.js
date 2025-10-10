const params = new URLSearchParams(window.location.search);
const slug = params.get("post");

const titleEl = document.getElementById("article-title");
const dateEl = document.getElementById("article-date");
const tagsEl = document.getElementById("article-tags");
const contentEl = document.getElementById("article-content");

async function loadArticle() {
  if (!slug) {
    contentEl.innerHTML = "<p>記事が指定されていません。</p>";
    return;
  }

  try {
    const manifestUrl = new URL("./posts/posts.json", window.location.href);
    const manifestRes = await fetch(manifestUrl.toString(), { cache: "no-cache" });
    if (!manifestRes.ok) throw new Error("記事一覧の取得に失敗しました。");
    const posts = await manifestRes.json();
    const entry = posts.find((post) => post.slug === slug);

    if (!entry) {
      contentEl.innerHTML = "<p>指定された記事が見つかりません。</p>";
      return;
    }

    titleEl.textContent = entry.title;
    dateEl.textContent = entry.date;
    tagsEl.textContent = Array.isArray(entry.tags) ? entry.tags.join(", ") : "";

    const markdownUrl = new URL(entry.contentPath, window.location.href);
    const markdownRes = await fetch(markdownUrl.toString(), { cache: "no-cache" });
    if (!markdownRes.ok) throw new Error("記事の読み込みに失敗しました。");
    const markdown = await markdownRes.text();
    const html = marked.parse(markdown, { mangle: false, headerIds: false });
    contentEl.innerHTML = html;
  } catch (error) {
    console.error(error);
    contentEl.innerHTML =
      '<p>記事の読み込み中にエラーが発生しました。GitHub Pages で公開中か、ローカルで確認する場合は <code>python3 -m http.server</code> を使ってサーバー経由でアクセスしてください。</p>';
  }
}

loadArticle();
