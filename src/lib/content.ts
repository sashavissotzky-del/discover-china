// Helpers for reading the content in src/data/.
import images from '../data/images.json';
import extraCredits from '../data/images-extra-credits.json';
import type { Lang } from '../i18n/ui';
import { existsSync } from 'node:fs';
import sizeOf from './imgsize';

/** A content text: plain (names in English/Chinese) or translatable {he, en}. */
export type Text = string | { he: string; en: string | null } | null | undefined;

/** Text in the page language. Until the English translation exists, English pages fall back to Hebrew. */
export function tx(v: Text, lang: Lang): string {
  if (v == null) return '';
  if (typeof v === 'string') return v;
  return (lang === 'en' ? v.en : v.he) ?? v.he;
}

/** Is this text still waiting for an English translation? */
export function needsTranslation(v: Text): boolean {
  return typeof v === 'object' && v !== null && v.en == null;
}

type ImgEntry = { file: string; credit?: string };
const all: Record<string, ImgEntry> = {
  ...(images as Record<string, ImgEntry>),
  ...Object.fromEntries(Object.entries(extraCredits as Record<string, string>).map(([k, c]) => [k, { file: `img/${k}.webp`, credit: c }])),
};

/** Image address; `thumb` gives the small 320px version. */
export function img(id: string, thumb = false): string {
  const e = all[id];
  if (!e) return '';
  const f = '/' + e.file;
  return thumb ? f.replace(/\.webp$/, '_t.webp') : f;
}

/**
 * All sizes of a photo for `srcset` (small 320px, medium 800px, full), so phones with sharp
 * screens get a sharp picture and small cards don't download the big file.
 */
export function imgSet(id: string): string {
  const full = img(id);
  if (!full) return '';
  const parts: string[] = [];
  for (const [suffix] of [['_t'], ['_m'], ['']]) {
    const f = full.replace(/\.webp$/, `${suffix}.webp`);
    const w = sizeOf('public' + f);
    if (existsSync('public' + f) && w) parts.push(`${f} ${w}w`);
  }
  return parts.join(', ');
}

/** Photo credit: author + licence, with a link to the original on Wikimedia Commons when there is one. */
export function credit(id: string): { text: string; href?: string } | null {
  const c = all[id]?.credit;
  if (!c) return null;
  const [file, who = ''] = c.split('|');
  if (file === '@') return who.trim() ? { text: who } : null; // source not recorded yet
  return { text: who.trim() || 'Wikimedia Commons', href: `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(file)}` };
}

/** Remove a leading emoji (the dashboard data starts some texts with one; the site uses line icons). */
export function noEmoji(s: string): string {
  return s.replace(/^(?:\p{Extended_Pictographic}|\uFE0F|\u200D|\s)+/u, '');
}
