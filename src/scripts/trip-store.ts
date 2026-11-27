// The visitor's own trip, kept in this browser (localStorage) until user accounts exist.
// route: chosen route id (null = viewing only) · start: landing date "YYYY-MM-DD" (null = not set)
// len: trip length in nights ("12" | "14"), shared with the routes page.

export type Trip = { route: string | null; start: string | null };
const KEY = 'dc-trip';

export function getTrip(): Trip {
  try {
    const v = JSON.parse(localStorage.getItem(KEY) || '{}');
    return { route: typeof v.route === 'string' ? v.route : null, start: typeof v.start === 'string' ? v.start : null };
  } catch {
    return { route: null, start: null };
  }
}

export function setTrip(patch: Partial<Trip>): Trip {
  const t = { ...getTrip(), ...patch };
  try { localStorage.setItem(KEY, JSON.stringify(t)); } catch {}
  return t;
}

export function getLen(): '12' | '14' {
  try { return localStorage.getItem('dc-len') === '12' ? '12' : '14'; } catch { return '14'; }
}

export function setLen(len: '12' | '14') {
  try { localStorage.setItem('dc-len', len); } catch {}
}
