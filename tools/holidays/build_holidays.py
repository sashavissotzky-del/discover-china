"""Build src/data/calendar-holidays.json: public holidays in China and Israel for the trip calendar.

- China: copied from the official State Council notices (国务院办公厅关于XXXX年部分节假日安排的通知),
  including the extra working days (调休). A year is added only after its notice is published (usually November).
- Israel: calculated from the Hebrew calendar (convertdate), so every year is covered.

A date can hold several holidays (e.g. 1–3 Oct 2027 is both Rosh Hashanah and China's Golden Week).
Run:  pip install convertdate && python3 tools/holidays/build_holidays.py
"""
import json, os
from datetime import date, timedelta
from convertdate import hebrew

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

# ---------------- China (official notices) ----------------
CN_SOURCES = {
    2026: '国办发明电〔2025〕7号 · 4.11.2025 · https://www.news.cn/politics/20251104/88bcffd88ae249e58c699b8772548e3d/c.html',
    2027: '国办发明电〔2026〕10号 · 5.11.2026 · https://www.news.cn/politics/20261105/f90cd6ad4df94ab4833b141e52ccfc13/c.html',
}
CN_NAMES = {
    'ny': ('元旦 New Year', 'ראש השנה האזרחית · חופשה בסין', "New Year's Day · holiday in China"),
    'sf': ('春节 Spring Festival', 'השנה הסינית · חופשה בסין, עומס גדול', 'Spring Festival · holiday in China, very crowded'),
    'qm': ('清明节 Qingming', 'צ׳ינגמינג · חופשה בסין', 'Qingming · holiday in China'),
    'ld': ('劳动节 Labour Day', 'חג העבודה · חופשה בסין, עומס גדול', 'Labour Day · holiday in China, very crowded'),
    'db': ('端午节 Dragon Boat', 'חג סירות הדרקון · חופשה בסין', 'Dragon Boat Festival · holiday in China'),
    'ma': ('中秋节 Mid-Autumn', 'אמצע הסתיו · חופשה בסין', 'Mid-Autumn Festival · holiday in China'),
    'nd': ('国庆节 Golden Week', 'Golden Week · חופשה בסין, עומס גדול', 'Golden Week · holiday in China, very crowded'),
}
# (key, first day, last day) and extra working days, exactly as in the notices
CN = {
    2026: {'off': [('ny', '01-01', '01-03'), ('sf', '02-15', '02-23'), ('qm', '04-04', '04-06'), ('ld', '05-01', '05-05'),
                   ('db', '06-19', '06-21'), ('ma', '09-25', '09-27'), ('nd', '10-01', '10-07')],
           'work': ['01-04', '02-14', '02-28', '05-09', '09-20', '10-10']},
    2027: {'off': [('ny', '01-01', '01-03'), ('sf', '02-05', '02-13'), ('qm', '04-03', '04-05'), ('ld', '05-01', '05-05'),
                   ('db', '06-09', '06-09'), ('ma', '09-15', '09-15'), ('nd', '10-01', '10-07')],
           'work': ['01-31', '02-14', '05-08', '09-26', '10-09']},
}

# ---------------- Israel (Hebrew calendar) ----------------
NISAN, IYAR, SIVAN, TISHREI = 1, 2, 3, 7


def g(y, m, d):
    return date(*hebrew.to_gregorian(y, m, d))


def israel(year):
    """Israeli holidays that fall in Gregorian `year`."""
    out = []
    hy_spring = year + 3760  # Hebrew year of Nisan–Sivan in this Gregorian year
    hy_autumn = year + 3761  # Hebrew year that starts in Tishrei of this Gregorian year
    pes = g(hy_spring, NISAN, 15)
    out.append((pes - timedelta(1), 'ערב פסח', 'Passover eve'))
    for i in range(7):
        out.append((pes + timedelta(i), 'פסח', 'Passover'))
    # Independence Day: 5 Iyar, moved when it falls next to Shabbat
    ind = g(hy_spring, IYAR, 5)
    wd = ind.weekday()  # Mon=0 … Sun=6
    if wd == 4: ind -= timedelta(1)      # Friday -> Thursday
    elif wd == 5: ind -= timedelta(2)    # Saturday -> Thursday
    elif wd == 0: ind += timedelta(1)    # Monday -> Tuesday
    out.append((ind, 'יום העצמאות', 'Independence Day'))
    out.append((g(hy_spring, SIVAN, 6), 'שבועות', 'Shavuot'))
    rh = g(hy_autumn, TISHREI, 1)
    out += [(rh - timedelta(1), 'ערב ראש השנה', 'Rosh Hashanah eve'), (rh, 'ראש השנה', 'Rosh Hashanah'),
            (rh + timedelta(1), 'ראש השנה', 'Rosh Hashanah')]
    yk = g(hy_autumn, TISHREI, 10)
    out += [(yk - timedelta(1), 'ערב יום כיפור', 'Yom Kippur eve'), (yk, 'יום כיפור', 'Yom Kippur')]
    for i in range(15, 23):
        out.append((g(hy_autumn, TISHREI, i), 'סוכות ושמחת תורה', 'Sukkot & Simchat Torah'))
    return [(d, he, en) for d, he, en in out if d.year == year]


def main():
    cal = {}
    add = lambda d, item: cal.setdefault(d.isoformat(), []).append(item)
    for y, spec in CN.items():
        for key, a, b in spec['off']:
            d, end = date.fromisoformat(f'{y}-{a}'), date.fromisoformat(f'{y}-{b}')
            zh, he, en = CN_NAMES[key]
            while d <= end:
                han = zh.split(' ')[0]  # Chinese name, e.g. 国庆节
                add(d, {'c': 'cn', 'he': f'{han} {he}', 'en': f'{han} {en}'})
                d += timedelta(1)
        for w in spec['work']:
            add(date.fromisoformat(f'{y}-{w}'), {'c': 'cn', 'w': 1, 'he': 'יום עבודה במקום חג (调休)', 'en': 'Working day instead of a holiday (调休)'})
    for y in range(2026, 2030):
        for d, he, en in israel(y):
            add(d, {'c': 'il', 'he': he, 'en': en})
    out = {'_about': {
        'cn': 'Official State Council notices: ' + ' | '.join(f'{y}: {s}' for y, s in CN_SOURCES.items()),
        'cnYears': sorted(CN), 'ilYears': [2026, 2027, 2028, 2029],
        'il': 'Calculated from the Hebrew calendar (convertdate).',
    }, **dict(sorted(cal.items()))}
    path = os.path.join(ROOT, 'src/data/calendar-holidays.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('dates:', len(cal), '| China years:', sorted(CN), '| file:', path)


if __name__ == '__main__':
    main()
