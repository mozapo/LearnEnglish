// Checks the shipped JS placement rule against an independent re-implementation, over all patterns.
const fs = require('fs'); const path = require('path');
const page = fs.readFileSync(path.join(__dirname, '..', 'staging', '4011-seviye-testi-40.html'), 'utf8');
const src = page.match(/var LT_CUTS = \[[^\]]*\]; function ltPlace\(correct, perLevel\)\{[\s\S]*?return \[pi, near\]; \}/)[0];
const ltPlace = new Function(src + ' return ltPlace;')();
const N = [7, 7, 7, 7, 6, 6], CUTS = [0, 17, 23, 28, 33, 36];
function ref(per) {
  const total = per.reduce((a, b) => a + b, 0);
  let lvl = 0; CUTS.forEach((c, i) => { if (i > 0 && total >= c) lvl = i; });
  let floor = -1; for (let i = 0; i < 6; i++) { if (per[i] >= N[i] - 1) floor = i; else break; }
  lvl = Math.max(lvl, floor);
  const near = lvl < 5 && CUTS[lvl + 1] - total === 1 ? lvl + 1 : -1;
  return [lvl, near];
}
let n = 0, bad = 0;
(function rec(i, per) {
  if (i === 6) { n++; const a = ltPlace(per.reduce((x, y) => x + y, 0), per.map((c, j) => [c, N[j]])); const b = ref(per);
    if (a[0] !== b[0] || a[1] !== b[1]) { bad++; if (bad < 5) console.log('mismatch', per, a, b); } return; }
  for (let c = 0; c <= N[i]; c++) rec(i + 1, per.concat([c]));
})(0, []);
const L = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
const show = per => L[ltPlace(per.reduce((x, y) => x + y, 0), per.map((c, j) => [c, N[j]]))[0]];
console.log(`checked ${n} per-level score patterns, mismatches: ${bad}`);
console.log('A1+A2 perfect, rest unknown ->', show([7, 7, 0, 0, 0, 0]), '| perfect test ->', show([7, 7, 7, 7, 6, 6]), '| all wrong ->', show([0, 0, 0, 0, 0, 0]));
function oldRule(per) { let p = 0; for (let i = 0; i < 6; i++) { const cum = per.slice(0, i + 1).reduce((a, b) => a + b, 0) / N.slice(0, i + 1).reduce((a, b) => a + b, 0); if (per[i] / N[i] >= 0.6 && cum >= 0.6) p = i; } return L[p]; }
const gap = [7, 4, 2, 5, 4, 4];
console.log('gaps at A2 and B1, strong above', JSON.stringify(gap), '-> new:', show(gap), '| old:', oldRule(gap));
process.exit(bad ? 1 : 0);
