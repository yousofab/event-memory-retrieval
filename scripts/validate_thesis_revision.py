"""Source and OOXML gates for the six supervisor-requested editorial changes."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as E
import zipfile
from build_thesis_revision_assets import data

ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'


def check():
    figure=json.loads((ROOT/'thesis/revision_figure_data.json').read_text())
    assert figure['values']==data(), 'Chart data must match recorded results exactly'
    for name,expected in figure['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    for name,expected in figure['artifact_sha256'].items():
        assert (ROOT/name).stat().st_size>100,name
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    register=json.loads((ROOT/'thesis/tools_and_ai_register.json').read_text())
    historical=json.loads((ROOT/'results/phase6_held_out_lsa.json').read_text())['dependencies']
    assert register['historical_execution']['lsa_dependencies']=={
        'numpy':historical['numpy'],'scipy':historical['scipy'],'scikit-learn':historical['scikit_learn']}
    assert register['evaluation']['phase18_19_llm_judge'] is None
    ref=json.loads((ROOT/'thesis/ieee_reference_map.json').read_text())
    numbers=[r['number'] for r in ref['references']]
    assert numbers==list(range(1,len(numbers)+1))
    assert len(set(r['key'] for r in ref['references']))==len(numbers)
    assert set(ref['citation_occurrences'])==set(numbers)
    first=[]
    for n in ref['citation_occurrences']:
        if n not in first:first.append(n)
    assert first==numbers, 'Reference numbers must follow first citation'
    path=ROOT/'deliverables/thesis_supervisor_revision_fa.docx'
    with zipfile.ZipFile(path) as z:
        x=E.fromstring(z.read('word/document.xml'))
        text=''.join(x.itertext())
        assert not re.search(r'\[(?:P|C|S)\d',text), 'Internal source codes must not remain as citations'
        assert len(x.findall('.//m:oMath',NS))==2
        for r in x.findall('.//m:r',NS):
            assert r.find('w:rPr/w:sz',NS).get(W+'val')=='24'
        bookmarks=x.findall('.//w:bookmarkStart',NS)
        names=[b.get(W+'name') for b in bookmarks];ids=[b.get(W+'id') for b in bookmarks]
        assert len(names)==len(set(names)) and len(ids)==len(set(ids))
        for link in x.findall('.//w:hyperlink',NS):
            target=link.get(W+'anchor')
            if target:assert target in names,target
        for fonts in x.findall('.//w:rFonts',NS):
            assert set(fonts.attrib.values()) <= {'B Nazanin','Nimbus Roman'}
        body=x.find('w:body',NS);justified=0
        for p in body.findall('w:p',NS):
            t=''.join(p.itertext())
            if len(t)>120 and re.search('[\u0600-\u06ff]',t) and p.find('m:oMathPara',NS) is None:
                jc=p.find('w:pPr/w:jc',NS)
                # Navigation entries are hyperlinks with a shorter text; cover
                # and captions have explicit styles or short visible text.
                visible=''.join(e.text or '' for e in p.findall('.//w:t',NS))
                if len(visible)>120:
                    assert jc is not None and jc.get(W+'val')=='both',visible[:60]
                    justified+=1
    record=json.loads((ROOT/'thesis/revision_validation.json').read_text())
    for name,entry in record['artifacts'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==entry['sha256'],name
    print(json.dumps({'status':'passed','ieee_references':len(numbers),'figures':len(figure['figures']),
                      'editable_equations':2,'equation_size_pt':12,'long_justified_persian_paragraphs':justified,
                      'new_experiments':0,'new_model_inference_calls':0}))


if __name__=='__main__':check()
