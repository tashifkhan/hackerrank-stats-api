from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HackerRank Stats API</title>
    <style>
        :root {
            color-scheme: dark;
            --bg: #0b1020;
            --panel: #111936;
            --panel-2: #182449;
            --text: #e5ecff;
            --muted: #9fb2dd;
            --accent: #32c766;
            --border: #26355f;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            background: radial-gradient(circle at top, #16244d 0, var(--bg) 55%);
            color: var(--text);
        }
        main {
            max-width: 1120px;
            margin: 0 auto;
            padding: 32px 16px 48px;
        }
        .hero, .panel {
            background: rgba(17, 25, 54, 0.92);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
        }
        .hero {
            padding: 28px;
            margin-bottom: 20px;
        }
        h1, h2, h3, p { margin-top: 0; }
        h1 { font-size: clamp(2rem, 5vw, 3.25rem); margin-bottom: 12px; }
        .accent { color: var(--accent); }
        .subtle { color: var(--muted); }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }
        .card {
            background: var(--panel-2);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 18px;
        }
        code, pre {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }
        code {
            background: rgba(255, 255, 255, 0.06);
            padding: 2px 6px;
            border-radius: 6px;
        }
        pre {
            background: #09101f;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px;
            overflow: auto;
            margin: 0;
        }
        .panel {
            padding: 22px;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        input {
            flex: 1 1 260px;
            padding: 14px 16px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: #0e1730;
            color: var(--text);
            font-size: 1rem;
        }
        button {
            padding: 14px 18px;
            border: 0;
            border-radius: 12px;
            background: var(--accent);
            color: #04110a;
            font-weight: 700;
            cursor: pointer;
        }
        .actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 14px;
        }
        .actions button.secondary {
            background: #21325e;
            color: var(--text);
        }
        .meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }
        .meta .card strong {
            display: block;
            font-size: 1.2rem;
            margin-top: 6px;
        }
        @media (max-width: 640px) {
            main { padding: 16px 12px 32px; }
            .hero, .panel { padding: 18px; }
        }
    </style>
</head>
<body>
    <main>
        <section class="hero">
            <p class="accent">FastAPI + uv</p>
            <h1>HackerRank Stats API</h1>
            <p class="subtle">A public-profile HackerRank port of the original LeetCode Stats API. Route names and response envelopes are kept aligned, while HackerRank-only public data is adapted into the same shape.</p>
            <div class="grid">
                <div class="card">
                    <h3>Routes</h3>
                    <p><code>GET /{username}</code></p>
                    <p><code>GET /{username}/profile</code></p>
                    <p><code>GET /{username}/contests</code></p>
                    <p><code>GET /{username}/badges</code></p>
                    <p><code>GET /{username}/heatmap</code></p>
                </div>
                <div class="card">
                    <h3>Docs</h3>
                    <p>Swagger UI is available at <code>/docs</code>.</p>
                    <p>ReDoc is available at <code>/redoc</code>.</p>
                </div>
                <div class="card">
                    <h3>Compatibility</h3>
                    <p>Some LeetCode-specific fields do not exist on public HackerRank profiles. Those stay zeroed or are derived from public track scores for compatibility.</p>
                </div>
            </div>
        </section>

        <section class="panel">
            <h2>Profile Analyzer</h2>
            <p class="subtle">Try a public HackerRank username and inspect the adapted payloads.</p>
            <form id="lookup-form">
                <input id="username" name="username" placeholder="Enter a HackerRank username" required>
                <button type="submit">Fetch Stats</button>
            </form>
            <div class="actions">
                <button class="secondary" type="button" data-endpoint="">Stats</button>
                <button class="secondary" type="button" data-endpoint="/profile">Profile</button>
                <button class="secondary" type="button" data-endpoint="/contests">Contests</button>
                <button class="secondary" type="button" data-endpoint="/badges">Badges</button>
                <button class="secondary" type="button" data-endpoint="/heatmap">Heatmap</button>
            </div>
        </section>

        <section class="panel">
            <div class="meta" id="summary"></div>
            <pre id="output">Choose an endpoint to begin.</pre>
        </section>
    </main>

    <script>
        const output = document.getElementById("output");
        const summary = document.getElementById("summary");
        const usernameInput = document.getElementById("username");
        let activeEndpoint = "";

        function renderSummary(data) {
            const items = [];
            if (data.username) items.push(["Username", data.username]);
            if (typeof data.totalSolved === "number") items.push(["Total Solved", data.totalSolved]);
            if (typeof data.rating === "number") items.push(["Rating", data.rating]);
            if (typeof data.totalSubmissions === "number") items.push(["Submissions", data.totalSubmissions]);
            if (Array.isArray(data.badges)) items.push(["Badges", data.badges.length]);
            summary.innerHTML = items
                .map(([label, value]) => `<div class="card"><span class="subtle">${label}</span><strong>${value}</strong></div>`)
                .join("");
        }

        async function loadEndpoint() {
            const username = usernameInput.value.trim();
            if (!username) return;
            const path = `/${encodeURIComponent(username)}${activeEndpoint}`;
            output.textContent = "Loading...";
            summary.innerHTML = "";
            try {
                const response = await fetch(path);
                const data = await response.json();
                renderSummary(data);
                output.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                output.textContent = String(error);
            }
        }

        document.getElementById("lookup-form").addEventListener("submit", async (event) => {
            event.preventDefault();
            await loadEndpoint();
        });

        document.querySelectorAll("[data-endpoint]").forEach((button) => {
            button.addEventListener("click", async () => {
                activeEndpoint = button.dataset.endpoint;
                await loadEndpoint();
            });
        });
    </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
async def docs() -> HTMLResponse:
    return HTMLResponse(HTML)
