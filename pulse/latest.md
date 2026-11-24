---
date: 2026-11-24
generated_at_utc: 2026-11-24T22:31:22Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-24

Official SET investor-type: Foreign ฿-5,270M, Individual +฿3,192M, Institution +฿1,340M, Proprietary +฿737M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign ฿-5,270M, Individual +฿3,192M, Institution +฿1,340M, Proprietary +฿737M

```json
{
  "date": "2026-11-24T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 71163720046.54,
  "investors": {
    "institution": {
      "buy_value_thb": 5167441692.49,
      "sell_value_thb": 3827164811.11,
      "net_value_thb": 1340276881.3799996,
      "percent_buy_value": 7.261342843109623,
      "percent_sell_value": 5.377971821325659
    },
    "proprietary": {
      "buy_value_thb": 15903475127.56,
      "sell_value_thb": 15166154458.97,
      "net_value_thb": 737320668.5900002,
      "percent_buy_value": 22.347728754426228,
      "percent_sell_value": 21.31163807773338
    },
    "foreign": {
      "buy_value_thb": 27266020799.5,
      "sell_value_thb": 32535692283.68,
      "net_value_thb": -5269671484.18,
      "percent_buy_value": 38.31449618101532,
      "percent_sell_value": 45.71949339129848
    },
    "individual": {
      "buy_value_thb": 22826782426.99,
      "sell_value_thb": 19634708492.78,
      "net_value_thb": 3192073934.210003,
      "percent_buy_value": 32.07643222144884,
      "percent_sell_value": 27.590896709642497
    }
  },
  "rolling_5d_net_mb": {
    "foreign": -9482.957141310002,
    "individual": 10326.622577770004,
    "institution": -751.1957597800002,
    "proprietary": -92.46967668000221
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: DELTA ฿1355M, AOT ฿1127M, PTTEP ฿1017M, PTT ฿606M, KBANK ฿462M

```json
{
  "date": "2026-11-24T00:00:00+07:00",
  "top20": [
    {
      "symbol": "DELTA",
      "short_value": 1355139750.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 1126946850.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 1016584800.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 605566240.0,
      "short_volume": null
    },
    {
      "symbol": "KBANK",
      "short_value": 461617400.0,
      "short_volume": null
    },
    {
      "symbol": "GULF",
      "short_value": 432816300.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 389578300.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 364043100.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 336625060.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 252563585.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 246012115.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 237225725.0,
      "short_volume": null
    },
    {
      "symbol": "BH",
      "short_value": 215644600.0,
      "short_volume": null
    },
    {
      "symbol": "TOP",
      "short_value": 206031125.0,
      "short_volume": null
    },
    {
      "symbol": "SCC",
      "short_value": 158793400.0,
      "short_volume": null
    },
    {
      "symbol": "KCE",
      "short_value": 119562925.0,
      "short_volume": null
    },
    {
      "symbol": "MINT",
      "short_value": 111054025.0,
      "short_volume": null
    },
    {
      "symbol": "TIDLOR",
      "short_value": 108745955.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 103344350.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 95919780.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: SCB +฿434M, KKP +฿320M, TRUE +฿278M, BBL +฿247M, KBANK +฿146M. NVDR net SELL top: AOT ฿-1174M, PTTEP ฿-955M, DELTA ฿-732M, PTT ฿-399M, HANA ฿-303M

```json
{
  "date": "2026-11-24",
  "top_buy": [
    {
      "symbol": "SCB",
      "buy_value": 904994363.0,
      "sell_value": 471382977.0,
      "net_value": 433611386.0,
      "total_value": 1376377340.0,
      "percent_of_underlying": 34.341102869886136
    },
    {
      "symbol": "KKP",
      "buy_value": 578304050.0,
      "sell_value": 258091150.0,
      "net_value": 320212900.0,
      "total_value": 836395200.0,
      "percent_of_underlying": 41.697423117216644
    },
    {
      "symbol": "TRUE",
      "buy_value": 993521585.0,
      "sell_value": 715953330.0,
      "net_value": 277568255.0,
      "total_value": 1709474915.0,
      "percent_of_underlying": 55.832220685033526
    },
    {
      "symbol": "BBL",
      "buy_value": 406777345.0,
      "sell_value": 159548107.5,
      "net_value": 247229237.5,
      "total_value": 566325452.5,
      "percent_of_underlying": 32.10741520214053
    },
    {
      "symbol": "KBANK",
      "buy_value": 1078459000.0,
      "sell_value": 931970800.0,
      "net_value": 146488200.0,
      "total_value": 2010429800.0,
      "percent_of_underlying": 26.13829193324846
    },
    {
      "symbol": "IVL",
      "buy_value": 269903297.0,
      "sell_value": 125522105.0,
      "net_value": 144381192.0,
      "total_value": 395425402.0,
      "percent_of_underlying": 26.761434019931016
    },
    {
      "symbol": "THAI",
      "buy_value": 196364220.0,
      "sell_value": 75756204.0,
      "net_value": 120608016.0,
      "total_value": 272120424.0,
      "percent_of_underlying": 18.060756783941972
    },
    {
      "symbol": "KTB",
      "buy_value": 758460900.0,
      "sell_value": 661748136.8,
      "net_value": 96712763.20000005,
      "total_value": 1420209036.8,
      "percent_of_underlying": 37.66100630822206
    },
    {
      "symbol": "BH",
      "buy_value": 289984900.0,
      "sell_value": 199822978.5,
      "net_value": 90161921.5,
      "total_value": 489807878.5,
      "percent_of_underlying": 30.38166449494293
    },
    {
      "symbol": "CRC",
      "buy_value": 122600450.0,
      "sell_value": 44265230.0,
      "net_value": 78335220.0,
      "total_value": 166865680.0,
      "percent_of_underlying": 30.630841475365692
    }
  ],
  "top_sell": [
    {
      "symbol": "AOT",
      "buy_value": 509766075.0,
      "sell_value": 1683922450.0,
      "net_value": -1174156375.0,
      "total_value": 2193688525.0,
      "percent_of_underlying": 27.527826376136908
    },
    {
      "symbol": "PTTEP",
      "buy_
```
