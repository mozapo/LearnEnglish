/* "Seviye testim": level test result, badge and mistake practice inside /panel.
   Source file. build_panel.py strips comments, joins lines and inserts DATA and PLACE_JS.
   Rules for the inline script (wpautop, kses): no double ampersand, no double slash, no tag-like "<" in
   strings, no single ampersand either (written as \x26 where needed). DOM is built with h(), never innerHTML,
   so card text can never inject markup. */
(function(){
  "use strict";
  var root = document.getElementById("seviye-testim");
  if(!root) return;

  var DATA = __DATA__;
  var ORDER = ["A1","A2","B1","B2","C1","C2"];
  __PLACE_JS__

  var KEY = "bai_lt_v1", PKEY = "bai_lt_prog_v1";
  var MAX_AGE = 365 * 24 * 3600 * 1000;
  var VALID = new RegExp("^1[0-9]{8}[0-4x]{" + DATA.q.length + "}$");
  var CALL_URL = "/deneme-dersi-al-4/";
  var TEST_URL = "/seviye-testi-40/";

  function load(k){ try{ var s = localStorage.getItem(k); return s ? JSON.parse(s) : null; }catch(e){ return null; } }
  function save(k, v){ try{ if(v === null){ localStorage.removeItem(k); } else { localStorage.setItem(k, JSON.stringify(v)); } }catch(e){} }
  function track(ev, data){ try{ window.dataLayer = window.dataLayer || []; var o = { event: ev, page_path: location.pathname }; if(data){ for(var k in data){ if(Object.prototype.hasOwnProperty.call(data, k)) o[k] = data[k]; } } window.dataLayer.push(o); }catch(e){} }

  /* h("div", {cls:"x", text:"y", onclick:fn}, [children]) */
  function h(tag, attrs, kids){
    var el = document.createElement(tag), k, v, i, c;
    if(attrs){
      for(k in attrs){
        if(!Object.prototype.hasOwnProperty.call(attrs, k)) continue;
        v = attrs[k];
        if(v === null || v === undefined || v === false) continue;
        if(k === "text") el.textContent = v;
        else if(k === "cls") el.className = v;
        else if(k.indexOf("on") === 0) el.addEventListener(k.slice(2), v);
        else el.setAttribute(k, v === true ? "" : String(v));
      }
    }
    if(kids){
      for(i = 0; i < kids.length; i++){
        c = kids[i];
        if(c === null || c === undefined || c === false) continue;
        el.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
      }
    }
    return el;
  }

  function parseCode(code){
    if(!code || !VALID.test(code)) return null;
    var y = +code.substr(1, 4), m = +code.substr(5, 2), d = +code.substr(7, 2), answers = [], i, ch;
    for(i = 9; i < code.length; i++){ ch = code.charAt(i); answers.push(ch === "x" ? null : +ch); }
    return { code: code, date: new Date(y, m - 1, d), answers: answers };
  }

  function scoreOf(att){
    var byL = {}, per = [], correct = 0, wrong = {}, i, q;
    for(i = 0; i < ORDER.length; i++) byL[ORDER[i]] = [0, 0];
    for(i = 0; i < DATA.q.length; i++){
      q = DATA.q[i];
      byL[q.level][1]++;
      if(att.answers[i] === q.answer){ correct++; byL[q.level][0]++; } else { wrong[q.id] = att.answers[i]; }
    }
    for(i = 0; i < ORDER.length; i++) per.push(byL[ORDER[i]]);
    var pr = ltPlace(correct, per);
    return { correct: correct, level: pr[0], near: pr[1], wrong: wrong };
  }

  function questionById(id){ for(var i = 0; i < DATA.q.length; i++){ if(DATA.q[i].id === id) return DATA.q[i]; } return null; }
  function levelIndex(code){ return ORDER.indexOf(code); }
  function dateTR(d){ return d.toLocaleDateString("tr-TR"); }
  function suffixTo(level){ return level + (level.charAt(1) === "1" ? "’e" : "’ye"); }

  /* ---------------------------------------------------------------- state */
  var params = null;
  try{ params = new URLSearchParams(location.search); }catch(e){ params = null; }
  var incoming = params ? params.get("lt") : null;
  if(incoming){
    if(parseCode(incoming)){
      var prev = load(KEY);
      if(!prev ? true : prev.code !== incoming) save(KEY, { code: incoming, saved: Date.now() });
    }
    try{ var u = new URL(location.href); u.searchParams.delete("lt"); history.replaceState(null, "", u.pathname + u.search + u.hash); }catch(e){}
  }
  var stored = load(KEY);
  if(stored){
    if(!stored.saved ? true : Date.now() - stored.saved > MAX_AGE){ save(KEY, null); save(PKEY, null); stored = null; }
  }
  var att = stored ? parseCode(stored.code) : null;
  var loggedIn = document.body.classList.contains("logged-in");

  function progress(){
    var p = load(PKEY);
    if(!p ? true : p.code !== att.code) p = { code: att.code, cards: {} };
    return p;
  }
  function setStatus(id, status){ var p = progress(); p.cards[id] = status; save(PKEY, p); }
  function statusOf(id){ var p = progress(); return p.cards[id] ? p.cards[id] : "new"; }
  function isFinished(status){ return status === "done" ? true : status === "known"; }

  function plan(sc){
    var pri = [], later = [], i, c, j, mistakes;
    for(i = 0; i < DATA.cards.length; i++){
      c = DATA.cards[i]; mistakes = [];
      for(j = 0; j < c.items.length; j++){ if(Object.prototype.hasOwnProperty.call(sc.wrong, c.items[j])) mistakes.push(c.items[j]); }
      if(!mistakes.length) continue;
      if(levelIndex(c.level) <= sc.level + 1) pri.push(c); else later.push(c);
    }
    return { pri: pri, later: later };
  }

  function show(nodes){
    root.textContent = "";
    for(var i = 0; i < nodes.length; i++){ if(nodes[i]) root.appendChild(nodes[i]); }
    root.hidden = false;
  }
  function focusTop(){ var t = root.querySelector("[data-focus]"); if(t){ try{ t.focus({ preventScroll: true }); }catch(e){ t.focus(); } } try{ root.scrollIntoView({ behavior: "smooth", block: "start" }); }catch(e){ root.scrollIntoView(); } }

  function badgeBox(sc){
    var lv = ORDER[sc.level], meta = DATA.meta[lv];
    return h("div", { cls: "bai-ltp__badge" }, [
      h("small", { text: "Seviye rozetin" }),
      h("strong", { text: meta.title }),
      h("span", { text: lv + " · " + meta.name }),
      sc.near >= 0 ? h("em", { text: suffixTo(ORDER[sc.near]) + " çok yakın" }) : null
    ]);
  }

  /* ---------------------------------------------------------------- views */
  function viewLoggedOut(sc){
    var back = "/panel/?lt=" + att.code + "#seviye-testim";
    var enc = encodeURIComponent(back);
    show([
      h("div", { cls: "bai-ltp__card" }, [
        h("span", { cls: "bai-ltp__eyebrow", text: "Seviye testim" }),
        h("h2", { text: "Seviye testi sonucun hazır", tabindex: "-1", "data-focus": true }),
        badgeBox(sc),
        h("p", { text: "Yanlış yaptığın konuları kısa açıklamalar ve alıştırmalarla çalışmak için giriş yap ya da bir dakikada ücretsiz hesap oluştur. Konular seviyene göre sıralanır." }),
        h("div", { cls: "bai-ltp__acts" }, [
          h("a", { cls: "bai-ltp__btn", href: "/giris-yap/?islem=kayit\x26redirect_to=" + enc, text: "Ücretsiz hesap oluştur" }),
          h("a", { cls: "bai-ltp__btn bai-ltp__btn--ghost", href: "/giris-yap/?redirect_to=" + enc, text: "Giriş yap" })
        ])
      ])
    ]);
  }

  function viewEmpty(){
    show([
      h("div", { cls: "bai-ltp__card" }, [
        h("span", { cls: "bai-ltp__eyebrow", text: "Seviye testim" }),
        h("h2", { text: "Henüz bir seviye testi sonucun yok" }),
        h("p", { text: "40 soruluk ücretsiz testi çöz; tahmini seviyen, rozetin ve hatalarınla çalışma kartların burada görünür." }),
        h("div", { cls: "bai-ltp__acts" }, [ h("a", { cls: "bai-ltp__btn", href: TEST_URL, text: "Seviye testini çöz" }) ]),
        h("p", { cls: "bai-ltp__note", text: "Testi başka bir cihazda çözdüysen, sonuç ekranındaki “bağlantıyı kopyala” ile aldığın bağlantıyı bu cihazda aç." })
      ])
    ]);
  }

  function row(card, sc){
    var st = statusOf(card.id);
    var label = { "new": "Çalış", tried: "Tekrar dene", done: "Tamamlandı ✓", known: "Biliyorsun ✓" }[st];
    return h("li", { cls: "bai-ltp__row" + (isFinished(st) ? " is-done" : "") }, [
      h("span", { cls: "bai-ltp__chip", text: card.level }),
      h("span", { cls: "bai-ltp__rowtitle" }, [ h("strong", { text: card.t_tr }), h("small", { text: card.t_en }) ]),
      h("button", { type: "button", cls: "bai-ltp__rowbtn", text: label, onclick: function(){ viewCard(card, sc); } })
    ]);
  }

  function viewHome(sc){
    var pl = plan(sc), done = 0, i;
    for(i = 0; i < pl.pri.length; i++){ if(isFinished(statusOf(pl.pri[i].id))) done++; }
    var allDone = pl.pri.length > 0 ? done === pl.pri.length : false;
    var pct = pl.pri.length ? Math.round(done / pl.pri.length * 100) : 100;
    var priList = h("ul", { cls: "bai-ltp__list" }), laterList = h("ul", { cls: "bai-ltp__list" });
    for(i = 0; i < pl.pri.length; i++) priList.appendChild(row(pl.pri[i], sc));
    for(i = 0; i < pl.later.length; i++) laterList.appendChild(row(pl.later[i], sc));

    var nodes = [
      h("div", { cls: "bai-ltp__card" }, [
        h("span", { cls: "bai-ltp__eyebrow", text: "Seviye testim" }),
        h("h2", { text: "Sonucun ve çalışma alanın", tabindex: "-1", "data-focus": true }),
        h("div", { cls: "bai-ltp__head" }, [
          badgeBox(sc),
          h("dl", { cls: "bai-ltp__facts" }, [
            h("div", null, [ h("dt", { text: "Puan" }), h("dd", { text: sc.correct + " / " + DATA.q.length }) ]),
            h("div", null, [ h("dt", { text: "Test tarihi" }), h("dd", { text: dateTR(att.date) }) ]),
            h("div", null, [ h("dt", { text: "Çalışılacak konu" }), h("dd", { text: String(pl.pri.length) }) ])
          ])
        ]),
        h("p", { cls: "bai-ltp__note", text: "Bu bir seviye tahminidir. Rozet, sitemizdeki testteki sonucunu gösterir; resmî bir belge değildir. Test dilbilgisi ve kelimeyi ölçer; konuşma ve yazma için bir eğitmenle değerlendirme gerekir." })
      ])
    ];

    if(!pl.pri.length ? !pl.later.length : false){
      nodes.push(h("div", { cls: "bai-ltp__card bai-ltp__win" }, [
        h("h3", { text: "Hiç hatan yok" }),
        h("p", { text: "Testteki tüm soruları doğru yanıtladın. Bir sonraki adım, konuşma ve yazma becerilerini bir eğitmenle değerlendirmek olabilir." }),
        h("a", { cls: "bai-ltp__btn", href: CALL_URL, text: "Ücretsiz ön görüşme planla" })
      ]));
    } else {
      if(allDone){
        nodes.push(h("div", { cls: "bai-ltp__card bai-ltp__win" }, [
          h("span", { cls: "bai-ltp__eyebrow", text: "Çalışma rozeti" }),
          h("h3", { text: "Öncelikli konularını tamamladın" }),
          h("p", { text: "Güzel bir adım. Birkaç gün sonra testi yeniden çözerek ilerlemeni görebilir ya da bir eğitmenle sıradaki hedefini belirleyebilirsin." }),
          h("div", { cls: "bai-ltp__acts" }, [
            h("a", { cls: "bai-ltp__btn", href: CALL_URL, text: "Ücretsiz ön görüşme planla" }),
            h("a", { cls: "bai-ltp__btn bai-ltp__btn--ghost", href: TEST_URL, text: "Testi yeniden çöz" })
          ])
        ]));
      }
      if(pl.pri.length){
        nodes.push(h("div", { cls: "bai-ltp__card" }, [
          h("h3", { text: "Öncelikli konular" }),
          h("p", { text: "Seviyene ve bir üst seviyeye ait hatalar. Her konu yaklaşık 5 dakika sürer: kısa bir kontrol, açıklama ve alıştırma." }),
          h("div", { cls: "bai-ltp__prog", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": String(pl.pri.length), "aria-valuenow": String(done), "aria-label": "Öncelikli konular" }, [ h("i", { style: "width:" + pct + "%" }) ]),
          h("p", { cls: "bai-ltp__note", text: done + " / " + pl.pri.length + " konu tamamlandı" }),
          priList
        ]));
      }
      if(pl.later.length){
        nodes.push(h("details", { cls: "bai-ltp__card bai-ltp__later" }, [
          h("summary", { text: "İleride çalışabileceğin konular (" + pl.later.length + ")" }),
          h("p", { text: "Bunlar şu anki seviyenin iki ya da daha fazla üstünde. Önce öncelikli konuları bitirmen daha verimli olur." }),
          laterList
        ]));
      }
    }

    nodes.push(h("div", { cls: "bai-ltp__foot" }, [
      h("a", { href: TEST_URL, text: "Testi yeniden çöz" }),
      h("a", { href: CALL_URL, text: "Bir eğitmenle çalış" }),
      h("button", { type: "button", cls: "bai-ltp__linkbtn", text: "Sonucu bu tarayıcıdan sil", onclick: function(){
        if(!window.confirm("Seviye testi sonucun ve çalışma ilerlemen bu tarayıcıdan silinsin mi?")) return;
        save(KEY, null); save(PKEY, null); att = null; track("lt_practice_cleared", {}); viewEmpty();
      } })
    ]));
    nodes.push(h("p", { cls: "bai-ltp__note", text: "Sonucun ve ilerlemen yalnızca bu tarayıcıda saklanır, sunucumuza gönderilmez ve 12 ay sonra silinir." }));
    show(nodes);
  }

  /* One multiple-choice question. onAnswer(correct) runs once. Options are shuffled. */
  function mcq(q, num, opts){
    var order = [], i, j, t, answered = false;
    for(i = 0; i < q[1].length; i++) order.push(i);
    for(i = order.length - 1; i > 0; i--){ j = Math.floor(Math.random() * (i + 1)); t = order[i]; order[i] = order[j]; order[j] = t; }
    var fb = h("p", { cls: "bai-ltp__fb", "aria-live": "polite" });
    var btns = h("div", { cls: "bai-ltp__opts", role: "group", "aria-label": "Soru " + num });
    var box = h("div", { cls: "bai-ltp__q" }, [ h("p", { cls: "bai-ltp__qtext" }, [ h("b", { text: num + ". " }), q[0] ]), btns, fb ]);
    for(i = 0; i < order.length; i++){
      (function(idx){
        btns.appendChild(h("button", { type: "button", cls: "bai-ltp__opt", text: q[1][idx], onclick: function(ev){
          if(answered) return;
          answered = true;
          var ok = idx === q[2], all = btns.querySelectorAll("button"), k;
          for(k = 0; k < all.length; k++){ all[k].disabled = true; if(all[k].textContent === q[1][q[2]]) all[k].className += " is-right"; }
          if(!ok) ev.currentTarget.className += " is-wrong";
          fb.textContent = (ok ? "Doğru. " : "Doğru yanıt: " + q[1][q[2]] + ". ") + (opts.why ? (q[3] ? q[3] : "") : "");
          fb.className = "bai-ltp__fb " + (ok ? "is-ok" : "is-no");
          opts.onAnswer(ok);
        } }));
      })(order[i]);
    }
    return box;
  }

  function nextCard(sc, current){
    var pl = plan(sc), i;
    for(i = 0; i < pl.pri.length; i++){ if(pl.pri[i].id !== current.id ? !isFinished(statusOf(pl.pri[i].id)) : false) return pl.pri[i]; }
    return null;
  }

  function viewCard(card, sc){
    var st = statusOf(card.id);
    track("lt_card_open", { card: card.id, status: st });
    var mistakes = [], i, q, chosen;
    for(i = 0; i < card.items.length; i++){
      if(!Object.prototype.hasOwnProperty.call(sc.wrong, card.items[i])) continue;
      q = questionById(card.items[i]); chosen = sc.wrong[card.items[i]];
      mistakes.push(h("li", null, [
        h("span", { cls: "bai-ltp__qtext", text: q.prompt }),
        h("small", { text: "Senin yanıtın: " + (chosen === null ? "yanıtlanmadı" : q.options[chosen]) + " · Doğru yanıt: " + q.options[q.answer] })
      ]));
    }
    var stage = h("div", { cls: "bai-ltp__stage" });
    var head = h("div", { cls: "bai-ltp__card" }, [
      h("button", { type: "button", cls: "bai-ltp__linkbtn", text: "← Konulara dön", onclick: function(){ viewHome(sc); focusTop(); } }),
      h("div", { cls: "bai-ltp__cardtitle" }, [
        h("span", { cls: "bai-ltp__chip", text: card.level }),
        h("h2", { text: card.t_tr, tabindex: "-1", "data-focus": true })
      ]),
      h("p", { cls: "bai-ltp__sub", text: card.t_en }),
      h("div", { cls: "bai-ltp__mistakes" }, [ h("h3", { text: "Testteki sorun" }), h("ul", null, mistakes) ])
    ]);
    show([head, stage]);
    focusTop();
    if(isFinished(st) ? true : st === "tried") lesson(card, sc, stage, false); else quickCheck(card, sc, stage);
  }

  function quickCheck(card, sc, stage){
    var right = 0, answered = 0, n = card.check.length, i;
    var box = h("div", { cls: "bai-ltp__card" }, [
      h("h3", { text: "1. Hızlı kontrol" }),
      h("p", { text: "Önce üç kısa soru. Hepsini doğru yanıtlarsan bu konuyu zaten biliyorsun demektir; testteki hata bir dikkatsizlik olabilir." })
    ]);
    var result = h("div", { cls: "bai-ltp__result", "aria-live": "polite" });
    for(i = 0; i < n; i++){
      box.appendChild(mcq(card.check[i], i + 1, { why: false, onAnswer: function(ok){
        answered++; if(ok) right++;
        if(answered !== n) return;
        if(right === n){
          setStatus(card.id, "known");
          track("lt_card_known", { card: card.id });
          result.appendChild(h("p", { cls: "bai-ltp__win", text: "Üçü de doğru: bunu aslında biliyorsun. Konu tamamlandı olarak işaretlendi." }));
          result.appendChild(h("div", { cls: "bai-ltp__acts" }, [
            h("button", { type: "button", cls: "bai-ltp__btn bai-ltp__btn--ghost", text: "Yine de konuyu çalış", onclick: function(){ result.textContent = ""; lesson(card, sc, stage, true); } }),
            nextButton(card, sc)
          ]));
        } else {
          result.appendChild(h("p", { text: right + " / " + n + " doğru. Şimdi konuyu kısaca toparlayalım." }));
          lesson(card, sc, stage, true);
        }
      } }));
    }
    box.appendChild(result);
    stage.appendChild(box);
  }

  function nextButton(card, sc){
    var nx = nextCard(sc, card);
    return nx
      ? h("button", { type: "button", cls: "bai-ltp__btn", text: "Sıradaki konu →", onclick: function(){ viewCard(nx, sc); } })
      : h("button", { type: "button", cls: "bai-ltp__btn", text: "Konulara dön", onclick: function(){ viewHome(sc); focusTop(); } });
  }

  function lesson(card, sc, stage, numbered){
    var lang = card.lead;
    var text = h("p", { cls: "bai-ltp__expl" });
    var tabTr = h("button", { type: "button", cls: "bai-ltp__tab", text: "Türkçe", onclick: function(){ setLang("tr"); } });
    var tabEn = h("button", { type: "button", cls: "bai-ltp__tab", text: "English", onclick: function(){ setLang("en"); } });
    function setLang(l){
      lang = l; text.textContent = l === "tr" ? card.tr : card.en;
      tabTr.setAttribute("aria-pressed", l === "tr" ? "true" : "false");
      tabEn.setAttribute("aria-pressed", l === "en" ? "true" : "false");
    }
    setLang(lang);
    var exList = h("ul", { cls: "bai-ltp__ex" });
    for(var i = 0; i < card.ex.length; i++) exList.appendChild(h("li", { text: card.ex[i] }));
    stage.appendChild(h("div", { cls: "bai-ltp__card" }, [
      h("h3", { text: (numbered ? "2. " : "") + "Konu" }),
      h("div", { cls: "bai-ltp__tabs", role: "group", "aria-label": "Açıklama dili" }, [ tabTr, tabEn ]),
      text,
      h("p", { cls: "bai-ltp__pat" }, [ h("b", { text: "Kalıp: " }), card.pat ]),
      h("h4", { text: "Örnekler" }),
      exList
    ]));

    var right = 0, answered = 0, n = card.prac.length;
    var result = h("div", { cls: "bai-ltp__result", "aria-live": "polite" });
    var box = h("div", { cls: "bai-ltp__card" }, [
      h("h3", { text: (numbered ? "3. " : "") + "Alıştırma" }),
      h("p", { text: "Her sorudan sonra kısa bir açıklama göreceksin." })
    ]);
    track("lt_card_start", { card: card.id });
    for(var j = 0; j < n; j++){
      box.appendChild(mcq(card.prac[j], j + 1, { why: true, onAnswer: function(ok){
        answered++; if(ok) right++;
        if(answered !== n) return;
        var passed = right / n >= 0.6;
        var before = statusOf(card.id);
        if(passed) setStatus(card.id, "done"); else if(!isFinished(before)) setStatus(card.id, "tried");
        track("lt_card_done", { card: card.id, score: right, of: n });
        result.appendChild(h("p", { cls: passed ? "bai-ltp__win" : "", text: right + " / " + n + " doğru. " + (passed ? "Konu tamamlandı." : "Birkaç gün sonra bu konuya yeniden bakmak iyi olur.") }));
        result.appendChild(h("div", { cls: "bai-ltp__acts" }, [
          nextButton(card, sc),
          h("a", { cls: "bai-ltp__btn bai-ltp__btn--ghost", href: CALL_URL, text: "Bu konuyu bir eğitmenle çalış" })
        ]));
      } }));
    }
    box.appendChild(result);
    stage.appendChild(box);
  }

  /* ---------------------------------------------------------------- start */
  if(!att){
    if(loggedIn) viewEmpty(); else root.hidden = true;
    return;
  }
  var sc = scoreOf(att);
  if(loggedIn){ viewHome(sc); track("lt_practice_open", { level: ORDER[sc.level] }); }
  else viewLoggedOut(sc);
  if(incoming ? true : location.hash === "#seviye-testim") focusTop();
})();
