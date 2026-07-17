"""AlphaAgent 3-year financial model — bottom-up, monthly, SITE-priced.

Pricing: per-hospital/ASC site license, $5K-$20K/month depending on size
(single service line -> department -> system). Model uses $10K/mo blended
average ($120K ACV). Hospital pays the subscription; glasses are free.

Accounting note (v2): the glasses are a DURABLE ASSET, so instead of
expensing the full $20K/site the month it deploys, we CAPITALIZE it and
DEPRECIATE straight-line over a 3-year (36-month) useful life. Cash still
leaves the day we buy the hardware (that is capex, tracked separately);
the P&L only sees monthly depreciation. This smooths net income and is the
standard GAAP treatment for deployed equipment.

Opex note: opex is TWO FOUNDERS + non-headcount costs, NOT a growing team.
  - Y1 (~$29K/mo): Nathanael's salary + base cloud + regulatory setup.
  - Y2: Manny moves from equity-only to salaried (the ONLY headcount change),
        510(k) work ramps.
  - Y3: 510(k) submission costs, medical-device / D&O insurance, cloud at
        scale, and 1099 implementation/sales contractors (not FTEs).
  The company runs on the two founders indefinitely; the ramp is regulatory,
  infrastructure, and GTM spend — not payroll.

Assumptions:
  - $10,000 / site / month blended ($5K entry service line, $15-20K expanded)
  - ~10 surgeons per site -> $20,000 hardware per new site (10 x $2K LX1)
  - Glasses depreciated straight-line over 36 months (useful life)
  - Cloud/inference/support: $1,000 / site / month
  - Cash payback on hardware: 20,000 / (10,000-1,000) = 2.2 months
  - Month 1 = close of $500K pre-seed (H2 2026)
  - Pilots months 1-8 (procurement + IT review realistic), paid from month 9
  - Seed (~$1.5M) raised ~month 14 on converted pilots
"""
import csv

PRICE, CLOUD, HW_PER_SITE = 10_000, 1_000, 20_000
USEFUL_LIFE = 36                      # months of straight-line depreciation
PRESEED, SEED, SEED_MONTH = 500_000, 1_500_000, 14

# Cumulative paying sites at month-end
sites = [
    0,0,0,0,0,0,0,0,1,2,3,3,                   # Y1: 8-mo pilots convert from m9
    4,4,5,6,6,7,8,8,9,9,10,10,                 # Y2: land-and-expand
    12,13,14,15,16,18,19,20,22,23,24,25,       # Y3: post-510(k) acceleration
]

# Monthly opex — two founders + non-headcount ramp (see Opex note above)
opex = [29_000]*12 + [60_000]*6 + [85_000]*6 + [110_000]*6 + [140_000]*6

dep_per_site = HW_PER_SITE / USEFUL_LIFE     # monthly depreciation per deployed site
rows, cash, prev = [], PRESEED, 0
cohorts = []                                 # (deploy_month_index, units) for depreciation
for m in range(36):
    n = sites[m]; new = max(0, n - prev)
    if new: cohorts.append((m, new))
    rev = n * PRICE
    cloud_cogs = n * CLOUD
    # depreciation: every cohort still inside its 36-month life depreciates this month
    dep = sum(units * dep_per_site for (dm, units) in cohorts if 0 <= m - dm < USEFUL_LIFE)
    total_cogs = cloud_cogs + dep
    gross_profit = rev - total_cogs
    net = gross_profit - opex[m]             # accrual net income (non-cash dep)
    capex = new * HW_PER_SITE                # cash out when hardware is bought
    operating_cf = net + dep                 # add back non-cash depreciation
    seed_in = SEED if m + 1 == SEED_MONTH else 0
    cash += operating_cf - capex + seed_in
    rows.append(dict(month=m+1, sites=n, new_sites=new, revenue=rev,
                     cloud_cogs=cloud_cogs, depreciation=round(dep),
                     total_cogs=round(total_cogs), gross_profit=round(gross_profit),
                     opex=opex[m], net=round(net), capex=capex, cash=round(cash)))
    prev = n

with open("model_monthly.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

def yr(k): return [sum(r[k] for r in rows[y*12:(y+1)*12]) for y in range(3)]
print(f"{'':16}{'Year 1':>11}{'Year 2':>11}{'Year 3':>11}")
for lbl, k in [("Revenue","revenue"),("Cloud COGS","cloud_cogs"),
               ("Depreciation","depreciation"),("Gross profit","gross_profit"),
               ("Opex","opex"),("Net income","net"),("Capex (cash)","capex")]:
    v = yr(k); print(f"{lbl:16}{v[0]:>11,.0f}{v[1]:>11,.0f}{v[2]:>11,.0f}")
for y in range(3):
    r = rows[y*12+11]
    print(f"End Y{y+1}: sites={r['sites']:>3}  ARR=${r['sites']*PRICE*12:>10,}  cash=${r['cash']:>10,.0f}")
gm = [yr('gross_profit')[y]/yr('revenue')[y]*100 for y in range(3)]
print(f"GM: Y1 {gm[0]:.0f}%  Y2 {gm[1]:.0f}%  Y3 {gm[2]:.0f}%   Cash payback: {HW_PER_SITE/(PRICE-CLOUD):.1f} mo")
low = min(rows[:SEED_MONTH-1], key=lambda r: r['cash'])
print(f"Pre-seed lowest cash: month {low['month']}: ${low['cash']:,.0f}")
pos = [r['month'] for r in rows if r['net'] > 0]
print(f"First net-income-positive month: {pos[0] if pos else None}  Y3-end cash: ${rows[-1]['cash']:,.0f}")

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
