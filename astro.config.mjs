// @ts-check
import { defineConfig } from 'astro/config';

// English first; more languages can be added to `locales` later.
export default defineConfig({
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
});
