"""Robustness check for the placement rule: derive cut points under one item model, evaluate under others.

Rules compared:
  current     - level L if that level >=60% and cumulative >=60% (gaps allowed)
  total       - total-score cut points
  total+floor - total-score cut points, but never below the highest level reached with every level up to it
                mastered (>=6/7 or >=5/6). Protects a learner who aces A1-A2 and honestly says "I don't know" after.
"""
import numpy as np

N = [7, 7, 7, 7, 6, 6]
CENTER = np.array([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5])
LVL = np.repeat(np.arange(6), N)
NEED = np.array([6, 6, 6, 6, 5, 5])

def model(a, c, seed=7):
    rng = np.random.default_rng(seed)
    b = CENTER[LVL] + rng.normal(0, 0.35, 40)
    return lambda t: c + (1 - c) / (1 + np.exp(-a * (t - b)))

def true_level(t):
    return max([0] + [i for i in range(6) if t >= CENTER[i] + 0.45])

def cuts_from(P):
    return [round(sum(P(CENTER[i] + 0.45))) for i in range(6)]

def r_current(x):
    p = 0
    for i in range(6):
        if x[LVL == i].mean() >= .6 and x[LVL <= i].mean() >= .6:
            p = i
    return p

def floor_level(x):
    p = 0
    for i in range(6):
        if x[LVL == i].sum() >= NEED[i]:
            p = i
        else:
            break
    return p

def make_total(cuts):
    return lambda x: max([0] + [i for i in range(1, 6) if x.sum() >= cuts[i]])

def evaluate(rule, P, n=20000, seed=1):
    rng = np.random.default_rng(seed)
    d = []
    for t in rng.uniform(-3.5, 3.5, n):
        x = (rng.random(40) < P(t)).astype(float)
        d.append(rule(x) - true_level(t))
    d = np.array(d)
    return np.mean(d == 0), np.mean(abs(d) <= 1), np.mean(d >= 2), np.mean(d <= -2)

if __name__ == "__main__":
    cuts = [0, 17, 23, 28, 33, 36]
    print("cut points used:", cuts)
    for a in (1.0, 1.7, 2.5):
        for c in (0.03, 0.12):
            P = model(a, c)
            print(f"\nitem model a={a} c={c}  (cuts this model would give: {cuts_from(P)})")
            total = make_total(cuts)
            rules = {"current": r_current, "total": total,
                     "total+floor": lambda x, total=total: max(total(x), floor_level(x))}
            for k, f in rules.items():
                e, w, o2, u2 = evaluate(f, P)
                print(f"  {k:12s} exact {e:.0%}  within-1 {w:.0%}  over by 2+ {o2:.1%}  under by 2+ {u2:.1%}")
    # the honest A2 learner: all A1-A2 right, "I don't know" for everything else
    x = np.zeros(40); x[:14] = 1
    print("\nA1+A2 all right, rest IDK ->", ["A1","A2","B1","B2","C1","C2"][max(make_total(cuts)(x), floor_level(x))],
          "(total alone:", ["A1","A2","B1","B2","C1","C2"][make_total(cuts)(x)] + ")")
