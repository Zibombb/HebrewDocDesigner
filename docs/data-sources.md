# ‏מקורות נתונים

‏פירוט טכני של המקורות שהפרויקט משתמש בהם. ‏כל הנתיבים והדוגמאות אומתו בפועל.

## ‏מקור 1 — Sefaria-Export (GCS bucket)

‏ייצוא חודשי של ספריית Sefaria ‏ב-Google Cloud Storage. ‏פומבי, ‏ללא אימות, ‏נגיש מהסנדבוקס (‏דומיין `storage.googleapis.com` ‏מאושר).

### ‏תאריך ייצוא אחרון

```
https://storage.googleapis.com/sefaria-export/last_export.txt
```

### ‏מבנה עליון

```
storage.googleapis.com/sefaria-export/
├── last_export.txt
├── table_of_contents.json        ‏טבלת תכנים מלאה (‏10MB)
├── json/                         ‏14 קטגוריות עליונות
│   ├── Tanakh/
│   │   ├── Torah/
│   │   ├── Prophets/
│   │   ├── Writings/
│   │   ├── Targum/
│   │   ├── Rishonim on Tanakh/
│   │   ├── Acharonim on Tanakh/
│   │   └── Modern Commentary on Tanakh/
│   ├── Mishnah/  Talmud/  Midrash/  Halakhah/
│   ├── Kabbalah/  Chasidut/  Musar/
│   ├── Liturgy/  Jewish Thought/
│   ├── Responsa/  Tosefta/  Second Temple/  Reference/
├── txt/                          ‏גרסאות טקסט חלקות
├── cltk-flat/  cltk-full/        ‏פורמטים ל-Classical Language Toolkit
├── schemas/                      ‏6,589 קבצי מטא־דטה (‏אחד לכל יצירה)
├── links/                        ‏16 קובצי CSV ‏של קישורים צולבים (~640MB)
└── misc/
    └── topic_graph.csv           ‏גרף נושאים (~15MB)
```

### ‏טקסט תורה בעברית

```bash
curl -sS "https://storage.googleapis.com/sefaria-export/json/Tanakh/Torah/Leviticus/Hebrew/merged.json"
```

‏שדות ב-JSON: `title`, `language`, `versionTitle`, `versionSource`, `text`, `heTitle`, `categories`, `sectionNames`.

‏שדה `text` = ‏רשימת פרקים; ‏כל פרק = ‏רשימת פסוקים (‏מחרוזות). ‏הטקסט עם ניקוד וטעמי מקרא מלאים (MAM — Miqra According to the Mesorah), ‏עם סימוני HTML ‏לסימונים מסורתיים (‏ראה `workflow.md`).

### ‏סכמה של ספר (‏כולל חלוקה לפרשיות)

```bash
curl -sS "https://storage.googleapis.com/sefaria-export/schemas/Leviticus.json"
```

‏שדה `alts.Parasha.nodes` ‏מכיל רשימת פרשיות עם `sharedTitle`, `wholeRef`, `heRef`. ‏זה המקור הסמכותי לטווחי פרשיות — ‏לא לחשב אותם ידנית.

### ‏פרשנים

‏ראשונים וראחרונים: ‏תחת `json/Tanakh/Rishonim on Tanakh/{Author}/{Category}/{Work}/Hebrew/merged.json`.

‏דוגמה: ‏רש״י על ויקרא

```bash
curl -sS "https://storage.googleapis.com/sefaria-export/json/Tanakh/Rishonim%20on%20Tanakh/Rashi/Torah/Rashi%20on%20Leviticus/Hebrew/merged.json"
```

‏מבנה: `text[chapter][verse]` ‏הוא **‏מערך** ‏של הערות (‏לא מחרוזת), ‏כי פרשן יכול לכתוב מספר הערות על פסוק אחד. `sectionNames: [Chapter, Verse, Comment]`.

### ‏מדרשי הלכה ואגדה

‏תחת `json/Midrash/Halakhah/` ‏ו-`json/Midrash/Aggadah/`. ‏למשל ספרא:

```bash
curl -sS "https://storage.googleapis.com/sefaria-export/json/Midrash/Halakhah/Sifra/Hebrew/merged.json"
```

‏ספרא מחולק ‏ב-schema ‏לפי פרשיות ויקרא (‏ויקרא דיבורא דנדבה, ‏צו, ‏שמיני, ‏תזריע פרשת יולדת, ‏תזריע פרשת נגעים, ‏מצורע, ‏וכו׳).

### ‏קישורים צולבים (CSVs)

```
https://storage.googleapis.com/sefaria-export/links/links{0..15}.csv
```

‏עמודות: `Citation 1, Citation 2, Connection Type, Text 1, Text 2, Category 1, Category 2`. ‏כל שורה = ‏קישור בין שני מקורות. ‏גדול — ‏יש להשתמש ב-streaming ‏וסינון לפי `Text 2 = {Book}`.

### ‏גרף נושאים

```
https://storage.googleapis.com/sefaria-export/misc/topic_graph.csv
```

‏עמודות: `Topic 1, Topic 2, Co-occurrence Count`. ‏זוגות נושאים עם ציון הופעות משותפות. ‏סטטיסטי, ‏לא AI.

### ‏GCS JSON API ‏(‏לדפדוף במבנה)

```bash
curl -sS "https://storage.googleapis.com/storage/v1/b/sefaria-export/o?prefix={prefix}&delimiter=/&maxResults=1000"
```

‏החזרה: `items` (‏קבצים) ‏ו-`prefixes` (‏תתי־תיקיות). ‏תמיכה ב-pagination ‏דרך `nextPageToken`.

## ‏מקור 2 — OSHB (Open Scriptures Hebrew Bible)

‏תנ״ך עברי ב-XML ‏לפי פורמט OSIS, ‏מבוסס WLC (‏Westminster Leningrad Codex), ‏תחת `openscriptures/morphhb` ‏ב-GitHub.

‏משמש כמקור **בלתי־תלוי** ‏ל-Sefaria. ‏מתבסס על כתב יד לנינגרד (‏לעומת MAM ‏של Sefaria).

### ‏שליפה ישירה

```bash
curl -sS "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Lev.xml"
```

‏שמות הקבצים (‏אמות לפי OSIS): `Gen.xml`, `Exod.xml`, `Lev.xml`, `Num.xml`, `Deut.xml` (‏לוודא לכל ספר לפני שימוש).

### ‏מבנה XML

‏OSIS XML. ‏namespace: `http://www.bibletechnologies.net/2003/OSIS/namespace`. ‏פסוק מסומן ב-`<verse osisID="Lev.12.1">`. ‏תוכן הפסוק שזור ב-`<w>` ‏עבור כל מילה (‏עם morphology ‏ו-Strong's).

‏לחילוץ טקסט רגיל: ‏לאסוף את `w.text` ‏של כל ה-`<w>` ‏בתוך `<verse>`, ‏לחברם ברווח.

## ‏מה חסום

| ‏דומיין | ‏סטטוס |
|---|---|
| `sefaria.org` | 403 (‏חסום) |
| `developers.sefaria.org` | 403 (‏חסום) |
| `api.sefaria.org` | 403 (‏חסום) |
| `he.wikisource.org` | 403 (‏חסום) |
| ‏רוב ה-APIs ‏של mediawiki | ‏חסום |

‏כל פעולה שמצריכה את המקורות הללו נכשלת. ‏אם נדרש מידע מהם, ‏צריך לחפש מירור או חלופה ב-GitHub ‏או ב-GCS.
