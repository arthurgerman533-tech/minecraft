import re,sys,os
sys.path.insert(0,os.path.dirname(__file__))
import wa_ru
SRC='/mnt/project-files/hoi4-mod/wa_ru/'
def tr(key,v):
    if key.endswith('_ADJ') or key.endswith('_adj'):
        if v in wa_ru.GEO: return wa_ru.GEO[v][1]
        if ' ' not in v and v in wa_ru.ADJ: return wa_ru.ADJ[v]
        return None
    if ' of ' in v or '$' in v: return None
    return wa_ru.translate(v)
def run(name,out):
    n=t=0; lines=[]
    for l in open(SRC+name+'_l_russian.yml',encoding='utf-8-sig'):
        m=re.match(r'(\s*)(\S+?):(\d*)\s+"(.*)"\s*$',l.rstrip('\n'))
        if m:
            n+=1; r=tr(m.group(2),m.group(4))
            if r: t+=1; l=f'{m.group(1)}{m.group(2)}:{m.group(3)} "{r}"\n'
        lines.append(l if l.endswith('\n') else l+'\n')
    os.makedirs(os.path.dirname(out),exist_ok=True)
    open(out,'w',encoding='utf-8-sig').write(''.join(lines))
    print(name,n,t)
if __name__=='__main__':
    o=sys.argv[1]
    for nm in ('countries','countries_cosmetic'): run(nm,f'{o}/{nm}_l_russian.yml')
