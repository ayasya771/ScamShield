/* ScamShield — front-end logic (vanilla JS, no dependencies). */

const $ = (id) => document.getElementById(id);
const LEVEL_COLOR = { danger: "#e11d48", warning: "#b45309", safe: "#047857" };
const CONFIDENCE_TEXT = {
  high:   "High confidence",
  medium: "Moderate confidence",
  low:    "Low confidence — this one is genuinely borderline",
};
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 52; // matches r=52 in the SVG

let lastMessage = "";

/* ----------------------------------------------------------------- helpers */
function escapeHTML(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function highlight(message, words) {
  let html = escapeHTML(message);
  const unique = [...new Set(words)].filter(Boolean)
    .sort((a, b) => b.length - a.length); // longer words first
  for (const word of unique) {
    const safe = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    html = html.replace(new RegExp(`\\b(${safe})\\b`, "gi"), "<mark>$1</mark>");
  }
  return html;
}

/* ------------------------------------------------------------------- render */
function renderResult(data) {
  lastMessage = data.text;
  const panel = $("result");
  panel.hidden = false;
  panel.dataset.level = data.level;

  // Risk dial
  const offset = GAUGE_CIRCUMFERENCE * (1 - data.risk / 100);
  const fill = $("gaugeFill");
  fill.style.stroke = LEVEL_COLOR[data.level];
  fill.style.strokeDashoffset = String(offset);
  animateNumber($("riskNum"), data.risk);

  // Verdict
  $("verdictTitle").textContent = data.verdict.replace(/--/g, "—");
  $("verdictConfidence").textContent =
    `${CONFIDENCE_TEXT[data.confidence]} · the model rates this ${data.risk}% likely to be a scam.`;

  // Message with suspicious words marked (only when there's actually concern --
  // highlighting a word under a "looks genuine" verdict is just confusing).
  $("echo").innerHTML = highlight(data.text, data.level === "safe" ? [] : data.flag_words);

  // Reasons
  const list = $("reasons");
  list.innerHTML = "";
  const peak = Math.max(1, ...data.reasons.map((r) => Math.abs(r.weight)));
  if (!data.reasons.length) {
    list.innerHTML = `<li class="reason"><span class="reason__text">No strong signals either way — there simply isn't much to go on in this message.</span></li>`;
  }
  for (const reason of data.reasons) {
    const li = document.createElement("li");
    li.className = `reason reason--${reason.direction}`;
    const width = Math.round((Math.abs(reason.weight) / peak) * 100);
    li.innerHTML = `
      <span class="reason__tag">${reason.direction === "scam" ? "scam" : "genuine"}</span>
      <span class="reason__text">${escapeHTML(reason.text)}</span>
      <span class="reason__bar" title="strength of this clue"><span style="width:${width}%"></span></span>`;
    list.appendChild(li);
  }

  // Advice
  $("advice").textContent = data.advice;

  // reset feedback line and re-trigger the entrance animation
  $("feedbackMsg").textContent = "";
  panel.classList.remove("result--in");
  void panel.offsetWidth;
  panel.classList.add("result--in");
  panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function animateNumber(el, target) {
  // The final value is set up front, so the display is always correct even if
  // the count-up animation never runs (reduced motion, or a throttled/hidden
  // tab where requestAnimationFrame is paused). The animation is pure polish.
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    el.textContent = target; return;
  }
  const start = performance.now(), from = 0, dur = 700;
  let settled = false;
  const finish = () => { if (!settled) { settled = true; el.textContent = target; } };
  function step(now) {
    if (settled) return;
    const t = Math.min(1, (now - start) / dur);
    el.textContent = Math.round(from + (target - from) * (1 - Math.pow(1 - t, 3)));
    if (t < 1) requestAnimationFrame(step); else finish();
  }
  requestAnimationFrame(step);
  setTimeout(finish, dur + 150);   // safety net so the value always lands
}

/* --------------------------------------------------------------- API calls */
async function check() {
  const message = $("message").value.trim();
  if (!message) { $("message").focus(); return; }
  const btn = $("check");
  btn.disabled = true; btn.lastChild.textContent = " Checking…";
  try {
    const res = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    renderResult(data);
  } catch (err) {
    alert(err.message);
  } finally {
    btn.disabled = false; btn.lastChild.textContent = " Check this message";
  }
}

async function teach(label) {
  if (!lastMessage) return;
  const note = $("feedbackMsg");
  note.textContent = "Teaching…";
  try {
    const res = await fetch("/api/teach", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: lastMessage, label }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not save that.");
    note.textContent = `Thanks — added to its memory (now ${data.stats.messages} messages). Re-checked with what it just learned.`;
    renderResult(data.result);
    note.textContent = `Thanks — ScamShield has learned from this and now knows ${data.stats.messages} messages.`;
  } catch (err) {
    note.style.color = "#e11d48";
    note.textContent = err.message;
  }
}

/* ------------------------------------------------------------------- setup */
function buildExamples() {
  const data = JSON.parse($("examplesData").textContent);
  const wrap = $("examples");
  for (const ex of data) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.innerHTML = `<span class="chip__dot chip__dot--${ex.label}"></span><span class="chip__text">${escapeHTML(ex.text)}</span>`;
    chip.addEventListener("click", () => {
      $("message").value = ex.text;
      $("message").focus();
      check();
    });
    wrap.appendChild(chip);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  buildExamples();
  $("check").addEventListener("click", check);
  $("clear").addEventListener("click", () => {
    $("message").value = "";
    $("result").hidden = true;
    lastMessage = "";
    $("message").focus();
  });
  $("message").addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") check();
  });
  document.querySelectorAll(".feedback__btns .btn").forEach((b) =>
    b.addEventListener("click", () => teach(b.dataset.label)));
});
