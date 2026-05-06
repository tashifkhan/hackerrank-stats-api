from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HackerRank Stats</title>
    <style>
        :root {
            --bg: #0d1117;
            --surface: #161b22;
            --surface-2: #1c2230;
            --surface-3: #21262d;
            --border: #30363d;
            --text: #e6edf3;
            --muted: #8b949e;
            --green-4: #32c766;
            --green-3: #1e8449;
            --green-2: #196f3d;
            --green-1: #1a4731;
            --green-0: #161b22;
            --red: #f85149;
            --blue: #58a6ff;
            --yellow: #e3b341;
            --radius: 12px;
            --radius-lg: 16px;
        }
        *, *::before, *::after { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            font-size: 14px;
            line-height: 1.5;
        }

        /* ── Layout ── */
        .page { max-width: 1100px; margin: 0 auto; padding: 40px 16px 80px; }

        /* ── Header ── */
        .header {
            text-align: center;
            margin-bottom: 48px;
        }
        .header .logo {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
        }
.header h1 {
            font-size: clamp(1.6rem, 4vw, 2.5rem);
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .header .tagline { color: var(--muted); margin: 8px 0 0; font-size: 15px; }

        /* ── Search ── */
        .search-wrap {
            max-width: 540px;
            margin: 32px auto 0;
            display: flex;
            gap: 10px;
        }
        .search-input {
            flex: 1;
            padding: 13px 18px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text);
            font-size: 15px;
            outline: none;
            transition: border-color 0.15s;
        }
        .search-input:focus { border-color: var(--green-4); }
        .search-input::placeholder { color: var(--muted); }
        .search-btn {
            padding: 13px 22px;
            border-radius: var(--radius);
            border: none;
            background: var(--green-4);
            color: #050e07;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            white-space: nowrap;
            transition: opacity 0.15s;
        }
        .search-btn:hover { opacity: 0.88; }
        .search-btn:disabled { opacity: 0.5; cursor: not-allowed; }

        /* ── Empty state ── */
        .empty-state {
            text-align: center;
            padding: 80px 20px;
            color: var(--muted);
        }
        .empty-state svg { opacity: 0.25; margin-bottom: 16px; }
        .empty-state p { font-size: 15px; margin: 0; }

        /* ── Dashboard ── */
        #dashboard { display: none; }

        /* ── Profile row ── */
        .profile-row {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            align-items: flex-start;
            flex-wrap: wrap;
        }
        .profile-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            display: flex;
            gap: 20px;
            align-items: flex-start;
            flex: 0 0 auto;
            min-width: 280px;
        }
        .avatar {
            width: 72px; height: 72px;
            border-radius: 50%;
            background: var(--surface-3);
            border: 2px solid var(--border);
            object-fit: cover;
            flex-shrink: 0;
        }
        .profile-info { min-width: 0; }
        .profile-name {
            font-size: 19px;
            font-weight: 700;
            margin: 0 0 2px;
            line-height: 1.3;
        }
        .profile-username {
            color: var(--muted);
            margin: 0 0 10px;
            font-size: 13px;
        }
        .profile-meta {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .profile-meta-item {
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--muted);
            font-size: 13px;
        }
        .profile-meta-item svg { width: 14px; height: 14px; flex-shrink: 0; }
        .profile-meta-item a { color: var(--blue); text-decoration: none; }
        .profile-meta-item a:hover { text-decoration: underline; }

        /* ── Stats grid ── */
        .stats-grid {
            flex: 1;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 12px;
            min-width: 0;
        }
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 18px 16px;
            display: flex;
            flex-direction: column;
        }
        .stat-label {
            font-size: 12px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .stat-value {
            font-size: 26px;
            font-weight: 700;
            line-height: 1;
        }
        .stat-sub { font-size: 12px; color: var(--muted); margin-top: 4px; }
        .stat-green { color: var(--green-4); }
        .stat-blue { color: var(--blue); }
        .stat-yellow { color: var(--yellow); }

        /* ── Bio / about ── */
        .about-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 16px 20px;
            margin-bottom: 20px;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.6;
        }
        .about-card:empty { display: none; }

        /* ── Skills ── */
        .skill-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
        .skill-tag {
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid var(--border);
            background: var(--surface);
            font-size: 12px;
            color: var(--muted);
        }

        /* ── Tabs ── */
        .tabs {
            display: flex;
            gap: 4px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
        }
        .tab-btn {
            padding: 10px 18px;
            border: none;
            background: none;
            color: var(--muted);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -1px;
            border-radius: 4px 4px 0 0;
            transition: color 0.15s;
        }
        .tab-btn:hover { color: var(--text); }
        .tab-btn.active { color: var(--text); border-bottom-color: var(--green-4); }
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }

        /* ── Heatmap ── */
        .heatmap-wrap {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            margin-bottom: 20px;
        }
        .heatmap-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 12px;
        }
        .heatmap-title { font-weight: 600; font-size: 15px; margin: 0; }
        .heatmap-streaks {
            display: flex;
            gap: 20px;
        }
        .streak-item { text-align: right; }
        .streak-val { font-size: 22px; font-weight: 700; color: var(--green-4); }
        .streak-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .heatmap-scroll { overflow-x: auto; padding-bottom: 4px; }
        .heatmap-svg { display: block; }
        .heatmap-cell { rx: 2; ry: 2; }
        .heatmap-legend {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 12px;
            font-size: 11px;
            color: var(--muted);
        }
        .heatmap-legend svg { flex-shrink: 0; }

        /* ── Submissions ── */
        .submissions-list { display: flex; flex-direction: column; gap: 1px; }
        .submission-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            transition: background 0.1s;
        }
        .submission-item:hover { background: var(--surface-2); }
        .submission-title { flex: 1; font-weight: 500; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .submission-lang {
            padding: 2px 8px;
            border-radius: 20px;
            background: var(--surface-3);
            font-size: 11px;
            color: var(--muted);
            white-space: nowrap;
        }
        .submission-status {
            font-size: 12px;
            font-weight: 600;
            color: var(--green-4);
            white-space: nowrap;
        }
        .submission-time { font-size: 12px; color: var(--muted); white-space: nowrap; }

        /* ── Badges ── */
        .badges-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 12px;
        }
        .badge-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px 16px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        .badge-card.active-badge { border-color: var(--green-4); }
        .badge-icon {
            width: 56px; height: 56px;
            border-radius: 50%;
            background: var(--surface-3);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .badge-icon img { width: 100%; height: 100%; object-fit: cover; }
        .badge-icon-placeholder {
            width: 100%; height: 100%;
            display: flex; align-items: center; justify-content: center;
            font-size: 24px;
        }
        .badge-name { font-size: 13px; font-weight: 600; line-height: 1.3; }
        .badge-date { font-size: 11px; color: var(--muted); }
        .badge-active-label {
            font-size: 10px;
            color: var(--green-4);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 700;
        }

        /* ── Contests ── */
        .contest-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }
        .contest-table-wrap {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            overflow: hidden;
        }
        table { width: 100%; border-collapse: collapse; }
        th {
            text-align: left;
            padding: 12px 16px;
            font-size: 12px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border);
            background: var(--surface-2);
        }
        td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: var(--surface-2); }
        .trend-up { color: var(--green-4); }
        .trend-down { color: var(--red); }

        /* ── Loading skeleton ── */
        .skeleton {
            background: linear-gradient(90deg, var(--surface) 25%, var(--surface-2) 50%, var(--surface) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.4s infinite;
            border-radius: 6px;
        }
        @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

        /* ── Error banner ── */
        .error-banner {
            background: rgba(248,81,73,0.1);
            border: 1px solid rgba(248,81,73,0.3);
            border-radius: var(--radius);
            padding: 14px 18px;
            color: var(--red);
            margin-bottom: 20px;
            display: none;
        }

        /* ── Year selector ── */
        .year-selector {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }
        .year-pill {
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid var(--border);
            background: none;
            color: var(--muted);
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: color 0.12s, border-color 0.12s, background 0.12s;
        }
        .year-pill:hover { color: var(--text); border-color: var(--text); }
        .year-pill.active {
            background: rgba(50,199,102,0.12);
            border-color: var(--green-4);
            color: var(--green-4);
        }

        /* ── API Docs ── */
        .api-docs {
            margin-top: 40px;
        }
        .api-docs-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin: 0 0 14px;
        }
        .endpoint-list { display: flex; flex-direction: column; gap: 8px; }
        .endpoint-row {
            display: flex;
            align-items: baseline;
            gap: 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 12px 16px;
            flex-wrap: wrap;
        }
        .method-badge {
            font-size: 11px;
            font-weight: 700;
            color: var(--green-4);
            background: rgba(50,199,102,0.1);
            border: 1px solid rgba(50,199,102,0.25);
            border-radius: 5px;
            padding: 2px 7px;
            flex-shrink: 0;
            font-family: ui-monospace, monospace;
        }
        .endpoint-path {
            font-family: ui-monospace, monospace;
            font-size: 13px;
            color: var(--text);
            flex-shrink: 0;
        }
        .endpoint-desc { font-size: 12px; color: var(--muted); }

        /* ── Footer ── */
        .footer {
            border-top: 1px solid var(--border);
            margin-top: 60px;
            padding-top: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            font-size: 13px;
            color: var(--muted);
            flex-wrap: wrap;
        }
        .footer a {
            color: var(--muted);
            text-decoration: none;
        }
        .footer a:hover { color: var(--text); }
        .footer .sep { opacity: 0.35; }

        /* ── Responsive ── */
        @media (max-width: 640px) {
            .page { padding: 24px 12px 60px; }
            .profile-row { flex-direction: column; }
            .profile-card { width: 100%; }
            .heatmap-streaks { gap: 12px; }
        }
    </style>
</head>
<body>
<div class="page">
    <!-- Header -->
    <div class="header">
        <div class="logo">
            <h1>HackerRank Stats</h1>
        </div>
        <p class="tagline">Public profile analytics &amp; activity tracker</p>
        <form class="search-wrap" id="search-form">
            <input
                class="search-input"
                id="username-input"
                type="text"
                placeholder="Enter a HackerRank username…"
                autocomplete="off"
                spellcheck="false"
                required
            >
            <button class="search-btn" type="submit" id="search-btn">Analyze</button>
        </form>
    </div>

    <!-- Error banner -->
    <div class="error-banner" id="error-banner"></div>

    <!-- Empty state -->
    <div class="empty-state" id="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <p>Enter a username to load their HackerRank profile dashboard</p>
    </div>

    <!-- API Docs -->
    <div class="api-docs" id="api-docs-section">
        <p class="api-docs-title">Endpoints</p>
        <div class="endpoint-list">
            <div class="endpoint-row">
                <span class="method-badge">GET</span>
                <span class="endpoint-path">/{username}</span>
                <span class="endpoint-desc">Aggregated stats — total solved, ranking, reputation, score, submission calendar</span>
            </div>
            <div class="endpoint-row">
                <span class="method-badge">GET</span>
                <span class="endpoint-path">/{username}/profile</span>
                <span class="endpoint-desc">Full profile — avatar, bio, social links, skill tags, badges, recent submissions</span>
            </div>
            <div class="endpoint-row">
                <span class="method-badge">GET</span>
                <span class="endpoint-path">/{username}/heatmap</span>
                <span class="endpoint-desc">Daily contribution heatmap with streaks and yearly summaries</span>
            </div>
            <div class="endpoint-row">
                <span class="method-badge">GET</span>
                <span class="endpoint-path">/{username}/badges</span>
                <span class="endpoint-desc">Awarded badges and inferred active badge</span>
            </div>
            <div class="endpoint-row">
                <span class="method-badge">GET</span>
                <span class="endpoint-path">/{username}/contests</span>
                <span class="endpoint-desc">Contest history, rating, global ranking, and percentile</span>
            </div>
        </div>
    </div>

    <!-- Dashboard -->
    <div id="dashboard">
        <!-- Profile + Stats -->
        <div class="profile-row">
            <div class="profile-card">
                <img class="avatar" id="d-avatar" src="" alt="avatar">
                <div class="profile-info">
                    <p class="profile-name" id="d-name">—</p>
                    <p class="profile-username" id="d-username">—</p>
                    <div class="profile-meta" id="d-meta"></div>
                </div>
            </div>
            <div class="stats-grid" id="d-stats-grid">
                <div class="stat-card">
                    <span class="stat-label">Solved</span>
                    <span class="stat-value stat-green" id="d-solved">—</span>
                    <span class="stat-sub" id="d-solved-sub"></span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Ranking</span>
                    <span class="stat-value stat-blue" id="d-ranking">—</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Score</span>
                    <span class="stat-value stat-yellow" id="d-points">—</span>
                    <span class="stat-sub">contribution pts</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Reputation</span>
                    <span class="stat-value" id="d-rep">—</span>
                </div>
            </div>
        </div>

        <!-- About -->
        <div class="about-card" id="d-about"></div>

        <!-- Skill tags -->
        <div class="skill-tags" id="d-skills"></div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab-btn active" data-tab="heatmap">Activity</button>
            <button class="tab-btn" data-tab="submissions">Submissions</button>
            <button class="tab-btn" data-tab="badges">Badges</button>
            <button class="tab-btn" data-tab="contests">Contests</button>
        </div>

        <!-- Heatmap tab -->
        <div class="tab-panel active" id="tab-heatmap">
            <div class="heatmap-wrap">
                <div class="heatmap-header">
                    <div>
                        <p class="heatmap-title" id="d-heatmap-title">Contributions this year</p>
                        <p style="color:var(--muted);font-size:12px;margin:4px 0 0" id="d-heatmap-sub"></p>
                    </div>
                    <div class="heatmap-streaks">
                        <div class="streak-item">
                            <div class="streak-val" id="d-streak-cur">—</div>
                            <div class="streak-label">Current streak</div>
                        </div>
                        <div class="streak-item">
                            <div class="streak-val" id="d-streak-max">—</div>
                            <div class="streak-label">Longest streak</div>
                        </div>
                    </div>
                </div>
                <div class="year-selector" id="d-year-selector"></div>
                <div class="heatmap-scroll">
                    <div id="d-heatmap-svg-wrap"></div>
                </div>
                <div class="heatmap-legend">
                    Less
                    <svg width="84" height="12">
                        <rect x="0"  y="0" width="12" height="12" rx="2" fill="#161b22"/>
                        <rect x="18" y="0" width="12" height="12" rx="2" fill="#1a4731"/>
                        <rect x="36" y="0" width="12" height="12" rx="2" fill="#196f3d"/>
                        <rect x="54" y="0" width="12" height="12" rx="2" fill="#1e8449"/>
                        <rect x="72" y="0" width="12" height="12" rx="2" fill="#32c766"/>
                    </svg>
                    More
                </div>
            </div>
        </div>

        <!-- Submissions tab -->
        <div class="tab-panel" id="tab-submissions">
            <div class="submissions-list" id="d-submissions"></div>
        </div>

        <!-- Badges tab -->
        <div class="tab-panel" id="tab-badges">
            <div class="badges-grid" id="d-badges"></div>
        </div>

        <!-- Contests tab -->
        <div class="tab-panel" id="tab-contests">
            <div class="contest-summary" id="d-contest-summary"></div>
            <div class="contest-table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Contest</th>
                            <th>Rating</th>
                            <th>Rank</th>
                            <th>Solved</th>
                        </tr>
                    </thead>
                    <tbody id="d-contest-rows"></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <a href="https://tashif.codes" target="_blank" rel="noopener">tashif.codes</a>
        <span class="sep">·</span>
        <a href="https://github.com/stars/tashifkhan/lists/stats-apis" target="_blank" rel="noopener">more stats APIs</a>
        <span class="sep">·</span>
        <a href="/docs" target="_blank">swagger</a>
    </footer>
</div>

<script>
const COLORS = ["#161b22", "#1a4731", "#196f3d", "#1e8449", "#32c766"];
const DAY_SIZE = 12, DAY_GAP = 3;

function $(id) { return document.getElementById(id); }
function el(tag, props = {}, ...children) {
    const e = document.createElementNS ? document.createElementNS("http://www.w3.org/2000/svg", tag) : document.createElement(tag);
    for (const [k, v] of Object.entries(props)) e.setAttribute(k, v);
    children.forEach(c => { if (c != null) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
}
function hel(tag, props = {}, ...children) {
    const e = document.createElement(tag);
    Object.assign(e, props);
    if (props.class) e.className = props.class;
    children.forEach(c => { if (c != null) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
}
function fmt(n) { return Number(n).toLocaleString(); }
function fmtDate(ts) {
    if (!ts) return "";
    const d = new Date(typeof ts === "number" && ts < 1e10 ? ts * 1000 : ts);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}
function timeAgo(ts) {
    const d = new Date(typeof ts === "number" && ts < 1e10 ? ts * 1000 : ts);
    const diff = (Date.now() - d.getTime()) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return Math.floor(diff / 60) + "m ago";
    if (diff < 86400) return Math.floor(diff / 3600) + "h ago";
    if (diff < 86400 * 30) return Math.floor(diff / 86400) + "d ago";
    return d.toLocaleDateString("en-US", { month: "short", year: "numeric" });
}

function showError(msg) {
    const b = $("error-banner");
    b.textContent = msg;
    b.style.display = "block";
}
function clearError() { $("error-banner").style.display = "none"; }

// ── Heatmap SVG ──────────────────────────────────────────────────────────────
// allContributions: full dailyContributions array
// rangeStart, rangeEnd: Date objects (inclusive)
function buildHeatmap(allContributions, rangeStart, rangeEnd) {
    const map = {};
    for (const d of (allContributions || [])) map[d.date] = d;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const end = new Date(Math.min(rangeEnd.getTime(), today.getTime()));
    end.setHours(0, 0, 0, 0);

    // align grid start to the Sunday on or before rangeStart
    const gridStart = new Date(rangeStart);
    gridStart.setHours(0, 0, 0, 0);
    gridStart.setDate(gridStart.getDate() - gridStart.getDay());

    const msPerDay = 86400 * 1000;
    const totalDays = Math.round((end - gridStart) / msPerDay) + 1;
    const weeks = Math.ceil(totalDays / 7);

    const CELL = DAY_SIZE + DAY_GAP;
    const svgW = weeks * CELL;
    const svgH = 7 * CELL + 20;

    const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("width", svgW);
    svg.setAttribute("height", svgH);
    svg.setAttribute("class", "heatmap-svg");
    svg.setAttribute("viewBox", `0 0 ${svgW} ${svgH}`);

    // day labels (Mon, Wed, Fri)
    [1, 3, 5].forEach(d => {
        const t = document.createElementNS(ns, "text");
        t.setAttribute("x", -4);
        t.setAttribute("y", d * CELL + DAY_SIZE - 1);
        t.setAttribute("font-size", "9");
        t.setAttribute("fill", "#8b949e");
        t.setAttribute("text-anchor", "end");
        t.textContent = DAYS[d];
        svg.appendChild(t);
    });

    const monthLabels = {};
    const cur = new Date(gridStart);

    for (let w = 0; w < weeks; w++) {
        for (let d = 0; d < 7; d++) {
            const iso = cur.toISOString().slice(0, 10);
            const inRange = cur >= rangeStart && cur <= end;
            const entry = inRange ? map[iso] : null;
            const level = entry ? entry.level : 0;
            const future = cur > end;

            const rect = document.createElementNS(ns, "rect");
            rect.setAttribute("x", w * CELL);
            rect.setAttribute("y", d * CELL + 18);
            rect.setAttribute("width", DAY_SIZE);
            rect.setAttribute("height", DAY_SIZE);
            rect.setAttribute("rx", 2);
            rect.setAttribute("fill", future ? "transparent" : (COLORS[level] || COLORS[0]));

            if (!future) {
                const count = entry ? entry.count : 0;
                const title = document.createElementNS(ns, "title");
                title.textContent = `${count} submission${count !== 1 ? "s" : ""} on ${iso}`;
                rect.appendChild(title);
            }
            svg.appendChild(rect);

            if (inRange && (cur.getDate() === 1 || (w === 0 && d === 0))) {
                monthLabels[w] = cur.toLocaleString("en-US", { month: "short" });
            }
            cur.setDate(cur.getDate() + 1);
        }
    }

    for (const [w, label] of Object.entries(monthLabels)) {
        const t = document.createElementNS(ns, "text");
        t.setAttribute("x", w * CELL);
        t.setAttribute("y", 10);
        t.setAttribute("font-size", "10");
        t.setAttribute("fill", "#8b949e");
        t.textContent = label;
        svg.appendChild(t);
    }

    return svg;
}

// ── Year selector ─────────────────────────────────────────────────────────────
let _heatmapData = null;

function buildYearSelector(firstActiveDate) {
    const sel = $("d-year-selector");
    sel.innerHTML = "";

    const today = new Date();
    const currentYear = today.getFullYear();
    const firstYear = firstActiveDate
        ? new Date(firstActiveDate).getFullYear()
        : currentYear - 1;

    const options = [{ label: "Last 365d", key: "365" }];
    for (let y = currentYear; y >= Math.min(firstYear, currentYear); y--) {
        options.push({ label: String(y), key: String(y) });
    }

    options.forEach(({ label, key }) => {
        const btn = document.createElement("button");
        btn.className = "year-pill" + (key === "365" ? " active" : "");
        btn.textContent = label;
        btn.dataset.range = key;
        btn.addEventListener("click", () => {
            sel.querySelectorAll(".year-pill").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            applyHeatmapRange(key);
        });
        sel.appendChild(btn);
    });
}

function applyHeatmapRange(key) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    let rangeStart, rangeEnd;
    if (key === "365") {
        rangeEnd = today;
        rangeStart = new Date(today);
        rangeStart.setDate(rangeStart.getDate() - 364);
    } else {
        const y = parseInt(key, 10);
        rangeStart = new Date(y, 0, 1);
        rangeEnd = y === today.getFullYear() ? today : new Date(y, 11, 31);
    }

    const contributions = _heatmapData?.dailyContributions || [];
    const inRange = contributions.filter(d => {
        const dt = new Date(d.date);
        return dt >= rangeStart && dt <= rangeEnd;
    });
    const total = inRange.reduce((s, d) => s + d.count, 0);
    const active = inRange.filter(d => d.count > 0).length;

    $("d-heatmap-title").textContent = fmt(total) + " submissions";
    $("d-heatmap-sub").textContent = active + " active days";

    const wrap = $("d-heatmap-svg-wrap");
    wrap.innerHTML = "";
    wrap.appendChild(buildHeatmap(contributions, rangeStart, rangeEnd));
}

// ── Render functions ──────────────────────────────────────────────────────────
function renderProfile(stats, profile, heatmap) {
    // avatar
    const av = $("d-avatar");
    av.src = profile?.profile?.userAvatar || "";
    av.onerror = () => { av.style.display = "none"; };

    // name / username
    $("d-name").textContent = profile?.profile?.realName || stats?.username || "—";
    $("d-username").textContent = "@" + (profile?.username || stats?.username || "");

    // meta
    const meta = $("d-meta");
    meta.innerHTML = "";
    const addMeta = (icon, text, href) => {
        if (!text) return;
        const item = document.createElement("div");
        item.className = "profile-meta-item";
        item.innerHTML = icon;
        if (href) {
            const a = document.createElement("a");
            a.href = href; a.target = "_blank"; a.textContent = text;
            item.appendChild(a);
        } else {
            item.appendChild(document.createTextNode(text));
        }
        meta.appendChild(item);
    };
    addMeta('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>', profile?.profile?.countryName);
    addMeta('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>', profile?.profile?.company);
    addMeta('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 14a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.56 3h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 10a16 16 0 0 0 5.91 5.91l.72-.81a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>', profile?.profile?.school);
    if (profile?.githubUrl) addMeta('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>', "GitHub", profile.githubUrl);
    if (profile?.linkedinUrl) addMeta('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>', "LinkedIn", profile.linkedinUrl);

    // stats
    $("d-solved").textContent = fmt(stats?.totalSolved ?? 0);
    $("d-ranking").textContent = stats?.ranking ? "#" + fmt(stats.ranking) : "—";
    $("d-points").textContent = fmt(stats?.contributionPoints ?? 0);
    $("d-rep").textContent = fmt(stats?.reputation ?? 0);

    // about
    const about = $("d-about");
    about.textContent = profile?.profile?.aboutMe || "";

    // skills
    const skillsEl = $("d-skills");
    skillsEl.innerHTML = "";
    (profile?.profile?.skillTags || []).forEach(t => {
        const s = document.createElement("span");
        s.className = "skill-tag";
        s.textContent = t;
        skillsEl.appendChild(s);
    });
}

function renderHeatmap(heatmap) {
    _heatmapData = heatmap;
    $("d-streak-cur").textContent = (heatmap?.currentStreak ?? 0) + "d";
    $("d-streak-max").textContent = (heatmap?.longestStreak ?? 0) + "d";
    buildYearSelector(heatmap?.firstActiveDate || "");
    applyHeatmapRange("365");
}

function renderSubmissions(profile) {
    const list = $("d-submissions");
    list.innerHTML = "";
    const subs = profile?.recentSubmissions || [];
    if (!subs.length) {
        list.innerHTML = '<p style="color:var(--muted);text-align:center;padding:40px">No recent submissions found</p>';
        return;
    }
    subs.forEach(s => {
        const item = document.createElement("div");
        item.className = "submission-item";
        item.innerHTML = `
            <span class="submission-title">${s.title || s.titleSlug || "—"}</span>
            <span class="submission-lang">${s.lang || ""}</span>
            <span class="submission-status">${s.statusDisplay || "Accepted"}</span>
            <span class="submission-time">${s.timestamp ? timeAgo(s.timestamp) : ""}</span>
        `;
        list.appendChild(item);
    });
}

function renderBadges(badgesData, activeBadge) {
    const grid = $("d-badges");
    grid.innerHTML = "";
    const all = badgesData?.badges || [];
    if (!all.length) {
        grid.innerHTML = '<p style="color:var(--muted);text-align:center;padding:40px;grid-column:1/-1">No badges found</p>';
        return;
    }
    all.forEach(b => {
        const isActive = activeBadge && activeBadge.id === b.id;
        const card = document.createElement("div");
        card.className = "badge-card" + (isActive ? " active-badge" : "");
        card.innerHTML = `
            <div class="badge-icon">
                ${b.icon ? `<img src="${b.icon}" alt="${b.displayName}" onerror="this.parentNode.innerHTML='<div class=badge-icon-placeholder>🏆</div>'">` : '<div class="badge-icon-placeholder">🏆</div>'}
            </div>
            <span class="badge-name">${b.displayName || "Badge"}</span>
            ${b.creationDate ? `<span class="badge-date">${fmtDate(b.creationDate)}</span>` : ""}
            ${isActive ? '<span class="badge-active-label">⭐ Active</span>' : ""}
        `;
        grid.appendChild(card);
    });
}

function renderContests(contests) {
    const summary = $("d-contest-summary");
    summary.innerHTML = "";
    const addStat = (label, val, cls) => {
        const c = document.createElement("div");
        c.className = "stat-card";
        c.innerHTML = `<span class="stat-label">${label}</span><span class="stat-value ${cls||""}">${val}</span>`;
        summary.appendChild(c);
    };
    addStat("Rating", contests?.rating ? Math.round(contests.rating) : "—", "stat-green");
    addStat("Global Rank", contests?.globalRanking ? "#" + fmt(contests.globalRanking) : "—", "stat-blue");
    addStat("Contests", contests?.attendedContestsCount ?? "—");
    if (contests?.topPercentage != null) addStat("Top", contests.topPercentage.toFixed(1) + "%", "stat-yellow");

    const tbody = $("d-contest-rows");
    tbody.innerHTML = "";
    const history = contests?.contestHistory || [];
    if (!history.length) {
        tbody.innerHTML = '<tr><td colspan="4" style="color:var(--muted);text-align:center;padding:32px">No contest history found</td></tr>';
        return;
    }
    history.forEach(c => {
        const tr = document.createElement("tr");
        const trend = c.trendDirection === "up" ? '<span class="trend-up">↑</span>' : c.trendDirection === "down" ? '<span class="trend-down">↓</span>' : "";
        tr.innerHTML = `
            <td>${c.title || c.contest || "—"}</td>
            <td>${c.rating != null ? Math.round(c.rating) : "—"} ${trend}</td>
            <td>${c.ranking != null ? "#" + fmt(c.ranking) : "—"}</td>
            <td>${c.problemsSolved ?? "—"}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ── Main load ────────────────────────────────────────────────────────────────
async function loadDashboard(username) {
    clearError();
    $("empty-state").style.display = "none";
    $("dashboard").style.display = "block";
    $("search-btn").disabled = true;
    $("search-btn").textContent = "Loading…";

    // reset
    ["d-name","d-username","d-solved","d-ranking","d-points","d-rep",
     "d-streak-cur","d-streak-max","d-heatmap-title","d-heatmap-sub"].forEach(id => {
        $(id).textContent = "—";
    });
    $("d-meta").innerHTML = "";
    $("d-about").textContent = "";
    $("d-skills").innerHTML = "";
    $("d-heatmap-svg-wrap").innerHTML = "";
    $("d-submissions").innerHTML = '<p style="color:var(--muted);text-align:center;padding:32px">Loading…</p>';
    $("d-badges").innerHTML = '<p style="color:var(--muted);text-align:center;padding:32px;grid-column:1/-1">Loading…</p>';
    $("d-contest-rows").innerHTML = '<tr><td colspan="4" style="color:var(--muted);text-align:center;padding:32px">Loading…</td></tr>';
    $("d-contest-summary").innerHTML = "";

    try {
        const enc = encodeURIComponent(username);
        const [stats, profile, heatmap, badges, contests] = await Promise.all([
            fetch(`/${enc}`).then(r => r.json()).catch(() => null),
            fetch(`/${enc}/profile`).then(r => r.json()).catch(() => null),
            fetch(`/${enc}/heatmap`).then(r => r.json()).catch(() => null),
            fetch(`/${enc}/badges`).then(r => r.json()).catch(() => null),
            fetch(`/${enc}/contests`).then(r => r.json()).catch(() => null),
        ]);

        if (stats?.status === "error" && !stats?.totalSolved) {
            showError("User not found or profile is private: " + (stats.message || username));
            $("dashboard").style.display = "none";
            $("empty-state").style.display = "block";
            $("api-docs-section").style.display = "block";
            return;
        }

        $("api-docs-section").style.display = "none";
        renderProfile(stats, profile, heatmap);
        renderHeatmap(heatmap);
        renderSubmissions(profile);
        renderBadges(badges, badges?.activeBadge || profile?.activeBadge);
        renderContests(contests);
    } catch (err) {
        showError("Failed to load data: " + err.message);
    } finally {
        $("search-btn").disabled = false;
        $("search-btn").textContent = "Analyze";
    }
}

// ── Tab switching ────────────────────────────────────────────────────────────
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    });
});

// ── Form submit ───────────────────────────────────────────────────────────────
document.getElementById("search-form").addEventListener("submit", async e => {
    e.preventDefault();
    const u = $("username-input").value.trim();
    if (u) await loadDashboard(u);
});
</script>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse)
async def docs() -> HTMLResponse:
    return HTMLResponse(HTML)
