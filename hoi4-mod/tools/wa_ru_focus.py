import re,json,glob,os
SRC='/mnt/project-files/hoi4-mod/wa_ru/wuw_focus_l_russian.yml'
names=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'wa_focus_names.json')))
tr={}
i=0
for f in sorted(glob.glob(''+os.path.join(os.path.dirname(os.path.abspath(__file__)),'wa_focus_tr','c*.txt')+'')):
    for l in open(f,encoding='utf-8').read().split('\n')[:-1] if open(f,encoding='utf-8').read().endswith('\n') else []:
        if i<len(names): tr[names[i][0]]=l
        i+=1
out=[]
for l in open(SRC,encoding='utf-8-sig'):
    m=re.match(r'(\s*)(\S+?):(\d*)\s+"(.*)"\s*$',l.rstrip('\n'))
    if m and m.group(2) in tr: l=f'{m.group(1)}{m.group(2)}:{m.group(3)} "{tr[m.group(2)]}"\n'
    out.append(l)
os.makedirs('/mnt/project-files/hoi4-mod/wa_ru_done',exist_ok=True)
open('/mnt/project-files/hoi4-mod/wa_ru_done/wuw_focus_l_russian.yml','w',encoding='utf-8-sig').write(''.join(out))
print(len(tr))
