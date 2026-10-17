import numpy as np
rng=np.random.default_rng(7)
ORDER=['A1','A2','B1','B2','C1','C2']; N=[7,7,7,7,6,6]
center=np.array([-2.5,-1.5,-0.5,0.5,1.5,2.5])
lvl=np.repeat(np.arange(6),N); b=center[lvl]+rng.normal(0,0.35,40)
c=0.12  # residual guessing ("I don't know" removes most of it)
cut=center+0.45  # theta at which a learner gets ~60% of a band's items
def true_level(t): return max([0]+[i for i in range(6) if t>=cut[i]])
def P(t): return c+(1-c)/(1+np.exp(-(t-b)))
# expected total score at each cut -> total-score cut points (Rasch: raw score is sufficient)
Tcut=[sum(P(cut[i])) for i in range(6)]
def rates(x): return np.array([x[lvl==i].mean() for i in range(6)])
def r_current(x):
    r=rates(x); p=0
    for i in range(6):
        cum=x[lvl<=i].mean()
        if r[i]>=.6 and cum>=.6: p=i
    return p
def r_consec(x):
    r=rates(x); p=0
    for i in range(6):
        if r[i]>=.6: p=i
        else: break
    return p
def r_total(x):
    s=x.sum(); return max([0]+[i for i in range(6) if s>=Tcut[i]])
def r_hybrid(x):  # total-score placement, but never above the first band failed badly (<45%)
    p=r_total(x); r=rates(x)
    for i in range(6):
        if r[i]<.45 and i<=p: return max(0,i-1) if i>0 else 0
    return p
rules=dict(current=r_current,consecutive=r_consec,total_score=r_total,hybrid=r_hybrid)
thetas=rng.uniform(-3.5,3.5,40000)
res={k:[] for k in rules}; tl=[]
for t in thetas:
    x=(rng.random(40)<P(t)).astype(float); tl.append(true_level(t))
    for k,f in rules.items(): res[k].append(f(x))
tl=np.array(tl)
print('total-score cutoffs (expected correct at each level):',[round(v,1) for v in Tcut])
for k,v in res.items():
    v=np.array(v); d=v-tl
    print(f'{k:12s} exact {np.mean(d==0):.1%}  within-1 {np.mean(abs(d)<=1):.1%}  over-placed {np.mean(d>0):.1%}  under-placed {np.mean(d<0):.1%}  over by 2+ {np.mean(d>=2):.2%}')
# borderline: how often is the learner's true level adjacent when the score is within 1 point of a cut
