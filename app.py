"""School Study App — Python server (stdlib only).

Run:  python3 app.py
Then open http://localhost:2009
"""

from __future__ import annotations

import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATIC_BASE = os.path.dirname(os.path.abspath(__file__))

PORT = 2009

# Load verb data from course/topic folders
with open(os.path.join(STATIC_BASE, "irish", "verbs", "data.json"), encoding="utf-8") as _f:
    VERBS = json.load(_f)

with open(os.path.join(STATIC_BASE, "spanish", "verbs", "data.json"), encoding="utf-8") as _f:
    SPANISH_VERBS = json.load(_f)


def _load_micro_images() -> list[str]:
  folder = os.path.join(STATIC_BASE, "biology", "micro")
  if not os.path.isdir(folder):
    return []
  allowed = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
  return sorted(
    name for name in os.listdir(folder)
    if os.path.splitext(name)[1].lower() in allowed
  )


BIOLOGY_MICRO_IMAGES = _load_micro_images()


def _load_past_papers() -> dict:
    """Scan each subject's pastpapers/ folder and return {SubjectName: [paths]}."""
    subjects_map = {
        "English": "english",
        "Irish": "irish",
        "Maths": "maths",
        "DCG": "dcg",
        "Art": "art",
        "Spanish": "spanish",
        "Biology": "biology",
    }
    allowed = {".pdf", ".mp3", ".wav", ".ogg", ".m4a"}
    result = {}
    for label, folder_name in subjects_map.items():
        folder = os.path.join(STATIC_BASE, folder_name, "pastpapers")
        if not os.path.isdir(folder):
            result[label] = []
            continue
        result[label] = sorted(
            f"{folder_name}/pastpapers/{name}"
            for name in os.listdir(folder)
            if os.path.splitext(name)[1].lower() in allowed
        )
    return result


PAST_PAPERS = _load_past_papers()

SUBJECTS = ["English", "Irish", "Maths", "DCG", "Art", "Spanish", "Biology"]

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
<title>Study — Léann</title>
<style>
  :root{
    --bg:#f6f7fb;
    --bg-2:#eef1f8;
    --ink:#0f172a;
    --muted:#64748b;
    --card:#ffffff;
    --line:#e6e8ef;
    --brand:#4f46e5;
    --brand-2:#7c3aed;
    --past:#0ea5e9;     /* slide right -> past */
    --future:#10b981;   /* slide left  -> future */
    --shadow:0 10px 30px rgba(15,23,42,.08), 0 2px 8px rgba(15,23,42,.04);
    --radius:18px;
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  body{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
    color:var(--ink);
    background:
      radial-gradient(1200px 600px at 10% -10%, #e9e7ff 0%, transparent 60%),
      radial-gradient(900px 500px at 110% 10%, #dcfce7 0%, transparent 55%),
      var(--bg);
    min-height:100vh;
    -webkit-font-smoothing:antialiased;
  }
  header{
    position:sticky;top:0;z-index:10;
    backdrop-filter:saturate(140%) blur(10px);
    background:rgba(246,247,251,.75);
    border-bottom:1px solid var(--line);
  }
  .wrap{max-width:1100px;margin:0 auto;padding:18px 20px}
  .brand{display:flex;align-items:center;gap:12px}
  .brand .logo{
    width:36px;height:36px;border-radius:10px;
    background:linear-gradient(135deg,var(--brand),var(--brand-2));
    display:grid;place-items:center;color:#fff;font-weight:700;
    box-shadow:var(--shadow);
  }
  .brand h1{font-size:18px;margin:0;letter-spacing:.2px}
  .brand small{color:var(--muted)}
  nav.tabs{
    display:flex;gap:6px;overflow-x:auto;padding:10px 16px 14px;
    scrollbar-width:none;-webkit-overflow-scrolling:touch;
  }
  nav.tabs::-webkit-scrollbar{display:none}
  .tab{
    flex:0 0 auto;
    padding:11px 16px;border-radius:999px;border:1px solid var(--line);
    background:#fff;color:var(--ink);font-weight:600;font-size:14px;
    cursor:pointer;transition:.2s ease;min-height:44px;
    -webkit-tap-highlight-color:transparent;
  }
  .tab:hover{transform:translateY(-1px)}
  .tab.active{
    background:linear-gradient(135deg,var(--brand),var(--brand-2));
    color:#fff;border-color:transparent;box-shadow:var(--shadow);
  }
  main{padding:8px 16px 80px}
  .hero{
    max-width:1100px;margin:14px auto 18px;
    display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap;
  }
  .hero h2{margin:0;font-size:26px;letter-spacing:-.2px}
  .hero p{margin:4px 0 0;color:var(--muted);font-size:14px}
  .hint{
    font-size:13px;color:var(--muted);background:#fff;border:1px solid var(--line);
    padding:8px 14px;border-radius:999px;box-shadow:var(--shadow);
    display:none;
  }
  .hint.visible{display:inline-block}
  .hint b{color:var(--past)}
  .hint i{color:var(--future);font-style:normal}
  .grid{
    max-width:1100px;margin:0 auto;
    display:grid;gap:16px;
    grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
  }
  .stage{
    position:relative;height:220px;border-radius:var(--radius);
    overflow:hidden;
    background:linear-gradient(180deg,#fafbff,#eef1f8);
    border:1px solid var(--line);
    touch-action:pan-y;
  }
  /* Reveal layers behind the card */
  .reveal{
    position:absolute;inset:0;display:flex;align-items:center;
    padding:18px 22px;font-weight:700;color:#fff;letter-spacing:.3px;
    opacity:0;transition:opacity .15s ease;pointer-events:none;
    font-size:14px;text-transform:uppercase;
  }
  .reveal.past{justify-content:flex-start;background:linear-gradient(90deg,var(--past),#38bdf8)}
  .reveal.future{justify-content:flex-end;background:linear-gradient(270deg,var(--future),#34d399)}
  .reveal .badge{
    background:rgba(255,255,255,.2);padding:6px 10px;border-radius:999px;
    border:1px solid rgba(255,255,255,.35);
  }
  .card{
    position:absolute;inset:0;
    background:var(--card);border-radius:var(--radius);
    box-shadow:var(--shadow);
    padding:18px 18px 44px;
    display:flex;flex-direction:column;gap:10px;
    cursor:grab;user-select:none;touch-action:pan-y;
    transition:transform .35s cubic-bezier(.2,.8,.2,1), box-shadow .2s;
    will-change:transform;
  }
  .card.dragging{transition:none;cursor:grabbing}
  .card .top{display:flex;align-items:center;justify-content:space-between}
  .verb{font-size:13px;color:var(--muted);font-weight:600;letter-spacing:.2px}
  .verb b{color:var(--ink)}
  .num{
    font-size:11px;color:var(--muted);background:var(--bg-2);
    padding:3px 8px;border-radius:999px;
  }
  .icon{font-size:64px;line-height:1;margin:6px 0 4px}
  .sentence{font-size:18px;font-weight:600;line-height:1.35;min-height:50px}
  .tense{
    margin-top:auto;display:flex;align-items:center;gap:8px;
    font-size:12px;color:var(--muted);
  }
  .pill{
    padding:4px 10px;border-radius:999px;font-weight:700;font-size:11px;
    text-transform:uppercase;letter-spacing:.4px;
    background:var(--bg-2);color:var(--ink);
  }
  .pill.past{background:rgba(14,165,233,.12);color:#0369a1}
  .pill.future{background:rgba(16,185,129,.12);color:#047857}
  .arrows{margin-left:auto;color:#cbd5e1;font-size:12px}
  .reset-btn{
    position:absolute;right:10px;bottom:10px;
    display:inline-flex;align-items:center;justify-content:center;
    border:1px solid #c7d2fe;border-radius:999px;padding:6px 10px;
    background:#eef2ff;color:#312e81;font-size:11px;font-weight:900;
    cursor:pointer;-webkit-tap-highlight-color:transparent;
    opacity:.85;box-shadow:0 1px 2px rgba(15,23,42,.08);
  }
  .reset-btn.active{opacity:1;background:#e0e7ff;border-color:#a5b4fc}
  .reset-btn:disabled{cursor:default;opacity:.78}
  .placeholder{
    max-width:1100px;margin:40px auto;text-align:center;color:var(--muted);
    background:#fff;border:1px dashed var(--line);border-radius:var(--radius);
    padding:60px 24px;
  }
  .placeholder h3{margin:0 0 6px;color:var(--ink)}
  @media (max-width:520px){
    .hero{flex-direction:column;align-items:flex-start;gap:8px}
    .hero h2{font-size:20px}
    .stage{height:210px}
    .icon{font-size:50px}
    .sentence{font-size:15px}
    .hint{font-size:12px;padding:7px 12px}
    .modal-body{max-height:72vh}
    .modal-hero{flex-wrap:wrap;gap:14px;padding:18px}
    .maths-wrap{gap:22px}
    .qa-qtext{font-size:14px}
    .qa-ans{padding:6px 14px 16px 14px}
    .shelf{gap:20px}
    .book-wrap{width:140px}
    .book-cover{width:140px;height:192px}
  }
  @media (hover:none){
    .tab:hover{transform:none}
    .book-wrap:hover .book-cover{transform:none;box-shadow:4px 6px 20px rgba(15,23,42,.18),-3px 0 0 #c4b5fd inset}
  }  /* ── English purple/violet theme ──────────────────── */
  body.english .tab.active{
    background:linear-gradient(135deg,#7c3aed,#6d28d9);
    box-shadow:0 0 0 3px rgba(124,58,237,.18),var(--shadow);
  }
  /* Bookshelf */
  .shelf{
    max-width:1100px;margin:0 auto;
    display:flex;flex-wrap:wrap;gap:28px;
  }
  .book-wrap{
    display:flex;flex-direction:column;align-items:center;gap:10px;
    cursor:pointer;width:160px;
  }
  .book-wrap:hover .book-cover{transform:translateY(-6px) scale(1.03);box-shadow:0 20px 48px rgba(124,58,237,.22);}
  .book-cover{
    width:160px;height:220px;border-radius:8px;
    object-fit:cover;display:block;
    box-shadow:4px 6px 20px rgba(15,23,42,.18), -3px 0 0 #c4b5fd inset;
    transition:transform .3s ease,box-shadow .3s ease;
  }
  .book-label{
    font-size:13px;font-weight:700;color:var(--ink);text-align:center;line-height:1.3;
  }
  .book-label small{display:block;font-weight:400;color:var(--muted);font-size:11px;margin-top:2px}
  /* Modal reader */
  .modal-bg{
    position:fixed;inset:0;z-index:100;
    background:rgba(15,23,42,.55);
    backdrop-filter:blur(6px);
    display:flex;align-items:flex-start;justify-content:center;
    padding:24px 16px 40px;
    overflow-y:auto;
    opacity:0;pointer-events:none;
    transition:opacity .25s ease;
  }
  .modal-bg.open{opacity:1;pointer-events:auto;}
  .modal{
    background:#fff;border-radius:20px;
    box-shadow:0 30px 80px rgba(15,23,42,.25);
    width:100%;max-width:740px;
    overflow:hidden;
    transform:translateY(20px);
    transition:transform .28s cubic-bezier(.2,.8,.2,1);
  }
  .modal-bg.open .modal{transform:translateY(0);}
  .modal-hero{
    display:flex;gap:22px;align-items:flex-end;
    padding:28px 28px 22px;
    background:linear-gradient(135deg,#ede9fe,#f5f3ff);
    border-bottom:1px solid #e9d5ff;
  }
  .modal-cover{
    width:90px;height:124px;object-fit:cover;
    border-radius:6px;box-shadow:3px 4px 14px rgba(124,58,237,.25);
    flex-shrink:0;
  }
  .modal-meta h2{margin:0 0 4px;font-size:20px;color:#3b0764}
  .modal-meta p{margin:0;color:#7e22ce;font-size:13px;font-weight:600}
  .modal-close{
    margin-left:auto;align-self:flex-start;
    background:rgba(124,58,237,.12);border:none;border-radius:999px;
    color:#6d28d9;font-size:20px;line-height:1;
    width:36px;height:36px;cursor:pointer;
    display:grid;place-items:center;
    transition:background .2s;
  }
  .modal-close:hover{background:rgba(124,58,237,.22);}
  .modal-body{
    padding:26px 28px 32px;
    max-height:68vh;overflow-y:auto;
    font-size:15px;line-height:1.7;color:var(--ink);
  }
  .modal-body::-webkit-scrollbar{width:4px}
  .modal-body::-webkit-scrollbar-thumb{background:#c4b5fd;border-radius:4px}
  .notes-section{margin:0 0 22px}
  .notes-h1{
    font-size:19px;font-weight:800;color:#3b0764;
    margin:28px 0 10px;padding-bottom:6px;
    border-bottom:2px solid #e9d5ff;
  }
  .notes-h1:first-child{margin-top:0}
  .notes-h2{font-size:15px;font-weight:700;color:#6d28d9;margin:16px 0 6px}
  .notes-p{margin:0 0 8px}
  .notes-ul{margin:0 0 10px;padding-left:20px}
  .notes-ul li{margin:2px 0}
  .exam-tip{
    background:linear-gradient(135deg,#fdf4ff,#f5f3ff);
    border-left:3px solid #a855f7;
    padding:10px 14px;border-radius:0 8px 8px 0;
    margin:10px 0 14px;font-size:13px;font-weight:600;color:#581c87;
  }
  .exam-tip::before{content:'📝 Exam Point: ';font-weight:800}
  .quote-block{
    background:#fdf4ff;border:1px solid #e9d5ff;
    border-radius:10px;padding:12px 16px;margin:10px 0;
    font-style:italic;color:#4c1d95;font-size:14px;
  }  /* ── Spanish orange theme ────────────────────────── */
  body.spanish .tab.active{
    background:linear-gradient(135deg,#f97316,#ea580c);
    box-shadow:0 0 0 3px rgba(249,115,22,.18),var(--shadow);
  }
  body.spanish .stage{
    border-color:rgba(249,115,22,.28);
    box-shadow:0 0 0 1px rgba(249,115,22,.12),0 8px 28px rgba(249,115,22,.12);
  }
  body.spanish .card{background:linear-gradient(160deg,#ffffff 60%,#fff7ed)}
  body.spanish .pill{background:rgba(249,115,22,.1);color:#c2410c}
  body.spanish .pill.past{background:rgba(14,165,233,.12);color:#0369a1}
  body.spanish .pill.future{background:rgba(16,185,129,.12);color:#047857}
  /* ── Maths teal theme ─────────────────────────────── */
  body.maths .tab.active{
    background:linear-gradient(135deg,#0d9488,#059669);
    box-shadow:0 0 0 3px rgba(13,148,136,.18),var(--shadow);
  }
  .maths-wrap{max-width:1100px;margin:0 auto;display:flex;flex-direction:column;gap:32px}
  .maths-section-title{font-size:22px;font-weight:800;color:#134e4a;margin:0 0 4px}
  .maths-section-sub{color:var(--muted);margin:0 0 18px;font-size:14px}
  .concept-list{display:flex;flex-direction:column;gap:8px}
  .concept-item{border:1px solid #99f6e4;border-radius:14px;background:#fff;overflow:hidden}
  .concept-hdr{
    display:flex;align-items:center;gap:12px;padding:14px 18px;cursor:pointer;
    font-weight:700;font-size:15px;color:#0f766e;list-style:none;user-select:none;
  }
  .concept-hdr::-webkit-details-marker{display:none}
  .concept-hdr .c-icon{
    width:36px;height:36px;border-radius:10px;flex-shrink:0;font-size:18px;
    background:linear-gradient(135deg,#ccfbf1,#99f6e4);display:grid;place-items:center;
  }
  .concept-hdr .c-chevron{margin-left:auto;color:#5eead4;transition:transform .22s;font-size:18px}
  details[open] .concept-hdr .c-chevron{transform:rotate(90deg)}
  .concept-body{
    padding:4px 18px 18px 66px;font-size:14px;line-height:1.7;color:var(--ink);
    border-top:1px solid #f0fdfa;
  }
  .formula{
    background:linear-gradient(135deg,#f0fdfa,#ccfbf1);border:1px solid #99f6e4;
    border-radius:10px;padding:10px 16px;margin:10px 0;
    font-family:ui-monospace,monospace;font-size:14px;color:#0f766e;font-weight:600;
  }
  .concept-body ul{margin:8px 0;padding-left:18px}
  .concept-body li{margin:3px 0}
  .qa-list{display:flex;flex-direction:column;gap:14px}
  .qa-card{background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:var(--shadow)}
  .qa-q{padding:16px 20px;cursor:pointer;display:flex;align-items:flex-start;gap:14px;user-select:none}
  .qa-q:hover{background:#f8fafc}
  .qa-num{
    flex-shrink:0;width:28px;height:28px;border-radius:999px;margin-top:2px;
    background:linear-gradient(135deg,#0d9488,#059669);color:#fff;
    font-weight:800;font-size:13px;display:grid;place-items:center;
  }
  .qa-qtext{flex:1;font-size:15px;font-weight:600;line-height:1.5}
  .qa-subtext{font-size:12px;color:var(--muted);font-weight:500;margin-top:3px}
  .qa-toggle{
    flex-shrink:0;border:none;background:none;color:#0d9488;
    font-size:24px;cursor:pointer;line-height:1;padding:0;margin-top:-2px;
    transition:transform .22s ease;
  }
  .qa-toggle.open{transform:rotate(45deg)}
  .qa-ans{
    display:none;padding:6px 20px 18px 62px;
    border-top:1px solid #f0fdfa;font-size:14px;line-height:1.7;
  }
  .qa-ans.open{display:block}
  .qa-ans p{margin:8px 0}
  .qa-ans .step{
    background:#f0fdfa;border-left:3px solid #0d9488;
    padding:8px 12px;border-radius:0 8px 8px 0;margin:6px 0;
  }
  .qa-ans .step b,.qa-ans .step strong{color:#0f766e}
  .qa-ans .answer{
    background:linear-gradient(135deg,#0d9488,#059669);
    color:#fff;border-radius:10px;padding:10px 16px;margin-top:12px;font-weight:700;
  }
  /* ── Biology micro page ───────────────────────────── */
  .bio-wrap{max-width:1100px;margin:0 auto;display:grid;gap:18px}
  .bio-banner{
    background:linear-gradient(135deg,#ecfeff,#f0fdf4);
    border:1px solid #bae6fd;border-radius:14px;padding:16px 18px;
  }
  .bio-banner h3{margin:0 0 4px;color:#134e4a;font-size:20px}
  .bio-banner p{margin:0;color:#0f766e;font-size:14px}
  .bio-note-card{
    background:#fff;border:1px solid var(--line);border-radius:14px;
    box-shadow:var(--shadow);padding:14px 16px;
  }
  .bio-note-card h4{margin:0 0 8px;color:#0f172a;font-size:16px}
  .bio-note-line{margin:0 0 6px;color:#334155;font-size:14px;line-height:1.6}
  .bio-tip{
    margin:10px 0 0;background:#ecfeff;border-left:3px solid #0891b2;
    color:#0f766e;padding:8px 10px;border-radius:0 8px 8px 0;font-size:13px;font-weight:700;
  }
  .bio-section{
    display:grid;grid-template-columns:minmax(0,1.35fr) minmax(220px,.9fr);
    gap:14px;align-items:stretch;
  }
  .bio-section--textonly{
    grid-template-columns:1fr;
  }
  .bio-media{
    margin:0;background:#fff;border:1px solid var(--line);border-radius:14px;
    overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column;
  }
  .bio-media img{display:block;width:100%;height:100%;min-height:220px;object-fit:cover}
  .bio-media figcaption{padding:8px 10px;font-size:12px;color:#475569;background:#fff}
  .bio-media .bio-media-tag{
    margin-top:auto;padding:8px 10px;background:#f8fafc;border-top:1px solid var(--line);
    font-size:12px;color:#0f766e;font-weight:700;
  }
  .bio-row{display:grid;gap:14px}
  .bio-row + .bio-row{margin-top:2px}
  .bio-empty{
    max-width:1100px;margin:18px auto 0;background:#fff7ed;color:#9a3412;
    border:1px solid #fed7aa;border-radius:12px;padding:12px 14px;font-size:14px;
  }
  @media (max-width:760px){
    .bio-section{grid-template-columns:1fr}
  }
  /* ── Art impressionism page ──────────────────────── */
  body.art .tab.active{
    background:linear-gradient(135deg,#f59e0b,#ea580c);
    box-shadow:0 0 0 3px rgba(245,158,11,.16),var(--shadow);
  }
  .art-wrap{max-width:1100px;margin:0 auto;display:grid;gap:18px}
  .art-banner{
    background:linear-gradient(135deg,#fff7ed,#fffbeb);
    border:1px solid #fed7aa;border-radius:16px;padding:16px 18px;
  }
  .art-banner h3{margin:0 0 4px;color:#7c2d12;font-size:20px}
  .art-banner p{margin:0;color:#9a3412;font-size:14px;line-height:1.6}
  .art-compare{
    display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:stretch;
  }
  .art-side{
    background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);
    padding:16px;
  }
  .art-side h4{margin:0 0 6px;font-size:17px}
  .art-side p{margin:0 0 10px;color:#334155;line-height:1.6;font-size:14px}
  .art-side .kicker{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.35px;margin-bottom:8px}
  .art-light .kicker{color:#0f766e}
  .art-structure .kicker{color:#7c2d12}
  .art-vs{display:grid;place-items:center;min-width:72px}
  .art-vs .vs-bubble{
    width:64px;height:64px;border-radius:999px;display:grid;place-items:center;
    background:linear-gradient(135deg,#fde68a,#fb923c);color:#7c2d12;font-weight:900;
    box-shadow:var(--shadow);border:1px solid #fdba74;
  }
  .art-bar{height:12px;border-radius:999px;background:#e2e8f0;overflow:hidden;margin:10px 0 0}
  .art-bar > span{display:block;height:100%;border-radius:999px}
  .art-bar.impressionism > span{width:78%;background:linear-gradient(90deg,#14b8a6,#38bdf8)}
  .art-bar.post > span{width:86%;background:linear-gradient(90deg,#f97316,#ef4444)}
  .art-chip-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
  .art-chip{padding:5px 10px;border-radius:999px;font-size:12px;font-weight:700;background:#f8fafc;color:#334155;border:1px solid #e2e8f0}
  .art-panel{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);padding:16px}
  .art-grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
  .art-card{background:linear-gradient(180deg,#fff,#fffaf2);border:1px solid #fee2b3;border-radius:14px;padding:14px}
  .art-card h4{margin:0 0 8px;font-size:16px;color:#7c2d12}
  .art-card p{margin:0;color:#334155;font-size:14px;line-height:1.6}
  .art-artist{display:flex;align-items:center;gap:10px;margin-bottom:8px}
  .art-artist .badge{
    width:38px;height:38px;border-radius:12px;display:grid;place-items:center;
    background:#ffedd5;color:#c2410c;font-size:18px;flex-shrink:0;
  }
  .art-quote{
    background:linear-gradient(135deg,#fff7ed,#fffbeb);border-left:3px solid #f59e0b;
    padding:10px 12px;border-radius:0 10px 10px 0;font-size:13px;font-weight:700;color:#9a3412;
  }
  .art-comparison{display:grid;gap:10px;grid-template-columns:1fr auto 1fr auto 1fr;align-items:center}
  .art-step{
    background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:10px 8px;text-align:center;
    font-size:12px;color:#334155;font-weight:700;min-height:72px;display:grid;place-items:center;
  }
  .art-step em{display:block;font-style:normal;color:#7c2d12;font-weight:800;margin-top:4px}
  .art-mini-arrow{color:#fb923c;font-weight:900;font-size:22px;text-align:center}
  .art-small-title{font-size:19px;font-weight:800;color:#7c2d12;margin:0 0 4px}
  .art-small-sub{margin:0 0 12px;color:var(--muted);font-size:14px}
  @media (max-width:760px){
    .art-compare,.art-comparison{grid-template-columns:1fr}
    .art-vs{min-width:0}
    .art-mini-arrow{transform:rotate(90deg)}
  }
  /* ── DCG dynamic mechanisms page ─────────────────── */
  body.dcg .tab.active{
    background:linear-gradient(135deg,#2563eb,#0f766e);
    box-shadow:0 0 0 3px rgba(37,99,235,.15),var(--shadow);
  }
  .dcg-wrap{max-width:1100px;margin:0 auto;display:grid;gap:18px}
  .dcg-banner{
    background:linear-gradient(135deg,#eff6ff,#ecfeff);
    border:1px solid #bfdbfe;border-radius:16px;padding:16px 18px;
  }
  .dcg-banner h3{margin:0 0 4px;color:#0f172a;font-size:20px}
  .dcg-banner p{margin:0;color:#334155;font-size:14px;line-height:1.6}
  .dcg-flow{
    display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:10px;align-items:center;
  }
  .dcg-node{
    background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);
    padding:14px 12px;text-align:center;min-height:96px;display:grid;place-items:center;gap:6px;
  }
  .dcg-node .label{font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:.35px}
  .dcg-node .value{font-size:16px;font-weight:800;color:#0f172a}
  .dcg-arrow{font-size:30px;color:#0ea5e9;font-weight:800}
  .dcg-grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
  .dcg-card{
    background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);
    padding:14px 14px 12px;
  }
  .dcg-card h4{margin:0 0 8px;font-size:16px;color:#0f172a}
  .dcg-card p{margin:0 0 8px;color:#334155;font-size:14px;line-height:1.6}
  .dcg-chip-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
  .dcg-chip{padding:5px 10px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px;font-weight:700}
  .dcg-motion-grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
  .dcg-motion{
    background:linear-gradient(180deg,#ffffff,#f8fbff);
    border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:14px;
  }
  .dcg-motion .motion-top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px}
  .dcg-motion .motion-top strong{font-size:15px;color:#0f172a}
  .dcg-motion .motion-badge{width:36px;height:36px;border-radius:12px;display:grid;place-items:center;background:#dbeafe;color:#1d4ed8;font-size:18px}
  .dcg-mini-arrow{display:block;text-align:center;color:#94a3b8;font-weight:800;margin:8px 0;font-size:18px}
  .dcg-example-rail{
    display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  }
  .dcg-example{
    background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:14px;
  }
  .dcg-example .example-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px}
  .dcg-example .example-head strong{font-size:15px;color:#0f172a}
  .dcg-example .example-icon{font-size:22px}
  .dcg-seq{display:grid;gap:8px;grid-template-columns:1fr auto 1fr auto 1fr;align-items:center;margin-top:10px}
  .dcg-step{
    background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:10px 8px;text-align:center;
    font-size:12px;color:#334155;font-weight:700;min-height:70px;display:grid;place-items:center;
  }
  .dcg-step em{display:block;font-style:normal;color:#0f172a;font-weight:800;margin-top:4px}
  .dcg-section-title{font-size:19px;font-weight:800;color:#0f172a;margin:0 0 4px}
  .dcg-section-sub{margin:0 0 12px;color:var(--muted);font-size:14px}
  @media (max-width:760px){
    .dcg-flow,.dcg-seq{grid-template-columns:1fr;}
    .dcg-arrow,.dcg-mini-arrow{transform:rotate(90deg);font-size:24px}
  }
  /* ── Back button ─────────────────────────────────── */
  .back-btn{
    display:inline-flex;align-items:center;gap:6px;
    padding:8px 16px;border-radius:999px;border:1px solid var(--line);
    background:#fff;color:var(--ink);font-weight:600;font-size:13px;
    cursor:pointer;transition:.15s ease;box-shadow:var(--shadow);
    -webkit-tap-highlight-color:transparent;
  }
  .back-btn:hover{transform:translateX(-2px)}
  /* ── Subject home pages ──────────────────────────── */
  .home-wrap{max-width:1100px;margin:0 auto}
  .home-banner{
    background:linear-gradient(135deg,var(--bg),var(--bg-2));
    border:1px solid var(--line);border-radius:18px;
    padding:24px 26px;margin-bottom:20px;
  }
  .home-banner h3{margin:0 0 4px;font-size:22px}
  .home-banner p{margin:0;color:var(--muted);font-size:14px}
  .home-grid{
    display:grid;gap:16px;
    grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  }
  .home-card{
    background:#fff;border:1px solid var(--line);border-radius:18px;
    box-shadow:var(--shadow);padding:24px;cursor:pointer;
    transition:transform .2s ease,box-shadow .2s ease;
    display:flex;flex-direction:column;gap:10px;
    -webkit-tap-highlight-color:transparent;
  }
  .home-card:hover{
    transform:translateY(-4px);
    box-shadow:0 20px 48px rgba(15,23,42,.12),0 4px 12px rgba(15,23,42,.06);
  }
  .hc-icon{font-size:40px;line-height:1}
  .hc-title{font-size:18px;font-weight:800;color:var(--ink)}
  .hc-desc{font-size:14px;color:var(--muted);line-height:1.5}
  .hc-arrow{margin-top:auto;font-size:20px;color:var(--brand);font-weight:900;align-self:flex-end}
  .home-card.pp-card{border-color:#c7d2fe;background:linear-gradient(160deg,#fff,#eef2ff)}
  .home-card.pp-card .hc-arrow{color:var(--brand-2)}
  /* ── Past papers page ────────────────────────────── */
  .pp-wrap{max-width:1100px;margin:0 auto;display:grid;gap:20px}
  .pp-year-label{font-size:16px;font-weight:800;color:var(--ink);margin:0 0 10px}
  .pp-file-list{display:flex;flex-direction:column;gap:8px}
  .pp-file-row{
    display:flex;align-items:center;gap:14px;
    background:#fff;border:1px solid var(--line);border-radius:14px;
    padding:14px 16px;cursor:pointer;box-shadow:var(--shadow);
    transition:transform .15s ease,box-shadow .15s ease;
    -webkit-tap-highlight-color:transparent;
  }
  .pp-file-row:hover{transform:translateX(4px);box-shadow:0 8px 24px rgba(15,23,42,.1)}
  .pp-file-icon{
    width:44px;height:44px;border-radius:12px;
    display:grid;place-items:center;font-size:22px;flex-shrink:0;
  }
  .pp-file-icon.pdf{background:rgba(239,68,68,.1);color:#dc2626}
  .pp-file-icon.audio{background:rgba(16,185,129,.1);color:#059669}
  .pp-file-name{font-size:15px;font-weight:600;color:var(--ink);flex:1}
  .pp-file-meta{font-size:12px;color:var(--muted);font-weight:600;background:var(--bg-2);padding:3px 8px;border-radius:999px}
  .pp-file-open{font-size:20px;color:#94a3b8;font-weight:900}
  /* ── File viewer modal ───────────────────────────── */
  .fv-bg{
    position:fixed;inset:0;z-index:200;
    background:rgba(15,23,42,.85);
    backdrop-filter:blur(8px);
    display:flex;flex-direction:column;
    opacity:0;pointer-events:none;
    transition:opacity .25s ease;
  }
  .fv-bg.open{opacity:1;pointer-events:auto}
  .fv-header{
    display:flex;align-items:center;gap:14px;
    padding:14px 20px;background:rgba(15,23,42,.95);color:#fff;flex-shrink:0;
  }
  .fv-header-title{
    flex:1;font-weight:700;font-size:15px;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  }
  .fv-close{
    background:rgba(255,255,255,.15);border:none;border-radius:999px;
    color:#fff;font-size:22px;width:38px;height:38px;
    cursor:pointer;display:grid;place-items:center;flex-shrink:0;
    transition:background .2s;
  }
  .fv-close:hover{background:rgba(255,255,255,.28)}
  .fv-open-btn{
    background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:999px;
    color:#fff;font-size:13px;font-weight:700;padding:6px 14px;
    cursor:pointer;white-space:nowrap;flex-shrink:0;
    transition:background .2s;text-decoration:none;display:inline-flex;align-items:center;gap:6px;
  }
  .fv-open-btn:hover{background:rgba(255,255,255,.24)}
  .fv-body{flex:1;display:flex;flex-direction:column;overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;background:#1e293b}
  .fv-body iframe{width:100%;height:300vh;border:none;display:block}
  .fv-audio-wrap{
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    gap:24px;padding:40px 24px;flex:1;
  }
  .fv-audio-icon{font-size:80px;line-height:1}
  .fv-audio-label{font-size:20px;font-weight:700;color:#e2e8f0;text-align:center;max-width:480px}
  .fv-audio-wrap audio{width:100%;max-width:480px;border-radius:12px;margin-top:8px}
</style>
</head>
<body>
<header>
  <div class="wrap brand">
    <div class="logo">L</div>
    <div>
      <h1>Léann · Study</h1>
      <small>A simpler way to learn.</small>
    </div>
  </div>
  <nav class="tabs" id="tabs"></nav>
</header>

<main>
  <section class="hero">
    <div>
      <h2 id="title">Gaeilge — 50 Verbs</h2>
      <p id="subtitle">Default card shows the present tense.</p>
    </div>
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <button class="back-btn" id="heroBackBtn" style="display:none">&#8592; Back</button>
      <div class="hint" id="swipeHint">Slide <b>→ right</b> for past · Slide <i>← left</i> for future</div>
    </div>
  </section>
  <section id="content" class="grid"></section>
</main>

<!-- Modal reader (English) -->
<div class="modal-bg" id="modalBg" role="dialog" aria-modal="true">
  <div class="modal" id="modal">
    <div class="modal-hero">
      <img class="modal-cover" id="modalCover" src="" alt="" />
      <div class="modal-meta">
        <h2 id="modalTitle"></h2>
        <p id="modalAuthor"></p>
      </div>
      <button class="modal-close" id="modalClose" aria-label="Close">&times;</button>
    </div>
    <div class="modal-body" id="modalBody"></div>
  </div>
</div>

<!-- File viewer modal (PDFs + Audio) -->
<div class="fv-bg" id="fvBg" role="dialog" aria-modal="true">
  <div class="fv-header">
    <span class="fv-header-title" id="fvTitle"></span>
    <a class="fv-open-btn" id="fvOpenBtn" href="#" target="_blank" rel="noopener">&#8599; Open</a>
    <button class="fv-close" id="fvClose" aria-label="Close">&times;</button>
  </div>
  <div class="fv-body" id="fvBody"></div>
</div>

<script>
const SUBJECTS = __SUBJECTS__;
const VERBS = __VERBS__;
const SPANISH_VERBS = __SPANISH_VERBS__;
const BIOLOGY_MICRO_IMAGES = __BIOLOGY_MICRO_IMAGES__;
const PAST_PAPERS = __PAST_PAPERS__;

const tabs = document.getElementById('tabs');
const content = document.getElementById('content');
const title = document.getElementById('title');
const subtitle = document.getElementById('subtitle');

let active = 'Irish';
let activeView = 'home';

// ── File viewer modal ────────────────────────────────────────
const fvBg    = document.getElementById('fvBg');
const fvTitle = document.getElementById('fvTitle');
const fvBody  = document.getElementById('fvBody');
const fvOpenBtn = document.getElementById('fvOpenBtn');
document.getElementById('fvClose').addEventListener('click', closeFileViewer);
fvBg.addEventListener('click', e => { if(e.target === fvBg) closeFileViewer(); });

function openFileViewer(path, type){
  fvTitle.textContent = prettyFile(path);
  fvOpenBtn.href = path;
  fvBody.innerHTML = '';
  if(type === 'pdf'){
    const iframe = document.createElement('iframe');
    iframe.src = path;
    fvBody.appendChild(iframe);
  } else {
    const wrap = document.createElement('div');
    wrap.className = 'fv-audio-wrap';
    wrap.innerHTML =
      '<div class="fv-audio-icon">🔊</div>' +
      '<div class="fv-audio-label">' + escapeHtml(prettyFile(path)) + '</div>' +
      '<audio controls autoplay src="' + escapeHtml(path) + '"></audio>';
    fvBody.appendChild(wrap);
  }
  fvBg.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeFileViewer(){
  fvBg.classList.remove('open');
  document.body.style.overflow = '';
  fvBody.innerHTML = '';
}

function prettyFile(path){
  const name = path.split('/').pop().replace(/\.[^.]+$/, '');
  const knownSubjects = ['english','irish','maths','dcg','art','spanish','biology'];
  const parts = name.split('-');
  const start = knownSubjects.includes(parts[0].toLowerCase()) ? 1 : 0;
  return parts.slice(start).map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
}

// ── Subject home page configuration ─────────────────────────
const SUBJECT_HOMES = {
  'Irish': {
    banner: { title:'Gaeilge', desc:'Irish language revision — verb flashcards and past exam papers.' },
    topics: [
      { key:'irish-verbs', icon:'🃏', title:'Briathra · 50 Verbs', desc:'Swipeable flashcards covering present, past and future tenses for 50 essential verbs.' },
      { key:'pastpapers', icon:'📄', title:'Past Papers', desc:'Leaving Cert Irish papers (Paper 1 & 2) and listening audio files from recent years.', isPP:true },
    ]
  },
  'Spanish': {
    banner: { title:'Español', desc:'Spanish language revision — verb flashcards and past exam papers.' },
    topics: [
      { key:'spanish-verbs', icon:'🃏', title:'Verbos · 50 Verbs', desc:'Swipeable flashcards covering present, preterite and future tenses for 50 essential verbs.' },
      { key:'pastpapers', icon:'📄', title:'Past Papers', desc:'Leaving Cert Spanish papers and aural audio files from recent years.', isPP:true },
    ]
  },
  'Maths': {
    banner: { title:'Mathematics', desc:'Maths revision for Leaving Certificate Ordinary Level.' },
    topics: [
      { key:'maths-stats', icon:'📊', title:'Statistics & Probability', desc:'Key concepts, formulas and 10 fully worked Ordinary Level practice questions with step-by-step solutions.' },
      { key:'pastpapers', icon:'📄', title:'Past Papers', desc:'Leaving Cert Maths papers (Paper 1 & Paper 2) from recent years.', isPP:true },
    ]
  },
  'DCG': {
    banner: { title:'Design & Communication Graphics', desc:'DCG revision — dynamic mechanisms and past exam papers.' },
    topics: [
      { key:'dcg-mechanisms', icon:'⚙️', title:'Dynamic Mechanisms', desc:'Motion types, mechanism examples and key exam vocabulary with visual input→mechanism→output flow diagrams.' },
      { key:'pastpapers', icon:'📄', title:'Past Papers', desc:'Leaving Cert DCG papers (Section A & B/C) from recent years.', isPP:true },
    ]
  },
  'Art': {
    banner: { title:'Art History & Appreciation', desc:'Art revision — style comparisons, key artists and past exam papers.' },
    topics: [
      { key:'art-impressionism', icon:'🎨', title:'Impressionism vs Post-Impressionism', desc:'Visual comparison of the two movements, key artists and phrases you need for exam answers.' },
      { key:'pastpapers', icon:'📄', title:'Past Papers', desc:'Leaving Cert Art papers and illustration papers from recent years.', isPP:true },
    ]
  },
  'Biology': {
    banner: { title:'Biology', desc:'Biology revision — microbiology notes with diagrams and past exam papers.' },
    topics: [
      { key:'bio-micro', icon:'🔬', title:'Microbiology', desc:'One-page revision guide built from your micro notes with matched cell diagrams and exam tips.' },
      { key:'pastpapers', icon:'📄', title:'Past Papers', desc:'Leaving Cert Biology papers (A and B/C sections) from recent years.', isPP:true },
    ]
  },
  'English': {
    banner: { title:'English', desc:'English revision — novel study notes and past exam papers.' },
    topics: [
      { key:'english-books', icon:'📚', title:'Books & Notes', desc:'Study notes for prescribed texts, including Purple Hibiscus by Chimamanda Ngozi Adichie.' },
      { key:'pastpapers', icon:'📄', title:'Past Papers', desc:'Leaving Cert English papers (Paper 1 & Paper 2) from recent years.', isPP:true },
    ]
  },
};

function renderHome(subject){
  const config = SUBJECT_HOMES[subject];
  if(!config) return;
  title.textContent = config.banner.title;
  subtitle.textContent = config.banner.desc;
  content.className = '';
  let h = '<div class="home-wrap"><div class="home-grid">';
  config.topics.forEach(t => {
    h += '<div class="home-card' + (t.isPP ? ' pp-card' : '') + '" data-topic="' + t.key + '">';
    h += '<div class="hc-icon">' + t.icon + '</div>';
    h += '<div class="hc-title">' + t.title + '</div>';
    h += '<div class="hc-desc">' + t.desc + '</div>';
    h += '<div class="hc-arrow">→</div>';
    h += '</div>';
  });
  h += '</div></div>';
  content.innerHTML = h;
  content.querySelectorAll('.home-card').forEach(card => {
    card.addEventListener('click', () => { activeView = card.dataset.topic; renderTabs(); renderContent(); });
  });
}

function renderPastPapers(subject){
  const files = PAST_PAPERS[subject] || [];
  title.textContent = subject + ' — Past Papers';
  subtitle.textContent = 'Click a file to open it. PDFs open inline; audio plays in the browser.';
  content.className = '';
  if(!files.length){
    content.innerHTML = '<div class="bio-empty">No past papers found for ' + subject + '.</div>';
    return;
  }
  const groups = {};
  files.forEach(path => {
    const m = path.match(/(\d{4})\./);
    const year = m ? m[1] : 'Other';
    if(!groups[year]) groups[year] = [];
    groups[year].push(path);
  });
  let h = '<div class="pp-wrap">';
  Object.keys(groups).sort().reverse().forEach(year => {
    h += '<div><div class="pp-year-label">' + year + '</div><div class="pp-file-list">';
    groups[year].forEach(path => {
      const ext = path.split('.').pop().toLowerCase();
      const isPdf = ext === 'pdf';
      const iconClass = isPdf ? 'pdf' : 'audio';
      const icon = isPdf ? '📄' : '🔊';
      h += '<div class="pp-file-row" data-path="' + escapeHtml(path) + '" data-type="' + (isPdf ? 'pdf' : 'audio') + '">';
      h += '<div class="pp-file-icon ' + iconClass + '">' + icon + '</div>';
      h += '<div class="pp-file-name">' + escapeHtml(prettyFile(path)) + '</div>';
      h += '<div class="pp-file-meta">' + ext.toUpperCase() + '</div>';
      h += '<div class="pp-file-open">›</div>';
      h += '</div>';
    });
    h += '</div></div>';
  });
  h += '</div>';
  content.innerHTML = h;
  content.querySelectorAll('.pp-file-row').forEach(row => {
    row.addEventListener('click', () => openFileViewer(row.dataset.path, row.dataset.type));
  });
}

const ENGLISH_BOOKS = [
  {
    title: 'Purple Hibiscus',
    author: 'Chimamanda Ngozi Adichie',
    cover: 'english/purple_hibiscus/cover.jpg',
    notes: 'english/purple_hibiscus/notes.txt',
  },
];

// Modal logic
const modalBg   = document.getElementById('modalBg');
const modalClose = document.getElementById('modalClose');
const modalCover = document.getElementById('modalCover');
const modalTitle = document.getElementById('modalTitle');
const modalAuthor = document.getElementById('modalAuthor');
const modalBody  = document.getElementById('modalBody');

function openBook(book){
  modalCover.src = book.cover;
  modalCover.alt = book.title + ' cover';
  modalTitle.textContent = book.title;
  modalAuthor.textContent = book.author;
  modalBody.innerHTML = '<p style="color:#a78bfa">Loading notes…</p>';
  modalBg.classList.add('open');
  document.body.style.overflow = 'hidden';
  fetch(book.notes)
    .then(r => r.text())
    .then(txt => { modalBody.innerHTML = parseNotes(txt); })
    .catch(() => { modalBody.innerHTML = '<p>Could not load notes.</p>'; });
}
function closeBook(){
  modalBg.classList.remove('open');
  document.body.style.overflow = '';
}
modalClose.addEventListener('click', closeBook);
modalBg.addEventListener('click', e => { if(e.target === modalBg) closeBook(); });
document.addEventListener('keydown', e => { if(e.key === 'Escape'){ closeBook(); closeFileViewer(); } });

function parseNotes(txt){
  const lines = txt.split('\n');
  let html = '';
  let inUl = false;
  const closeUl = () => { if(inUl){ html += '</ul>'; inUl = false; } };

  const isHeading = l => {
    // All-caps words, or short lines with no trailing punctuation that look like titles
    if(!l.trim()) return false;
    if(/^(Key Themes|Important Characters|Symbols|Style and Techniques|Quotes to Learn|Sample Exam Points|Overview|Plot Summary)/.test(l)) return 'h1';
    if(/^\d+\.\s/.test(l) || /^(Why|How|Discuss|For the Leaving)/.test(l)) return 'h2';
    if(/^(Exam Point:|Exam phrase:|Exam Point$)/.test(l.trim())) return 'exam';
    return false;
  };

  for(let i=0; i<lines.length; i++){
    const raw = lines[i];
    const l = raw.trim();
    if(!l){ closeUl(); html += ''; continue; }
    const h = isHeading(l);
    if(h === 'h1'){ closeUl(); html += `<div class="notes-h1">${l}</div>`; continue; }
    if(h === 'h2'){ closeUl(); html += `<div class="notes-h2">${l}</div>`; continue; }
    if(h === 'exam'){
      closeUl();
      // peek ahead for the exam text
      const next = lines[i+1] ? lines[i+1].trim() : '';
      const body = next && !isHeading(next) ? next : '';
      if(body){ i++; }
      html += `<div class="exam-tip">${body}</div>`;
      continue;
    }
    // quoted lines
    if(l.startsWith('"') && l.endsWith('"')){
      closeUl();
      html += `<div class="quote-block">${l}</div>`;
      continue;
    }
    // short lines (likely bullet items when under a heading)
    if(l.length < 80 && !l.endsWith('.') && !l.endsWith(':') && i > 0 && !isHeading(lines[i-1] ? lines[i-1].trim() : '')){
      if(!inUl){ html += '<ul class="notes-ul">'; inUl = true; }
      html += `<li>${l}</li>`;
    } else {
      closeUl();
      html += `<p class="notes-p">${l}</p>`;
    }
  }
  closeUl();
  return html;
}

function escapeHtml(s){
  return s
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function titleFromFilename(name){
  return name
    .replace(/\.[^.]+$/, '')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

function bioImageForTitle(title){
  const t = title.toLowerCase();
  if(t.includes('bacterial cell structure')) return 'bacterial_cell.jpeg';
  if(t.includes('virus structure')) return 'virus.jpeg';
  if(t.includes('yeast cell')) return 'yeast_cell.jpeg';
  if(t.includes('microscopic plant vs animal cell')) return 'animal_plant_cell.jpeg';
  if(t.includes('bacterial reproduction')) return 'bacterial_cell.jpeg';
  return null;
}

function buildMicroPage(txt){
  const blocks = txt.split(/\n\s*\n/).map(b => b.trim()).filter(Boolean);
  let html = '<div class="bio-wrap">';
  html += '<section class="bio-banner"><h3>Mircobiology — One Pager</h3>';
  html += '<p>Built from your micro notes and diagram set.</p></section>';

  blocks.forEach(block => {
    const lines = block.split('\n').map(l => l.trim()).filter(Boolean);
    if(!lines.length) return;
    const first = lines[0];
    const imageName = bioImageForTitle(first);
    html += '<section class="bio-row">';
    html += '<div class="bio-section' + (imageName ? '' : ' bio-section--textonly') + '">';
    html += '<section class="bio-note-card">';
    html += '<h4>' + escapeHtml(first) + '</h4>';
    lines.slice(1).forEach(line => {
      if(/^\d+$/.test(line)) return;
      if(line.startsWith('👉')){
        html += '<div class="bio-tip">' + escapeHtml(line) + '</div>';
      } else {
        html += '<p class="bio-note-line">' + escapeHtml(line) + '</p>';
      }
    });
    html += '</section>';

    if(imageName){
      const safeName = encodeURIComponent(imageName);
      const caption = titleFromFilename(imageName);
      html += '<figure class="bio-media">';
      html += '<img loading="lazy" src="biology/micro/' + safeName + '" alt="' + escapeHtml(caption) + '" />';
      html += '<figcaption>' + escapeHtml(caption) + '</figcaption>';
      html += '<div class="bio-media-tag">Matched visual for this cell type</div>';
      html += '</figure>';
    }

    html += '</div></section>';
  });

  html += '</div>';
  return html;
}

function renderBiology(){
  title.textContent = 'Biology — Mircobiology';
  subtitle.textContent = 'One-page revision from micro.txt and your microbiology images.';
  content.className = '';
  content.innerHTML = '<div class="bio-empty">Loading microbiology notes…</div>';
  fetch('biology/micro/micro.txt')
    .then(r => {
      if(!r.ok) throw new Error('missing notes');
      return r.text();
    })
    .then(txt => { content.innerHTML = buildMicroPage(txt); })
    .catch(() => {
      content.innerHTML = '<div class="bio-empty">Could not load biology/micro.txt.</div>';
    });
}

function buildArtPage(txt){
  let html = '<div class="art-wrap">';
  html += '<section class="art-banner">';
  html += '<h3>Impressionism vs Post-Impressionism</h3>';
  html += '<p>This one-pager turns the notes into a quick visual comparison: light vs structure, observation vs interpretation, and the artists most likely to appear in exams.</p>';
  html += '</section>';

  html += '<section class="art-compare">';
  html += '<article class="art-side art-light">';
  html += '<div class="kicker">Impressionism</div>';
  html += '<h4>Capture a moment in time</h4>';
  html += '<p>Think <strong>light</strong>, <strong>colour</strong> and <strong>atmosphere</strong>. Artists painted outdoors and used loose, visible brushstrokes.</p>';
  html += '<div class="art-bar impressionism"><span></span></div>';
  html += '<div class="art-chip-row">';
  ['Plein air', 'Loose brushwork', 'Natural light', 'Everyday scenes'].forEach(chip => html += '<span class="art-chip">' + chip + '</span>');
  html += '</div></article>';
  html += '<div class="art-vs"><div class="vs-bubble">VS</div></div>';
  html += '<article class="art-side art-structure">';
  html += '<div class="kicker">Post-Impressionism</div>';
  html += '<h4>More emotion, structure and meaning</h4>';
  html += '<p>Think <strong>bold shapes</strong>, <strong>expressive colour</strong> and more personal interpretation. It reacts against pure observation.</p>';
  html += '<div class="art-bar post"><span></span></div>';
  html += '<div class="art-chip-row">';
  ['Structure', 'Emotion', 'Symbolic meaning', 'Personal interpretation'].forEach(chip => html += '<span class="art-chip">' + chip + '</span>');
  html += '</div></article>';
  html += '</section>';

  html += '<section class="art-panel">';
  html += '<div class="art-small-title">Quick visual comparison</div>';
  html += '<p class="art-small-sub">Use this sequence in answers to show how the two styles differ.</p>';
  html += '<div class="art-comparison">';
  html += '<div class="art-step">Light, air, moment<em>Impressionism</em></div>';
  html += '<div class="art-mini-arrow">→</div>';
  html += '<div class="art-step">Brushstroke, shape, colour<em>How it is painted</em></div>';
  html += '<div class="art-mini-arrow">→</div>';
  html += '<div class="art-step">Emotion, symbol, meaning<em>Post-Impressionism</em></div>';
  html += '</div>';
  html += '</section>';

  html += '<section class="art-panel">';
  html += '<div class="art-small-title">Key artists</div>';
  html += '<div class="art-grid">';
  [
    {icon:'🌤️', name:'Claude Monet', text:'Painted the same scene at different times to show changing light and atmosphere.'},
    {icon:'💃', name:'Edgar Degas', text:'Focused on dancers, movement and unusual viewpoints.'},
    {icon:'🌾', name:'Pierre-Auguste Renoir', text:'Used soft, warm colours for social scenes and people enjoying life.'},
    {icon:'🌋', name:'Vincent van Gogh', text:'Used swirling brushwork and intense colour to express emotion.'},
    {icon:'🧱', name:'Paul Cézanne', text:'Built forms with geometric shapes and influenced Cubism.'},
    {icon:'🌺', name:'Paul Gauguin', text:'Used symbolic colour and simplified scenes with stronger meaning.'},
  ].forEach(item => {
    html += '<article class="art-card">';
    html += '<div class="art-artist"><div class="badge">' + item.icon + '</div><h4>' + item.name + '</h4></div>';
    html += '<p>' + item.text + '</p>';
    html += '</article>';
  });
  html += '</div></section>';

  html += '<section class="art-panel">';
  html += '<div class="art-small-title">Exam phrases and memory trick</div>';
  html += '<div class="art-quote">“capture the impression of light” · “momentary effects of atmosphere” · “art based on emotion rather than observation”</div>';
  html += '<div class="art-chip-row">';
  ['Impressionism = I see light', 'Post-Impressionism = I feel it', 'Mention an artist', 'Mention a subject'].forEach(chip => html += '<span class="art-chip">' + chip + '</span>');
  html += '</div>';
  html += '</section>';

  html += '</div>';
  return html;
}

function renderArt(){
  title.textContent = 'Art — Impressionism vs Post-Impressionism';
  subtitle.textContent = 'Simple comparison visuals built from the impressionism notes.';
  content.className = '';
  content.innerHTML = '<div class="bio-empty">Loading art notes…</div>';
  fetch('art/impressionism/impressionism_vs_post_impressionism.txt')
    .then(r => {
      if(!r.ok) throw new Error('missing notes');
      return r.text();
    })
    .then(txt => { content.innerHTML = buildArtPage(txt); })
    .catch(() => {
      content.innerHTML = '<div class="bio-empty">Could not load art/impressionism/impressionism_vs_post_impressionism.txt.</div>';
    });
}

function parseDcgSections(txt){
  return txt.split(/\n\s*\n/).map(block => block.trim()).filter(Boolean).map(block => {
    const lines = block.split('\n').map(l => l.trim()).filter(Boolean);
    return {
      title: lines[0] || '',
      body: lines.slice(1),
    };
  });
}

function renderDCGSection(section){
  const title = section.title.toLowerCase();
  if(title.startsWith('in simple terms')) return '';
  if(title.startsWith('what “dynamic” means')) return '';
  if(title.startsWith('the main idea')) return '';
  return '';
}

function buildDCGPage(txt){
  const sections = parseDcgSections(txt);
  let html = '<div class="dcg-wrap">';
  html += '<section class="dcg-banner">';
  html += '<h3>Dynamic Mechanisms</h3>';
  html += '<p>A dynamic mechanism is a moving system that changes one type of motion into another. The visuals below show input motion, the mechanism, and the output motion in one glance.</p>';
  html += '</section>';

  html += '<section class="dcg-card">';
  html += '<div class="dcg-section-title">Motion flow</div>';
  html += '<p class="dcg-section-sub">Think: input motion → mechanism → output motion.</p>';
  html += '<div class="dcg-flow">';
  html += '<div class="dcg-node"><span class="label">Input</span><span class="value">What you do</span><span>Pedals, motor, push</span></div>';
  html += '<div class="dcg-arrow">→</div>';
  html += '<div class="dcg-node"><span class="label">Mechanism</span><span class="value">Moving parts</span><span>Gears, cams, linkages</span></div>';
  html += '<div class="dcg-arrow">→</div>';
  html += '<div class="dcg-node"><span class="label">Output</span><span class="value">What it makes happen</span><span>Spin, lift, sweep, slide</span></div>';
  html += '</div></section>';

  html += '<section><div class="dcg-section-title">Motion types</div>';
  html += '<p class="dcg-section-sub">The exam usually wants you to name the motion before and after the mechanism acts on it.</p>';
  html += '<div class="dcg-motion-grid">';
  [
    {icon:'🌀', title:'Rotary motion', text:'Spinning motion like a wheel, gear, or motor shaft.', tag:'Spin'},
    {icon:'➡️', title:'Linear motion', text:'Straight-line motion like a drawer sliding or a push.', tag:'Straight line'},
    {icon:'↔️', title:'Reciprocating motion', text:'Back-and-forth in a straight line, like a piston.', tag:'Back and forth'},
    {icon:'〰️', title:'Oscillating motion', text:'Back-and-forth in an arc, like a pendulum or wiper.', tag:'Swing'},
  ].forEach(item => {
    html += '<article class="dcg-motion">';
    html += '<div class="motion-top"><strong>' + item.title + '</strong><span class="motion-badge">' + item.icon + '</span></div>';
    html += '<p>' + item.text + '</p>';
    html += '<div class="dcg-chip-row"><span class="dcg-chip">' + item.tag + '</span></div>';
    html += '</article>';
  });
  html += '</div></section>';

  html += '<section><div class="dcg-section-title">Common examples</div>';
  html += '<p class="dcg-section-sub">Each example shows the motion change as a simple three-step visual.</p>';
  html += '<div class="dcg-example-rail">';
  [
    {icon:'🚲', title:'Bicycle gears', a:'Legs turn pedals', b:'Gears transfer motion', c:'Wheel turns faster or slower', hint:'Changes speed and force'},
    {icon:'🪟', title:'Windscreen wipers', a:'Motor spins', b:'Linkage changes the motion', c:'Wipers sweep across the screen', hint:'Circular → oscillating'},
    {icon:'🚪', title:'Door hinge', a:'Push the door', b:'Hinge controls rotation', c:'Door rotates open', hint:'Linear → rotary'},
  ].forEach(item => {
    html += '<article class="dcg-example">';
    html += '<div class="example-head"><strong>' + item.title + '</strong><span class="example-icon">' + item.icon + '</span></div>';
    html += '<div class="dcg-seq">';
    html += '<div class="dcg-step">Input<em>' + item.a + '</em></div>';
    html += '<div class="dcg-mini-arrow">→</div>';
    html += '<div class="dcg-step">Mechanism<em>' + item.b + '</em></div>';
    html += '<div class="dcg-mini-arrow">→</div>';
    html += '<div class="dcg-step">Output<em>' + item.c + '</em></div>';
    html += '</div>';
    html += '<div class="bio-tip" style="margin-top:12px">' + item.hint + '</div>';
    html += '</article>';
  });
  html += '</div></section>';

  html += '<section><div class="dcg-section-title">Key mechanism cards</div>';
  html += '<div class="dcg-grid">';
  [
    {title:'Crank and slider', body:'Used in engines. Rotary motion is changed into reciprocating motion.', chips:['Engine pistons', 'Rotary → reciprocating']},
    {title:'Cam and follower', body:'A cam is a shaped rotating piece. As it turns, the follower moves up and down.', chips:['Very important', 'Rotary → up/down']},
    {title:'Gear system', body:'Gears transfer motion and change speed, force, or direction.', chips:['Speed change', 'Direction change']},
    {title:'Linkages', body:'Connected bars can change the direction of motion or make movement smoother.', chips:['Change direction', 'Controlled movement']},
  ].forEach(item => {
    html += '<article class="dcg-card">';
    html += '<h4>' + item.title + '</h4>';
    html += '<p>' + item.body + '</p>';
    html += '<div class="dcg-chip-row">' + item.chips.map(chip => '<span class="dcg-chip">' + chip + '</span>').join('') + '</div>';
    html += '</article>';
  });
  html += '</div></section>';

  html += '<section class="dcg-card">';
  html += '<h4>Exam sentence</h4>';
  html += '<p>“A dynamic mechanism is a system of moving parts that transmits and transforms motion from an input motion to an output motion.”</p>';
  html += '<div class="bio-tip">Move in → mechanism → different move out</div>';
  html += '</section>';

  html += '</div>';
  return html;
}

function renderDCG(){
  title.textContent = 'DCG — Dynamic Mechanisms';
  subtitle.textContent = 'Simple motion visuals built from dynamic_mechanisms.txt.';
  content.className = '';
  content.innerHTML = '<div class="bio-empty">Loading dynamic mechanisms…</div>';
  fetch('dcg/dynamic_mechanisms.txt')
    .then(r => {
      if(!r.ok) throw new Error('missing notes');
      return r.text();
    })
    .then(txt => { content.innerHTML = buildDCGPage(txt); })
    .catch(() => {
      content.innerHTML = '<div class="bio-empty">Could not load dcg/dynamic_mechanisms.txt.</div>';
    });
}

function renderMaths(){
  title.textContent = 'Maths — Statistics & Probability';
  subtitle.textContent = 'Interactive guide · Leaving Certificate Ordinary Level';
  content.className = '';

  const CONCEPTS = [
    {icon:'📊', name:'Mean (Average)',
     formula:'Mean = Σx ÷ n',
     body:'Add all values together, then divide by the number of values. The mean is the most common average but can be affected by very large or small numbers (outliers).',
     tips:['Add all values first to find Σx','Then divide by n (the count of values)','The mean is sensitive to outliers — the median may be more appropriate']},
    {icon:'📏', name:'Median',
     formula:'Middle value when data is arranged in order',
     body:'Sort all values from smallest to largest. The median is the middle value. If there is an even number of values, find the mean of the two middle values.',
     tips:['Always sort the data first','For n values: median position = ½(n + 1)','The median is NOT affected by outliers']},
    {icon:'🎯', name:'Mode',
     formula:'The value that appears most often in the data set',
     body:'The mode is the most frequently occurring value. A data set can have no mode, one mode, or multiple modes.',
     tips:['Easiest to spot from a frequency table — look for the highest frequency','A data set can have more than one mode','Useful for categorical or discrete data']},
    {icon:'📐', name:'Range & Interquartile Range (IQR)',
     formula:'Range = Max − Min      IQR = Q₃ − Q₁',
     body:'The range measures overall spread. The IQR measures the spread of the middle 50% of the data, making it resistant to outliers.',
     tips:['Range = largest value minus smallest value','Q₁ = lower quartile (25th %), Q₃ = upper quartile (75th %)','A smaller IQR means the data is more consistent']},
    {icon:'📋', name:'Frequency Tables',
     formula:'Mean = Σ(f × x) ÷ Σf',
     body:'A frequency table records how often each value occurs. To find the mean, multiply each value (x) by its frequency (f), sum those products, then divide by the total frequency.',
     tips:['Σf = total number of data items — always verify this matches the given total','The mode is the value with the highest frequency','Use columns: x | f | f×x — then sum each column']},
    {icon:'🎲', name:'Basic Probability',
     formula:'P(A) = Number of favourable outcomes ÷ Total number of outcomes',
     body:'Probability is always between 0 (impossible) and 1 (certain). The sample space S is the list of all possible outcomes. Always count carefully before calculating.',
     tips:['List the full sample space before calculating','0 ≤ P(A) ≤ 1 always','P(A) = n(A) ÷ n(S)']},
    {icon:'🔄', name:'Complementary Events',
     formula:"P(A') = 1 − P(A)",
     body:"The complement of A is everything that is NOT A. Their probabilities always add to 1. Especially useful for 'at least one' questions.",
     tips:['"At least one" → use 1 − P(none at all)','P(A) + P(not A) = 1 always','Use this when the complement is simpler to calculate']},
    {icon:'⛔', name:'Mutually Exclusive Events',
     formula:'P(A or B) = P(A) + P(B)',
     body:'Events A and B are mutually exclusive if they cannot both happen at the same time. For example, a single card cannot be both a heart and a club.',
     tips:['Cannot happen simultaneously — P(A and B) = 0','Simply add their individual probabilities','Example: rolling a 3 or a 5 on one die']},
    {icon:'⚙️', name:'Independent Events',
     formula:'P(A and B) = P(A) × P(B)',
     body:'Events are independent if the outcome of one has no effect on the other. Draw a tree diagram to organise outcomes and multiply along the branches.',
     tips:['Outcomes do not affect each other','Multiply the individual probabilities','Tree diagrams: multiply along branches, add between branches']},
    {icon:'🪙', name:'Bernoulli Trials',
     formula:'P(X = r) = C(n,r) × pʳ × qⁿ⁻ʳ     where q = 1 − p',
     body:'A Bernoulli trial has exactly two outcomes: success (probability p) or failure (q = 1 − p). When the trial is repeated n times, use the binomial formula. C(n,r) = n! ÷ (r! × (n−r)!)',
     tips:['Identify n (trials), r (successes needed), p (probability of success)','q = 1 − p (probability of failure)','C(n,r) = n! ÷ (r!(n−r)!) — Pascals Triangle is a useful shortcut']},
    {icon:'💡', name:'Expected Value',
     formula:'E(X) = Σ [ x × P(x) ]',
     body:'The expected value is the long-run average outcome. Multiply each possible outcome by its probability, then sum all results. A game is fair if E(X) equals the cost to play.',
     tips:['List all outcomes and their probabilities first','Multiply each outcome by its probability then add all results','If E(X) > cost to play, the game favours the player']},
  ];

  const QS = [
    {num:1, topic:'Measures of Central Tendency',
     q:'The marks of 9 students in a test are: 45, 67, 52, 78, 67, 89, 45, 67, 90.<br>Find: (a) the mode &nbsp; (b) the median &nbsp; (c) the mean &nbsp; (d) the range.',
     ans:'<p><strong>First, sort the data:</strong> 45, 45, 52, 67, 67, 67, 78, 89, 90</p>'+
         '<div class="step"><strong>(a) Mode</strong> — most frequent value: <strong>67</strong> (appears 3 times)</div>'+
         '<div class="step"><strong>(b) Median</strong> — 9 values so median = 5th value: <strong>67</strong></div>'+
         '<div class="step"><strong>(c) Mean</strong> — Σx = 45+45+52+67+67+67+78+89+90 = 600<br>Mean = 600 ÷ 9 ≈ <strong>66.7</strong></div>'+
         '<div class="step"><strong>(d) Range</strong> = 90 − 45 = <strong>45</strong></div>'+
         '<div class="answer">Mode = 67 &nbsp;·&nbsp; Median = 67 &nbsp;·&nbsp; Mean ≈ 66.7 &nbsp;·&nbsp; Range = 45</div>'},
    {num:2, topic:'Frequency Tables',
     q:'Goals scored by a football team in 20 matches:<br><br>'+
       '<table style="border-collapse:collapse;font-size:13px;margin:4px 0">'+
       '<tr><td style="padding:4px 14px;background:#f0fdfa;font-weight:700">Goals</td>'+
       '<td style="padding:4px 12px;background:#f0fdfa">0</td><td style="padding:4px 12px;background:#f0fdfa">1</td>'+
       '<td style="padding:4px 12px;background:#f0fdfa">2</td><td style="padding:4px 12px;background:#f0fdfa">3</td>'+
       '<td style="padding:4px 12px;background:#f0fdfa">4</td></tr>'+
       '<tr><td style="padding:4px 14px;font-weight:700">Frequency</td>'+
       '<td style="padding:4px 12px">2</td><td style="padding:4px 12px">5</td>'+
       '<td style="padding:4px 12px">8</td><td style="padding:4px 12px">3</td>'+
       '<td style="padding:4px 12px">2</td></tr></table><br>'+
       'Find: (a) the modal number of goals &nbsp; (b) the mean number of goals per match.',
     ans:'<div class="step"><strong>(a) Mode</strong> — highest frequency is 8, which corresponds to <strong>2 goals</strong></div>'+
         '<div class="step"><strong>(b) Mean</strong> — calculate Σ(f×x):<br>'+
         '(0×2)+(1×5)+(2×8)+(3×3)+(4×2) = 0+5+16+9+8 = 38<br>'+
         'Σf = 2+5+8+3+2 = 20<br>Mean = 38 ÷ 20 = <strong>1.9 goals per match</strong></div>'+
         '<div class="answer">Mode = 2 goals &nbsp;·&nbsp; Mean = 1.9 goals per match</div>'},
    {num:3, topic:'Basic Probability',
     q:'A bag contains 4 red, 3 blue and 5 green balls. One ball is picked at random.<br>Find: (a) P(red) &nbsp; (b) P(blue) &nbsp; (c) P(not green) &nbsp; (d) P(red or blue)',
     ans:'<div class="step"><strong>Total balls</strong> = 4 + 3 + 5 = <strong>12</strong></div>'+
         '<div class="step"><strong>(a) P(red)</strong> = 4/12 = <strong>1/3</strong></div>'+
         '<div class="step"><strong>(b) P(blue)</strong> = 3/12 = <strong>1/4</strong></div>'+
         '<div class="step"><strong>(c) P(not green)</strong> = 1 − 5/12 = <strong>7/12</strong></div>'+
         '<div class="step"><strong>(d) P(red or blue)</strong> — mutually exclusive, so add:<br>4/12 + 3/12 = <strong>7/12</strong></div>'+
         '<div class="answer">P(red)=1/3 &nbsp;·&nbsp; P(blue)=1/4 &nbsp;·&nbsp; P(not green)=7/12 &nbsp;·&nbsp; P(red or blue)=7/12</div>'},
    {num:4, topic:'Two Dice — Sample Space',
     q:'Two fair dice are thrown. Find the probability that:<br>(a) the sum equals 8 &nbsp; (b) both dice show the same number &nbsp; (c) the sum is greater than 9',
     ans:'<div class="step"><strong>Total outcomes</strong> = 6 × 6 = <strong>36</strong></div>'+
         '<div class="step"><strong>(a) Sum = 8:</strong> (2,6),(3,5),(4,4),(5,3),(6,2) → 5 outcomes<br>P = <strong>5/36</strong></div>'+
         '<div class="step"><strong>(b) Doubles:</strong> (1,1),(2,2),(3,3),(4,4),(5,5),(6,6) → 6 outcomes<br>P = 6/36 = <strong>1/6</strong></div>'+
         '<div class="step"><strong>(c) Sum &gt; 9:</strong> Sum=10: (4,6),(5,5),(6,4) · Sum=11: (5,6),(6,5) · Sum=12: (6,6) → 6 outcomes<br>P = 6/36 = <strong>1/6</strong></div>'+
         '<div class="answer">P(sum=8)=5/36 &nbsp;·&nbsp; P(doubles)=1/6 &nbsp;·&nbsp; P(sum&gt;9)=1/6</div>'},
    {num:5, topic:'Complementary Events',
     q:'The probability of rain on any day in June is 0.35. Two days are chosen at random.<br>(a) Find P(no rain on a given day).<br>(b) Find P(rain on at least one of the two days).',
     ans:'<div class="step"><strong>(a) P(no rain)</strong> = 1 − 0.35 = <strong>0.65</strong></div>'+
         '<div class="step"><strong>(b) “At least one”</strong> → use complement:<br>P(no rain on either day) = 0.65 × 0.65 = 0.4225<br>P(rain on at least one day) = 1 − 0.4225 = <strong>0.5775</strong></div>'+
         '<div class="answer">P(no rain) = 0.65 &nbsp;·&nbsp; P(rain on at least one day) = 0.5775</div>'},
    {num:6, topic:'Playing Cards',
     q:'A card is drawn at random from a standard deck of 52 cards. Find:<br>(a) P(heart) &nbsp; (b) P(king) &nbsp; (c) P(heart or king) &nbsp; (d) P(red card)',
     ans:'<div class="step"><strong>(a) P(heart)</strong> = 13/52 = <strong>1/4</strong> &nbsp;(13 hearts in the deck)</div>'+
         '<div class="step"><strong>(b) P(king)</strong> = 4/52 = <strong>1/13</strong> &nbsp;(4 kings in the deck)</div>'+
         '<div class="step"><strong>(c) P(heart or king)</strong> — NOT mutually exclusive (king of hearts is both):<br>P = 13/52 + 4/52 − 1/52 = <strong>16/52 = 4/13</strong></div>'+
         '<div class="step"><strong>(d) P(red card)</strong> = 26/52 = <strong>1/2</strong> &nbsp;(hearts + diamonds = 26 red cards)</div>'+
         '<div class="answer">P(heart)=1/4 &nbsp;·&nbsp; P(king)=1/13 &nbsp;·&nbsp; P(heart or king)=4/13 &nbsp;·&nbsp; P(red)=1/2</div>'},
    {num:7, topic:'Independent Events',
     q:'P(Aoife passes maths) = 0.7. P(Ciarán passes maths) = 0.6. The tests are independent.<br>Find the probability that: (a) both pass &nbsp; (b) both fail &nbsp; (c) at least one passes',
     ans:'<div class="step"><strong>Failures:</strong> P(Aoife fails) = 0.3 &nbsp;·&nbsp; P(Ciarán fails) = 0.4</div>'+
         '<div class="step"><strong>(a) Both pass</strong> = 0.7 × 0.6 = <strong>0.42</strong></div>'+
         '<div class="step"><strong>(b) Both fail</strong> = 0.3 × 0.4 = <strong>0.12</strong></div>'+
         '<div class="step"><strong>(c) At least one passes</strong> = 1 − P(both fail) = 1 − 0.12 = <strong>0.88</strong></div>'+
         '<div class="answer">P(both pass)=0.42 &nbsp;·&nbsp; P(both fail)=0.12 &nbsp;·&nbsp; P(at least one)=0.88</div>'},
    {num:8, topic:'Bernoulli Trials',
     q:'A biased coin has P(heads) = 0.6. The coin is tossed 5 times.<br>Find the probability of: (a) exactly 3 heads &nbsp; (b) at least 4 heads',
     ans:'<div class="step"><strong>Setup:</strong> n = 5, p = 0.6, q = 0.4 &nbsp;·&nbsp; Formula: P(X=r) = C(n,r) × p<sup>r</sup> × q<sup>n−r</sup></div>'+
         '<div class="step"><strong>(a) P(X = 3):</strong><br>C(5,3) = 10<br>P = 10 × 0.6<sup>3</sup> × 0.4<sup>2</sup> = 10 × 0.216 × 0.16 = <strong>0.3456</strong></div>'+
         '<div class="step"><strong>(b) P(X ≥ 4) = P(X=4) + P(X=5):</strong><br>P(X=4) = C(5,4) × 0.6<sup>4</sup> × 0.4 = 5 × 0.1296 × 0.4 = 0.2592<br>P(X=5) = 1 × 0.6<sup>5</sup> = 0.07776<br>P(X≥4) = 0.2592 + 0.07776 = <strong>0.3370</strong></div>'+
         '<div class="answer">P(exactly 3 heads) = 0.3456 &nbsp;·&nbsp; P(at least 4 heads) ≈ 0.337</div>'},
    {num:9, topic:'Expected Value',
     q:'A game costs €3 to play. You roll a fair die and win:<br>• €10 if you roll a 6 &nbsp;• €4 if you roll a 5 &nbsp;• €0 otherwise<br><br>(a) Find the expected winnings per game. &nbsp; (b) Is the game fair?',
     ans:'<div class="step"><strong>Outcomes:</strong> Win €10 (P=1/6) &nbsp;·&nbsp; Win €4 (P=1/6) &nbsp;·&nbsp; Win €0 (P=4/6)</div>'+
         '<div class="step"><strong>(a) E(winnings)</strong> = (10×1/6) + (4×1/6) + (0×4/6) = 10/6 + 4/6 = 14/6 ≈ <strong>€2.33</strong></div>'+
         '<div class="step"><strong>Net</strong> = €2.33 − €3.00 (cost) = <strong>−€0.67</strong></div>'+
         '<div class="step"><strong>(b)</strong> A game is fair when E(winnings) = cost to play.<br>Here €2.33 &lt; €3.00 so the game is <strong>NOT fair</strong> — you expect to lose €0.67 per game on average.</div>'+
         '<div class="answer">E(winnings) ≈ €2.33 &nbsp;·&nbsp; Net per game = −€0.67 &nbsp;·&nbsp; NOT a fair game</div>'},
    {num:10, topic:'Venn Diagrams & Conditional Probability',
     q:'In a class of 30 students, 18 study French and 14 study German. 6 study both languages.<br>(a) How many study French only? &nbsp;(b) How many study neither language?<br>(c) Find P(a randomly chosen student studies French).<br>(d) Given a student studies German, find P(they also study French).',
     ans:'<div class="step"><strong>Venn diagram:</strong> French only = 18−6 = 12 &nbsp;·&nbsp; Both = 6 &nbsp;·&nbsp; German only = 14−6 = 8<br>Total in at least one language = 12+6+8 = 26</div>'+
         '<div class="step"><strong>(a) French only</strong> = 18 − 6 = <strong>12</strong></div>'+
         '<div class="step"><strong>(b) Neither</strong> = 30 − 26 = <strong>4</strong></div>'+
         '<div class="step"><strong>(c) P(French)</strong> = 18/30 = <strong>3/5</strong></div>'+
         '<div class="step"><strong>(d) Conditional probability</strong> — restricted to German students (14):<br>P(French | German) = 6/14 = <strong>3/7</strong></div>'+
         '<div class="answer">French only=12 &nbsp;·&nbsp; Neither=4 &nbsp;·&nbsp; P(French)=3/5 &nbsp;·&nbsp; P(French|German)=3/7</div>'},
  ];

  let h = '<div class="maths-wrap">';
  h += '<div><div class="maths-section-title">📖 Key Concepts</div>';
  h += '<p class="maths-section-sub">Click any concept to expand the explanation and formula.</p>';
  h += '<div class="concept-list">';
  CONCEPTS.forEach(c => {
    h += '<details class="concept-item"><summary class="concept-hdr">';
    h += '<span class="c-icon">' + c.icon + '</span><span>' + c.name + '</span>';
    h += '<span class="c-chevron">›</span></summary>';
    h += '<div class="concept-body"><p>' + c.body + '</p>';
    h += '<div class="formula">' + c.formula + '</div>';
    h += '<ul>' + c.tips.map(t => '<li>' + t + '</li>').join('') + '</ul>';
    h += '</div></details>';
  });
  h += '</div></div>';
  h += '<div><div class="maths-section-title">✏️ Practice Questions</div>';
  h += '<p class="maths-section-sub">LC Ordinary Level style — tap a question to reveal the full worked solution.</p>';
  h += '<div class="qa-list">';
  QS.forEach(q => {
    h += '<div class="qa-card"><div class="qa-q">';
    h += '<span class="qa-num">' + q.num + '</span>';
    h += '<div class="qa-qtext">' + q.q + '<div class="qa-subtext">Topic: ' + q.topic + '</div></div>';
    h += '<button class="qa-toggle" aria-label="Show answer">+</button></div>';
    h += '<div class="qa-ans">' + q.ans + '</div></div>';
  });
  h += '</div></div></div>';
  content.innerHTML = h;

  content.querySelectorAll('.qa-q').forEach(row => {
    row.addEventListener('click', () => {
      const ans = row.nextElementSibling;
      const btn = row.querySelector('.qa-toggle');
      const isOpen = ans.classList.toggle('open');
      btn.classList.toggle('open', isOpen);
    });
  });
}

function renderTabs(){
  if(active === 'Spanish') document.body.className = 'spanish';
  else if(active === 'English') document.body.className = 'english';
  else if(active === 'Art') document.body.className = 'art';
  else if(active === 'DCG') document.body.className = 'dcg';
  else if(active === 'Maths') document.body.className = 'maths';
  else document.body.className = '';
  // Swipe hint only when on verb card views
  const hint = document.getElementById('swipeHint');
  if(hint) hint.classList.toggle('visible',
    (active==='Irish' && activeView==='irish-verbs') ||
    (active==='Spanish' && activeView==='spanish-verbs'));
  // Back button
  const backBtn = document.getElementById('heroBackBtn');
  if(backBtn){
    backBtn.style.display = activeView !== 'home' ? 'inline-flex' : 'none';
    backBtn.textContent = '\u2190 ' + active;
    backBtn.onclick = () => { activeView = 'home'; renderTabs(); renderContent(); };
  }
  tabs.innerHTML = '';
  SUBJECTS.forEach(s => {
    const b = document.createElement('button');
    b.className = 'tab' + (s===active ? ' active' : '');
    b.textContent = s;
    b.onclick = () => { active = s; activeView = 'home'; renderTabs(); renderContent(); };
    tabs.appendChild(b);
  });
}

function renderContent(){
  if(activeView === 'home'){ renderHome(active); return; }
  if(activeView === 'pastpapers'){ renderPastPapers(active); return; }
  if(activeView === 'maths-stats'){ renderMaths(); return; }
  if(activeView === 'english-books'){ renderEnglishBooks(); return; }
  if(activeView === 'irish-verbs'){ renderIrishVerbs(); return; }
  if(activeView === 'spanish-verbs'){ renderSpanishVerbs(); return; }
  if(activeView === 'bio-micro'){ renderBiology(); return; }
  if(activeView === 'art-impressionism'){ renderArt(); return; }
  if(activeView === 'dcg-mechanisms'){ renderDCG(); return; }
  renderHome(active);
}

function renderEnglishBooks(){
  title.textContent = 'English — Books & Notes';
  subtitle.textContent = 'Tap a book to open your study notes.';
  content.className = '';
  content.innerHTML = '';
  const shelf = document.createElement('div');
  shelf.className = 'shelf';
  ENGLISH_BOOKS.forEach(book => {
    const wrap = document.createElement('div');
    wrap.className = 'book-wrap';
    wrap.setAttribute('role','button');
    wrap.setAttribute('tabindex','0');
    wrap.innerHTML = `
        <img class="book-cover" src="${book.cover}" alt="${book.title} cover" />
        <div class="book-label">${book.title}<small>${book.author}</small></div>`;
    wrap.addEventListener('click', () => openBook(book));
    wrap.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' ') openBook(book); });
    shelf.appendChild(wrap);
  });
  content.appendChild(shelf);
}

function renderIrishVerbs(){
  title.textContent = 'Gaeilge — 50 Verbs';
  subtitle.textContent = 'Default card shows the present tense.';
  content.className = 'grid';
  content.innerHTML = '';
  VERBS.forEach((v, i) => content.appendChild(buildCard(v, i+1)));
}

function renderSpanishVerbs(){
  title.textContent = 'Español — 50 Verbos';
  subtitle.textContent = 'La tarjeta muestra el presente por defecto.';
  content.className = 'grid';
  content.innerHTML = '';
  SPANISH_VERBS.forEach((v, i) => content.appendChild(
    buildCard(v, i+1, {pastLabel:'Pretérito', futureLabel:'Futuro', presentLabel:'Presente', verbField:'es'})
  ));
}

function buildCard(v, n, opts){
  opts = opts || {};
  const pastLabel  = opts.pastLabel    || 'Past · Aimsir Chaite';
  const futLabel   = opts.futureLabel  || 'Future · Aimsir Fháistineach';
  const presLabel  = opts.presentLabel || 'Present';
  const verbField  = opts.verbField    || 'ga';
  const stage = document.createElement('div');
  stage.className = 'stage';
  stage.innerHTML = `
    <div class="reveal past"><span class="badge">◀ ${pastLabel}</span></div>
    <div class="reveal future"><span class="badge">${futLabel} ▶</span></div>
    <article class="card" data-past-label="${pastLabel}" data-fut-label="${futLabel}" data-pres-label="${presLabel}">
      <div class="top">
        <div class="verb"><b>${v[verbField]}</b> · ${v.en}</div>
        <span class="num">#${n}</span>
      </div>
      <div class="icon">${v.icon}</div>
      <div class="sentence" data-present="${v.present}" data-past="${v.past}" data-future="${v.future}">${v.present}</div>
      <div class="tense">
        <span class="pill" data-pill>Present</span>
        <span class="arrows">← future · past →</span>
      </div>
      <button type="button" class="reset-btn" data-reset>Back to present</button>
    </article>`;
  attachSwipe(stage);
  return stage;
}

function attachSwipe(stage){
  const card = stage.querySelector('.card');
  const sentence = stage.querySelector('.sentence');
  const pill = stage.querySelector('[data-pill]');
  const resetBtn = stage.querySelector('[data-reset]');
  const pastLayer = stage.querySelector('.reveal.past');
  const futureLayer = stage.querySelector('.reveal.future');

  let startX=0, dx=0, dragging=false, locked=null;
  let currentTense = 'present';
  const THRESHOLD = 70;

  function setTense(t){
    const pastLabel = card.dataset.pastLabel;
    const futLabel  = card.dataset.futLabel;
    const presLabel = card.dataset.presLabel;
    currentTense = t;
    if(t==='past'){
      sentence.textContent = sentence.dataset.past;
      pill.textContent = pastLabel;
      pill.className='pill past';
    } else if(t==='future'){
      sentence.textContent = sentence.dataset.future;
      pill.textContent = futLabel;
      pill.className='pill future';
    } else {
      sentence.textContent = sentence.dataset.present;
      pill.textContent = presLabel;
      pill.className='pill';
    }
    const canReset = t !== 'present';
    resetBtn.disabled = !canReset;
    resetBtn.classList.toggle('active', canReset);
  }

  function onDown(e){
    dragging = true; locked = null;
    startX = (e.touches ? e.touches[0].clientX : e.clientX);
    dx = 0;
    card.classList.add('dragging');
  }
  function onMove(e){
    if(!dragging) return;
    const x = (e.touches ? e.touches[0].clientX : e.clientX);
    const ny = (e.touches ? e.touches[0].clientY : e.clientY);
    dx = x - startX;
    if(locked === null && Math.abs(dx) > 6){ locked = 'x'; }
    if(locked !== 'x') return;
    if(e.cancelable) e.preventDefault();
    card.style.transform = `translateX(${dx}px) rotate(${dx*0.03}deg)`;
    const p = Math.min(Math.abs(dx)/THRESHOLD, 1);
    if(dx > 0){ pastLayer.style.opacity = p; futureLayer.style.opacity = 0; }
    else if(dx < 0){ futureLayer.style.opacity = p; pastLayer.style.opacity = 0; }
    else { pastLayer.style.opacity = 0; futureLayer.style.opacity = 0; }
  }
  function onUp(){
    if(!dragging) return;
    dragging = false;
    card.classList.remove('dragging');
    const w = stage.clientWidth;
    if(dx > THRESHOLD){
      // Slide right -> past
      card.style.transform = `translateX(${w}px) rotate(8deg)`;
      setTimeout(()=>{
        setTense('past');
        card.style.transition='none';
        card.style.transform = `translateX(-${w}px) rotate(-8deg)`;
        requestAnimationFrame(()=>{
          card.style.transition='';
          card.style.transform = 'translateX(0) rotate(0)';
          pastLayer.style.opacity = 0;
        });
      }, 220);
    } else if(dx < -THRESHOLD){
      // Slide left -> future
      card.style.transform = `translateX(-${w}px) rotate(-8deg)`;
      setTimeout(()=>{
        setTense('future');
        card.style.transition='none';
        card.style.transform = `translateX(${w}px) rotate(8deg)`;
        requestAnimationFrame(()=>{
          card.style.transition='';
          card.style.transform = 'translateX(0) rotate(0)';
          futureLayer.style.opacity = 0;
        });
      }, 220);
    } else if(currentTense !== 'present' && Math.abs(dx) > 16){
      // Short swipe back toward center restores the present tense
      setTense('present');
      card.style.transform = 'translateX(0) rotate(0)';
      pastLayer.style.opacity = 0;
      futureLayer.style.opacity = 0;
    } else {
      card.style.transform = 'translateX(0) rotate(0)';
      pastLayer.style.opacity = 0;
      futureLayer.style.opacity = 0;
    }
    dx = 0;
  }

  card.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
  card.addEventListener('touchstart', onDown, {passive:true});
  card.addEventListener('touchmove', onMove, {passive:false});
  card.addEventListener('touchend', onUp);

  resetBtn.addEventListener('click', e => {
    e.stopPropagation();
    setTense('present');
    card.style.transform = 'translateX(0) rotate(0)';
    pastLayer.style.opacity = 0;
    futureLayer.style.opacity = 0;
  });
  setTense('present');
  card.addEventListener('dblclick', ()=> setTense('present'));
}

renderTabs();
renderContent();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            html = (
                INDEX_HTML
                .replace("__SUBJECTS__", json.dumps(SUBJECTS))
                .replace("__VERBS__", json.dumps(VERBS, ensure_ascii=False))
                .replace("__SPANISH_VERBS__", json.dumps(SPANISH_VERBS, ensure_ascii=False))
              .replace("__BIOLOGY_MICRO_IMAGES__", json.dumps(BIOLOGY_MICRO_IMAGES, ensure_ascii=False))
              .replace("__PAST_PAPERS__", json.dumps(PAST_PAPERS, ensure_ascii=False))
            )
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path == "/api/verbs":
            self._send(
                200,
                json.dumps(VERBS, ensure_ascii=False).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        # Serve static files from subject subfolders
        safe = self.path.lstrip("/")
        # Only allow alphanumeric, dash, underscore, dot, slash
        import re as _re
        if _re.match(r'^[a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-\.]+){1,2}$', safe):
            fpath = os.path.join(STATIC_BASE, safe)
            if os.path.isfile(fpath):
                ctype, _ = mimetypes.guess_type(fpath)
                ctype = ctype or "application/octet-stream"
                file_size = os.path.getsize(fpath)
                range_header = self.headers.get("Range")
                if range_header:
                    m = _re.match(r'bytes=(\d+)-(\d*)', range_header)
                    if m:
                        start = int(m.group(1))
                        end = int(m.group(2)) if m.group(2) else file_size - 1
                        end = min(end, file_size - 1)
                        length = end - start + 1
                        with open(fpath, "rb") as f:
                            f.seek(start)
                            data = f.read(length)
                        self.send_response(206)
                        self.send_header("Content-Type", ctype)
                        self.send_header("Content-Length", str(length))
                        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                        self.send_header("Accept-Ranges", "bytes")
                        self.send_header("Cache-Control", "no-store")
                        self.end_headers()
                        self.wfile.write(data)
                        return
                with open(fpath, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(file_size))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
                return
        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:  # quieter logs
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Léann study app running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
