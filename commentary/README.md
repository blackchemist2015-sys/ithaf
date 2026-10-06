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
  - ملحق: معجم المصطلحات العلمية في الكتاب.
- `Mujam_al-Mustalahat.docx`: معجم المصطلحات مستقلًّا: تعريف ١٥٨ مصطلحًا من القائمة المرفقة (مصطلحات الآلة، والهندسة والحساب، والفلك الكروي، والظل والميقات، والكون والجغرافيا)، مع ٣٢ رسمًا توضيحيًّا.
- `figures/png` و`figures/svg`: الأشكال المعاد رسمها (٤٤ شكلًا للتعليق، و١٥ شكلًا بالبادئة G للمعجم).
- `figures/manuscript`: صور الأشكال من النسخة المحققة.
- `tools/`: أدوات إعادة البناء:
  - `figs.py` يولّد الأشكال بصيغة SVG بالحساب الهندسي.
  - `render.js` يحوّلها إلى PNG بمتصفح Chromium (Playwright) بخط Amiri؛ يُعطى مجلد ملفات `amiri-*.woff2` (من حزمة `@fontsource/amiri`) في المتغير `AMIRI_DIR`.
  - `figs_glossary.py` يولّد رسوم المعجم.
  - `content.txt` نص التعليق، و`glossary.txt` نص المعجم، و`content_full.txt` التعليق مع ملحق المعجم؛ و`build_docx.js` يبني منها ملفات Word (حزمة `docx`).

```bash
cd commentary/tools
python3 figs.py && python3 figs_glossary.py
AMIRI_DIR=/path/to/fontsource-amiri/files node render.js
node build_docx.js ../Ithaf_al-Mahbub_Taliq.docx content_full.txt
node build_docx.js ../Mujam_al-Mustalahat.docx glossary.txt
```

المصدر المساعد: Nejib Boulahia, *Some numerical examples, using the sine-quadrant, by ʿAli Ibn Māmī Karbāṣā*, Actes du 14e Colloque maghrébin sur l’histoire des mathématiques arabes (Sousse 2022), pp. 65–81.
