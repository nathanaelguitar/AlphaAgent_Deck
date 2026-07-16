"""AlphaAgent 3-year financial model — bottom-up, monthly, SITE-priced.

Pricing: per-hospital/ASC site license, $5K-$20K/month depending on size
(single service line -> department -> system). Model uses $10K/mo blended
average ($120K ACV). Hospital pays the subscription; glasses are free.

Assumptions:
  - $10,000 / site / month blended ($5K entry service line, $15-20K expanded)
  - ~10 surgeons per site -> $20,000 hardware per new site (10 x $2K LX1)
  - Cloud/inference/support: $1,000 / site / month -> 90% software GM
  - Hardware payback: 20,000 / (10,000-1,000) = 2.2 months
  - Month 1 = close of $500K pre-seed (H2 2026)
  - Pilots months 1-8 (procurement + IT review realistic), paid from month 9
  - Y3 acceleration assumes 510(k) clearance lands ~end of Y2
  - Seed (~$1.5M) raised ~month 14 on converted pilots
"""
import csv

PRICE, CLOUD, HW_PER_SITE = 10_000, 1_000, 20_000
PRESEED, SEED, SEED_MONTH = 500_000, 1_500_000, 14

# Cumulative paying sites at month-end
sites = [
    0,0,0,0,0,0,0,0,1,2,3,3,                   # Y1: 8-mo pilots convert from m9
    4,4,5,6,6,7,8,8,9,9,10,10,                 # Y2: land-and-expand
    12,13,14,15,16,18,19,20,22,23,24,25,       # Y3: post-510(k) acceleration
]

# Monthly opex — Y1 mirrors the deck's use-of-funds midpoint (~$29K/mo)
opex = [29_000]*12 + [60_000]*6 + [85_000]*6 + [110_000]*6 + [140_000]*6

rows, cash, prev = [], PRESEED, 0
for m in range(36):
    n = sites[m]; new = max(0, n - prev)
    rev = n * PRICE
    cogs = n * CLOUD + new * HW_PER_SITE
    net = rev - cogs - opex[m]
    if m + 1 == SEED_MONTH: cash += SEED
    cash += net
    rows.append(dict(month=m+1, sites=n, new_sites=new, revenue=rev, cogs=cogs,
                     gross_profit=rev-cogs, opex=opex[m], net=net, cash=cash))
    prev = n

with open("model_monthly.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

def yr(k): return [sum(r[k] for r in rows[y*12:(y+1)*12]) for y in range(3)]
print(f"{'':16}{'Year 1':>11}{'Year 2':>11}{'Year 3':>11}")
for lbl, k in [("Revenue","revenue"),("COGS","cogs"),("Gross profit","gross_profit"),
               ("Opex","opex"),("Net","net")]:
    v = yr(k); print(f"{lbl:16}{v[0]:>11,.0f}{v[1]:>11,.0f}{v[2]:>11,.0f}")
for y in range(3):
    r = rows[y*12+11]
    print(f"End Y{y+1}: sites={r['sites']:>3}  ARR=${r['sites']*PRICE*12:>10,}  cash=${r['cash']:>10,.0f}")
gm = [yr('gross_profit')[y]/yr('revenue')[y]*100 for y in range(3)]
print(f"GM: Y1 {gm[0]:.0f}%  Y2 {gm[1]:.0f}%  Y3 {gm[2]:.0f}%   HW payback: {HW_PER_SITE/(PRICE-CLOUD):.1f} mo")
low = min(rows[:SEED_MONTH-1], key=lambda r: r['cash'])
print(f"Pre-seed lowest cash: month {low['month']}: ${low['cash']:,.0f}")
pos = [r['month'] for r in rows if r['net'] > 0]
print(f"Cashflow-positive months: {pos[:6]}{'...' if len(pos)>6 else ''}  Y3-end cash: ${rows[-1]['cash']:,.0f}")

# ---- Years 4-10 long view (annual): sites x rising ACV as departments expand ----
print()
print("LONG VIEW (post-510(k), US: ~6,100 hospitals + ~11,000 ASCs)")
print(f"{'Year':>6}{'Sites':>8}{'Avg ACV':>10}{'ARR':>10}{'Penetration':>13}")
long_sites = {4: 50, 5: 90, 6: 160, 7: 260, 8: 400, 9: 560, 10: 750}
acv = {4: 130, 5: 150, 6: 158, 7: 165, 8: 170, 9: 175, 10: 180}  # $K
for y in (3, 4, 5, 7, 10):
    n = 25 if y == 3 else long_sites[y]
    a = 120 if y == 3 else acv[y]
    print(f"{y:>6}{n:>8}{a:>9}K{n*a/1000:>9.1f}M{n/17100*100:>12.1f}%")
