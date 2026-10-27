"""Write the curated primary-source review and its bibliography.

Metadata and reading scopes were checked against primary pages on 2026-10-27.
This is an inspectable focused review, not a systematic-review search engine.
No paper implementation is executed by this script.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sources():
    rows = [
        ('P01', 'Minds, brains, and programs', ['John R. Searle'], 1980,
         'Behavioral and Brain Sciences 3(3), 417–424', 'journal',
         'https://doi.org/10.1017/S0140525X00005756', '10.1017/S0140525X00005756', None,
         'چکیده و اطلاعات انتشار در Cambridge؛ سال اصلی ۱۹۸۰ از تاریخ انتشار آنلاین ۲۰۱۰ جدا شد.',
         'بحث اجرای برنامه و قصدیت، زمینه‌ی فلسفی پرسش است.',
         'هیچ آزمون فهم فلسفی از پوشش واژه نتیجه نمی‌شود.'),
        ('P02', 'Event perception: a mind-brain perspective',
         ['Jeffrey M. Zacks', 'Nicole K. Speer', 'Khena M. Swallow', 'Todd S. Braver', 'Jeremy R. Reynolds'], 2007,
         'Psychological Bulletin 133(2), 273–293', 'journal',
         'https://pubmed.ncbi.nlm.nih.gov/17338600/', '10.1037/0033-2909.133.2.273', None,
         'چکیده و شرح شکل‌ها در PubMed؛ متن PMC با دیوار بررسی مرورگر روبه‌رو شد.',
         'پیش‌بینی و به‌روزرسانی مدل رویداد، مبنای شناختی مرزبندی‌اند.',
         'این نظریه معادل آستانه‌ی نویی واژگانی پروژه نیست.'),
        ('P03', 'Multiple event segmentation mechanisms in the human brain',
         ['Tan T. Nguyen', 'Joset A. Etzel', 'Matthew A. Bezdek', 'Jeffrey M. Zacks'], 2026,
         'eLife 107955.3, Version of Record, 7 July 2026', 'journal',
         'https://elifesciences.org/articles/107955', '10.7554/eLife.107955.3', 'Version of Record',
         'چکیده، بخش مقدمه، بحث و محدودیت و آغاز روش با مدل‌سازی و fMRI.',
         'خطا و عدم قطعیت پیش‌بینی با الگوهای هم‌پوشان و متمایز مرتبط‌اند.',
         'نویسنده‌ی متنی این دو سازه یا شبکه‌ی عصبی را اندازه نمی‌گیرد.'),
        ('P04', 'The Probabilistic Relevance Framework: BM25 and Beyond',
         ['Stephen Robertson', 'Hugo Zaragoza'], 2009,
         'Foundations and Trends in Information Retrieval 4(1–2), 1–174', 'journal',
         'https://doi.org/10.1561/1500000019', '10.1561/1500000019', None,
         'فراداده و چکیده‌ی ناشر؛ دسترسی متن کامل در این صفحه محدود بود.',
         'مبنای رتبه‌بندی واژگانی و نقش آمار سند و طول را مشخص می‌کند.',
         'مقادیر دقیق پیاده‌سازی از کد پروژه خوانده می‌شوند.'),
        ('P05', 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks',
         ['Patrick Lewis', 'Ethan Perez', 'Aleksandra Piktus', 'Fabio Petroni', 'Vladimir Karpukhin', 'Naman Goyal',
          'Heinrich Küttler', 'Mike Lewis', 'Wen-tau Yih', 'Tim Rocktäschel', 'Sebastian Riedel', 'Douwe Kiela'], 2020,
         'NeurIPS 2020 acceptance stated on author arXiv record', 'conference_author_record',
         'https://arxiv.org/abs/2005.11401v4', None, 'v4',
         'چکیده و سابقه‌ی نسخه و عبارت پذیرش NeurIPS در رکورد نویسندگان؛ صفحه‌ی مجموعه‌مقالات در این محیط باز نشد.',
         'بازیابی حافظه‌ی غیرپارامتری و تولید زبانی در یک چارچوب پیوند می‌یابند.',
         'پروژه‌ی حاضر بخش تولید و آموزش آن را اجرا نمی‌کند.'),
        ('P06', 'Evaluating Very Long-Term Conversational Memory of LLM Agents',
         ['Adyasha Maharana', 'Dong-Ho Lee', 'Sergey Tulyakov', 'Mohit Bansal', 'Francesco Barbieri', 'Yuwei Fang'], 2024,
         'ACL 2024, 13851–13870', 'conference',
         'https://aclanthology.org/2024.acl-long.747/', '10.18653/v1/2024.acl-long.747', None,
         'چکیده، اطلاعات منبع و کتاب‌شناسی رسمی ACL؛ قرارداد داده‌ی اجرای ما از ممیزی مخزن خوانده شد.',
         'LoCoMo منبع ارزیابی تاریخچه‌های طولانی و چندجلسه‌ای است.',
         'امتیاز پوشش این پروژه، امتیاز پاسخ رسمی مقاله نیست.'),
        ('P07', 'QMSum: A New Benchmark for Query-based Multi-domain Meeting Summarization',
         ['Ming Zhong', 'Da Yin', 'Tao Yu', 'Ahmad Zaidi', 'Mutethia Mutuma', 'Rahul Jha',
          'Ahmed Hassan Awadallah', 'Asli Celikyilmaz', 'Yang Liu', 'Xipeng Qiu', 'Dragomir Radev'], 2021,
         'NAACL 2021, 5905–5921', 'conference',
         'https://aclanthology.org/2021.naacl-main.472/', '10.18653/v1/2021.naacl-main.472', None,
         'چکیده و اطلاعات رسمی ACL؛ تفاوت بازه‌ی موضوع و بازه‌ی مرتبط با پرسش با قرارداد پروژه تطبیق شد.',
         'مرجع برای انتخاب و خلاصه‌سازی بازه‌های مرتبط با پرسش ساخته شده است.',
         'بازه‌ی مرتبط با شاهد کمینه‌ی پاسخ یا مرز ادراک انسانی یکسان نیست.'),
        ('P08', 'LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory',
         ['Di Wu', 'Hongwei Wang', 'Wenhao Yu', 'Yuwei Zhang', 'Kai-Wei Chang', 'Dong Yu'], 2025,
         'ICLR 2025 official proceedings', 'conference',
         'https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html',
         None, None, 'چکیده و صفحه‌ی رسمی ICLR؛ تفکیک indexing و retrieval و reading.',
         'توانایی‌های حافظه و مراحل خط لوله را تفکیک می‌کند.',
         'تفکیک مراحل، پیشینه‌ی مستقیم دارد و نوآوری عمومی ما نیست.'),
        ('P09', 'SeCom: On Memory Construction and Retrieval for Personalized Conversational Agents',
         ['Zhuoshi Pan', 'Qianhui Wu', 'Huiqiang Jiang', 'Xufang Luo', 'Hao Cheng', 'Dongsheng Li',
          'Yuqing Yang', 'Chin-Yew Lin', 'H. Vicky Zhao', 'Lili Qiu', 'Jianfeng Gao'], 2025,
         'ICLR 2025 official proceedings', 'conference',
         'https://proceedings.iclr.cc/paper_files/paper/2025/hash/e56f394bbd4f0ec81393d767caa5a31b-Abstract-Conference.html',
         None, None, 'صفحه‌ی رسمی و بخش‌های معرفی ریزدانگی و فشرده‌سازی در متن نویسندگان arXiv:2502.05589v1.',
         'واحد منسجم گفت‌وگو و فشرده‌سازی برای بازیابی بررسی می‌شوند.',
         'قرارداد آن با فرصت و هزینه‌ی دقیقا مشترک این پروژه یکسان نیست.'),
        ('P10', 'ES-Mem: Event Segmentation-Based Memory for Long-Term Dialogue Agents',
         ['Huhai Zou', 'Tianhao Sun', 'Chuanjiang He', 'Yu Tian', 'Zhenyang Li', 'Li Jin', 'Nayu Liu', 'Jiang Zhong', 'Kaiwen Wei'], 2026,
         'arXiv preprint; reviewed venue not verified here', 'preprint',
         'https://arxiv.org/abs/2601.07582v2', None, 'v2, 13 January 2026',
         'چکیده و شناسنامه‌ی نسخه‌ی دوم؛ معماری مقاله بازاجرا نشد.',
         'بخش‌بندی رویداد و حافظه‌ی سلسله‌مراتبی برای عامل گفت‌وگو پیشنهاد می‌شود.',
         'اصل ایده‌ی حافظه‌ی رویدادی پیش از پژوهش حاضر وجود دارد.'),
        ('P11', 'Lost in the Middle: How Language Models Use Long Contexts',
         ['Nelson F. Liu', 'Kevin Lin', 'John Hewitt', 'Ashwin Paranjape', 'Michele Bevilacqua', 'Fabio Petroni', 'Percy Liang'], 2024,
         'Transactions of the Association for Computational Linguistics 12, 157–173', 'journal',
         'https://aclanthology.org/2024.tacl-1.9/', '10.1162/tacl_a_00638', None,
         'چکیده و شناسنامه‌ی رسمی TACL و ACL.',
         'استفاده از اطلاعات زمینه می‌تواند به جایگاه آن حساس باشد.',
         'پوشش متن با استفاده‌ی درست خواننده یکسان نیست.'),
        ('P12', 'Relevance Is Not Sufficiency: What Actually Closes the Evidence Gap in Long-Term Memory QA',
         ['Yufeng Li', 'Shuxin Li', 'Zhenhua Xu', 'Junxian Li', 'Peng Zeng', 'Sheng Yao', 'Changting Lin', 'Gaolei Li', 'Ran Bi', 'Meng Han'], 2026,
         'arXiv preprint, 7 October 2026', 'preprint',
         'https://arxiv.org/html/2610.09348v1', None, 'v1',
         'چکیده و بخش‌های ۳ و ۴ درباره‌ی کفایت، شاخص‌های جانشین، ترکیب و تکمیل و بودجه‌ی فراخوانی.',
         'ارتباط تک‌رکوردی از کفایت مجموعه و تکمیل شاهد جدا می‌شود.',
         'کفایت داوری‌شده و بودجه‌ی فراخوانی با کامل‌پوشانی واژه‌ای ما متفاوت‌اند.'),
        ('P13', 'Is Complex Agentic Memory Always Needed? Naive RAG Is Stronger Than We Thought',
         ['Zhengye Bao', 'Shengtao Zhang', 'Haokai Zhang', 'Shiqi Lou', 'Muning Wen', 'Minnan Luo'], 2026,
         'arXiv preprint, 22 October 2026', 'preprint',
         'https://arxiv.org/html/2610.30755v1', None, 'v1',
         'چکیده، بخش‌های خط پایه و پوشش و استفاده و محدودیت و قسمت‌های مقایسه‌ی complete-store و source-oracle؛ کل متن بلند خط‌به‌خط خوانده نشد.',
         'بازیابی متراکم و بازرتبه‌بندی متن خام مبنای رقابتی و تشخیصی می‌سازد.',
         'روش اجرا نشده و اعداد پاسخ آن با پوشش این پروژه رتبه‌بندی نمی‌شوند.'),
        ('P14', 'MemDerive: A Diagnostic Benchmark for Agent Memory over Evolving Data',
         ['Sen Gao', 'Yongan Li', 'Han Chen', 'Bingsheng He', 'Ming Wu', 'Jason Zeng', 'Michael Heinrich', 'Shixuan Sun'], 2026,
         'arXiv preprint, 18 October 2026', 'preprint',
         'https://arxiv.org/abs/2610.25373v1', None, 'v1',
         'چکیده و شناسنامه‌ی منبع اصلی؛ داده و روش مقاله در این پروژه اجرا نشده‌اند.',
         'حالت مشتق‌شده و گراف استنتاج مرجع برای تشخیص شکست تعریف می‌شوند.',
         'ممیز ما مسیر استنتاج یا تحول حالت را ارزیابی نمی‌کند.'),
        ('P15', 'MemTrace: Probing What Final Accuracy Misses in Long-Term Memory',
         ['Xianxuan Long', 'Zhikai Chen', 'Shenglai Zeng', 'Shouren Wang', 'Kai Guo', 'Jiliang Tang'], 2026,
         'arXiv preprint, 15 June 2026', 'preprint',
         'https://arxiv.org/abs/2606.17328v1', None, 'v1',
         'چکیده و واحد دانش‌نقطه و شرایط شاهد در منبع اصلی؛ تحلیل عمیق‌تر قبلی در اطلس مرحله‌ی ۱۸ موجود است.',
         'واحد ارزیابی و تغییر شرایط می‌توانند خطاهای پنهان در تجمیع را آشکار کنند.',
         'گلوگاه غالب به واحد شاهد و بازیاب و خواننده و طراحی وابسته است.'),
        ('P16', 'Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues',
         ['Chuanrui Hu', 'Tong Li', 'Xingze Gao', 'Hongda Chen', 'Yi Bai', 'Dannong Xu', 'Tianwei Lin', 'Xiaohong Li', 'Yunyun Han', 'Jian Pei', 'Yafeng Deng'], 2026,
         'Author arXiv v3; dataset-card KDD statement not independently verified in this review', 'author_version',
         'https://arxiv.org/abs/2602.01313v3', None, 'v3, 11 March 2026',
         'چکیده و نسخه‌ی سوم؛ قرارداد داده‌ی اجرا از manifest و ممیزی مرحله‌ی ۱۹ خوانده شد.',
         'حافظه در زمینه‌ی چندنفره و چندگروهی و تحول زمانی بررسی می‌شود.',
         'اجرای ما فقط زیرمجموعه‌ی ریزدانه و سنجه‌ی پوشش پیام را استفاده می‌کند.'),
    ]
    names = ['id', 'title', 'authors', 'year', 'venue', 'status', 'url', 'doi', 'version',
             'reading_scope_fa', 'finding_fa', 'limit_fa']
    return [dict(zip(names, row), accessed_on='2026-10-27', primary=True,
                 implementation_rerun=False) for row in rows]


def build():
    refs = sources()
    queries = [
        ('system1', 'conversational agent memory event segmentation SeCom ES-Mem evidence retrieval diagnostic benchmark October 2026', 35),
        ('system1', '"Relevance Is Not Sufficiency" "memory"', None),
        ('system1', '"Is Complex Agentic Memory Always Needed"', None),
        ('system2', '"Event perception: A mind-brain perspective" Zacks 2007 pdf', None),
        ('system2', '"Relevance Is Not Sufficiency" evidence memory 2610.09348', None),
        ('system2', '"Minds, brains, and programs" Searle Cambridge 1980', None),
        ('system2', '"LongMemEval" ICLR 2025 official', None),
        ('system1', 'site.cs.cmu.edu Carbonell Goldstein 1998 MMR diversity reranking', None),
        ('system1', 'site.proceedings.neurips.cc "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"', None),
        ('system1', 'site.arxiv.org memory evidence diagnostic event segmentation "Oct 2026"', 7),
    ]
    return {'review_date': '2026-10-27', 'scope': 'focused primary-source synthesis',
            'systematic_review_claim': False, 'quartile_certification': False,
            'selection': 'Direct relevance to constructs, memory units, evidence metrics and diagnosis; prior project atlases plus current search and primary-page verification.',
            'queries': [{'engine': a, 'query': b, 'recency_days': c} for a,b,c in queries],
            'access_limits': ['PMC browser check; used PubMed record for P02',
                              'Publisher full text unavailable for P04; only abstract and metadata used',
                              'NeurIPS page unavailable for P05; acceptance statement checked in author record',
                              'ACM MMR page returned 403 and is not a core entry in this review',
                              'Search returned secondary blogs; they were not used as technical evidence'],
            'sources': refs}


def main():
    folder = ROOT / 'thesis'
    data = build()
    (folder / 'literature_review_20261027.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    bib, lines = [], ['# منابع بیرونی', '', 'شناسه‌های P به منابع اصلی زیر ارجاع دارند. وضعیت انتشار و دامنه‌ی خواندن در دفتر پیشینه ثبت شده است.', '']
    for s in data['sources']:
        kind = 'article' if s['status'] in ['journal', 'preprint', 'author_version'] else 'inproceedings'
        fields = {'title': '{'+s['title']+'}', 'author': ' and '.join(s['authors']),
                  'year': str(s['year']), 'url': s['url'], 'note': s['venue']}
        if s['doi']:
            fields['doi'] = s['doi']
        bib.append('@'+kind+'{'+s['id']+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}')
        lines += ['## '+s['id'], '', '; '.join(s['authors'])+'. '+str(s['year'])+'. '+s['title']+'. '+s['venue']+'.', '', s['url'], '']
    (folder / 'references.bib').write_text('\n\n'.join(bib)+'\n')
    (folder / 'references_fa.md').write_text('\n'.join(lines))
    print('Wrote 16 primary-source records and bibliography')


if __name__ == '__main__':
    main()
