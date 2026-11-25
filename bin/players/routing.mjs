// Which answer the behaviour runner gives a document request: the URL
// matching and the route selection, apart from the runner so that
// bin/test_behaviour_harness.py runs them under node without a browser.
// The routes are computed in Python (conformance/behaviour.py,
// document_routes); this file decides nothing beyond taking them in order.

// The declared URL covers the requested one: same origin and path, and every
// query parameter of the declared one present with the same value.
export function covers(declared, requested) {
  let d; let r;
  try { d = new URL(declared); r = new URL(requested); } catch (e) { return false; }
  if (d.origin !== r.origin || d.pathname !== r.pathname) return false;
  for (const [k, v] of d.searchParams) if (!r.searchParams.getAll(k).includes(v)) return false;
  return true;
}

// The answer of the first route covering `url` (routes come most specific
// first) for its n-th request, n counted per route in `served`; null when no
// route covers it.
export function routeAnswer(routes, served, url) {
  const route = routes.find((r) => covers(r.url, url));
  if (!route || !route.answers.length) return null;
  const n = (served.get(route.url) || 0) + 1;
  served.set(route.url, n);
  return { n, doc: route.answers[Math.min(n, route.answers.length) - 1] };
}
