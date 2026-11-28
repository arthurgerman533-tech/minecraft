#!/usr/bin/env python3
"""Apply Russian translation chunks to won_l_russian.yml (index-aligned)."""
import json,re,sys
SRC="/home/user/minecraft/hoi4-mod/tools/won_src/localisation/russian/won_l_russian.yml"
W="/tmp/wt/"
def rd(n): return open(W+n,encoding="utf-8").read().split("\n")[:-1] if open(W+n,encoding="utf-8").read().endswith("\n") else open(W+n,encoding="utf-8").read().split("\n")
items=json.load(open("/tmp/won_items.json"))
rest=json.load(open("/tmp/rest.json"))
exec(open("/tmp/wt_tail.py").read())
tl=[]
for n in ["c0","c1","c2","c3","c4","c5"]: tl+=rd(n+".txt")
assert len(tl)==945,len(tl)
rl=[]
for n in ["r0","r1","r2"]: rl+=rd(n+".txt")
assert len(rl)==400,len(rl)
ridx={i:k for k,(i,t) in enumerate(rest)}
out=[]
for i,(k,t) in enumerate(items):
    if i<945: v=tl[i]
    elif t.startswith("GFX_"): v=t
    elif i in ridx:
        j=ridx[i]; v=rl[j] if j<400 else tr(t)
    else:
        m=re.match(r'(GDP|Treasury) (\d+) months ago: (.*)',t)
        if m:
            w="ВВП" if m[1]=="GDP" else "Казна"; v=f"{w} {m[2]} мес. назад: "+m[3].replace(" bn"," млрд")
        else:
            m=re.match(r'(GDP|Treasury) last month: (.*)',t)
            w="ВВП" if m[1]=="GDP" else "Казна"; v=f"{w} в прошлом месяце: "+m[2].replace(" bn"," млрд")
    out.append(v)
json.dump(out,open("/tmp/won_out.json","w"),ensure_ascii=False)
# rewrite file
pat=re.compile(r'^(\s*)(\S+?):(\d*)\s+"(.*)"\s*$')
lines=open(SRC,encoding="utf-8-sig").read().split("\n")
n=0;res=[]
for ln in lines:
    m=pat.match(ln)
    if m:
        v=out[n].replace('"','\\"') if False else out[n]
        res.append(f'{m[1]}{m[2]}:{m[3]} "{v}"'); n+=1
    else: res.append(ln)
assert n==len(items),(n,len(items))
open(SRC,"w",encoding="utf-8-sig",newline="").write("\n".join(res))
print("ok",n)
