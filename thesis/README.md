<div dir="rtl">

# پیش‌نویس یکپارچه‌ی پایان‌نامه

پایان‌نامه حول سه مشارکت سازمان یافته است: چارچوب کنترل‌شده‌ی ارزیابی حافظه، تجزیه‌ی تشخیصی فاز ۱۸ و تمایز دسترسی و مونتاژ شاهد در فاز ۱۹. دامنه‌ی تجربی تا مرحله‌ی ۱۹ بسته است و این گام آزمایش یا تحلیل همبستگی تازه ندارد.

## سند جاری

[نسخه‌ی بازبینی‌شده PDF](../deliverables/thesis_supervisor_revision_fa.pdf) و [Word قابل ویرایش](../deliverables/thesis_supervisor_revision_fa.docx) اصلاحات شش‌گانه‌ی استاد در ۲۸ اکتبر ۲۰۲۶ را اعمال می‌کنند: ارجاع IEEE، تراز دوطرفه، فونت یکدست فارسی و انگلیسی، دو فرمول قابل ویرایش، شش شکل و هشت جدول و توضیح ابزارها و نقش هوش مصنوعی. این نسخه شامل هشت فصل و چکیده‌های فارسی و انگلیسی است. تایید نهایی متن بازبینی‌شده و تطبیق با شیوه‌نامه‌ی رسمی دانشکده باقی است.

[راهنمای بررسی اصلاحات](review_guide_supervisor_revision_fa.md) · [کتاب‌شناسی IEEE](references_ieee.md) · [نگاشت ارجاع‌ها](ieee_reference_map.json) · [ثبت ابزارها و مدل‌ها](tools_and_ai_register.json) · [داده‌ی شکل‌ها](revision_figure_data.json)

[نسخه‌ی یکپارچه‌ی پیش از اصلاحات](../deliverables/thesis_integrated_fa.pdf) برای سابقه حفظ شده است.

## متن فصل‌ها

- [فصل ۱ کلیات](chapters/01_introduction_fa.md)
- [فصل ۲ مبانی و پیشینه](chapters/02_related_work_fa.md)
- [فصل ۳ داده و روش](chapters/03_methods_fa.md)
- [فصل ۴ چارچوب کنترل‌شده](chapters/04_controlled_framework_fa.md)
- [فصل ۵ شکاف QMSum](chapters/05_qmsum_gap_fa.md)
- [فصل ۶ تشخیص و مونتاژ شاهد](chapters/06_diagnostics_fa.md)
- [فصل ۷ بحث](chapters/07_discussion_fa.md)
- [فصل ۸ نتیجه‌گیری](chapters/08_conclusion_fa.md)

## منابع و ردیابی

- [تحلیل تطبیقی پیشینه](literature_synthesis_fa.md) و [دفتر ۱۶ منبع اصلی](literature_review_20261027.json)
- [کتاب‌شناسی BibTeX](references.bib) و [منابع بیرونی خواندنی](references_fa.md)
- [دفتر یکپارچه‌ی ۱۶ ادعا](evidence_ledger_integrated.json) و [نگاشت منابع داخلی](internal_sources_fa.md)
- [پیوست‌ها](appendices_fa.md)، [برنامه‌ی تدوین](synthesis_plan_fa.md) و [راهنمای بازبینی جاری](review_guide_batch2_fa.md)

منابع اصلی در ۲۷ اکتبر ۲۰۲۶ بررسی شده‌اند؛ وضعیت انتشار و دامنه‌ی خواندن جدا ثبت شده است. این مرور متمرکز، ادعای پوشش نظام‌مند جامع یا رتبه‌بندی مجلات ندارد. روش مقالات دیگر بازاجرا نشده و امتیاز پاسخ آن‌ها با پوشش شاهد این پروژه رتبه‌بندی نشده است.

## اعتبارسنجی و سابقه

`python scripts/build_thesis_evidence.py --check` دفتر بسته‌ی اول را کنترل می‌کند. `python scripts/build_thesis_synthesis.py --check` دفتر یکپارچه، ارجاع‌ها، کتاب‌شناسی و حفظ پرونده‌های تاریخی را بررسی می‌کند. ساخت Word با `python scripts/package_thesis_integrated.py --page-map thesis/integrated_page_map.json` انجام می‌شود و به python-docx و B Nazanin نصب‌شده نیاز دارد. گزارش باید پس از ساخت رندر و بازبینی بصری شود؛ نقشه‌ی صفحه از طرح PDF فعلی می‌آید و پس از تغییر محتوا باید بازسازی شود.

برای نسخه‌ی جاری، شکل‌ها با `python scripts/build_thesis_revision_assets.py` و Word با `python scripts/package_thesis_revision.py --page-map thesis/revision_page_map.json` ساخته می‌شوند. کنترل مستقل نسخه با `python scripts/validate_thesis_revision.py` اجرا می‌شود. نگاشت شماره‌های منابع در هنگام ساخت از ترتیب نخستین استفاده به دست می‌آید؛ کدهای داخلی فصل‌های منبع برای ردیابی باقی‌اند و در Word و PDF به شماره تبدیل می‌شوند.

[گزارش PDF بسته‌ی اول](../deliverables/thesis_batch1_fa.pdf)، [Word بسته‌ی اول](../deliverables/thesis_batch1_fa.docx)، [دفتر ۱۳ ادعای اصلی](evidence_ledger.json) و [راهنمای بازبینی آن بسته](review_guide_fa.md) برای سابقه حفظ شده‌اند. وضعیت کارهای باقی‌مانده را راهنمای جاری مشخص می‌کند.

## هویت دانشگاهی

دانشگاه آزاد اسلامی واحد کرج، درس پروژه‌ی کارشناسی مهندسی کامپیوتر، پژوهشگر یوسف ابوالفتحی روزبهانی، استاد راهنمای دانشگاهی استاد امیر نوری. از دکتر آرش فکری و فردیت FARDIAT، مجتمع فوق تخصصی مغز و شناخت، برای آموزش علوم اعصاب شناختی و بررسی و تایید پروپوزال قدردانی می‌شود. قالب فارسی راست‌چین و RTL با B Nazanin و نشان دانشگاه است.

</div>
