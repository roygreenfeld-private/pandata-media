import re,subprocess,json,sys
TXT={
'roles':"שלושה אנשים עובדים על אותה שקשוקה... ואף אחד מהם לא טבח. נגיד שבשישי בבוקר מישהו מזמין שקשוקה במסעדה. ופה בדיוק נכנס ה-Data Engineer: הוא בונה את הצינור שמחבר בין הקופה למחשב, ודואג שההזמנה הזאת תעבור בו בלי ללכת לאיבוד. ככה, ביום ראשון, ה-Data Analyst יכול לעבור על כל ההזמנות ולגלות משהו מעניין: בשישי מוכרים פי שלושה שקשוקות... ואף אחד לא נוגע בסלט הקינואה. וה-Data Scientist? הוא כבר חושב קדימה: מה יקרה בשישי הבא? כנראה... שנצטרך עוד ביצים. אז בקיצור: אחד אוסף, אחד מבין מה קרה, ואחד מנחש מה יקרה. תשמרו את זה. ואני? אני רק אוכל במבוק.",
'dash':"ברוכים הבאים לחנות של פנדאטא, חנות הבמבוק הכי טרייה ברשת! מקלות במבוק, במבוק טרי, ואפילו... במבוק דיאט. אבל רגע, איך בכלל הולך לי העסק? אני פותח את האתר, את הבנק, את האינסטגרם ועשרה קבצי אקסל... ואני לא מבין כלום. זה כמו לנהוג ברכב בלי מד מהירות ובלי מד דלק: אתה נוסע, אבל אין לך מושג כמה מהר. בשביל זה המציאו את הדשבורד: מסך אחד שמרכז את כל המספרים החשובים, ויכול להתעדכן לבד. כמה מכרתי היום, איזה במבוק הכי פופולרי, ומתי עומד להיגמר המלאי. ככה, במבט אחד, אני יודע מה קורה בעסק. ומה אני עושה עם כל הזמן שחסכתי? כנראה... אוכל את המלאי. אז בקיצור: דשבורד זה מד המהירות של העסק. תשמרו את זה.",
'db':"זוכרים את חנות הבמבוק שלי? בהתחלה רשמתי כל הזמנה על פתק. פתק אחד על המקרר, פתק אחד בכיס... ואחד כנראה אכלתי. ואז לקוח שואל: איפה ההזמנה שלי? ואני... אין לי מושג. בשביל זה יש בסיס נתונים: מקום אחד שבו כל המידע שמור מסודר, בטבלאות. טבלה של לקוחות, טבלה של הזמנות, טבלה של מוצרים, וכולן מחוברות אחת לשנייה. ככה, כשהלקוח שואל, אני מוצא את ההזמנה שלו בשנייה, ואפילו יודע מה הוא הזמין בפעם הקודמת. ואיך מוצאים דברים בבסיס נתונים? שואלים אותו שאלה, בשפה שנקראת SQL... אבל על זה ברילס הבא. אז בקיצור: בסיס נתונים זה הזיכרון המסודר של העסק. עקבו, כדי לא לפספס."}
def chunks(t,maxw=4):
    out=[]
    for ph in re.split(r'(?<=[,.?!:])\s+|\.\.\.\s*',t):
        ph=ph.strip().rstrip(',:')
        if not ph: continue
        w=ph.split()
        n=max(1,-(-len(w)//maxw)); k=-(-len(w)//n)
        for i in range(0,len(w),k): out.append(' '.join(w[i:i+k]).rstrip(',.'))
    return out
def speech(f):
    o=subprocess.run(['ffmpeg','-i',f,'-af','silencedetect=n=-35dB:d=0.2','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
    sp=[];c=0
    for a,b in zip(st,en):
        if a-c>0.08: sp.append((c,a))
        c=b
    if dur-c>0.08: sp.append((c,dur))
    return sp,dur
def timed(text,f):
    sp,dur=speech(f); tot=sum(b-a for a,b in sp); ch=chunks(text)
    L=[len(c.replace(' ',''))+2 for c in ch]; T=sum(L)
    def at(x):
        x*=tot
        for a,b in sp:
            if x<=b-a+1e-6: return a+x
            x-=b-a
        return dur
    res=[];cum=0
    for c,l in zip(ch,L):
        s=at(cum/T); cum+=l; e=at(cum/T)
        res.append([round(s,2),round(e,2),c])
    for i in range(len(res)-1): res[i][1]=res[i+1][0]
    res[-1][1]=round(dur,2)
    return res
if __name__=='__main__':
    for k in ['roles','dash','db']:
        cfg=json.load(open(f'hfv/{k}_nt.json')) if k!='db' else json.load(open('hfv/db_nt.json'))
        cfg['titles']=timed(TXT[k],cfg['audio']); cfg['y']=880; cfg['fade']=0
        json.dump(cfg,open(f'hfv/{k}_cap.json','w'),ensure_ascii=False)
        print(k,len(cfg['titles']),cfg['titles'][:4])

def gaps(f):
    o=subprocess.run(['ffmpeg','-i',f,'-af','silencedetect=n=-30dB:d=0.07','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
    return list(zip(st,en))
def timed2(text,f):
    res=timed(text,f); G=gaps(f)
    # snap each start to the end of the nearest gap (speech onset) within 0.7s
    for r in res:
        s=r[0]; best=None
        for a,b in G:
            if abs(b-s)<0.7 and (best is None or abs(b-s)<abs(best-s)): best=b
        if best is not None: r[0]=round(best-0.05,2)
    for i in range(1,len(res)):
        if res[i][0]<=res[i-1][0]+0.3: res[i][0]=round(res[i-1][0]+0.3,2)
    for i in range(len(res)-1): res[i][1]=res[i+1][0]
    res[0][0]=0
    return res
if __name__=='__main__' and len(sys.argv)>1:
    for k in ['roles','dash','db']:
        cfg=json.load(open(f'hfv/{k}_cap.json')); cfg['titles']=timed2(TXT[k],cfg['audio'])
        json.dump(cfg,open(f'hfv/{k}_cap.json','w'),ensure_ascii=False); print(k,cfg['titles'][:8])

def timed3(text,f):
    sp,dur=speech(f)  # pauses >=0.2s
    onsets=[a for a,b in sp]; tot=sum(b-a for a,b in sp)
    phrases=[p.strip() for p in re.split(r'(?<=[,.?!:])\s+|\.\.\.\s*',text) if p.strip()]
    L=[len(p.replace(' ','')) for p in phrases]; T=sum(L)
    def at(x):
        x*=tot
        for a,b in sp:
            if x<=b-a+1e-6: return a+x
            x-=b-a
        return dur
    starts=[];cum=0
    for l in L: starts.append(at(cum/T)); cum+=l
    used=set(); snapped=[]
    for s in starts:
        cand=[o for o in onsets if abs(o-s)<1.2 and o not in used and (not snapped or o>snapped[-1]+0.25)]
        if cand:
            o=min(cand,key=lambda o:abs(o-s)); used.add(o); snapped.append(o)
        else: snapped.append(max(s,(snapped[-1]+0.3) if snapped else 0))
    snapped[0]=0
    ends=snapped[1:]+[dur]
    res=[]
    for p,s,e in zip(phrases,snapped,ends):
        # trim trailing silence of phrase window
        ee=e
        for a,b in sp:
            if a<e<=b+0.01: pass
        cs=chunks(p); cl=[len(c.replace(' ',''))+1 for c in cs]; ct=sum(cl); x=s
        for c,l in zip(cs,cl):
            d=(e-s)*l/ct; res.append([round(max(0,x-0.05),2),round(x+d,2),c]); x+=d
    for i in range(len(res)-1): res[i][1]=res[i+1][0]
    return res
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='v3':
    for k in ['roles','dash','db']:
        cfg=json.load(open(f'hfv/{k}_cap.json')); cfg['titles']=timed3(TXT[k],cfg['audio'])
        json.dump(cfg,open(f'hfv/{k}_cap.json','w'),ensure_ascii=False); print(k,[t[:2]+[t[2][:12]] for t in cfg['titles'][:10]])

def timed4(text,f):
    sp,dur=speech(f); onsets=[a for a,b in sp]; tot=sum(b-a for a,b in sp)
    phrases=[p.strip() for p in re.split(r'(?<=[,.?!:])\s+|\.\.\.\s*',text) if p.strip()]
    L=[len(p.replace(' ',''))+1 for p in phrases]; T=sum(L)
    def at(x):
        x*=tot
        for a,b in sp:
            if x<=b-a+1e-6: return a+x
            x-=b-a
        return dur
    est=[];cum=0
    for l in L: est.append(at(cum/T)); cum+=l
    n,m=len(phrases),len(onsets); INF=1e9; PEN=0.9
    # dp[i][j]: min cost for first i phrases using onsets < j ; choice per phrase: snap to onset j-1 or unsnapped
    import functools
    dp=[[INF]*(m+1) for _ in range(n+1)]; bk=[[None]*(m+1) for _ in range(n+1)]
    for j in range(m+1): dp[0][j]=0
    for i in range(1,n+1):
        for j in range(m+1):
            best=dp[i][j-1] if j>0 else INF; b=('skip',) if j>0 else None
            if dp[i-1][j]+PEN<best: best=dp[i-1][j]+PEN; b=('un',)
            if j>0 and dp[i-1][j-1]+abs(onsets[j-1]-est[i-1])<best: best=dp[i-1][j-1]+abs(onsets[j-1]-est[i-1]); b=('snap',)
            dp[i][j]=best; bk[i][j]=b
    i,j=n,m; st=[None]*n
    while i>0:
        b=bk[i][j]
        if b[0]=='skip': j-=1
        elif b[0]=='un': st[i-1]=None; i-=1
        else: st[i-1]=onsets[j-1]; i-=1; j-=1
    for k in range(n):
        if st[k] is None:
            prv=max([s for s in st[:k] if s is not None] or [0]); st[k]=max(est[k],prv+0.3)
    st[0]=0; ends=st[1:]+[dur]; res=[]
    for p,s,e in zip(phrases,st,ends):
        cs=chunks(p); cl=[len(c.replace(' ',''))+1 for c in cs]; ct=sum(cl); x=s
        for c,l in zip(cs,cl):
            d=(e-s)*l/ct; res.append([round(max(0,x-0.05),2),round(x+d,2),c]); x+=d
    for q in range(len(res)-1): res[q][1]=res[q+1][0]
    return res
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='v4':
    for k in ['roles','dash','db']:
        cfg=json.load(open(f'hfv/{k}_cap.json')); cfg['titles']=timed4(TXT[k],cfg['audio'])
        json.dump(cfg,open(f'hfv/{k}_cap.json','w'),ensure_ascii=False); print(k,[t[:2]+[t[2][:10]] for t in cfg['titles'][:12]])

def timed5(text,f):
    sp,dur=speech(f); tot=sum(b-a for a,b in sp)
    phrases=[p.strip() for p in re.split(r'(?<=[,.?!:])\s+|\.\.\.\s*',text) if p.strip()]
    L=[len(p.replace(' ',''))+1 for p in phrases]; r=sum(L)/tot
    n,m=len(phrases),len(sp); INF=1e18
    dp=[[INF]*(m+1) for _ in range(n+1)]; bk=[[None]*(m+1) for _ in range(n+1)]; dp[0][0]=0
    for i in range(n+1):
        for k in range(m+1):
            if dp[i][k]>=INF: continue
            for a in range(1,4):
                for b in range(1,4):
                    if i+a>n or k+b>m: continue
                    c=sum(L[i:i+a])/r; d=sum(e-s for s,e in sp[k:k+b])
                    cost=dp[i][k]+(c-d)**2/(d+0.5)+0.15*(a+b-2)
                    if cost<dp[i+a][k+b]: dp[i+a][k+b]=cost; bk[i+a][k+b]=(a,b)
    i,k=n,m; blocks=[]
    while i>0: a,b=bk[i][k]; blocks.append((i-a,i,k-b,k)); i-=a; k-=b
    blocks.reverse(); res=[]
    for i0,i1,k0,k1 in blocks:
        segs=sp[k0:k1]; segtot=sum(e-s for s,e in segs)
        def at(x):
            for s,e in segs:
                if x<=e-s+1e-6: return s+x
                x-=e-s
            return segs[-1][1]
        cs=[];
        for p in phrases[i0:i1]: cs+=chunks(p)
        cl=[len(c.replace(' ',''))+1 for c in cs]; ct=sum(cl); cum=0
        for c,l in zip(cs,cl):
            res.append([round(max(0,at(segtot*cum/ct)-0.08),2),0,c]); cum+=l
        res[-1][1]=segs[-1][1]
    for q in range(len(res)-1): res[q][1]=max(res[q][1],res[q+1][0]) if res[q][1] and res[q][1]<res[q+1][0] and res[q+1][0]-res[q][1]<0.6 else res[q+1][0]
    res[-1][1]=round(dur,2); res[0][0]=0
    return res
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='v5':
    for k in ['roles','dash','db']:
        cfg=json.load(open(f'hfv/{k}_cap.json')); cfg['titles']=timed5(TXT[k],cfg['audio'])
        json.dump(cfg,open(f'hfv/{k}_cap.json','w'),ensure_ascii=False); print(k,[t[:1]+[t[2][:10]] for t in cfg['titles'][:14]])
