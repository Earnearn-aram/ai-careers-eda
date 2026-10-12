"use strict";
const PAL = ["--c0","--c1","--c2","--c3","--c4","--c5","--c6","--c7","--c8"];
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const NS = "http://www.w3.org/2000/svg";
const BASE = document.currentScript.src.replace(/app\.js.*$/, "");
let OBS = [], SRC = {}, FX = {}, includeC = /[?&]c=1/.test(location.search);
const REGION = {US:"United States",GB:"United Kingdom",DE:"Germany",FR:"France",NL:"Netherlands",IE:"Ireland",IT:"Italy",AU:"Australia",CA:"Canada",TH:"Thailand",SG:"Singapore",HK:"Hong Kong",LU:"Luxembourg",CH:"Switzerland",AT:"Austria",AE:"UAE",BE:"Belgium",CL:"Chile",ES:"Spain",HR:"Croatia",MX:"Mexico",NZ:"New Zealand",PL:"Poland",SE:"Sweden"};
const rn = c => REGION[c] || c;
const el = (t, a = {}, kids = []) => { const e = t === "svg" || a.ns ? document.createElementNS(NS, t) : document.createElement(t);
  for (const [k, v] of Object.entries(a)) if (k !== "ns") e.setAttribute(k, v); kids.forEach(k => e.append(k)); return e; };
const svgEl = (t, a = {}, kids = []) => { const e = document.createElementNS(NS, t); for (const [k, v] of Object.entries(a)) e.setAttribute(k, v); kids.forEach(k => e.append(k)); return e; };
const tip = o => `${o.region} ${o.period}: ${o.value}${o.unit === "%" ? "%" : " " + o.unit}\nSource: ${(SRC[o.source_id] || {}).name || o.source_id}\nRetrieved: ${o.retrieved_on}\nConfidence: ${o.confidence}${o.reported_via ? "\nReported via: " + o.reported_via : ""}${o.sample_size ? "\nn=" + o.sample_size + (o.sample_size < 30 ? " (small)" : "") : ""}${o.is_estimate ? "\n(estimate)" : ""}`;
const vis = o => includeC || o.confidence !== "C";
const fmt = v => v >= 1000 ? Math.round(v).toLocaleString("en-US") : String(Math.round(v * 100) / 100);

function frame(host, title, sub, rows, svg, legend) {
  host.classList.add("chart"); host.replaceChildren();
  const srcs = [...new Set(rows.map(r => r.source_id))].map(id => SRC[id]?.name || id);
  const conf = [...new Set(rows.map(r => r.confidence))].sort().join("/");
  const retr = [...new Set(rows.map(r => r.retrieved_on))].sort().join(", ");
  const btn = el("button", {}, ["Download data (CSV)"]);
  btn.onclick = () => { const cols = ["id","metric","role","region","period","value","unit","source_id","retrieved_on","definition","confidence","is_estimate","sample_size","notes","reported_via"];
    const q = v => `"${String(v ?? "").replace(/"/g, '""')}"`; const blob = new Blob([[cols.join(","), ...rows.map(r => cols.map(c => q(r[c])).join(","))].join("\n")], {type: "text/csv"});
    const a = el("a", {href: URL.createObjectURL(blob), download: (host.dataset.name || "data") + ".csv"}); a.click(); };
  host.append(el("h3", {}, [title]), el("div", {class: "sub"}, [sub]), legend || "", svg,
    el("div", {class: "foot"}, [`Source and confidence: ${srcs.join("; ") || "none"} · confidence ${conf || "n/a"} · retrieved ${retr || "n/a"}. Hover a point for details. `, btn]));
}

function timeseries(host) {
  const metric = host.dataset.metric, regions = host.dataset.regions.split(",");
  const rows = OBS.filter(o => o.metric === metric && regions.includes(o.region) && vis(o));
  const W = 900, H = 340, m = {l: 44, r: 12, t: 10, b: 28};
  const months = [...new Set(rows.map(r => r.period))].sort();
  if (!months.length) return frame(host, host.dataset.title, "", rows, el("p", {class: "gap"}, ["No data at the selected confidence level."]));
  const idx = new Map(months.map((p, i) => [p, i]));
  const max = Math.max(...rows.map(r => r.value)) * 1.08;
  const x = p => m.l + idx.get(p) / (months.length - 1) * (W - m.l - m.r), y = v => H - m.b - v / max * (H - m.t - m.b);
  const svg = svgEl("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": host.dataset.title});
  for (let i = 0; i <= 4; i++) { const v = max * i / 4; svg.append(svgEl("line", {x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), stroke: css("--line")}), svgEl("text", {x: m.l - 6, y: y(v) + 4, "text-anchor": "end"}, [document.createTextNode(v.toFixed(1) + "%")])); }
  months.filter(p => p.endsWith("-01") || p.endsWith("-07")).forEach(p => svg.append(svgEl("text", {x: x(p), y: H - 8, "text-anchor": "middle"}, [document.createTextNode(p)])));
  const lg = el("div", {class: "legend"});
  regions.forEach((c, i) => { const col = css(PAL[i % PAL.length]); const pts = rows.filter(r => r.region === c).sort((a, b) => a.period.localeCompare(b.period));
    if (!pts.length) { lg.append(el("span", {class: "gap"}, [`${rn(c)}: no data`])); return; }
    let d = ""; pts.forEach((p, j) => { const prev = pts[j - 1]; const contiguous = prev && idx.get(p.period) - idx.get(prev.period) === 1; d += (contiguous ? "L" : "M") + x(p.period).toFixed(1) + " " + y(p.value).toFixed(1); });
    svg.append(svgEl("path", {d, fill: "none", stroke: col, "stroke-width": 2.2}));
    pts.forEach(p => svg.append(svgEl("circle", {cx: x(p.period), cy: y(p.value), r: 4, fill: col, "fill-opacity": 0.01, stroke: "none"}, [Object.assign(svgEl("title"), {textContent: tip(p)})])));
    lg.append(el("span", {}, [el("i", {style: `background:${col}`}), rn(c)])); });
  frame(host, host.dataset.title, host.dataset.sub, rows, svg, lg);
}

function bars(host) { // grouped horizontal bars: one row per region (or skill), one bar per period; gaps stay visible
  const metric = host.dataset.metric, grp = host.dataset.group, bySkill = grp === "skill" || grp === "segment";
  const rows = OBS.filter(o => o.metric === metric && vis(o)), key = o => grp === "segment" ? o.segment : bySkill ? o.skill : o.region, lab = k => bySkill ? k : rn(k);
  const keys = [...new Set(rows.map(key))].sort((a, b) => bySkill ? Math.max(...rows.filter(r => key(r) === b).map(r => r.value)) - Math.max(...rows.filter(r => key(r) === a).map(r => r.value)) : lab(a).localeCompare(lab(b)));
  const years = [...new Set(rows.map(r => r.period))].sort();
  if (!rows.length) return frame(host, host.dataset.title, host.dataset.sub, rows, el("p", {class: "gap"}, ["No data at the selected confidence level. Tick “include confidence C” above to see secondary or unverified figures."]));
  const W = 900, rowH = 12 * years.length + 10, H = keys.length * rowH + 20, m = {l: bySkill ? 210 : 130, r: 70, t: 6};
  const vals = rows.map(r => r.value), lo = Math.min(0, ...vals) * 1.15, hi = Math.max(0, ...vals) * 1.12, x = v => m.l + (v - lo) / (hi - lo) * (W - m.l - m.r);
  const unit = rows[0].unit, show = v => unit === "%" ? fmt(v) + "%" : fmt(v);
  const svg = svgEl("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": host.dataset.title});
  keys.forEach((k, i) => { const yy = m.t + i * rowH; svg.append(svgEl("text", {x: m.l - 8, y: yy + rowH / 2 + 2, "text-anchor": "end"}, [document.createTextNode(lab(k))]));
    years.forEach((yr, j) => { const o = rows.find(r => key(r) === k && r.period === yr); if (!o) return; const h = 10, y0 = yy + j * 12;
      const neg = o.value < 0, x0 = x(0), x1 = x(o.value);
      svg.append(svgEl("rect", {x: Math.min(x0, x1), y: y0, width: Math.max(1, Math.abs(x1 - x0)), height: h, fill: css(PAL[j % PAL.length])}, [Object.assign(svgEl("title"), {textContent: tip(o)})]),
        svgEl("text", {x: neg ? x1 - 4 : x1 + 4, y: y0 + 9, "text-anchor": neg ? "end" : "start"}, [document.createTextNode(show(o.value) + (o.is_estimate ? " ≈" : ""))])); }); });
  if (lo < 0) svg.append(svgEl("line", {x1: x(0), x2: x(0), y1: 0, y2: H - 14, stroke: css("--mut"), "stroke-width": 1}));
  const lg = el("div", {class: "legend"}); years.forEach((yr, j) => lg.append(el("span", {}, [el("i", {style: `background:${css(PAL[j % PAL.length])}`}), yr])));
  frame(host, host.dataset.title, host.dataset.sub, rows, svg, lg);
}

function pay(host) { // one row per role+region+source; local currency first, USD beside it at the stated ECB rate; never merged across sources
  const role = host.dataset.role, all = OBS.filter(o => o.metric.startsWith("salary") && vis(o) && (!role || o.role === role));
  const sib = (o, m) => all.find(r => r.metric === m && r.role === o.role && r.region === o.region && r.source_id === o.source_id && r.unit === o.unit);
  const rows = all.filter(o => o.metric !== "salary_p25_total" && o.metric !== "salary_p75_total" && o.metric !== "salary_p90_total");
  if (!rows.length) return frame(host, host.dataset.title, host.dataset.sub, all, el("p", {class: "gap"}, ["No pay observations at the selected confidence level."]));
  const usd = o => FX[o.unit] ? ` ≈ USD ${fmt(o.value * FX[o.unit].usd_per_unit)}` : "";
  const fig = o => { const a = sib(o, "salary_p25_total"), b = sib(o, "salary_p75_total"), c = sib(o, "salary_p90_total");
    return `${o.unit} ${fmt(o.value)}${o.is_estimate ? " (est.)" : ""}${o.unit !== "USD" ? usd(o) : ""}` + (a && b ? ` · p25–p75 ${fmt(a.value)}–${fmt(b.value)}` : "") + (c ? ` · p90 ${fmt(c.value)}` : ""); };
  const t = el("table", {}, [el("thead", {}, [el("tr", {}, ["Role", "Region", "Figure (local currency; USD at ECB rate)", "Definition", "Source", "n", "Conf."].map(h => el("th", {}, [h])))]),
    el("tbody", {}, rows.sort((a, b) => (a.role + a.region + a.source_id + a.unit).localeCompare(b.role + b.region + b.source_id + b.unit)).map(o => el("tr", {title: tip(o)}, [o.role, rn(o.region), fig(o), o.definition, SRC[o.source_id]?.name || o.source_id, o.sample_size ? o.sample_size + (o.sample_size < 30 ? " ⚠ small" : "") : "n/a", o.confidence].map(v => el("td", {}, [v])))))]);
  const fx = Object.values(FX)[0], note = fx ? el("div", {class: "sub"}, [`USD conversions use ${fx.source} dated ${fx.as_of} (reference rates, not a salary-date or purchasing-power adjustment).`]) : "";
  frame(host, host.dataset.title, host.dataset.sub, all, el("div", {}, [t, note]));
}

function sources(host) {
  host.replaceChildren(el("table", {}, [el("thead", {}, [el("tr", {}, ["id", "Source", "Tier", "Status", "Retrieved", "Notes"].map(h => el("th", {}, [h])))]),
    el("tbody", {}, Object.values(SRC).map(s => el("tr", {}, [s.id, el("a", {href: s.url}, [s.name]), s.tier, s.status, s.retrieved_on || "not retrieved", s.notes].map(v => el("td", {}, [v])))))]));
}

const KINDS = {timeseries, bars, pay, sources};
async function render() { document.querySelectorAll("[data-chart]").forEach(h => KINDS[h.dataset.chart](h)); }
(async () => {
  try { [OBS, SRC, FX] = await Promise.all([fetch(BASE + "data/observations.json").then(r => r.json()), fetch(BASE + "data/sources.json").then(r => r.json()).then(a => Object.fromEntries(a.map(s => [s.id, s]))), fetch(BASE + "data/fx.json").then(r => r.json()).catch(() => ({}))]); }
  catch (e) { document.querySelector("main").prepend(el("p", {class: "banner"}, ["Could not load data/*.json (open via a web server, not file://)."])); return; }
  const cb = document.getElementById("incl-c"); if (cb) cb.checked = includeC;
  if (cb) cb.onchange = () => { includeC = cb.checked; render(); };
  render();
})();
