# Equiti-AI — Micro-Equity Intelligence Platform

> **Safe Mode Active** — Data-only analytical platform. No funds are handled, routed, or custodied. All execution occurs via licensed Broker-Dealer portals.

## Mission

Democratize venture capital by giving retail investors institutional-grade deal intelligence for SEC Regulation Crowdfunding (Reg CF) opportunities — starting at $50.

---

## Architecture

```
Stage 1 (Built) │ Intelligence Layer — Alpha Scanner
Stage 2 (Planned)│ Regulatory Shield — Licensed BD Partner Integration
Stage 3 (Planned)│ SPV Engine — Automated Delaware LLC Formation
```

---

## Stage 1: Alpha Scanner

The Intelligence Layer identifies high-potential Reg CF deals using alternative data and traditional financial models, then generates AI-powered Investment Memos.

### Pipeline

```
SEC EDGAR (Reg CF Feed)
        │
        ▼
┌───────────────────────────────────────────────┐
│              Alpha Scanner                     │
│                                               │
│  GitHub Fetcher    ──┐                        │
│  Crunchbase Fetcher──┼──► Composite Scorer    │
│  Hiring Fetcher    ──┤         │              │
│  DCF/NPV Model     ──┘         ▼              │
│                         Investment Memo        │
│                         (Claude claude-opus-4-6)│
└───────────────────────────────────────────────┘
        │
        ▼
   Alpha Score (0–100) + Investment Memo
```

### Data Sources

| Source | Signal | API Key Required |
|--------|--------|-----------------|
| SEC EDGAR | Reg CF Form C filings | No (public) |
| GitHub REST API | Star growth, commit velocity, contributors | No (token recommended) |
| Crunchbase Basic API | Round history, investor quality, funding | Yes |
| Proxycurl (LinkedIn) | Hiring velocity, seniority of new hires | Yes |
| Anthropic Claude | Investment memo generation | Yes |

### Alpha Score Weights

| Signal | Weight | Description |
|--------|--------|-------------|
| DCF Upside | 35% | Implied upside vs. offering valuation |
| GitHub Momentum | 25% | Star growth, commits, contributors |
| Hiring Velocity | 20% | Employee growth, senior hires |
| Deal Quality | 20% | Crunchbase round type, investor count |

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run the demo (no API keys needed)

```bash
python main.py --demo
```

Uses the public `huggingface/transformers` GitHub repo as a demo target.

### 4. Scan a specific company

```bash
python main.py \
  --company "Acme AI" \
  --github-owner acme-ai \
  --github-repo core \
  --valuation 5000000 \
  --arr 800000
```

### 5. Scan the live Reg CF EDGAR feed

```bash
python main.py --feed --days-back 90 --max-deals 10
```

---

## Project Structure

```
equiti-ai/
├── main.py                          # CLI entry point
├── config.py                        # Environment config & constants
├── requirements.txt
├── .env.example
├── scanner/
│   ├── alpha_scanner.py             # Pipeline orchestrator
│   ├── data_fetchers/
│   │   ├── github_fetcher.py        # GitHub momentum signals
│   │   ├── regcf_fetcher.py         # SEC EDGAR Form C filings
│   │   ├── crunchbase_fetcher.py    # Deal-flow & funding data
│   │   └── hiring_fetcher.py        # LinkedIn hiring velocity
│   ├── models/
│   │   ├── dcf_model.py             # DCF/NPV financial model
│   │   ├── scoring_model.py         # Composite Alpha Score
│   │   └── memo_generator.py        # Claude-powered memo writer
│   └── output/
│       └── memo_formatter.py        # Rich terminal display
└── tests/
    ├── test_dcf_model.py            # 19 DCF model tests
    └── test_scoring_model.py        # 14 scoring model tests
```

---

## Compliance

- **Reg CF 2026**: Max raise $5M per issuer per 12 months
- **Non-accredited investor cap**: 10% of annual income or net worth
- **Safe Mode**: Platform never handles, routes, or custodies funds
- **Data-only output**: Not investment advice; not a registered broker-dealer

---

## Roadmap

- **Stage 2**: Licensed Broker-Dealer UI/UX integration (redirect to FINRA-registered portals)
- **Stage 3**: Automated SPV formation (Delaware LLC spin-up, EIN procurement, cap table management)
