const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector(".nav-links");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const postList = document.getElementById("post-list");
const revealSelector = ".card, .about-text, .community-link";
let revealObserver = null;

if (navToggle) {
  navToggle.addEventListener("click", () => {
    navLinks?.classList.toggle("open");
    navToggle.classList.toggle("open");
  });

  navLinks?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
      navToggle.classList.remove("open");
    });
  });
}

function registerReveal(target) {
  if (!target) return;
  if (prefersReducedMotion) {
    target.classList.add("visible");
    return;
  }
  if (revealObserver) {
    target.classList.add("reveal");
    revealObserver.observe(target);
  } else if (!("IntersectionObserver" in window)) {
    target.classList.add("visible");
  }
}

function initReveal() {
  const initialTargets = document.querySelectorAll(revealSelector);
  if (prefersReducedMotion) {
    initialTargets.forEach((target) => target.classList.add("visible"));
    return;
  }
  if ("IntersectionObserver" in window) {
    revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            revealObserver?.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -10%", threshold: 0.1 }
    );
    initialTargets.forEach((target) => registerReveal(target));
  } else {
    initialTargets.forEach((target) => target.classList.add("visible"));
  }
}

async function renderPosts() {
  if (!postList) return;

  try {
    const manifestUrl = new URL("./posts/posts.json", window.location.href);
    const response = await fetch(manifestUrl.toString(), { cache: "no-cache" });
    if (!response.ok) throw new Error("記事一覧の取得に失敗しました。");
    const posts = await response.json();

    if (!Array.isArray(posts) || posts.length === 0) {
      postList.innerHTML = "<p>公開済みの記事はまだありません。</p>";
      return;
    }

    postList.innerHTML = "";
    posts.forEach((post) => {
      const article = document.createElement("article");
      article.className = "card";

      const header = document.createElement("header");
      header.className = "post-meta";

      const dateSpan = document.createElement("span");
      dateSpan.className = "post-date";
      dateSpan.textContent = post.date;

      const tagSpan = document.createElement("span");
      tagSpan.className = "post-tag";
      tagSpan.textContent = Array.isArray(post.tags) && post.tags.length > 0 ? post.tags[0] : "Blog";

      header.append(dateSpan, tagSpan);

      const title = document.createElement("h3");
      title.textContent = post.title;

      const summary = document.createElement("p");
      summary.textContent = post.summary ?? "";

      const link = document.createElement("a");
      link.className = "post-link";
      link.href = `article.html?post=${encodeURIComponent(post.slug)}`;
      link.textContent = "記事を読む";

      article.append(header, title, summary, link);
      postList.append(article);
      registerReveal(article);
    });
  } catch (error) {
    console.error(error);
    postList.innerHTML =
      '<p>記事の読み込み中にエラーが発生しました。GitHub Pages へデプロイ済みか、もしくはローカルで確認する場合は <code>python3 -m http.server</code> などでサーバーを起動してください。</p>';
  }
}

renderPosts();
initReveal();
