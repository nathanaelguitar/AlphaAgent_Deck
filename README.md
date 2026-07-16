# AlphaAgent Deck — Financial Model & Slide Generator

Code behind the financial projections in `AlphaAgent_Pitch_Deck_v2.pptx`.

## Files

- **`model.py`** — bottom-up 3-year monthly financial model plus a Year 4–10
  long view. All assumptions (site pricing, hardware cost, cloud COGS, opex
  ramp, site counts, raise amounts) are constants at the top. Running it
  prints the annual P&L / ARR / cash summary and writes `model_monthly.csv`.
- **`add_slides.py`** — rebuilds the deck from the original
  `AlphaAgent_Pitch_Deck.pptx` (expected in `~/Downloads/`): rewords slide 8
  to site-license pricing, inserts the Financial Projections and Long View
  slides, renumbers the Ask slide, and saves `AlphaAgent_Pitch_Deck_v2.pptx`.
- **`model_monthly.csv`** — month-by-month model output (36 months).

## Usage

```bash
pip install python-pptx
python3 model.py        # recompute projections
python3 add_slides.py   # regenerate deck v2 (update slide numbers manually
                        # in add_slides.py if model assumptions change)
```

## Key assumptions (base case)

- $10K/mo blended site license ($5K entry service line → $15–20K expanded)
- $2K per glasses unit, ~10 units per site, free to the hospital
- $1K/site/mo cloud + support → 90% software gross margin
- 8-month unpaid pilots, paid conversion from month 9; Y3 ramp follows 510(k)
- $500K pre-seed + ~$1.5M seed (month 14) — cashflow-positive in Year 3
