# اطلس ادبیات مرحله‌ی ۱۷

تاریخ قطع جست‌وجو: ۲۱ اکتبر ۲۰۲۶. ۳۷ منبع؛ تمرکز بر ۲۰۲۴ تا ۲۰۲۶ همراه با مبانی ضروری. این مرور هدفمند و قابل پیگیری است؛ مرور نظام‌مند جامع با ثبت PRISMA نیست. شناسه‌ها در تمام گزارش‌ها ثابت‌اند. «تایید نشد» به معنی «وجود ندارد» نیست. یافته‌های مقاله‌ها گزارش نویسندگان آن‌هاست و در این پروژه بازتولید نشده است.

## نقشه‌ی مقایسه

| منبع | سال/محل و وضعیت | روش/یافته | داده و ارزیابی | محدودیت و ارتباط |
|---|---|---|---|---|
| [R01](https://aclanthology.org/2024.acl-long.747/) | ACL 2024؛ داوری‌شده | گفت‌وگوهای طولانی با پرسش و شاهد نوبتی؛ حافظه‌ی بلندمدت دشوار باقی می‌ماند | LoCoMo؛ پرسش‌پاسخ و بازیابی | ساخت نیمه‌مصنوعی و شاهد احتمالا ناکامل؛ مرز رویداد انسانی نیست |
| [R02](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html) | ICLR 2025؛ داوری‌شده | پنج توانایی حافظه؛ جداسازی نمایه‌سازی، بازیابی و خواندن | LongMemEval؛ ۵۰۰ پرسش، پاسخ و شاهد | ساخت تاریخچه و سطح برچسب با LoCoMo متفاوت؛ تجمیع بی‌تفکیک ناموجه |
| [R03](https://aclanthology.org/2021.naacl-main.472/) | NAACL 2021؛ داوری‌شده | خلاصه‌سازی جلسه بر اساس پرسش و بازه‌ی مرتبط | QMSum؛ جلسه‌های چندحوزه‌ای، خلاصه و بازه | بازه‌ی مرتبط لزوما شاهد کمینه‌ی پاسخ نیست؛ معیار انتقال ما محدود است |
| [R04](https://aclanthology.org/2026.findings-acl.1337/) | Findings ACL 2026؛ داوری‌شده | حافظه‌ی شخصی همراه با حفظ، اصلاح و فراموشی | Memora؛ حالت حافظه و بازیابی جلسه | شناسه‌ی جلسه محل دقیق شاهد را تعیین نمی‌کند؛ مسیر بارگذاری نقش‌ها باید ممیزی شود |
| [R05](https://aclanthology.org/2026.findings-acl.1123/) | Findings ACL 2026؛ داوری‌شده | CompassMem؛ گراف رخداد و رابطه‌ی منطقی برای جست‌وجو | LoCoMo و NarrativeQA؛ پاسخ و اجزای بازیابی | گراف، قطعه و ناوبری هم‌زمان تغییر می‌کنند؛ کنترل اندازه‌ی تقریبی، تساوی فرصت نیست |
| [R06](https://aclanthology.org/2026.acl-long.277/) | ACL 2026؛ داوری‌شده | SEEM؛ قاب رویداد و زنجیره‌ی منشأ، گسترش معکوس شاهد | LoCoMo و LongMemEval؛ بازیابی/پاسخ و حذف مولفه | اجرای اصلی دسته‌ای و مکمل چهار بلوک؛ برخط بودن در سطح هر نوبت نتیجه نمی‌شود |
| [R07](https://aclanthology.org/2026.acl-long.749/) | ACL 2026؛ داوری‌شده | APEX-MEM؛ گراف افزایشی موجودیت، رویداد و ویژگی با ابزار زمانی | LoCoMo و SealQA-Hard؛ پاسخ نهایی | ساخت برخط وابسته به پرسش جاری است؛ هم‌ارز نویسنده‌ی مستقل از پرسش نیست |
| [R08](https://aclanthology.org/2026.acl-long.1150/) | ACL 2026؛ داوری‌شده | قیود نهفته و فاصله‌ی معنایی میان نشانه و حافظه | LoCoMo-Plus؛ پاسخ با داوری مدل | به‌یادآوری واقعیت کافی نیست؛ داوری مولد و ساخت نمونه‌ها محدودیت دارند |
| [R09](https://proceedings.iclr.cc/paper_files/paper/2025/hash/e56f394bbd4f0ec81393d767caa5a31b-Abstract-Conference.html) | ICLR 2025؛ داوری‌شده | SeCom؛ قطعه‌ی موضوعی همراه با فشرده‌سازی و حذف نویز | LoCoMo و Long-MT-Bench+؛ بازیابی/پاسخ، معیارهای قطعه‌بندی | قطعه‌بندی معنایی از قبل انجام شده؛ تغییر محتوا و هزینه جدا باید کنترل شوند |
| [R10](https://arxiv.org/abs/2601.07582) | arXiv 2026؛ پیش‌چاپ، محل داوری تایید نشد | ES-Mem؛ قطعه‌بندی رویدادی پویا و حافظه‌ی سلسله‌مراتبی | ارزیابی حافظه‌ی مکالمه و قطعه‌بندی | نام‌گذاری رویدادمحور نوآوری ما نیست؛ قرارداد دسترسی به آینده نیازمند تطبیق پیاده‌سازی است |
| [R11](https://doi.org/10.1145/3774904.3792089) | The Web Conference 2026؛ داوری‌شده | HingeMem؛ تغییر شخص، زمان، مکان و موضوع همراه با خواندن تطبیقی | LoCoMo؛ حافظه و پاسخ | مستقیما به ایده‌ی مرز چندمولفه‌ای نزدیک؛ اثر مرز از سیاست خواندن جدا نیست |
| [R12](https://aclanthology.org/2026.findings-acl.1091/) | Findings ACL 2026؛ داوری‌شده | TiMem؛ تثبیت حافظه در سلسله‌مراتب زمانی | حافظه‌ی مکالمه‌ی بلندمدت؛ ارزیابی پاسخ | سلسله‌مراتب به‌تنهایی ایده‌ی جدید نیست؛ هزینه و حذف اطلاعات باید کنترل شوند |
| [R13](https://aclanthology.org/2026.findings-acl.1690/) | Findings ACL 2026؛ داوری‌شده | HiGMem؛ هدایت مدل برای حافظه‌ی چندسطحی | مکالمه‌ی بلندمدت؛ پاسخ و مولفه‌ها | مدل هدایت‌کننده متغیر اضافی دارد؛ ادعای مزیت صرفِ مقیاس ناموجه است |
| [R14](https://arxiv.org/abs/2505.19549) | arXiv 2025؛ پیش‌چاپ، محل داوری تایید نشد | MemGAS؛ پیوند چنددانه‌بندی، مسیریابی و پالایش | چند معیار حافظه؛ ارزیابی سامانه | یادگیری انتخاب دانه‌بندی پیشینه دارد؛ هزینه‌ی پالایش و انتخاب مخدوش‌کننده‌اند |
| [R15](https://arxiv.org/abs/2601.00821) | arXiv؛ نخست ۲۰۲۵، نسخه‌ی ۴ در ژوئیه‌ی ۲۰۲۶؛ پیش‌چاپ | مقایسه‌ی متن دست‌نخورده با استخراج اتلافی و کنترل‌های مخدوش‌کننده | LoCoMo و LongMemEval-S؛ پاسخ، کنترل هزینه‌ی شاهد | بودجه‌ی artifact همسان است، اما واحد و فرصت نامزدها لزوما یکسان نیست؛ نزدیک‌ترین هشدار به ادعای ساختار بهتر |
| [R16](https://arxiv.org/abs/2608.12888) | arXiv 2026؛ پیش‌چاپ | ReFind؛ جست‌وجوی عاملی روی نوبت خام، ادغام جلسه و گسترش زمینه | MemoryAgentBench و LongMemEval-S/M؛ پاسخ و هزینه | گسترش زمینه و نوبت خام از قبل وجود دارند؛ خواننده‌ی عاملی هزینه و عوامل اضافی دارد |
| [R17](https://arxiv.org/abs/2608.12990) | arXiv؛ نسخه‌ی ۲ در ۱۴ اکتبر ۲۰۲۶؛ پیش‌چاپ | LycheeMemory V2؛ تجمیع قطعه‌ی معنایی پیش از تثبیت حافظه | LoCoMo و LongMemEval-S؛ پاسخ و هزینه | کاهش فراوانی تثبیت با برتری مرز یکی نیست؛ استخراج مدل به منابع نیاز دارد |
| [R18](https://arxiv.org/abs/2608.30508) | arXiv 2026؛ پیش‌چاپ | UTILMEM؛ سنجش استفاده از شاهد، ربط ضمنی و حواس‌پرتی | ۱۷۱۷ نمونه در پنج حوزه؛ حذف مقابله‌ای شاهد و پاسخ | ساخت و داوری با مدل؛ دسترسی به شاهد، استفاده‌ی صحیح را تضمین نمی‌کند |
| [R19](https://arxiv.org/abs/2602.16974) | arXiv 2026؛ پیش‌چاپ | تقسیم‌بندی راهبردها به انتخاب قطعه و زمان embedding؛ بازسنجی روش‌ها | بازیابی درون سند و مجموعه؛ مقایسه‌ی قطعه‌بندی | نتیجه به محیط بازیابی وابسته است؛ برنده‌ی واحد از این مطالعه نتیجه نمی‌شود |
| [R20](https://arxiv.org/abs/2409.04701) | arXiv؛ نخست ۲۰۲۴، نسخه‌ی ۳ در ۲۰۲۵؛ پیش‌چاپ | Late Chunking؛ embedding با زمینه‌ی بلند سپس تجمیع قطعه | بازیابی متنی؛ کیفیت بردار قطعه | به زمینه‌ی وسیع پیش از قطعه‌بندی دسترسی دارد؛ هم‌ارز نویسنده‌ی علّی نیست |
| [R21](https://aclanthology.org/2024.findings-emnlp.377/) | Findings EMNLP 2024؛ داوری‌شده | LumberChunker؛ مرزبندی روایی با مدل زبانی | اسناد روایی بلند؛ ارزیابی بازیابی | خواندن بلوکی و هزینه‌ی مدل؛ انتقال مستقیم به مکالمه‌ی برخط اثبات نشده |
| [R22](https://aclanthology.org/2024.emnlp-main.845/) | EMNLP 2024؛ داوری‌شده | Dense X Retrieval؛ گزاره‌ی اتمی به‌عنوان واحد بازیابی | بازیابی و پاسخ در دانه‌بندی‌های متفاوت | استخراج گزاره محتوا را عوض می‌کند؛ اثر محل مرز را به‌تنهایی نشان نمی‌دهد |
| [R23](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8a2acd174940dbca361a6398a4f9df91-Abstract-Conference.html) | ICLR 2024؛ داوری‌شده | RAPTOR؛ خوشه‌بندی بازگشتی، خلاصه و درخت بازیابی | پرسش‌پاسخ سند بلند از جمله QuALITY | خلاصه‌سازی و ساخت درخت با مرزبندی متفاوت‌اند؛ حفظ شاهد لفظی نیازمند کنترل است |
| [R24](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ddc001d07ca4f319af96a3024f6dbd1-Abstract-Conference.html) | NeurIPS 2024؛ داوری‌شده | HippoRAG؛ گراف دانش و Personalized PageRank | پرسش‌پاسخ چندگامی | الهام شناختی، شاهد شباهت عصبی نیست؛ استخراج و پیوندها هزینه دارند |
| [R25](https://proceedings.neurips.cc/paper_files/paper/2025/hash/19909c36f51abc4856b4560aff3d36d6-Abstract-Conference.html) | NeurIPS 2025؛ داوری‌شده | A-Mem؛ یادداشت، پیوند و تحول حافظه با الهام از Zettelkasten | حافظه‌ی عامل؛ چند مدل پایه | کنترل اثر مرز محور اصلی نیست؛ تغییر چند مولفه مانع انتساب ساده است |
| [R26](https://elifesciences.org/articles/107955) | eLife 14:RP107955؛ نسخه‌ی نهایی ۷ ژوئیه‌ی ۲۰۲۶ | سازوکارهای متعدد قطعه‌بندی با نشانه‌های خطا و عدم قطعیت | انسان؛ تصویربرداری و مدل‌سازی رویداد | انتقال به عامل زبانی فرضیه است؛ novelty واژگانی جانشین معتبر همه‌ی سازوکارها نیست |
| [R27](https://www.nature.com/articles/s41539-025-00321-6) | npj Science of Learning 10:25؛ 2025؛ داوری‌شده | مرزهای مکانی و هدف/ماموریت در ساختار اپیزودیک سلسله‌مراتبی | واقعیت مجازی؛ حافظه و ترتیب | آزمون انسانی با متن‌کاوی متفاوت است؛ هدف و واژه را نباید یک متغیر دانست |
| [R28](https://www.nature.com/articles/s44271-025-00359-7) | Communications Psychology 3:184؛ 2025؛ داوری‌شده | قطعه‌بندی با مدل زبانی برای سنجش خودکار یادآوری روایت | مرزگذاری و بازگویی روایت انسانی | کاربرد مدل در اندازه‌گیری شناخت، اثبات ادراک یا فهم مدل نیست |
| [R29](https://link.springer.com/article/10.3758/s13415-026-01399-0) | Cognitive, Affective, & Behavioral Neuroscience؛ 2026؛ داوری‌شده | شواهد ERP درباره‌ی مرز روایت و تشکیل حافظه | انسان؛ روایت، ERP و حافظه | پیوند عصبی باید در همان تکلیف تفسیر شود؛ نتیجه‌ی LLM از آن استنتاج نمی‌شود |
| [R30](https://arxiv.org/abs/0710.3742) | arXiv 2007؛ پیش‌چاپ بنیانی | BOCPD؛ استنباط پسین طول رژیم به‌صورت برخط | مدل‌سازی دنباله و تشخیص نقطه‌ی تغییر | نیازمند مدل احتمال و hazard؛ تغییر آماری لزوما تغییر معنایی نیست |
| [R31](https://aclanthology.org/J97-1003/) | Computational Linguistics 23(1)؛ 1997؛ داوری‌شده | TextTiling؛ انسجام واژگانی برای زیرموضوع‌ها | متن چندپاراگرافی؛ قطعه‌بندی | تغییر واژه با مرز تجربه یکی نیست؛ novelty واژگانی سابقه‌ی طولانی دارد |
| [R32](https://proceedings.iclr.cc/paper_files/paper/2026/hash/fd1eff9dd295df50a41f2521942fa31d-Abstract-Conference.html) | ICLR 2026؛ داوری‌شده؛ نسخه‌ی اولیه ۲۰۲۵ | MemoryAgentBench؛ حافظه در تعامل افزایشی و چند توانایی | تعامل چندنوبتی؛ بازیابی، یادگیری و فراموشی | QA ایستا کل حافظه‌ی عامل را نمی‌سنجد؛ مهاجرت پروتکل نیازمند قرارداد وظیفه است |
| [R33](https://profiles.wustl.edu/en/publications/event-perception-a-mind-brain-perspective/) | Psychological Bulletin 133(2)؛ 2007؛ مقاله‌ی مروری داوری‌شده | نظریه‌ی قطعه‌بندی رویداد؛ به‌روزرسانی مدل رخداد و پیش‌بینی | مرور شواهد رفتاری و عصبی | منبع نظری، نه الگوریتم آماده؛ مفهوم خطای پیش‌بینی را نباید به هم‌پوشانی واژه فروکاست |
| [R34](https://arxiv.org/abs/2609.23465) | arXiv؛ نسخه‌ی ۲ در ۱۳ اکتبر ۲۰۲۶؛ پیش‌چاپ | EGMemory؛ زنجیره‌ی شاهد، وضعیت فعال و تاریخچه‌ی اصلاح با propose–verify–commit | GroupMemBench، EverMemBench و LoCoMo؛ پاسخ | منشأ و نسخه‌بندی قبلا پیاده شده؛ سیاست نوشتن/خواندن عاملی هزینه و عوامل متعدد دارد |
| [R35](https://arxiv.org/abs/2610.21900) | arXiv؛ ۱۵ اکتبر ۲۰۲۶؛ پیش‌چاپ | TEM؛ نسخه‌های واقعیت با ترتیب منبع و برچسب تاریخی | ۶۰ شخصیت، ۶۰۰ جلسه، ۴۲۰ پرسش و LoCoMo؛ پاسخ | معیار اصابت موجودیت با صحت کامل پاسخ یکی نیست؛ تعمیم مستقل لازم است |
| [R36](https://arxiv.org/abs/2605.28732) | arXiv؛ نسخه‌ی ۴ در ۸ اکتبر ۲۰۲۶؛ پیش‌چاپ | MemTrace؛ گراف اجرای حافظه و انتساب خطا به عملیات | MemTraceBench؛ ۱۶۰ شکست برچسب‌خورده، تشخیص نوع/عملیات | تشخیص پسینی با پاسخ مرجع؛ بازپخش مداخله‌ای واقعی انجام نمی‌دهد؛ برچسب انسانی لازم دارد |
| [R37](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a05b72653ec5b473732129829ae04195-Abstract-Conference.html) | ICLR 2026؛ داوری‌شده | LightMem؛ فیلتر و گروه‌بندی موضوعی، تثبیت کوتاه‌مدت و به‌روزرسانی آفلاین | LongMemEval با چند مدل؛ پاسخ و هزینه | تثبیت آفلاین با نویسنده‌ی هرنوبتی یکسان نیست؛ اثر موضوع از فشرده‌سازی جدا نمی‌شود |

## شناسنامه و مسیر راستی‌آزمایی

### R01 — Evaluating Very Long-Term Conversational Memory of LLM Agents

نویسندگان: Adyasha Maharana; Dong-Ho Lee; Sergey Tulyakov; Mohit Bansal; Francesco Barbieri; Yuwei Fang.

وضعیت: ACL 2024؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2024/8. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://aclanthology.org/2024.acl-long.747/) · [صفحه‌ی انتشار](https://aclanthology.org/2024.acl-long.747/) · DOI: 10.18653/v1/2024.acl-long.747.

کد/داده: [https://github.com/snap-research/locomo](https://github.com/snap-research/locomo).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R02 — LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory

نویسندگان: Wu, Di; Wang, Hongwei; Yu, Wenhao; Zhang, Yuwei; Chang, Kai-Wei; Yu, Dong.

وضعیت: ICLR 2025؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2025-05-01. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html) · [صفحه‌ی انتشار](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: [https://github.com/xiaowu0162/LongMemEval](https://github.com/xiaowu0162/LongMemEval).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R03 — QMSum: A New Benchmark for Query-based Multi-domain Meeting Summarization

نویسندگان: Ming Zhong; Da Yin; Tao Yu; Ahmad Zaidi; Mutethia Mutuma; Rahul Jha; Ahmed Hassan; Asli Celikyilmaz; Yang Liu; Xipeng Qiu (邱锡鹏); Dragomir Radev.

وضعیت: NAACL 2021؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2021/6. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://aclanthology.org/2021.naacl-main.472/) · [صفحه‌ی انتشار](https://aclanthology.org/2021.naacl-main.472/) · DOI: 10.18653/v1/2021.naacl-main.472.

کد/داده: [https://github.com/Yale-LILY/QMSum](https://github.com/Yale-LILY/QMSum).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R04 — From Recall to Forgetting: Benchmarking Long-Term Memory for Personalized Agents

نویسندگان: Md Nayem Uddin; Kumar Shubham; Eduardo Blanco; Chitta Baral; Gengyu Wang.

وضعیت: Findings ACL 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/7. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://aclanthology.org/2026.findings-acl.1337/) · [صفحه‌ی انتشار](https://aclanthology.org/2026.findings-acl.1337/) · DOI: 10.18653/v1/2026.findings-acl.1337.

کد/داده: [https://github.com/geniesinc/Memora](https://github.com/geniesinc/Memora).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R05 — Memory Matters More: Event-Centric Memory as a Logic Map for Agent Searching and Reasoning

نویسندگان: Yuyang Hu; Jiongnan Liu; Jiejun Tan; Yutao Zhu (朱余韬); Zhicheng Dou (窦志成).

وضعیت: Findings ACL 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/7. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://aclanthology.org/2026.findings-acl.1123/) · [صفحه‌ی انتشار](https://aclanthology.org/2026.findings-acl.1123/) · DOI: 10.18653/v1/2026.findings-acl.1123.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R06 — Structured Episodic Event Memory

نویسندگان: Zhengxuan Lu; Dongfang Li; Yukun Shi; Beilun Wang; Longyue Wang; Baotian Hu.

وضعیت: ACL 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/7. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://aclanthology.org/2026.acl-long.277/) · [صفحه‌ی انتشار](https://aclanthology.org/2026.acl-long.277/) · DOI: 10.18653/v1/2026.acl-long.277.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R07 — APEX-MEM: Agentic Semi-Structured Memory with Temporal Reasoning for Long-Term Conversational AI

نویسندگان: Pratyay Banerjee; Masud Moshtaghi; Shivashankar Subramanian; Amita Misra; Ankit Chadha.

وضعیت: ACL 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/7. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://aclanthology.org/2026.acl-long.749/) · [صفحه‌ی انتشار](https://aclanthology.org/2026.acl-long.749/) · DOI: 10.18653/v1/2026.acl-long.749.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R08 — Locomo-Plus: Beyond-Factual Cognitive Memory Evaluation Framework for LLM Agents

نویسندگان: Yifei Li; Weidong Guo; Lingling Zhang; Rongman Xu; Muye Huang; Hui Liu; Lijiao Xu; Yu Xu; Jun Liu.

وضعیت: ACL 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/7. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://aclanthology.org/2026.acl-long.1150/) · [صفحه‌ی انتشار](https://aclanthology.org/2026.acl-long.1150/) · DOI: 10.18653/v1/2026.acl-long.1150.

کد/داده: [https://github.com/xjtuleeyf/Locomo-Plus](https://github.com/xjtuleeyf/Locomo-Plus).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R09 — SeCom: On Memory Construction and Retrieval for Personalized Conversational Agents

نویسندگان: Pan, Zhuoshi; Wu, Qianhui; Jiang, Huiqiang; Luo, Xufang; Cheng, Hao; Li, Dongsheng; Yang, Yuqing; Lin, Chin-Yew; Zhao, H. Vicky; Qiu, Lili; Gao, Jianfeng.

وضعیت: ICLR 2025؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2025-05-01. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://proceedings.iclr.cc/paper_files/paper/2025/hash/e56f394bbd4f0ec81393d767caa5a31b-Abstract-Conference.html) · [صفحه‌ی انتشار](https://proceedings.iclr.cc/paper_files/paper/2025/hash/e56f394bbd4f0ec81393d767caa5a31b-Abstract-Conference.html) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R10 — ES-Mem: Event Segmentation-Based Memory for Long-Term Dialogue Agents

نویسندگان: Zou, Huhai; Sun, Tianhao; He, Chuanjiang; Tian, Yu; Li, Zhenyang; Jin, Li; Liu, Nayu; Zhong, Jiang; Wei, Kaiwen.

وضعیت: arXiv 2026؛ پیش‌چاپ، محل داوری تایید نشد. تاریخ منبع اولیه/ناشر: 2026/01/12. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2601.07582) · [صفحه‌ی انتشار](https://arxiv.org/abs/2601.07582) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R11 — HingeMem: Boundary Guided Long-Term Memory with Query Adaptive Retrieval for Scalable Dialogues

نویسندگان: Zhong, Yijie; Gao, Yunfan; Wang, Haofen.

وضعیت: The Web Conference 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/04/08. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2604.06845) · [صفحه‌ی انتشار](https://doi.org/10.1145/3774904.3792089) · DOI: 10.1145/3774904.3792089.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R12 — TiMem: Temporal-Hierarchical Memory Consolidation for Long-Horizon Conversational Agents

نویسندگان: Kai Li; Xuanqing Yu; Ziyi Ni; Yi Zeng; Yao Xu; Zheqing Zhang; Xin Li; Jitao Sang (桑基韬); Xiaogang Duan; Xuelei Wang; Chengbao Liu; Jie Tan.

وضعیت: Findings ACL 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/7. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://aclanthology.org/2026.findings-acl.1091/) · [صفحه‌ی انتشار](https://aclanthology.org/2026.findings-acl.1091/) · DOI: 10.18653/v1/2026.findings-acl.1091.

کد/داده: [https://github.com/TiMEM-AI/timem](https://github.com/TiMEM-AI/timem).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R13 — HiGMem: A Hierarchical and LLM-Guided Memory System for Long-Term Conversational Agents

نویسندگان: Shuqi Cao; Jingyi He; Fei Tan.

وضعیت: Findings ACL 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/7. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://aclanthology.org/2026.findings-acl.1690/) · [صفحه‌ی انتشار](https://aclanthology.org/2026.findings-acl.1690/) · DOI: 10.18653/v1/2026.findings-acl.1690.

کد/داده: [https://github.com/ZeroLoss-Lab/HiGMem](https://github.com/ZeroLoss-Lab/HiGMem).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R14 — From Single to Multi-Granularity: Toward Long-Term Memory Association and Selection of Conversational Agents

نویسندگان: Xu, Derong; Wen, Yi; Jia, Pengyue; Zhang, Yingyi; zhang, wenlin; Wang, Yichao; Guo, Huifeng; Tang, Ruiming; Zhao, Xiangyu; Chen, Enhong; Xu, Tong.

وضعیت: arXiv 2025؛ پیش‌چاپ، محل داوری تایید نشد. تاریخ منبع اولیه/ناشر: 2025/05/26. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2505.19549) · [صفحه‌ی انتشار](https://arxiv.org/abs/2505.19549) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: [https://github.com/quqxui/MemGAS](https://github.com/quqxui/MemGAS).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R15 — Fidelity Before Structure: Verbatim Chunks Beat Lossy Artifact Extraction in Long-Conversation LLM Memory

نویسندگان: An, Tao.

وضعیت: arXiv؛ نخست ۲۰۲۵، نسخه‌ی ۴ در ژوئیه‌ی ۲۰۲۶؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2025/12/23. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://arxiv.org/abs/2601.00821) · [صفحه‌ی انتشار](https://arxiv.org/abs/2601.00821) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: [https://github.com/tao-hpu/cog-canvas](https://github.com/tao-hpu/cog-canvas).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R16 — When Your Agent Opens the Chat App: Agent-Controlled Search over Raw Chat Logs Rivals Structured Memory

نویسندگان: Li, Ruizhe; Zhang, Licheng; Xu, Benfeng; Du, Mingxuan; Fu, Zheren; Chen, Weidong.

وضعیت: arXiv 2026؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2026/08/13. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://arxiv.org/abs/2608.12888) · [صفحه‌ی انتشار](https://arxiv.org/abs/2608.12888) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R17 — LycheeMemory V2: Efficient Long-Term Memory for LLM Agents via Semantic Segment-Level Consolidation

نویسندگان: Li, Dongfang; Liu, Zixuan; Wang, Junmai; Huang, Jiahe; Li, Fuhao; Zhang, Lin; Jia, Bonian; Hu, Baotian; Zhang, Min.

وضعیت: arXiv؛ نسخه‌ی ۲ در ۱۴ اکتبر ۲۰۲۶؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2026/08/13. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2608.12990) · [صفحه‌ی انتشار](https://arxiv.org/abs/2608.12990) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R18 — UTILMEM: Benchmarking Evidence Utilization in Long-Term Conversational Memory

نویسندگان: Qing, Peijun; Shi, Fobo; Vosoughi, Soroush.

وضعیت: arXiv 2026؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2026/08/31. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://arxiv.org/abs/2608.30508) · [صفحه‌ی انتشار](https://arxiv.org/abs/2608.30508) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: [https://github.com/peijunallin/UtilMem](https://github.com/peijunallin/UtilMem).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R19 — Beyond Chunk-Then-Embed: A Comprehensive Taxonomy and Evaluation of Document Chunking Strategies for Information Retrieval

نویسندگان: Zhou, Yongjie; Wang, Shuai; Koopman, Bevan; Zuccon, Guido.

وضعیت: arXiv 2026؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2026/02/19. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://arxiv.org/abs/2602.16974) · [صفحه‌ی انتشار](https://arxiv.org/abs/2602.16974) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R20 — Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models

نویسندگان: Günther, Michael; Mohr, Isabelle; Williams, Daniel James; Wang, Bo; Xiao, Han.

وضعیت: arXiv؛ نخست ۲۰۲۴، نسخه‌ی ۳ در ۲۰۲۵؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2024/09/07. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2409.04701) · [صفحه‌ی انتشار](https://arxiv.org/abs/2409.04701) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R21 — LumberChunker: Long-Form Narrative Document Segmentation

نویسندگان: Andre Vicente Duarte; João DS Marques; Miguel Graça; Miguel Freire; Lei Li; Arlindo L. Oliveira.

وضعیت: Findings EMNLP 2024؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2024/11. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://aclanthology.org/2024.findings-emnlp.377/) · [صفحه‌ی انتشار](https://aclanthology.org/2024.findings-emnlp.377/) · DOI: 10.18653/v1/2024.findings-emnlp.377.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R22 — Dense X Retrieval: What Retrieval Granularity Should We Use?

نویسندگان: Tong Chen; Hongwei Wang; Sihao Chen; Wenhao Yu; Kaixin Ma; Xinran Zhao; Hongming Zhang; Dong Yu.

وضعیت: EMNLP 2024؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2024/11. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://aclanthology.org/2024.emnlp-main.845/) · [صفحه‌ی انتشار](https://aclanthology.org/2024.emnlp-main.845/) · DOI: 10.18653/v1/2024.emnlp-main.845.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R23 — RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

نویسندگان: Sarthi, Parth; Abdullah, Salman; Tuli, Aditi; Khanna, Shubh; Goldie, Anna; Manning, Christopher D..

وضعیت: ICLR 2024؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2024/01/31. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2401.18059) · [صفحه‌ی انتشار](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8a2acd174940dbca361a6398a4f9df91-Abstract-Conference.html) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R24 — HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models

نویسندگان: Gutiérrez, Bernal Jiménez; Shu, Yiheng; Gu, Yu; Yasunaga, Michihiro; Su, Yu.

وضعیت: NeurIPS 2024؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2024/05/23. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2405.14831) · [صفحه‌ی انتشار](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ddc001d07ca4f319af96a3024f6dbd1-Abstract-Conference.html) · DOI: 10.52202/079017-1902.

کد/داده: [https://github.com/OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R25 — A-MEM: Agentic Memory for LLM Agents

نویسندگان: Xu, Wujiang; Liang, Zujie; Mei, Kai; Gao, Hang; Tan, Juntao; Zhang, Yongfeng.

وضعیت: NeurIPS 2025؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2025/02/17. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2502.12110) · [صفحه‌ی انتشار](https://proceedings.neurips.cc/paper_files/paper/2025/hash/19909c36f51abc4856b4560aff3d36d6-Abstract-Conference.html) · DOI: 10.52202/085713-0593.

کد/داده: [https://github.com/WujiangXu/A-mem](https://github.com/WujiangXu/A-mem).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R26 — Multiple event segmentation mechanisms in the human brain

نویسندگان: Tan T. Nguyen; Joset A. Etzel; Matthew A. Bezdek; Jeffrey M. Zacks.

وضعیت: eLife 14:RP107955؛ نسخه‌ی نهایی ۷ ژوئیه‌ی ۲۰۲۶. تاریخ منبع اولیه/ناشر: 2026-07-07. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://elifesciences.org/articles/107955) · [صفحه‌ی انتشار](https://elifesciences.org/articles/107955) · DOI: 10.7554/eLife.107955.3.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: تایید کامل سال/دسته از JCR یا SJR در این مرور ممکن نشد؛ رتبه‌ای ادعا نمی‌شود.

### R27 — Hierarchical event segmentation of episodic memory in virtual reality

نویسندگان: Li, Yue; Johansson, Mikael; Nikolaev, Andrey R..

وضعیت: npj Science of Learning 10:25؛ 2025؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2025-05-11. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://www.nature.com/articles/s41539-025-00321-6) · [صفحه‌ی انتشار](https://www.nature.com/articles/s41539-025-00321-6) · DOI: 10.1038/s41539-025-00321-6.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: تایید کامل سال/دسته از JCR یا SJR در این مرور ممکن نشد؛ رتبه‌ای ادعا نمی‌شود.

### R28 — Event segmentation applications in large language model enabled automated recall assessments

نویسندگان: Panela, Ryan A.; Barnett, Alexander J.; Barense, Morgan D.; Herrmann, Björn.

وضعیت: Communications Psychology 3:184؛ 2025؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2025-12-15. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://www.nature.com/articles/s44271-025-00359-7) · [صفحه‌ی انتشار](https://www.nature.com/articles/s44271-025-00359-7) · DOI: 10.1038/s44271-025-00359-7.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: تایید کامل سال/دسته از JCR یا SJR در این مرور ممکن نشد؛ رتبه‌ای ادعا نمی‌شود.

### R29 — How the brain segments experience: ERP evidence of event boundaries enhancing memory formation in narratives

نویسندگان: Zogaj, Doruntinë; Bader, Regine; Mecklinger, Axel.

وضعیت: Cognitive, Affective, & Behavioral Neuroscience؛ 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026/06. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://link.springer.com/article/10.3758/s13415-026-01399-0) · [صفحه‌ی انتشار](https://link.springer.com/article/10.3758/s13415-026-01399-0) · DOI: 10.3758/s13415-026-01399-0.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: Q1؛ SJR 2025؛ Behavioral Neuroscience؛ [منبع رسمی](https://www.scimagojr.com/journalrank.php?category=2802). تایید از نمایه‌ی رسمی جست‌وجو؛ صفحه‌ی مستقیم پاسخ ۴۰۳ داد..

### R30 — Bayesian Online Changepoint Detection

نویسندگان: Adams, Ryan Prescott; MacKay, David J. C..

وضعیت: arXiv 2007؛ پیش‌چاپ بنیانی. تاریخ منبع اولیه/ناشر: 2007/10/19. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/0710.3742) · [صفحه‌ی انتشار](https://arxiv.org/abs/0710.3742) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R31 — Text Tiling: Segmenting Text into Multi-paragraph Subtopic Passages

نویسندگان: Marti A. Hearst.

وضعیت: Computational Linguistics 23(1)؛ 1997؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 1997. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://aclanthology.org/J97-1003/) · [صفحه‌ی انتشار](https://aclanthology.org/J97-1003/) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: تایید کامل سال/دسته از JCR یا SJR در این مرور ممکن نشد؛ رتبه‌ای ادعا نمی‌شود.

### R32 — Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions

نویسندگان: Hu, Yuanzhe; Wang, Yu; McAuley, Julian.

وضعیت: ICLR 2026؛ داوری‌شده؛ نسخه‌ی اولیه ۲۰۲۵. تاریخ منبع اولیه/ناشر: 2025/07/07. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2507.05257) · [صفحه‌ی انتشار](https://proceedings.iclr.cc/paper_files/paper/2026/hash/fd1eff9dd295df50a41f2521942fa31d-Abstract-Conference.html) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R33 — Event perception: A mind-brain perspective

نویسندگان: Jeffrey M. Zacks; Nicole K. Speer; Khena M. Swallow; Todd S. Braver; Jeremy R. Reynolds.

وضعیت: Psychological Bulletin 133(2)؛ 2007؛ مقاله‌ی مروری داوری‌شده. تاریخ منبع اولیه/ناشر: 2007/03. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://profiles.wustl.edu/en/publications/event-perception-a-mind-brain-perspective/) · [صفحه‌ی انتشار](https://profiles.wustl.edu/en/publications/event-perception-a-mind-brain-perspective/) · DOI: 10.1037/0033-2909.133.2.273.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: تایید کامل سال/دسته از JCR یا SJR در این مرور ممکن نشد؛ رتبه‌ای ادعا نمی‌شود.

### R34 — Propose, Verify, Commit: Evidence-Grounded Memory for Long-Horizon Multi-Actor Conversations

نویسندگان: Lu, Zihao; Yuan, Zhihang; Ou, Litu; Shi, Lei.

وضعیت: arXiv؛ نسخه‌ی ۲ در ۱۳ اکتبر ۲۰۲۶؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2026/09/20. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://arxiv.org/abs/2609.23465) · [صفحه‌ی انتشار](https://arxiv.org/abs/2609.23465) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R35 — TEM: Temporal State Tracking Memory for Large Language Model Agents

نویسندگان: Song, Pengfeng; Zhuang, Yunkai; Shi, Liye.

وضعیت: arXiv؛ ۱۵ اکتبر ۲۰۲۶؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2026/10/15. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://arxiv.org/abs/2610.21900) · [صفحه‌ی انتشار](https://arxiv.org/abs/2610.21900) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R36 — MemTrace: Tracing and Attributing Errors in Large Language Model Memory Systems

نویسندگان: Deng, Xinle; Zhong, Ruobin; Peng, Hujin; Lu, Xiaoben; Wu, Yanzhe; Li, Guang; Xu, Buqiang; Yao, Yunzhi; Fang, Jizhan; Cao, Haoliang; Guo, Junjie; Yuan, Yuan; Ma, Ziqing; Yu, Yuanqiang; Hu, Rui; Dong, Baohua; Zhu, Hangcheng; Zhang, Ningyu.

وضعیت: arXiv؛ نسخه‌ی ۴ در ۸ اکتبر ۲۰۲۶؛ پیش‌چاپ. تاریخ منبع اولیه/ناشر: 2026/05/27. دامنه‌ی مطالعه: چکیده، روش یا بخش‌های مرتبط متن اصلی.

[صفحه‌ی منبع](https://arxiv.org/abs/2605.28732) · [صفحه‌ی انتشار](https://arxiv.org/abs/2605.28732) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: [https://github.com/zjunlp/MemTrace](https://github.com/zjunlp/MemTrace).

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.

### R37 — LightMem: Lightweight and Efficient Memory-Augmented Generation

نویسندگان: Fang, Jizhan; Deng, Xinle; Xu, Haoming; Jiang, Ziyan; Tang, Yuqi; Xu, Ziwen; Deng, Shumin; Yao, Yunzhi; Wang, Mengru; Qiao, Shuofei; Chen, Huajun; Zhang, Ningyu.

وضعیت: ICLR 2026؛ داوری‌شده. تاریخ منبع اولیه/ناشر: 2026-04-20. دامنه‌ی مطالعه: فراداده و چکیده؛ داوری کامل روش انجام نشده.

[صفحه‌ی منبع](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a05b72653ec5b473732129829ae04195-Abstract-Conference.html) · [صفحه‌ی انتشار](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a05b72653ec5b473732129829ae04195-Abstract-Conference.html) · DOI: در صفحه‌ی بررسی‌شده ثبت/تایید نشد.

کد/داده: پیوند اختصاصی کد در دامنه‌ی این مرور تایید نشد؛ به معنی نبود کد نیست.

رتبه‌ی ژورنال: کاربرد ندارد؛ کنفرانس یا پیش‌چاپ.
