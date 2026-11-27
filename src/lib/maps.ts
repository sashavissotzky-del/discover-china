// Map links, same as in the dashboard. Amap comes first (better inside China), Google Maps second.
export const gm = (q: string) => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}`;
export const am = (zh: string, city = '') =>
  `https://uri.amap.com/search?keyword=${encodeURIComponent(zh)}&city=${encodeURIComponent(city)}`;
