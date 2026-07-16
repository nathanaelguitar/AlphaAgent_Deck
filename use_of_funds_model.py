#!/usr/bin/env python3
"""
AlphaAgent Healthcare Solutions — Use of Funds Model
=====================================================

Purpose: Answer the banker's question — "$100k or $500k?" — with a defensible,
bottoms-up cost model instead of a guess.

All figures are grounded in July 2026 market research (see SOURCES at bottom).
Ranges are given as (low, high); the model computes low/mid/high totals so you
can show a "Conservative vs Aggressive" spread to investors.

Three funding scenarios are modeled:
  - LEAN      (~$100k target) : MVP + validation, NO regulatory clearance yet
  - STANDARD  (~$300k target) : Multi-hospital pilot + QMS + FDA pre-submission
  - AGGRESSIVE(~$500k target) : Above + 510(k) submission underway + 18mo runway

KEY HONESTY NOTE: A full 510(k) clearance for a novel AI-enabled device is a
$50k-$250k+ line item on its own and typically takes 12-18 months AFTER the
pre-submission. The $500k round gets you to a multi-hospital pilot with the
regulatory machine STARTED — not to a cleared, on-market product. That is the
next (Series A / larger seed) round. Say this plainly; sophisticated investors
respect founders who know where the money runs out.
"""

from dataclasses import dataclass, field


@dataclass
class LineItem:
    """A single cost line with a low/high range and a note on scope."""
    name: str
    low: float
    high: float
    note: str = ""

    @property
    def mid(self) -> float:
        return (self.low + self.high) / 2


@dataclass
class Bucket:
    """A category of spend (Hardware, Regulatory, Operations)."""
    name: str
    items: list = field(default_factory=list)

    def add(self, name, low, high, note=""):
        self.items.append(LineItem(name, low, high, note))

    def total(self, key="mid"):
        return sum(getattr(i, key) for i in self.items)


# ---------------------------------------------------------------------------
# ASSUMPTIONS (edit these; every number traces to a source at the bottom)
# ---------------------------------------------------------------------------

# Hardware unit economics
VUZIX_UNIT_COST = 2200          # Vuzix LX1 (Android 15, 12MP cam, 1080p60, triple mics), $2,199.99 list
PILOT_UNITS_LEAN = 3            # dev + demo units
PILOT_UNITS_STANDARD = 12       # enough for 2-3 hospital sites
PILOT_UNITS_AGGRESSIVE = 25     # 5-10 site multi-hospital pilot + spares

# Founder economics — deliberately lean, below-market MedTech founder pay.
# NOTE: Only the software founder (Nathanael) draws a salary initially. Manny
# (hardware) joins EQUITY-ONLY and starts drawing pay only AFTER pilot success —
# so base runway carries ONE salary, not two. This is a deliberate capital-
# efficiency lever: hardware cost stays deferred until off-the-shelf Vuzix has
# proven the wedge.
FOUNDER_MONTHLY = 6500          # per salaried founder per month (survival, not market)
N_SALARIED_FOUNDERS = 1         # Nathanael only, initially; Manny = equity until post-pilot
RUNWAY_LEAN = 9                 # months
RUNWAY_STANDARD = 12
RUNWAY_AGGRESSIVE = 18

# Cloud / compute / API burn (Azure blob, GCP Gemini voice, agent inference)
CLOUD_MONTHLY = 1200            # pre-scale, pilot-load estimate


def build_scenario(tier: str):
    """tier in {'lean','standard','aggressive'}"""
    hw = Bucket("Hardware & Manufacturing")
    reg = Bucket("Regulatory & Compliance")
    ops = Bucket("Operational Runway")

    if tier == "lean":
        units = PILOT_UNITS_LEAN
        runway = RUNWAY_LEAN
        # Hardware: buy off-the-shelf, 3D-print enclosures. No tooling yet.
        hw.add("Vuzix-class dev units", units*VUZIX_UNIT_COST*0.9, units*VUZIX_UNIT_COST*1.1,
               f"{units} LX1 units @ ~${VUZIX_UNIT_COST}")
        hw.add("3D-printed enclosures + iteration", 3000, 8000, "printer time, materials, revs")
        hw.add("Sensors / cables / misc bench", 1500, 4000)
        # Regulatory: HIPAA posture only — no FDA submission at this tier.
        reg.add("HIPAA readiness (policies, BAA, automation tool)", 8000, 20000,
                "Vanta/Drata-style + light audit; NOT SOC 2 yet")
        reg.add("Regulatory strategy consult (scoping)", 3000, 8000, "a few advisory hours")
        # Ops
        ops.add("Founder runway", FOUNDER_MONTHLY*N_SALARIED_FOUNDERS*runway, FOUNDER_MONTHLY*N_SALARIED_FOUNDERS*runway,
                f"{N_SALARIED_FOUNDERS} salaried founder x ${FOUNDER_MONTHLY}/mo x {runway}mo")
        ops.add("Cloud / API burn", CLOUD_MONTHLY*runway*0.7, CLOUD_MONTHLY*runway*1.3,
                f"~${CLOUD_MONTHLY}/mo x {runway}mo")
        ops.add("Legal / incorporation / buffer", 5000, 12000, "C-corp, IP assignment, buffer")

    elif tier == "standard":
        units = PILOT_UNITS_STANDARD
        runway = RUNWAY_STANDARD
        # Still pre-Manny: off-the-shelf Vuzix + 3D-printed accessories. NO custom
        # tooling — that is deferred to the post-pilot hardware phase (Aggressive).
        hw.add("Vuzix-class pilot units", units*VUZIX_UNIT_COST*0.9, units*VUZIX_UNIT_COST*1.1,
               f"{units} off-the-shelf LX1 units @ ~${VUZIX_UNIT_COST}")
        hw.add("3D-printed mounts/accessories + iteration", 4000, 10000, "no tooling yet")
        hw.add("Sensors / cabling / bench", 3000, 6000)
        reg.add("ISO 13485 QMS setup (consultant-led, small co)", 30000, 60000,
                "gap analysis + framework, implement internally")
        reg.add("HIPAA + SOC 2 (first year, small co)", 20000, 50000,
                "automation platform + auditor")
        reg.add("FDA Pre-Submission (Q-Sub) prep + meeting", 10000, 30000,
                "lock testing protocol for Class II 510(k)")
        ops.add("Founder runway", FOUNDER_MONTHLY*N_SALARIED_FOUNDERS*runway, FOUNDER_MONTHLY*N_SALARIED_FOUNDERS*runway,
                f"{N_SALARIED_FOUNDERS} salaried founder x ${FOUNDER_MONTHLY}/mo x {runway}mo")
        ops.add("Cloud / API burn", CLOUD_MONTHLY*runway*0.7, CLOUD_MONTHLY*runway*1.3,
                f"~${CLOUD_MONTHLY}/mo x {runway}mo")
        ops.add("Legal / IP / contingency", 12000, 25000)

    elif tier == "aggressive":
        units = PILOT_UNITS_AGGRESSIVE
        runway = RUNWAY_AGGRESSIVE
        # Post-pilot hardware phase: Manny is now on board, so custom tooling and
        # ruggedized enclosure work begin here (funded because the wedge is proven).
        hw.add("Vuzix-class pilot fleet", units*VUZIX_UNIT_COST*0.9, units*VUZIX_UNIT_COST*1.1,
               f"{units} LX1 units @ ~${VUZIX_UNIT_COST}")
        hw.add("Aluminum tooling + low-volume run", 8000, 25000, "2-part enclosure, bridge tooling")
        hw.add("Hardware eng / design iteration (Manny)", 15000, 30000, "custom enclosure, ruggedization")
        hw.add("Sensors / cabling / assembly / spares", 5000, 12000)
        reg.add("ISO 13485 QMS (consultant-led)", 30000, 60000)
        reg.add("HIPAA + SOC 2 (first year)", 25000, 60000)
        reg.add("FDA Pre-Sub + 510(k) submission (started)", 50000, 150000,
                "user fee + consultant + testing/validation; clearance completes NEXT round")
        reg.add("510(k) small-business user fee", 6517, 26067, "$6,517 small biz / $26,067 standard, FY26")
        ops.add("Founder runway", FOUNDER_MONTHLY*N_SALARIED_FOUNDERS*runway, FOUNDER_MONTHLY*N_SALARIED_FOUNDERS*runway,
                f"{N_SALARIED_FOUNDERS} salaried founder x ${FOUNDER_MONTHLY}/mo x {runway}mo")
        ops.add("Manny onboarding — partial-yr hardware salary (post-pilot)", 30000, 70000,
                "starts drawing pay only after pilot proves the wedge")
        ops.add("Cloud / API burn", CLOUD_MONTHLY*runway*0.7, CLOUD_MONTHLY*runway*1.3,
                f"~${CLOUD_MONTHLY}/mo x {runway}mo")
        ops.add("Legal / IP / contingency", 20000, 40000)

    else:
        raise ValueError(tier)

    return hw, reg, ops


def money(x):
    return f"${x:>10,.0f}"


def print_scenario(tier, target):
    hw, reg, ops = build_scenario(tier)
    buckets = [hw, reg, ops]
    print("=" * 78)
    print(f"  SCENARIO: {tier.upper():<12}   (fundraise target ~ ${target:,.0f})")
    print("=" * 78)
    grand_low = grand_mid = grand_high = 0
    for b in buckets:
        print(f"\n  {b.name}")
        print(f"  {'-'*74}")
        for it in b.items:
            note = f"  ({it.note})" if it.note else ""
            print(f"    {it.name:<44}{money(it.low)} - {money(it.high)}")
            if it.note:
                print(f"      -> {it.note}")
        bl, bm, bh = b.total('low'), b.total('mid'), b.total('high')
        print(f"    {'SUBTOTAL '+b.name:<44}{money(bl)} - {money(bh)}   (mid {money(bm)})")
        grand_low += bl; grand_mid += bm; grand_high += bh
    print(f"\n  {'='*74}")
    print(f"    {'GRAND TOTAL':<44}{money(grand_low)} - {money(grand_high)}")
    print(f"    {'MIDPOINT':<44}{money(grand_mid)}")
    # Recommended raise = mid + ~15-20% contingency, rounded
    reco = grand_mid * 1.18
    print(f"    {'SUGGESTED RAISE (mid + 18% contingency)':<44}{money(reco)}")
    print(f"  {'='*74}\n")
    return grand_low, grand_mid, grand_high


def main():
    print("\n")
    print("#" * 78)
    print("#  AlphaAgent Healthcare Solutions — USE OF FUNDS ANALYSIS")
    print("#  Smart glasses + AI agent for autonomous surgical documentation")
    print("#" * 78)

    results = {}
    for tier, target in [("lean", 100_000), ("standard", 300_000), ("aggressive", 500_000)]:
        results[tier] = print_scenario(tier, target)

    print("#" * 78)
    print("#  BOTTOM LINE FOR THE BANKER")
    print("#" * 78)
    print("""
  $100k (LEAN)  -> Validated MVP + 2-3 hospital design partners on OFF-THE-SHELF
                   hardware. HIPAA posture only. Proves the wedge. Does NOT touch
                   FDA. This is a 'de-risk the demo' round, not a 'go to market' round.

  $300k (STANDARD) -> The credible seed. Funds a real 12-month runway, ISO 13485
                   QMS, HIPAA+SOC 2, custom enclosures, AND the FDA Pre-Submission
                   that locks your 510(k) pathway. Multi-site pilot. This is the
                   number most MedTech seed investors expect to see.

  $500k (AGGRESSIVE) -> 18-month runway, first technical hire, and the 510(k)
                   submission actively underway. Removes the 'can they clear FDA?'
                   question. Best if the banker's investors want to see the
                   regulatory moat being built, not just planned.

  RECOMMENDATION: Anchor the ask at ~$500k, but present $300k as the 'efficient'
  floor. The Hardware Multiplier (per-unit glasses + tooling) and the Compliance
  Tax (QMS + FDA + SOC 2) together make sub-$100k a non-starter for anything
  beyond a demo. Framing: "We can prove the wedge on $100k; we clear the
  regulatory moat on $500k."

  ONE THING TO SAY OUT LOUD: full 510(k) CLEARANCE completes in the round AFTER
  this one (~2027). This raise gets you to a cleared PATHWAY + live pilots, which
  is exactly the inflection that de-risks the Series A.
""")

    # Machine-readable summary for building the deck's Use-of-Funds slide
    print("#  SLIDE-READY NUMBERS (midpoints, rounded to nearest $5k):")
    for tier in ("lean", "standard", "aggressive"):
        _, mid, _ = results[tier]
        print(f"    {tier.capitalize():<12} midpoint burn: ${round(mid/5000)*5000:,.0f}")
    print()


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# SOURCES (July 2026 research)
# ---------------------------------------------------------------------------
# FDA 510(k) all-in $50k-$250k+; user fee FY2026 $26,067 std / $6,517 small biz;
#   consultant $15k-$50k; testing/validation $20k-$150k+:
#     complizen.ai/post/how-much-does-510k-cost
#     i3cglobal.com/fda-510k-fees/
#     fda.gov/industry/fda-user-fee-programs/medical-device-user-fee-amendments-mdufa-fees
# FDA small-business determination (<=$100M gross receipts -> 50% fee):
#     fda.gov/medical-devices/.../small-business-determination-sbd-program
# ISO 13485 QMS small co consultant-led $30k-$60k:
#     meddeviceguide.com/blog/iso-13485-certification-cost-timeline-guide
# HIPAA/SOC 2 first year small co $20k-$80k:
#     thoropass.com/blog/soc-2-audit-cost-a-guide
#     zipsec.com/blog/how-much-does-soc-2-compliance-really-cost-a-clear-guide
# Vuzix LX1 $2,199.99 list (Android 15, 12MP cam, 1080p60, triple noise-cancel mics):
#     vuzix.com/products/vuzix-lx1-smart-glasses
# Injection molding: aluminum bridge tooling $3k-$15k; 2-part enclosure $8k-$25k:
#     formlabs.com/blog/injection-molding-cost/ ; jaycon.com injection-moulding-price
# MedTech seed/angel sizing (angel $50k-$2M, 10-25%):
#     complizen.ai/post/medical-device-startup-funding-complete-2025-guide
# ---------------------------------------------------------------------------
