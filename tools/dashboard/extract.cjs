// Run the dashboard script in a sandbox with a fake browser, then dump its data constants.
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let big = scripts.reduce((a, b) => (b.length > a.length ? b : a));
big = big.replace(/^(const|let)\s+/gm, 'var ');
const handler = {
  get(t, p) {
    if (p === Symbol.toPrimitive) return () => '';
    if (p === Symbol.iterator) return function* () {};
    if (p === 'length') return 0;
    if (p === 'then') return undefined;
    return any;
  },
  apply() { return any; }, construct() { return any; }, set() { return true; }, has() { return true; },
};
const any = new Proxy(function () {}, handler);
const store = {};
const ctx = {
  console, Math, Date, JSON, Object, Array, String, Number, Boolean, RegExp, Map, Set, Promise, Intl, Symbol, Error,
  parseInt, parseFloat, isNaN, encodeURIComponent, decodeURIComponent, setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0,
  requestAnimationFrame: () => 0, document: any, navigator: any, location: any, history: any, fetch: () => new Promise(() => {}),
  localStorage: { getItem: k => store[k] ?? null, setItem: (k, v) => (store[k] = String(v)), removeItem: k => delete store[k] },
  matchMedia: () => any, getComputedStyle: () => any, IntersectionObserver: any, MutationObserver: any, ResizeObserver: any,
  Image: any, URL, URLSearchParams, structuredClone, claude: undefined, addEventListener() {}, CSS: any, performance: any,
};
ctx.window = ctx; ctx.self = ctx; ctx.globalThis = ctx;
vm.createContext(ctx);
try { vm.runInContext(big, ctx, { timeout: 20000 }); } catch (e) { console.error('stopped at:', String(e).slice(0, 200)); }
const names = process.argv.slice(4);
const out = {};
for (const n of names) {
  const v = ctx[n];
  if (v === undefined) { console.error('missing', n); continue; }
  if (typeof v === 'function') continue;
  out[n] = v;
}
fs.writeFileSync(process.argv[3], JSON.stringify(out, null, 1));
console.error('wrote', Object.keys(out).length, 'items');
