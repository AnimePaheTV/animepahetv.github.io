function initTheme() {
  const storedTheme = localStorage.getItem("ktv-animepahe-theme");
  if (storedTheme) {
    document.documentElement.setAttribute("data-theme", storedTheme);
  } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.setAttribute("data-theme", "dark");
  } else {
    document.documentElement.setAttribute("data-theme", "light");
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("ktv-animepahe-theme", next);
}

function getFallbackPromo() {
  return `
    <div class="promo-card">
      <div class="promo-badge">POPULAR</div>
      <div class="promo-content">
        <span class="promo-meta"><i class="fa-solid fa-fire"></i> Trending Now</span>
        <h3>Demon Slayer: Infinity Castle</h3>
        <p>Experience spectacular widescreen animation and cinematic subbed or dubbed action in full HD. Direct remote D-pad control and lightning fast player loads.</p>
        <a href="#download" class="promo-btn"><i class="fa-solid fa-circle-down"></i> Get Widescreen App</a>
      </div>
    </div>
  `;
}

async function loadPromo() {
  const container = document.getElementById("dynamic-promo");
  if (!container) return;
  try {
    const resp = await fetch("promo.html");
    if (!resp.ok) throw new Error("Promo fragment not available");
    const html = await resp.text();
    if (html.trim().length > 0) {
      container.innerHTML = html;
      return;
    }
    throw new Error("Empty promo response");
  } catch (err) {
    console.log("[Serverless] Active fallback promo:", err.message);
    container.innerHTML = getFallbackPromo();
  }
}

async function loadWcBanner() {
  const container = document.getElementById("wc-banner");
  if (!container) return;
  if (Date.now() > new Date("2026-07-20").getTime()) {
    container.style.display = "none";
    return;
  }
  try {
    const resp = await fetch("wc-banner.html");
    if (!resp.ok) throw new Error("WC banner not found");
    const html = await resp.text();
    if (html.trim().length > 0) {
      container.innerHTML = html;
      return;
    }
    throw new Error("Empty banner");
  } catch (err) {
    console.log("[Serverless] WC banner not available:", err.message);
    container.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  loadPromo();
  loadWcBanner();
});
