---
date: 2026-11-19
generated_at_utc: 2026-11-19T22:30:32Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-19

Official SET investor-type: Foreign ฿-2,495M, Individual +฿3,031M, Institution ฿-232M, Proprietary ฿-305M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign ฿-2,495M, Individual +฿3,031M, Institution ฿-232M, Proprietary ฿-305M

```json
{
  "date": "2026-11-19T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 64920167627.74,
  "investors": {
    "institution": {
      "buy_value_thb": 3983301925.21,
      "sell_value_thb": 4215018389.64,
      "net_value_thb": -231716464.42999983,
      "percent_buy_value": 6.1356926064189015,
      "percent_sell_value": 6.492617846906095
    },
    "proprietary": {
      "buy_value_thb": 13860486844.65,
      "sell_value_thb": 14165041368.56,
      "net_value_thb": -304554523.90999985,
      "percent_buy_value": 21.350047837411154,
      "percent_sell_value": 21.8191694294199
    },
    "foreign": {
      "buy_value_thb": 27023141855.05,
      "sell_value_thb": 29518367279.64,
      "net_value_thb": -2495225424.59,
      "percent_buy_value": 41.62518804634629,
      "percent_sell_value": 45.46871697698294
    },
    "individual": {
      "buy_value_thb": 20053237002.83,
      "sell_value_thb": 17021740589.9,
      "net_value_thb": 3031496412.930002,
      "percent_buy_value": 30.889071509823665,
      "percent_sell_value": 26.219495746691067
    }
  },
  "rolling_5d_net_mb": {
    "foreign": 2029.9375033300018,
    "individual": 2850.3463475200024,
    "institution": -2391.5206414300005,
    "proprietary": -2488.763209420001
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: BH ฿957M, KBANK ฿662M, PTT ฿526M, KTB ฿453M, ADVANC ฿411M

```json
{
  "date": "2026-11-19T00:00:00+07:00",
  "top20": [
    {
      "symbol": "BH",
      "short_value": 956805750.0,
      "short_volume": null
    },
    {
      "symbol": "KBANK",
      "short_value": 661532400.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 525927790.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 452891460.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 411348100.0,
      "short_volume": null
    },
    {
      "symbol": "DELTA",
      "short_value": 398965450.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 317870675.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 310197500.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 285777100.0,
      "short_volume": null
    },
    {
      "symbol": "GULF",
      "short_value": 265292750.0,
      "short_volume": null
    },
    {
      "symbol": "SCC",
      "short_value": 241388000.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 210056600.0,
      "short_volume": null
    },
    {
      "symbol": "CPF",
      "short_value": 200052200.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 194392225.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 166828420.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 123162300.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 120120670.0,
      "short_volume": null
    },
    {
      "symbol": "TOP",
      "short_value": 116143750.0,
      "short_volume": null
    },
    {
      "symbol": "KCE",
      "short_value": 109710550.0,
      "short_volume": null
    },
    {
      "symbol": "TISCO",
      "short_value": 97452000.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: BGRIM +฿226M, CPALL +฿209M, TRUE +฿149M, KTC +฿120M, CK +฿107M. NVDR net SELL top: BH ฿-767M, GULF ฿-460M, KTB ฿-364M, KCE ฿-305M, HANA ฿-239M

```json
{
  "date": "2026-11-19",
  "top_buy": [
    {
      "symbol": "BGRIM",
      "buy_value": 325137555.0,
      "sell_value": 99288355.0,
      "net_value": 225849200.0,
      "total_value": 424425910.0,
      "percent_of_underlying": 15.515987597684548
    },
    {
      "symbol": "CPALL",
      "buy_value": 686242120.0,
      "sell_value": 477705650.0,
      "net_value": 208536470.0,
      "total_value": 1163947770.0,
      "percent_of_underlying": 36.28276245048752
    },
    {
      "symbol": "TRUE",
      "buy_value": 1150321491.25,
      "sell_value": 1000975910.85,
      "net_value": 149345580.39999998,
      "total_value": 2151297402.1,
      "percent_of_underlying": 50.69212842086146
    },
    {
      "symbol": "KTC",
      "buy_value": 196042630.0,
      "sell_value": 76283920.0,
      "net_value": 119758710.0,
      "total_value": 272326550.0,
      "percent_of_underlying": 23.67730042593531
    },
    {
      "symbol": "CK",
      "buy_value": 115009805.0,
      "sell_value": 7974660.0,
      "net_value": 107035145.0,
      "total_value": 122984465.0,
      "percent_of_underlying": 29.055091839913672
    },
    {
      "symbol": "GPSC",
      "buy_value": 196739975.0,
      "sell_value": 103727100.0,
      "net_value": 93012875.0,
      "total_value": 300467075.0,
      "percent_of_underlying": 20.205961959626258
    },
    {
      "symbol": "CPAXT",
      "buy_value": 90915490.0,
      "sell_value": 9035150.0,
      "net_value": 81880340.0,
      "total_value": 99950640.0,
      "percent_of_underlying": 22.807315764672712
    },
    {
      "symbol": "SCGP",
      "buy_value": 157050435.0,
      "sell_value": 80129780.0,
      "net_value": 76920655.0,
      "total_value": 237180215.0,
      "percent_of_underlying": 30.476203648403
    },
    {
      "symbol": "GUNKUL",
      "buy_value": 86055904.0,
      "sell_value": 14110558.0,
      "net_value": 71945346.0,
      "total_value": 100166462.0,
      "percent_of_underlying": 19.3059338440025
    },
    {
      "symbol": "EGCO",
      "buy_value": 100077850.0,
      "sell_value": 45248800.0,
      "net_value": 54829050.0,
      "total_value": 145326650.0,
      "percent_of_underlying": 33.3801031522941
    }
  ],
  "top_sell": [
    {
      "symbol": "BH",
      "buy_value": 401493550.0,
      "sell_value": 1168782750.0,
      "net_value": -767289200.0,
      "total_value": 1570276300.0,
      "percent_of_underlying": 18.144227759436603
    },
    {
      "symbol": "GULF",
      "buy_value": 388
```
