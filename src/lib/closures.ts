// Weekly closing days of places in the day plans (from verified practical info), used for warnings.
import dayplans from '../data/dayplans.json';
import practical from '../data/practical.json';
import holidays from '../data/calendar-holidays.json';

const PR = practical as Record<string, { closedMonday?: number }>;

/** For each city: its regular days in order (extra "x" days left out), each with the places closed on Mondays. */
export function cityDays(): Record<string, { id: string; closedMon: string[] }[]> {
  const out: Record<string, { id: string; closedMon: string[] }[]> = {};
  for (const [city, v] of Object.entries(dayplans as Record<string, { days: { id: string; stops: { n: string }[] }[] }>)) {
    out[city] = v.days.filter((d) => !d.id.startsWith('x')).map((d) => ({
      id: d.id,
      closedMon: [...new Set(d.stops.filter((s) => PR[s.n]?.closedMonday).map((s) => s.n))],
    }));
  }
  return out;
}

/** Dates that are official holidays in China (places closed on Mondays open on holidays). */
export function cnHolidayDates(): string[] {
  return Object.entries(holidays as Record<string, any>)
    .filter(([d, list]) => !d.startsWith('_') && (list as { c: string; w?: number }[]).some((h) => h.c === 'cn' && !h.w))
    .map(([d]) => d);
}
