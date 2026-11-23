// All interface text, in every language the site supports.
// To add a language later: add it to `languages` and give it its own block in `ui`.

export const languages = {
  en: { name: 'English', short: 'EN', dir: 'ltr' },
  he: { name: 'עברית', short: 'עב', dir: 'rtl' },
} as const;

export type Lang = keyof typeof languages;
export const defaultLang: Lang = 'en';

export const ui = {
  en: {
    'site.title': 'Discover China — Smart China Travel Guide',
    'site.description': 'Free China travel guides, interactive maps, itineraries and live travel updates.',
    'hero.subtitle': 'Destination guides, interactive maps, itineraries and live travel updates — all in one place.',
    'hero.badge': 'Coming soon',
    'home.destinations': 'Starting destinations',
    'lang.switch': 'Language',
  },
  he: {
    'site.title': 'Discover China — מדריך חכם לטיול בסין',
    'site.description': 'מדריכי טיול לסין, מפות אינטראקטיביות, מסלולים ועדכונים חיים — בחינם.',
    'hero.subtitle': 'מדריכי יעדים, מפות אינטראקטיביות, מסלולים ועדכוני טיול חיים — הכול במקום אחד.',
    'hero.badge': 'בקרוב',
    'home.destinations': 'היעדים הראשונים',
    'lang.switch': 'שפה',
  },
} as const;

export type UIKey = keyof (typeof ui)['en'];

export function t(lang: Lang, key: UIKey): string {
  return ui[lang][key] ?? ui[defaultLang][key];
}
