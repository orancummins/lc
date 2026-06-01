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

# 50 most popular verbs in Irish with simple example sentences in
# present / past / future tense, plus an emoji as the "simple picture".
VERBS = [
    {"en": "be", "ga": "bí", "icon": "🌟",
     "present": "Tá sé anseo.", "past": "Bhí sé anseo.", "future": "Beidh sé anseo."},
    {"en": "have", "ga": "bí ag", "icon": "🎒",
     "present": "Tá mála agam.", "past": "Bhí mála agam.", "future": "Beidh mála agam."},
    {"en": "do", "ga": "déan", "icon": "🛠️",
     "present": "Déanann sé obair.", "past": "Rinne sé obair.", "future": "Déanfaidh sé obair."},
    {"en": "say", "ga": "abair", "icon": "💬",
     "present": "Deir sé dia duit.", "past": "Dúirt sé dia duit.", "future": "Déarfaidh sé dia duit."},
    {"en": "go", "ga": "téigh", "icon": "🚶",
     "present": "Téann sé abhaile.", "past": "Chuaigh sé abhaile.", "future": "Rachaidh sé abhaile."},
    {"en": "get", "ga": "faigh", "icon": "🎁",
     "present": "Faigheann sé bronntanas.", "past": "Fuair sé bronntanas.", "future": "Gheobhaidh sé bronntanas."},
    {"en": "make", "ga": "déan", "icon": "🎂",
     "present": "Déanann sé cáca.", "past": "Rinne sé cáca.", "future": "Déanfaidh sé cáca."},
    {"en": "know", "ga": "bí a fhios ag", "icon": "🧠",
     "present": "Tá a fhios aige.", "past": "Bhí a fhios aige.", "future": "Beidh a fhios aige."},
    {"en": "think", "ga": "smaoinigh", "icon": "💭",
     "present": "Smaoiníonn sé air.", "past": "Smaoinigh sé air.", "future": "Smaoineoidh sé air."},
    {"en": "take", "ga": "tóg", "icon": "📖",
     "present": "Tógann sé an leabhar.", "past": "Thóg sé an leabhar.", "future": "Tógfaidh sé an leabhar."},
    {"en": "see", "ga": "feic", "icon": "👀",
     "present": "Feiceann sé an cat.", "past": "Chonaic sé an cat.", "future": "Feicfidh sé an cat."},
    {"en": "come", "ga": "tar", "icon": "🚪",
     "present": "Tagann sé isteach.", "past": "Tháinig sé isteach.", "future": "Tiocfaidh sé isteach."},
    {"en": "want", "ga": "teastaigh", "icon": "💧",
     "present": "Teastaíonn uisce uaidh.", "past": "Theastaigh uisce uaidh.", "future": "Teastóidh uisce uaidh."},
    {"en": "look", "ga": "féach", "icon": "🌌",
     "present": "Féachann sé ar an spéir.", "past": "D'fhéach sé ar an spéir.", "future": "Féachfaidh sé ar an spéir."},
    {"en": "use", "ga": "úsáid", "icon": "🖊️",
     "present": "Úsáideann sé peann.", "past": "D'úsáid sé peann.", "future": "Úsáidfidh sé peann."},
    {"en": "find", "ga": "aimsigh", "icon": "🔑",
     "present": "Aimsíonn sé an eochair.", "past": "D'aimsigh sé an eochair.", "future": "Aimseoidh sé an eochair."},
    {"en": "give", "ga": "tabhair", "icon": "🎀",
     "present": "Tugann sé bronntanas.", "past": "Thug sé bronntanas.", "future": "Tabharfaidh sé bronntanas."},
    {"en": "tell", "ga": "inis", "icon": "📚",
     "present": "Insíonn sé scéal.", "past": "D'inis sé scéal.", "future": "Inseoidh sé scéal."},
    {"en": "work", "ga": "oibrigh", "icon": "💼",
     "present": "Oibríonn sé go crua.", "past": "D'oibrigh sé go crua.", "future": "Oibreoidh sé go crua."},
    {"en": "call", "ga": "glaoigh", "icon": "📞",
     "present": "Glaonn sé ar a mháthair.", "past": "Ghlaoigh sé ar a mháthair.", "future": "Glaofaidh sé ar a mháthair."},
    {"en": "try", "ga": "déan iarracht", "icon": "🎯",
     "present": "Déanann sé iarracht.", "past": "Rinne sé iarracht.", "future": "Déanfaidh sé iarracht."},
    {"en": "ask", "ga": "fiafraigh", "icon": "❓",
     "present": "Fiafraíonn sé ceist.", "past": "D'fhiafraigh sé ceist.", "future": "Fiafróidh sé ceist."},
    {"en": "need", "ga": "teastaigh ó", "icon": "😴",
     "present": "Tá sos uaidh.", "past": "Bhí sos uaidh.", "future": "Beidh sos uaidh."},
    {"en": "feel", "ga": "mothaigh", "icon": "😪",
     "present": "Mothaíonn sé tuirseach.", "past": "Mhothaigh sé tuirseach.", "future": "Mothóidh sé tuirseach."},
    {"en": "become", "ga": "éirigh", "icon": "🥱",
     "present": "Éiríonn sé tuirseach.", "past": "D'éirigh sé tuirseach.", "future": "Éireoidh sé tuirseach."},
    {"en": "leave", "ga": "fág", "icon": "🏠",
     "present": "Fágann sé an teach.", "past": "D'fhág sé an teach.", "future": "Fágfaidh sé an teach."},
    {"en": "put", "ga": "cuir", "icon": "📕",
     "present": "Cuireann sé an leabhar síos.", "past": "Chuir sé an leabhar síos.", "future": "Cuirfidh sé an leabhar síos."},
    {"en": "mean", "ga": "ciallaigh", "icon": "💡",
     "present": "Ciallaíonn sé sin.", "past": "Chiallaigh sé sin.", "future": "Ciallóidh sé sin."},
    {"en": "keep", "ga": "coinnigh", "icon": "💶",
     "present": "Coinníonn sé an t-airgead.", "past": "Choinnigh sé an t-airgead.", "future": "Coinneoidh sé an t-airgead."},
    {"en": "let", "ga": "lig", "icon": "🕊️",
     "present": "Ligeann sé dó imeacht.", "past": "Lig sé dó imeacht.", "future": "Ligfidh sé dó imeacht."},
    {"en": "begin", "ga": "tosaigh", "icon": "🚦",
     "present": "Tosaíonn sé an obair.", "past": "Thosaigh sé an obair.", "future": "Tosóidh sé an obair."},
    {"en": "seem", "ga": "is cosúil", "icon": "🤔",
     "present": "Tá cuma thuirseach air.", "past": "Bhí cuma thuirseach air.", "future": "Beidh cuma thuirseach air."},
    {"en": "help", "ga": "cabhraigh", "icon": "🤝",
     "present": "Cabhraíonn sé liom.", "past": "Chabhraigh sé liom.", "future": "Cabhróidh sé liom."},
    {"en": "talk", "ga": "labhair", "icon": "🗣️",
     "present": "Labhraíonn sé Gaeilge.", "past": "Labhair sé Gaeilge.", "future": "Labhróidh sé Gaeilge."},
    {"en": "turn", "ga": "cas", "icon": "🎡",
     "present": "Casann sé an roth.", "past": "Chas sé an roth.", "future": "Casfaidh sé an roth."},
    {"en": "start", "ga": "tosaigh", "icon": "🚗",
     "present": "Tosaíonn sé an carr.", "past": "Thosaigh sé an carr.", "future": "Tosóidh sé an carr."},
    {"en": "show", "ga": "taispeáin", "icon": "🖼️",
     "present": "Taispeánann sé an pictiúr.", "past": "Thaispeáin sé an pictiúr.", "future": "Taispeánfaidh sé an pictiúr."},
    {"en": "hear", "ga": "clois", "icon": "🎵",
     "present": "Cloiseann sé ceol.", "past": "Chuala sé ceol.", "future": "Cloisfidh sé ceol."},
    {"en": "play", "ga": "imir", "icon": "⚽",
     "present": "Imríonn sé peil.", "past": "D'imir sé peil.", "future": "Imreoidh sé peil."},
    {"en": "run", "ga": "rith", "icon": "🏃",
     "present": "Ritheann sé go tapa.", "past": "Rith sé go tapa.", "future": "Rithfidh sé go tapa."},
    {"en": "move", "ga": "bog", "icon": "📦",
     "present": "Bogann sé an bord.", "past": "Bhog sé an bord.", "future": "Bogfaidh sé an bord."},
    {"en": "live", "ga": "cónaigh", "icon": "🏙️",
     "present": "Cónaíonn sé i mBaile Átha Cliath.", "past": "Chónaigh sé i mBaile Átha Cliath.", "future": "Cónóidh sé i mBaile Átha Cliath."},
    {"en": "believe", "ga": "creid", "icon": "🙏",
     "present": "Creideann sé an scéal.", "past": "Chreid sé an scéal.", "future": "Creidfidh sé an scéal."},
    {"en": "bring", "ga": "tabhair leis", "icon": "📘",
     "present": "Tugann sé leabhar leis.", "past": "Thug sé leabhar leis.", "future": "Tabharfaidh sé leabhar leis."},
    {"en": "happen", "ga": "tarlaigh", "icon": "✨",
     "present": "Tarlaíonn sé go minic.", "past": "Tharla sé go minic.", "future": "Tarlóidh sé go minic."},
    {"en": "write", "ga": "scríobh", "icon": "✉️",
     "present": "Scríobhann sé litir.", "past": "Scríobh sé litir.", "future": "Scríobhfaidh sé litir."},
    {"en": "provide", "ga": "soláthair", "icon": "🍞",
     "present": "Soláthraíonn sé bia.", "past": "Sholáthair sé bia.", "future": "Soláthróidh sé bia."},
    {"en": "sit", "ga": "suigh", "icon": "🪑",
     "present": "Suíonn sé síos.", "past": "Shuigh sé síos.", "future": "Suífidh sé síos."},
    {"en": "stand", "ga": "seas", "icon": "🧍",
     "present": "Seasann sé suas.", "past": "Sheas sé suas.", "future": "Seasfaidh sé suas."},
    {"en": "lose", "ga": "caill", "icon": "🏆",
     "present": "Cailleann sé an cluiche.", "past": "Chaill sé an cluiche.", "future": "Caillfidh sé an cluiche."},
]

# 50 most popular verbs in Spanish (él/ella form), present / preterite / future.
SPANISH_VERBS = [
    {"en": "be", "es": "ser", "icon": "🌟",
     "present": "Él es estudiante.", "past": "Él fue estudiante.", "future": "Él será estudiante."},
    {"en": "have", "es": "tener", "icon": "🎒",
     "present": "Él tiene un libro.", "past": "Él tuvo un libro.", "future": "Él tendrá un libro."},
    {"en": "do/make", "es": "hacer", "icon": "🛠️",
     "present": "Él hace la tarea.", "past": "Él hizo la tarea.", "future": "Él hará la tarea."},
    {"en": "say", "es": "decir", "icon": "💬",
     "present": "Él dice la verdad.", "past": "Él dijo la verdad.", "future": "Él dirá la verdad."},
    {"en": "go", "es": "ir", "icon": "🚶",
     "present": "Él va a casa.", "past": "Él fue a casa.", "future": "Él irá a casa."},
    {"en": "see", "es": "ver", "icon": "👀",
     "present": "Él ve el mar.", "past": "Él vio el mar.", "future": "Él verá el mar."},
    {"en": "give", "es": "dar", "icon": "🎁",
     "present": "Él da un regalo.", "past": "Él dio un regalo.", "future": "Él dará un regalo."},
    {"en": "know", "es": "saber", "icon": "🧠",
     "present": "Él sabe la respuesta.", "past": "Él supo la respuesta.", "future": "Él sabrá la respuesta."},
    {"en": "want", "es": "querer", "icon": "💧",
     "present": "Él quiere agua.", "past": "Él quiso agua.", "future": "Él querrá agua."},
    {"en": "arrive", "es": "llegar", "icon": "🚪",
     "present": "Él llega tarde.", "past": "Él llegó tarde.", "future": "Él llegará tarde."},
    {"en": "happen", "es": "pasar", "icon": "✨",
     "present": "Pasa a menudo.", "past": "Pasó a menudo.", "future": "Pasará a menudo."},
    {"en": "must/owe", "es": "deber", "icon": "📚",
     "present": "Él debe estudiar.", "past": "Él debió estudiar.", "future": "Él deberá estudiar."},
    {"en": "put", "es": "poner", "icon": "📕",
     "present": "Él pone el libro aquí.", "past": "Él puso el libro aquí.", "future": "Él pondrá el libro aquí."},
    {"en": "seem", "es": "parecer", "icon": "🤔",
     "present": "Parece fácil.", "past": "Pareció fácil.", "future": "Parecerá fácil."},
    {"en": "stay", "es": "quedar", "icon": "🏠",
     "present": "Él queda en casa.", "past": "Él quedó en casa.", "future": "Él quedará en casa."},
    {"en": "believe", "es": "creer", "icon": "🙏",
     "present": "Él cree el cuento.", "past": "Él creyó el cuento.", "future": "Él creerá el cuento."},
    {"en": "speak", "es": "hablar", "icon": "🗣️",
     "present": "Él habla español.", "past": "Él habló español.", "future": "Él hablará español."},
    {"en": "carry", "es": "llevar", "icon": "📦",
     "present": "Él lleva una mochila.", "past": "Él llevó una mochila.", "future": "Él llevará una mochila."},
    {"en": "leave/let", "es": "dejar", "icon": "🕊️",
     "present": "Él deja el trabajo.", "past": "Él dejó el trabajo.", "future": "Él dejará el trabajo."},
    {"en": "follow", "es": "seguir", "icon": "🚦",
     "present": "Él sigue el camino.", "past": "Él siguió el camino.", "future": "Él seguirá el camino."},
    {"en": "find", "es": "encontrar", "icon": "🔑",
     "present": "Él encuentra la llave.", "past": "Él encontró la llave.", "future": "Él encontrará la llave."},
    {"en": "call", "es": "llamar", "icon": "📞",
     "present": "Él llama a su madre.", "past": "Él llamó a su madre.", "future": "Él llamará a su madre."},
    {"en": "come", "es": "venir", "icon": "🚗",
     "present": "Él viene aquí.", "past": "Él vino aquí.", "future": "Él vendrá aquí."},
    {"en": "think", "es": "pensar", "icon": "💭",
     "present": "Él piensa mucho.", "past": "Él pensó mucho.", "future": "Él pensará mucho."},
    {"en": "go out", "es": "salir", "icon": "🎡",
     "present": "Él sale de casa.", "past": "Él salió de casa.", "future": "Él saldrá de casa."},
    {"en": "return", "es": "volver", "icon": "🔄",
     "present": "Él vuelve tarde.", "past": "Él volvió tarde.", "future": "Él volverá tarde."},
    {"en": "take", "es": "tomar", "icon": "☕",
     "present": "Él toma un café.", "past": "Él tomó un café.", "future": "Él tomará un café."},
    {"en": "know (person)", "es": "conocer", "icon": "🤝",
     "present": "Él conoce Madrid.", "past": "Él conoció Madrid.", "future": "Él conocerá Madrid."},
    {"en": "live", "es": "vivir", "icon": "🏙️",
     "present": "Él vive en Madrid.", "past": "Él vivió en Madrid.", "future": "Él vivirá en Madrid."},
    {"en": "feel", "es": "sentir", "icon": "😪",
     "present": "Él siente cansancio.", "past": "Él sintió cansancio.", "future": "Él sentirá cansancio."},
    {"en": "try", "es": "tratar", "icon": "🎯",
     "present": "Él trata de ganar.", "past": "Él trató de ganar.", "future": "Él tratará de ganar."},
    {"en": "look", "es": "mirar", "icon": "🌌",
     "present": "Él mira el cielo.", "past": "Él miró el cielo.", "future": "Él mirará el cielo."},
    {"en": "tell", "es": "contar", "icon": "📖",
     "present": "Él cuenta un cuento.", "past": "Él contó un cuento.", "future": "Él contará un cuento."},
    {"en": "begin", "es": "empezar", "icon": "🚀",
     "present": "Él empieza la tarea.", "past": "Él empezó la tarea.", "future": "Él empezará la tarea."},
    {"en": "wait", "es": "esperar", "icon": "⏳",
     "present": "Él espera el autobús.", "past": "Él esperó el autobús.", "future": "Él esperará el autobús."},
    {"en": "search", "es": "buscar", "icon": "🔍",
     "present": "Él busca trabajo.", "past": "Él buscó trabajo.", "future": "Él buscará trabajo."},
    {"en": "exist", "es": "existir", "icon": "⭐",
     "present": "Existe una solución.", "past": "Existió una solución.", "future": "Existirá una solución."},
    {"en": "enter", "es": "entrar", "icon": "🏫",
     "present": "Él entra en clase.", "past": "Él entró en clase.", "future": "Él entrará en clase."},
    {"en": "work", "es": "trabajar", "icon": "💼",
     "present": "Él trabaja duro.", "past": "Él trabajó duro.", "future": "Él trabajará duro."},
    {"en": "write", "es": "escribir", "icon": "✉️",
     "present": "Él escribe una carta.", "past": "Él escribió una carta.", "future": "Él escribirá una carta."},
    {"en": "lose", "es": "perder", "icon": "🏆",
     "present": "Él pierde el partido.", "past": "Él perdió el partido.", "future": "Él perderá el partido."},
    {"en": "produce", "es": "producir", "icon": "🏭",
     "present": "Él produce energía.", "past": "Él produjo energía.", "future": "Él producirá energía."},
    {"en": "occur", "es": "ocurrir", "icon": "🌀",
     "present": "Ocurre algo raro.", "past": "Ocurrió algo raro.", "future": "Ocurrirá algo raro."},
    {"en": "understand", "es": "entender", "icon": "💡",
     "present": "Él entiende bien.", "past": "Él entendió bien.", "future": "Él entenderá bien."},
    {"en": "ask for", "es": "pedir", "icon": "❓",
     "present": "Él pide ayuda.", "past": "Él pidió ayuda.", "future": "Él pedirá ayuda."},
    {"en": "receive", "es": "recibir", "icon": "🎀",
     "present": "Él recibe una carta.", "past": "Él recibió una carta.", "future": "Él recibirá una carta."},
    {"en": "remember", "es": "recordar", "icon": "🧩",
     "present": "Él recuerda todo.", "past": "Él recordó todo.", "future": "Él recordará todo."},
    {"en": "finish", "es": "terminar", "icon": "🏁",
     "present": "Él termina pronto.", "past": "Él terminó pronto.", "future": "Él terminará pronto."},
    {"en": "allow", "es": "permitir", "icon": "🟢",
     "present": "Él permite entrar.", "past": "Él permitió entrar.", "future": "Él permitirá entrar."},
    {"en": "appear", "es": "aparecer", "icon": "🌅",
     "present": "Él aparece tarde.", "past": "Él apareció tarde.", "future": "Él aparecerá tarde."},
]

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
    display:flex;gap:6px;overflow-x:auto;padding:10px 20px 14px;
    scrollbar-width:none;
  }
  nav.tabs::-webkit-scrollbar{display:none}
  .tab{
    flex:0 0 auto;
    padding:9px 14px;border-radius:999px;border:1px solid var(--line);
    background:#fff;color:var(--ink);font-weight:600;font-size:14px;
    cursor:pointer;transition:.2s ease;
  }
  .tab:hover{transform:translateY(-1px)}
  .tab.active{
    background:linear-gradient(135deg,var(--brand),var(--brand-2));
    color:#fff;border-color:transparent;box-shadow:var(--shadow);
  }
  main{padding:8px 20px 60px}
  .hero{
    max-width:1100px;margin:14px auto 22px;
    display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;
  }
  .hero h2{margin:0;font-size:28px;letter-spacing:-.2px}
  .hero p{margin:4px 0 0;color:var(--muted)}
  .hint{
    font-size:13px;color:var(--muted);background:#fff;border:1px solid var(--line);
    padding:8px 12px;border-radius:999px;box-shadow:var(--shadow);
  }
  .hint b{color:var(--past)}
  .hint i{color:var(--future);font-style:normal}
  .grid{
    max-width:1100px;margin:0 auto;
    display:grid;gap:18px;
    grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
  }
  .stage{
    position:relative;height:230px;border-radius:var(--radius);
    overflow:hidden;
    background:linear-gradient(180deg,#fafbff,#eef1f8);
    border:1px solid var(--line);
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
    padding:18px 18px 16px;
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
  .placeholder{
    max-width:1100px;margin:40px auto;text-align:center;color:var(--muted);
    background:#fff;border:1px dashed var(--line);border-radius:var(--radius);
    padding:60px 24px;
  }
  .placeholder h3{margin:0 0 6px;color:var(--ink)}
  @media (max-width:520px){
    .hero h2{font-size:22px}
    .stage{height:215px}
    .icon{font-size:54px}
    .sentence{font-size:16px}
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
</style>
</head>
<body>
<header>
  <div class="wrap brand">
    <div class="logo">L</div>
    <div>
      <h1>Léann · Study</h1>
      <small>A clean, simple way to learn.</small>
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
    <div class="hint">Slide <b>→ right</b> for past · Slide <i>← left</i> for future</div>
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

<script>
const SUBJECTS = __SUBJECTS__;
const VERBS = __VERBS__;
const SPANISH_VERBS = __SPANISH_VERBS__;

const tabs = document.getElementById('tabs');
const content = document.getElementById('content');
const title = document.getElementById('title');
const subtitle = document.getElementById('subtitle');

let active = 'Irish';

const ENGLISH_BOOKS = [
  {
    title: 'Purple Hibiscus',
    author: 'Chimamanda Ngozi Adichie',
    cover: '/english/purple_hibiscus.jpg',
    notes: '/english/purple_hibiscus.txt',
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
document.addEventListener('keydown', e => { if(e.key === 'Escape') closeBook(); });

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

function renderTabs(){
  if(active === 'Spanish') document.body.className = 'spanish';
  else if(active === 'English') document.body.className = 'english';
  else document.body.className = '';
  tabs.innerHTML = '';
  SUBJECTS.forEach(s => {
    const b = document.createElement('button');
    b.className = 'tab' + (s===active ? ' active' : '');
    b.textContent = s;
    b.onclick = () => { active = s; renderTabs(); renderContent(); };
    tabs.appendChild(b);
  });
}

function renderContent(){
  if(active === 'English'){
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
    return;
  }
  if(active === 'Irish'){
    title.textContent = 'Gaeilge — 50 Verbs';
    subtitle.textContent = 'Default card shows the present tense.';
    content.className = 'grid';
    content.innerHTML = '';
    VERBS.forEach((v, i) => content.appendChild(buildCard(v, i+1)));
    return;
  }
  if(active === 'Spanish'){
    title.textContent = 'Español — 50 Verbos';
    subtitle.textContent = 'La tarjeta muestra el presente por defecto.';
    content.className = 'grid';
    content.innerHTML = '';
    SPANISH_VERBS.forEach((v, i) => content.appendChild(
      buildCard(v, i+1, {pastLabel:'Pretérito', futureLabel:'Futuro', presentLabel:'Presente', verbField:'es'})
    ));
    return;
  }
  title.textContent = active;
  subtitle.textContent = 'Coming soon — try Irish or Spanish.';
  content.className = '';
  content.innerHTML = `
    <div class="placeholder">
      <h3>${active} is on the way</h3>
      <p>Tap <b>Irish</b> or <b>Spanish</b> to study the 50 most popular verbs.</p>
    </div>`;
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
    </article>`;
  attachSwipe(stage);
  return stage;
}

function attachSwipe(stage){
  const card = stage.querySelector('.card');
  const sentence = stage.querySelector('.sentence');
  const pill = stage.querySelector('[data-pill]');
  const pastLayer = stage.querySelector('.reveal.past');
  const futureLayer = stage.querySelector('.reveal.future');

  let startX=0, dx=0, dragging=false, locked=null;
  const THRESHOLD = 70;

  function setTense(t){
    const pastLabel = card.dataset.pastLabel;
    const futLabel  = card.dataset.futLabel;
    const presLabel = card.dataset.presLabel;
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

  // Tap to reset to present
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
        if _re.match(r'^[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+$', safe):
            fpath = os.path.join(STATIC_BASE, safe)
            if os.path.isfile(fpath):
                ctype, _ = mimetypes.guess_type(fpath)
                ctype = ctype or "application/octet-stream"
                with open(fpath, "rb") as f:
                    data = f.read()
                self._send(200, data, ctype)
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
