/* ============================================================
   ANIMEPAHE TV — Application Logic & Theme Switcher
   ============================================================ */

// 1. Theme Initialization (System preference default)
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


// 2. Theme Toggle Switcher
function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("ktv-animepahe-theme", next);
}

// 3. Fallback Promo Card (If custom promo.html is absent/empty)
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

// 4. Serverless Promo Loader
async function loadPromo() {
  const container = document.getElementById("dynamic-promo");
  if (!container) return;
  
  try {
    const resp = await fetch("promo.html");
    if (!resp.ok) {
      throw new Error("Promo fragment not available today");
    }
    const html = await resp.text();
    if (html.trim().length > 0) {
      container.innerHTML = html;
      return;
    }
    throw new Error("Empty promo response");
  } catch (err) {
    console.log("[AnimePahe TV Serverless] Active fallback promo:", err.message);
    container.innerHTML = getFallbackPromo();
  }
}

// 5. DOM Initialization
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  loadPromo();

  // Add micro-interactions for buttons
  const buttons = document.querySelectorAll(".btn-download, .promo-btn, .eco-mini-card");
  buttons.forEach(btn => {
    btn.addEventListener("mouseenter", () => {
      btn.style.transform = "translateY(-2px)";
    });
    btn.addEventListener("mouseleave", () => {
      btn.style.transform = "none";
    });
  });
});
