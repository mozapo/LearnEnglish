/* Teacher Academy – Preview: behaviour for the new .bai-ta sections.
   WordPress content rules (same as the original hub script): ES5 only, every statement ends
   with a semicolon, no "&&", no line comments, no literal "<" in strings. build.py checks this.
   Reads the hub's progress (localStorage "bai_ac_" + language) but never writes to it.
   All visible strings come from the per-language data block (D.s). */
(function(){
  "use strict";
  var doc = document;
  function $(id){ return doc.getElementById(id); }
  function each(list, fn){ Array.prototype.forEach.call(list, fn); }
  function el(tag, cls, text){ var e = doc.createElement(tag); if(cls){ e.className = cls; } if(text != null){ e.textContent = text; } return e; }
  var RM = false;
  try { RM = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch(err){ RM = false; }

  var D = { mods: [], quiz: [] };
  try { D = JSON.parse($("bai-ta-data").textContent); } catch(err){ return; }
  var S = D.s;
  function fmt(t, n){ return t.replace("{n}", String(n)); }

  function readState(){
    try {
      var o = JSON.parse(window.localStorage.getItem("bai_ac_" + D.lang) || "null");
      if(!o){ return { m: {} }; }
      if(!o.m){ o.m = {}; }
      return o;
    } catch(err){ return { m: {} }; }
  }
  function isDone(st, i){ var r = st.m[String(i)]; return r ? !!r.done : false; }
  function hasCert(st){ if(st.cert){ if(st.cert.code){ return true; } } return false; }

  /* Scroll reveal */
  function reveal(){
    var items = doc.querySelectorAll(".bai-ta-rv");
    if(RM || !("IntersectionObserver" in window)){ each(items, function(x){ x.classList.add("is-in"); }); return; }
    doc.documentElement.classList.add("bai-ta-anim");
    var io = new IntersectionObserver(function(entries){
      each(entries, function(en){ if(en.isIntersecting){ en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
    each(items, function(x){ io.observe(x); });
  }

  /* Hero badge counters ("10 Modül", "~3 saat") */
  function counters(){
    if(RM){ return; }
    each(doc.querySelectorAll(".bai-ac__badges .bai-ac__badge span"), function(s){
      var m = /^(~?)(\d+)(\s.*)$/.exec(s.textContent);
      if(!m){ return; }
      var pre = m[1], to = parseInt(m[2], 10), post = m[3], t0 = null, dur = 1200;
      function step(t){
        if(t0 === null){ t0 = t; }
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
        s.textContent = pre + Math.round(to * e) + post;
        if(p !== 1){ window.requestAnimationFrame(step); }
      }
      s.textContent = pre + "0" + post;
      window.requestAnimationFrame(step);
    });
  }

  /* Real progress from the hub, shown on ring, roadmap, chart and path */
  function progress(){
    var st = readState(), n = 0, i, firstOpen = 0;
    for(i = 1; i <= 10; i++){ if(isDone(st, i)){ n++; } else if(!firstOpen){ firstOpen = i; } }
    var cert = hasCert(st);
    each(doc.querySelectorAll(".bai-ta-ring path[data-i]"), function(p){
      var k = parseInt(p.getAttribute("data-i"), 10);
      p.classList.toggle("is-done", isDone(st, k));
      p.classList.toggle("is-next", k === firstOpen);
    });
    if($("bai-ta-ringn")){ $("bai-ta-ringn").textContent = String(n); }
    if($("bai-ta-ringtxt")){
      $("bai-ta-ringtxt").textContent = n === 0 ? S.ring0 : (n === 10 ? S.ringAll : fmt(n === 1 ? S.ringOne : S.ringN, n));
    }
    each(doc.querySelectorAll(".bai-ta-stops li[data-stop]"), function(li){
      var s = li.getAttribute("data-stop");
      li.classList.toggle("is-done", (s === "1" || s === "2") ? n === 10 : cert);
    });
    each(doc.querySelectorAll(".bai-ta-chart li[data-m]"), function(li){
      li.classList.toggle("is-done", isDone(st, li.getAttribute("data-m")));
    });
    var pp = $("bai-ta-pathprog");
    if(pp){ pp.textContent = cert ? S.certReady : (n > 0 ? fmt(S.pathN, n) : ""); }
  }

  /* Our CTAs follow the hub's hero CTA (Programa başla / Kaldığın yerden devam et / Sertifika sınavına gir) */
  function mirror(){
    var c = $("bai-ac-cta");
    if(!c){ return; }
    each(doc.querySelectorAll(".bai-ta-cta-mirror"), function(a){ a.textContent = c.textContent; a.setAttribute("href", c.getAttribute("href")); });
  }

  /* Journey bar: chapters fill in as the visitor reaches them */
  function journey(){
    var nav = $("bai-ta-journey"); if(!nav){ return; }
    var links = nav.querySelectorAll("a[data-ch]"), chs = [], i, ticking = false;
    for(i = 1; i <= 4; i++){ chs.push($("bai-ta-ch" + i)); }
    var fill = $("bai-ta-jfill");
    function update(){
      ticking = false;
      var vh = window.innerHeight || 800, active = 0, k;
      for(k = 0; k !== 4; k++){
        if(chs[k]){ if(chs[k].getBoundingClientRect().top - vh * 0.6 <= 0){ active = k + 1; links[k].classList.add("is-done"); } }
      }
      each(links, function(a, j){ if(j + 1 === active){ a.setAttribute("aria-current", "step"); } else { a.removeAttribute("aria-current"); } });
      if(fill){
        var first = chs[0], last = chs[3], f = 0;
        if(first){ if(last){
          var a0 = first.getBoundingClientRect().top + window.pageYOffset - vh * 0.6;
          var a1 = last.getBoundingClientRect().top + window.pageYOffset - vh * 0.6;
          f = (window.pageYOffset - a0) / Math.max(1, a1 - a0);
        } }
        fill.style.transform = "scaleX(" + Math.max(0, Math.min(1, f)) + ")";
      }
    }
    function onScroll(){ if(!ticking){ ticking = true; window.requestAnimationFrame(update); } }
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    update();
  }

  /* Module-match quiz ("Hangi modül sana en çok yarar?" / "Which module will help you most?") */
  function quiz(){
    var intro = $("bai-ta-qintro"), play = $("bai-ta-qplay"), res = $("bai-ta-qresult");
    if(!intro){ return; }
    var Q = D.quiz, cur = 0, ans = [];
    function show(which){ intro.hidden = which !== intro; play.hidden = which !== play; res.hidden = which !== res; }
    function render(){
      var q = Q[cur], box = $("bai-ta-qopts");
      $("bai-ta-qcount").textContent = S.question + " " + (cur + 1) + " / " + Q.length;
      $("bai-ta-qfill").style.transform = "scaleX(" + ((cur + 1) / Q.length) + ")";
      $("bai-ta-qtext").textContent = q.q;
      while(box.firstChild){ box.removeChild(box.firstChild); }
      each(q.o, function(o, k){
        var b = el("button", "bai-ta-opt", o.t);
        b.type = "button";
        b.setAttribute("aria-pressed", ans[cur] === k ? "true" : "false");
        b.addEventListener("click", function(){ ans[cur] = k; if(cur === Q.length - 1){ finish(); } else { cur++; render(); } });
        box.appendChild(b);
      });
      if(!RM){ box.classList.remove("bai-ta-qswap"); void box.offsetWidth; box.classList.add("bai-ta-qswap"); }
      $("bai-ta-qtext").focus();
    }
    function finish(){
      var score = {}, i, k;
      for(i = 1; i <= 10; i++){ score[i] = 0; }
      each(ans, function(a, qi){ each(Q[qi].o[a].m, function(m, w){ score[m] += w === 0 ? 2 : 1; }); });
      var order = D.mods.slice().sort(function(x, y){ return (score[y.n] - score[x.n]) || (x.n - y.n); });
      var box = $("bai-ta-rcards");
      while(box.firstChild){ box.removeChild(box.firstChild); }
      for(k = 0; k !== 2; k++){
        var m = order[k], a = el("a", "bai-ta-rcard");
        a.href = m.u;
        a.appendChild(el("span", "bai-ta-rcard__n", S.module + " " + m.n));
        a.appendChild(el("b", null, m.t));
        a.appendChild(el("span", "bai-ta-rcard__d", m.d));
        a.appendChild(el("span", "bai-ta-rcard__m", m.min + " " + S.minRead));
        box.appendChild(a);
      }
      mirror();
      show(res);
      $("bai-ta-rtitle").focus();
    }
    $("bai-ta-qstart").addEventListener("click", function(){ cur = 0; ans = []; show(play); render(); });
    $("bai-ta-qback").addEventListener("click", function(){ if(cur === 0){ show(intro); $("bai-ta-qstart").focus(); } else { cur--; render(); } });
    $("bai-ta-qagain").addEventListener("click", function(){ cur = 0; ans = []; show(play); render(); });
  }

  /* Exam pool: highlight a random 30 of the 64 questions */
  function pool(){
    var cells = doc.querySelectorAll("#bai-ta-pool i");
    if(!cells.length){ return; }
    function draw(){
      var idx = [], i, j, t;
      for(i = 0; i !== cells.length; i++){ idx.push(i); }
      for(i = idx.length - 1; i > 0; i--){ j = Math.floor(Math.random() * (i + 1)); t = idx[i]; idx[i] = idx[j]; idx[j] = t; }
      each(cells, function(c){ c.classList.remove("is-on"); });
      for(i = 0; i !== 30; i++){ cells[idx[i]].classList.add("is-on"); }
    }
    draw();
    var b = $("bai-ta-shuffle");
    if(b){ b.addEventListener("click", function(){ draw(); var lv = $("bai-ta-poollive"); if(lv){ lv.textContent = ""; window.setTimeout(function(){ lv.textContent = S.newPaper; }, 60); } }); }
  }

  function boot(){
    reveal(); counters(); progress(); mirror(); journey(); quiz(); pool();
    window.setTimeout(mirror, 800);
    window.setTimeout(function(){ progress(); mirror(); }, 2500);
    window.addEventListener("storage", progress);
  }
  if(doc.readyState === "loading"){ doc.addEventListener("DOMContentLoaded", boot); } else { boot(); }
})();
