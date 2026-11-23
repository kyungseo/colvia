"""Refine the preserved README drawings; keep their nodes, labels and routes.

Build-only, standard library. Font subsets in gallery/fonts are committed build
inputs. See gallery/README.md to extend their glyph coverage when editing labels.
"""
from pathlib import Path
import argparse,base64,hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
def tag(n):return '{'+NS+'}'+n
def el(n,**attrs):return ET.Element(tag(n),{k.replace('_','-'):str(v) for k,v in attrs.items()})
TRANSLATE={'나':'You','범위':'Scope','다시 고치기':'Revise','수락':'Accept','월요일':'Monday','수요일':'Wednesday','기록':'Records','범위 · 수락한 제출본 · 다음 할 일':'Scope · accepted submission · next steps','수락한 제출본':'Accepted submission','현재 파일':'Current file','변경 내용':'Changes','일정 항목 수정':'Schedule item edited','알림':'Notice / inbox','알림 · 수신함':'Notice / inbox','상위 Work':'Parent','전체 결과':'Combined result','격리 폴더 1':'Isolated folder 1','격리 폴더 2':'Isolated folder 2','대상 폴더':'Destination','한 건씩 합치기':'One at a time','처음 한 번':'ONE-TIME SETUP','Colvia 설치':'Install Colvia','프로젝트 폴더':'Project folder','“Colvia 연결해 줘”':'“Connect Colvia”','미리보기':'Preview','그 뒤 매일':'EVERYDAY WORK','목표·계획':'Goals & plan','프로젝트 문서':'Project documents','후보 목록':'Candidates','큰 일은 하위 Work로':'Split into child Work','결과':'Result','다음 할 일':'Next steps','다음 Work로 계속':'Continue with the next Work','대조 요청':'Compare'}
TITLES={'scope':('범위를 정하고 결과를 검토합니다','Agree on scope, then review the result'),'switch':('같은 프로젝트 기록에서 이어갑니다','Pick up from the same project records'),'drift':('수락한 제출본과 현재 파일 비교하기','Compare the accepted submission with current files'),'notify':('준비한 결과를 알리고 사람이 검토합니다','Notify the owner and review the prepared result'),'split':('하위 결과와 전체 결과를 따로 검토합니다','Review child results and the combined result separately'),'parallel':('격리 폴더의 결과를 한 건씩 반영합니다','Apply results from isolated folders one at a time'),'overview':('설치와 연결, 새 일과 하던 일', 'Connect a folder, start a task or pick up existing work')}
DESC={'scope':('사람이 범위를 승인하고 에이전트가 Work를 준비합니다. 결과를 검토해 수정하거나 수락합니다.','You approve the scope; the agent prepares the Work. Review the result, request revisions or accept it.'),'switch':('월요일의 범위·수락한 제출본·다음 할 일을 프로젝트에 기록합니다. 수요일의 에이전트가 같은 기록에서 이어갑니다.','Keep Monday’s scope, accepted submission and next steps in the project. Wednesday’s agent resumes from those records.'),'drift':('수락한 제출본과 현재 파일을 비교해 바뀐 내용을 확인합니다.','Compare the accepted submission with current files to see what changed.'),'notify':('확인한 단계와 기한 안에 준비된 결과를 제출합니다. 알림이나 수신함에서 결과를 찾고 사람이 수락합니다.','Submit the prepared result within the confirmed step and deadline. Find it through a notification or the inbox; acceptance stays with you.'),'split':('하위 Work의 결과를 각각 수락한 뒤 전체 결과는 사람이 따로 검토하고 수락합니다.','Accept each child Work result, then review and accept the combined result separately.'),'parallel':('에이전트가 격리 폴더에서 준비한 결과를 검토하고, 승인한 제출본은 Colvia로 대상 폴더에 한 건씩 반영합니다.','Review the agent’s submissions from isolated folders. Use Colvia to apply approved submissions to the destination one at a time.'),'overview':('사용할 계정에 설치한 뒤 폴더마다 연결 내용을 확인하고 승인합니다. 새 일은 작업안을 보고 범위를 승인합니다. 제출본을 검토해 수락하거나 수정을 요청합니다. 하던 일은 프로젝트 현황에서 이어갑니다.', 'Install in your account, then preview and approve each folder connection. For a new task, approve the scope, review the submission and accept it or request changes. Use project status to pick up existing work.')}

TRANSLATE.update({'추가·수정': 'Added or edited', 'AI API 키': 'AI API key', '인증 토큰': 'Auth token', '로컬 검사': 'Local check', '커밋 준비 중단': 'Commit blocked', '예: .npmrc 2행': 'e.g. .npmrc, line 2'})
TRANSLATE.update({'제출본 1':'Submission 1','제출본 N':'Submission N','원래 폴더':'Original','통합 검사 · 함께 수락 · 한 번에 반영':'Integration checks · Accept and apply all','macOS · 2~8개 결과 함께':'macOS · 2–8 results together'})
TRANSLATE.update({'macOS · Claude Code CLI · 2~8':'macOS · Claude Code CLI · 2–8','조정':'Coordinator','자동 실행·회수 → 검사 → 내가 함께 수락':'Agents run and collect; you review and accept'})
TITLES['parallel'] = ('2~8개 제출본을 보고 함께 수락·반영', 'Review, accept and apply 2–8 submissions together')
DESC['parallel'] = ('macOS에서 정확한 모든 제출본과 통합 검사 결과를 보고 한 번의 결정으로 수락해 원래 폴더에 반영합니다.', 'On macOS, review every exact submission and integration checks, then accept and apply all to the original folder in one decision.')

TITLES['credential'] = ('Git 반영 전 자격증명 검사', 'Credential check before a Git commit')
DESC['credential'] = ('.env 추가·수정, 소스에 적은 AI API 키, .npmrc 인증 토큰을 Colvia가 로컬에서 검사하고 차단 위치를 알려 줍니다.', 'Colvia checks proposed changes locally, including edits to .env, an AI API key in source code, and a token in .npmrc. A blocked candidate reports a location without revealing the value.')

TITLES['status'] = ('오늘 내가 볼 건 뭐지?', 'What needs my attention today?')
DESC['status'] = ('프로젝트 기록에서 검토할 일, 에이전트가 고칠 일, 수락을 기다리는 일을 확인합니다.', 'Project records show what needs review, which changes the agent was asked to make, and which result another task needs.')
TITLES['workflow'] = ('한 작업을 맡기고 검토하는 흐름', 'From a plan to a reviewed result')
DESC['workflow'] = ('사용자가 범위를 승인하고 제출본을 검토합니다. 범위 밖 변경이 있으면 Colvia가 제출을 멈춥니다. 승인 범위와 제출한 판, 수락과 수정 요청이 기록에 남습니다.', 'You approve the scope and review the submission. Colvia stops submission if tracked changes exceed the scope. It keeps the approved scope, submitted version and decision.')
TITLES['system'] = ('작업 파일과 Colvia 기록의 저장 위치', 'Where project files and Colvia records live')
DESC['system'] = ('프로젝트 폴더에는 현재 파일과 선택한 Git 저장소가 있습니다. Colvia는 별도 사용자 데이터 폴더의 프로젝트별 SQLite 데이터베이스에 승인과 제출본, 결정을 보관합니다. git push로는 커밋한 이력을 원격에 보냅니다.', 'Your project folder holds current files and, optionally, a Git repository. Colvia stores each project’s approvals, submissions and decisions in a SQLite database in your local user data folder. A Git push sends committed history to the remote.')
PROJECT_LABELS = {
    '작업 기록': 'Work records',
    '내 검토': 'Your review',
    '제안서 2판': 'Proposal · rev 2',
    '에이전트가 고칠 일': 'For the agent to revise',
    '견적표': 'Price quote',
    '수락 대기': 'Awaiting acceptance',
    '메일 초안': 'Cover email',
    '사용자': 'You',
    '범위 승인': 'Approve scope',
    '제안받은 계획': 'Proposed plan',
    '작업과 검사': 'Work and test',
    '검토용 제출': 'Submit for review',
    '승인 범위 대조': 'Check scope',
    '범위 밖이면 제출 멈춤': 'Stop if out of scope',
    '결과 검토': 'Review result',
    '수락 또는 수정 요청': 'Accept or ask for changes',
    '에이전트': 'Agent',
    'Colvia': 'Colvia',
    '에이전트에게 수정 요청': 'Ask the agent to revise',
    'Colvia 기록: 승인한 범위 · 제출한 판 · 수락·수정 요청': 'Colvia records: approved scope · submitted version · acceptance or change request',
    '프로젝트 폴더': 'Project folder',
    '현재 파일': 'Current files',
    '문서 · 코드 · 프로젝트 규칙': 'Documents, code and project rules',
    'Git 저장소 (선택)': 'Git repository (optional)',
    '내 기기의 사용자 데이터 폴더': 'User data folder on your device',
    'Colvia 기록': 'Colvia records',
    '승인한 범위 · 제출본': 'Approved scope and submissions',
    '수락 · 수정 요청': 'Acceptance and change requests',
    'git push': 'git push',
    '원격 Git 저장소 · 커밋한 이력': 'Git remote · committed history',
    'git push로 올라가지 않습니다': 'Not sent by git push',
    '프로젝트별 DB (SQLite)': 'Project database (SQLite)',
}

OVERVIEW_LABELS = {
    '처음 연결할 때': 'First connection',
    '계정에 설치': 'Install once',
    '미리보기 확인': 'Check preview',
    '연결 승인': 'Approve connection',
    '연결한 뒤에는': 'Once connected',
    '새 일 맡기기': 'Start a new task',
    '하려는 일 말하기': 'Describe the goal',
    '제안받은 계획': PROJECT_LABELS['제안받은 계획'],
    '범위 승인': 'Approve scope',
    '작업 · 검사': 'Work and test',
    '검토용 제출': 'Submit for review',
    '결과 검토': PROJECT_LABELS['결과 검토'],
    '수락 또는 수정 요청': PROJECT_LABELS['수락 또는 수정 요청'],
    '수락': 'Accept',
    '다음 일은 선택': 'Next step is optional',
    '수정 요청': 'Request changes',
    '하던 일 이어가기': 'Resume a task',
    '“오늘 내가 볼 건 뭐지?”': '“What needs my attention today?”',
    '검토할 일 · 고칠 일 확인': 'Find work to review or revise',
    '같은 Work에서 계속': 'Continue the same Work',
}

def style_rules(css,theme):
    light,dark=css.split('@media',1)
    chosen=light+(dark[dark.index('{')+1:dark.rfind('}')] if theme=='dark' else '')
    rules={}
    for selector,body in re.findall(r'\.([a-z]+)\s*\{([^}]+)\}',chosen):
        rules.setdefault(selector,{}).update(dict(x.strip().split(':',1) for x in body.split(';') if ':' in x))
    return rules

def build(scene,lang,theme,fonts):
    source=ROOT/f'manual/assets/readme-{scene}.ko.svg';root=ET.fromstring(source.read_text(encoding='utf-8'));root.set('{http://www.w3.org/XML/1998/namespace}lang',lang)
    root.set('font-family','SkinSans-Subset, sans-serif');root.set('style','font-synthesis:none')
    root.find(tag('title')).text=TITLES[scene][lang=='en'];root.find(tag('desc')).text=DESC[scene][lang=='en']
    css=root.find(tag('style'));rules=style_rules(css.text,theme);root.remove(css)
    # Preserve original color roles while replacing implicit CSS with direct paint.
    for node in root.iter():
        for c in node.get('class','').split():
            if c not in rules:raise ValueError(f'Undefined original style class: {c}')
            for k,v in rules[c].items():node.set(k,v)
        if node.get('class') in ('ln','lnd'):node.set('stroke-linecap','round');node.set('stroke-linejoin','round')
        if node.tag==tag('rect') and node.get('rx')=='9':node.set('rx','7')
    st=el('style');st.text='\n'.join("@font-face{font-family:'SkinSans-Subset';font-style:normal;font-weight:"+str(w)+";src:url(data:font/woff2;base64,"+base64.b64encode(fonts[w]).decode()+") format('woff2');}" for w in fonts);root.insert(2,st)
    # A 4.8-unit visible open arrowhead for a 1.6-unit shaft. No strokeWidth multiplier.
    marker = root.find('.//' + tag('marker'))
    if marker is not None:
        marker.attrib.update({'viewBox':'0 0 12 12','refX':'9','refY':'6','markerWidth':'7.2','markerHeight':'7.2','markerUnits':'userSpaceOnUse','orient':'auto'})
        for child in list(marker):marker.remove(child)
        marker.append(el('path',d='M2 2 L10 6 L2 10',fill='none',stroke=rules['ln']['stroke'],stroke_width='2',stroke_linecap='round',stroke_linejoin='round'))
        dashed=ET.fromstring(ET.tostring(marker))
        dashed.set('id','ah-dashed');dashed[0].set('stroke',rules['lnd']['stroke']);root.find(tag('defs')).append(dashed)
        for n in root.iter():
            if n.get('class')=='lnd' and n.get('marker-end'):n.set('marker-end','url(#ah-dashed)')
    # Original Colvia rectangles remain. Replace the baseline-positioned pair with
    # the approved outlines, centered by actual ink bounds in the same rectangle.
    g=json.loads((ROOT/'assets/brand/source/geometry.json').read_text(encoding='utf-8'));alignments=[]
    for box in [e for e in root if e.tag==tag('rect') and e.get('class')=='col']:
        x,y,w,h=(float(box.get(k)) for k in ('x','y','width','height'));cx=x+w/2;cy=y+h/2
        kids=list(root);idx=kids.index(box)
        old_symbol=kids[idx+1];old_text=kids[idx+2]
        assert old_symbol.tag==tag('g') and old_text.text=='Colvia'
        root.remove(old_symbol);root.remove(old_text)
        sb,tb=g['symbol']['bounds'],g['colvia']['bounds']
        th,sh,gap=(8.5,10.4,4.5) if scene=='parallel' else (10.5,12.8,5.5)
        ss=sh/sb[3];ts=th/tb[3];total=sb[2]*ss+gap+tb[2]*ts;left=cx-total/2
        a=el('path',d=g['symbol']['path'],fill=rules['colt']['fill'],transform=f'translate({left-sb[0]*ss} {cy-(sb[1]+sb[3]/2)*ss}) scale({ss})')
        b=el('path',d=g['colvia']['path'],fill=rules['colt']['fill'],transform=f'translate({left+sb[2]*ss+gap-tb[0]*ts} {cy-(tb[1]+tb[3]/2)*ts}) scale({ts})')
        root.insert(idx+1,a);root.insert(idx+2,b);alignments.append({'box':[x,y,w,h],'group_width':total,'center':[cx,cy]})
    # Center single/two-line labels inside existing boxes, preserving all positions.
    boxes=[n for n in root if n.tag==tag('rect') and n.get('class') in ('agent','note','work')]
    for box in boxes if scene not in ('workflow','system','overview') else []:
        x,y,w,h=(float(box.get(k)) for k in ('x','y','width','height'))
        texts=[n for n in root if n.tag==tag('text') and x<=float(n.get('x',0))<=x+w and y<float(n.get('y',0))<y+h]
        for i,t in enumerate(texts):t.set('y',str(y+h/2+(i-(len(texts)-1)/2)*17));t.set('dominant-baseline','central')
    for n in root.iter(tag('text')):
        n.set('font-weight','700' if int(n.get('font-weight','400'))>=600 else '400')
        if scene=='parallel' and n.text=='조정':n.set('font-size','8.5' if lang=='en' else '13')
        if scene=='notify' and n.text=='알림':n.text='알림 · 수신함'
        if lang=='en' and scene=='overview' and n.text in OVERVIEW_LABELS:n.text=OVERVIEW_LABELS[n.text]
        elif lang=='en' and scene in ('workflow','status','system'):n.text=PROJECT_LABELS[n.text]
        elif lang=='en' and n.text in TRANSLATE:n.text=TRANSLATE[n.text]
        if scene=='split' and n.text=='Combined result':
            n.set('y','125');n.set('font-size','10.5');n.text=None
            a=ET.SubElement(n,tag('tspan'),{'x':'332','dy':'0'});a.text='Combined'
            b=ET.SubElement(n,tag('tspan'),{'x':'332','dy':'12'});b.text='result'
        if scene=='drift' and n.text=='Accepted submission':
            n.set('y','84');n.text=None
            a=ET.SubElement(n,tag('tspan'),{'x':'46','dy':'0'});a.text='Accepted'
            b=ET.SubElement(n,tag('tspan'),{'x':'46','dy':'12'});b.text='submission'
        # Sequence labels in circles share their circle center, not a baseline offset.
        if scene=='parallel' and n.text in ('1','2'):
            n.set('y','72' if n.text=='1' else '138');n.set('dominant-baseline','central')
    # Keep the revise icon above the return route; use a left-pointing undo arrow.
    if scene=='scope':
        for n in list(root):
            if n.tag==tag('path') and n.get('d','').startswith(('M226 152','M221 154')):root.remove(n)
        root.append(el('path',d='M227 135 L221 141 L227 147 M221 141 H236 A6 6 0 0 1 236 153 H232',fill='none',stroke=rules['mut']['fill'],stroke_width=1.8,stroke_linecap='round',stroke_linejoin='round'))
    # Paint is now explicit; remove the original CSS class references.
    for n in root.iter():
        n.attrib.pop('class',None)
    return ET.tostring(root,encoding='unicode')+'\n',alignments

def all_text():
    chars=set(''.join(TRANSLATE.values())+''.join(TRANSLATE.keys()))
    chars.update(''.join(PROJECT_LABELS.values()))
    chars.update(''.join(OVERVIEW_LABELS.values()))
    for p in (ROOT/'manual/assets').glob('readme-*.ko.svg'):
        for t in ET.parse(p).iter(tag('text')):chars.update(t.text or '')
    return ''.join(sorted(chars))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'manual/assets/gallery');ap.add_argument('--text-file',type=Path);args=ap.parse_args()
    if args.text_file:args.text_file.write_text(all_text(),encoding='utf-8');return
    dest=args.output
    dest.mkdir(parents=True,exist_ok=True)
    font_root=ROOT/'manual/assets/gallery/fonts'
    coverage=json.loads((font_root/'PROVENANCE.json').read_text(encoding='utf-8'))
    checked_fonts={}
    for name,digest in coverage['subsets'].items():
        raw=(font_root/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Font subset digest mismatch')
        checked_fonts[name]=raw
    result={'schema':2,'basis':'Editable originals with localized labels and theme-specific rendering.','sources':{},'files':{},'alignments':[]}
    for scene in TITLES:
        variant=next((name for name,group in coverage['variants'].items() if scene in group['scenes']),None)
        suffix=f'-{variant}' if variant else ''
        fonts={weight:checked_fonts[f'SkinSans-{weight}{suffix}.woff2'] for weight in (400,700)}
        additional=coverage['variants'][variant]['characters'] if variant else ''
        characters=coverage['characters']+additional
        source=ROOT/f'manual/assets/readme-{scene}.ko.svg';result['sources'][str(source.relative_to(ROOT))]=hashlib.sha256(source.read_bytes()).hexdigest()
        for lang in ('ko','en'):
            for theme in ('light','dark'):
                svg,a=build(scene,lang,theme,fonts)
                visible=''.join(''.join(t.itertext()) for t in ET.fromstring(svg).iter(tag('text')))
                missing=set(visible)-set(characters)
                if missing:raise ValueError(f'Rebuild font subsets for missing glyphs: {sorted(missing)}')
                if lang=='en' and re.search('[가-힣]',visible):raise ValueError('Untranslated English label')
                name=f'{scene}{"-en" if lang=="en" else ""}-{theme}.svg';(dest/name).write_text(svg,encoding='utf-8');result['files'][name]=hashlib.sha256(svg.encode()).hexdigest();result['alignments']+= [{'file':name,**x} for x in a]
    (dest/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Refined',len(result['files']),'SVGs from',len(result['sources']),'preserved originals')
if __name__=='__main__':main()
