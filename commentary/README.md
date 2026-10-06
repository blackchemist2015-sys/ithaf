# التعليق التراثي على «إتحاف المحبوب بشرح مجملة المطلوب في العمل بربع الجيوب»

لعلي بن مامي الحنفي التونسي (كرباصة)، شرحًا على رسالة جمال الدين المارديني في الربع المجيب.

## المحتويات

- `Ithaf_al-Mahbub_Taliq.docx`: التعليق الكامل (ملف Word، من اليمين إلى اليسار، بخط Traditional Arabic). يتضمن:
  - التعريف بالمؤلف والمتن والنسخ ومنهج الشارح ومصادره.
  - موقع الكتاب في تاريخ الآلات الفلكية وتاريخ الفلك الإسلامي، مع خط زمني.
  - وصف الربع المجيب ورسومه على اصطلاح الكتاب، واختبارات صحة الرسوم، وأصل العمل بالأعداد الأربعة المتناسبة.
  - الأشكال التسعة عشر الواردة في المخطوط: الأصل بجانب إعادة الرسم، مع التعليق على كل شكل.
  - الأبواب العشرون: نص العمل، وزيادات الشارح، والصياغة الحديثة، ومثال على عرض تونس مع رسم لمواضع الخيط والمري.
  - تقويم الأمثلة العددية للشارح بإعادة حسابها، والمصادر والمراجع.
- `figures/png` و`figures/svg`: الأشكال المعاد رسمها (٤٤ شكلًا).
- `figures/manuscript`: صور الأشكال من النسخة المحققة.
- `tools/`: أدوات إعادة البناء:
  - `figs.py` يولّد الأشكال بصيغة SVG بالحساب الهندسي.
  - `render.js` يحوّلها إلى PNG بمتصفح Chromium (Playwright) بخط Amiri؛ يُعطى مجلد ملفات `amiri-*.woff2` (من حزمة `@fontsource/amiri`) في المتغير `AMIRI_DIR`.
  - `content.txt` نص التعليق بترميز مبسط، و`build_docx.js` يبني منه ملف Word (حزمة `docx`).

```bash
cd commentary/tools
python3 figs.py
AMIRI_DIR=/path/to/fontsource-amiri/files node render.js
node build_docx.js ../Ithaf_al-Mahbub_Taliq.docx
```

المصدر المساعد: Nejib Boulahia, *Some numerical examples, using the sine-quadrant, by ʿAli Ibn Māmī Karbāṣā*, Actes du 14e Colloque maghrébin sur l’histoire des mathématiques arabes (Sousse 2022), pp. 65–81.
