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
    'lang.switch': 'Language',
    'nav.home': 'Home',
    'nav.destinations': 'Destinations',
    'nav.routes': 'Routes',
    'nav.prep': 'Prepare',
    'nav.main': 'Main menu',
    'arrow.fwd': '→',
    'arrow.back': '←',
    'home.title': 'Discover China',
    'home.subtitle': 'Destination guides, ready-made routes and practical tips for travelling in China.',
    'home.photo': 'Corner tower of the Forbidden City, Beijing',
    'home.start': 'Start here',
    'home.s1.title': 'Get to know the destinations',
    'home.s1.desc': 'Seven cities, the places worth seeing and practical information.',
    'home.s2.title': 'Choose a route',
    'home.s2.desc': 'Five routes of 12–14 nights, with a map and a side-by-side comparison.',
    'home.s3.title': 'Prepare for the trip',
    'home.s3.desc': 'Visa, entry forms, apps, payments and internet in China.',
    'common.soon': 'Coming in the next step',
    'common.photo': 'Photo',
  },
  he: {
    'site.title': 'Discover China — מדריך חכם לטיול בסין',
    'site.description': 'מדריכי טיול לסין, מפות אינטראקטיביות, מסלולים ועדכונים חיים — בחינם.',
    'lang.switch': 'שפה',
    'nav.home': 'ראשי',
    'nav.destinations': 'יעדים',
    'nav.routes': 'מסלולים',
    'nav.prep': 'הכנות',
    'nav.main': 'תפריט ראשי',
    'arrow.fwd': '←',
    'arrow.back': '→',
    'home.title': 'Discover China',
    'home.subtitle': 'מדריכי יעדים, מסלולים מוכנים וטיפים מעשיים לטיול בסין.',
    'home.photo': 'מגדל הפינה של העיר האסורה, בייג׳ינג',
    'home.start': 'מתחילים כאן',
    'home.s1.title': 'מכירים את היעדים',
    'home.s1.desc': 'שבע ערים, המקומות ששווה לראות ומידע מעשי.',
    'home.s2.title': 'בוחרים מסלול',
    'home.s2.desc': 'חמישה מסלולים של 12–14 לילות, עם מפה והשוואה.',
    'home.s3.title': 'מתכוננים לטיול',
    'home.s3.desc': 'ויזה, טפסי כניסה, אפליקציות, תשלומים ואינטרנט בסין.',
    'common.soon': 'בשלב הבא',
    'common.photo': 'צילום',
  },
} as const;

export type UIKey = keyof (typeof ui)['en'];

export function t(lang: Lang, key: UIKey): string {
  return ui[lang][key] ?? ui[defaultLang][key];
}
