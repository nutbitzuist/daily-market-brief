---
date: 2026-11-23
generated_at_utc: 2026-11-23T22:31:14Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-23

Official SET investor-type: Foreign +฿682M, Individual +฿737M, Institution ฿-1,197M, Proprietary ฿-222M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign +฿682M, Individual +฿737M, Institution ฿-1,197M, Proprietary ฿-222M

```json
{
  "date": "2026-11-23T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 56406017833.34,
  "investors": {
    "institution": {
      "buy_value_thb": 2695081615.18,
      "sell_value_thb": 3892206235.99,
      "net_value_thb": -1197124620.81,
      "percent_buy_value": 4.778003693051016,
      "percent_sell_value": 6.900338626084374
    },
    "proprietary": {
      "buy_value_thb": 11629220477.89,
      "sell_value_thb": 11851387604.86,
      "net_value_thb": -222167126.97000122,
      "percent_buy_value": 20.616985429197054,
      "percent_sell_value": 21.01085674914456
    },
    "foreign": {
      "buy_value_thb": 25868245256.46,
      "sell_value_thb": 25185851863.21,
      "net_value_thb": 682393393.25,
      "percent_buy_value": 45.86078977050214,
      "percent_sell_value": 44.65100148999236
    },
    "individual": {
      "buy_value_thb": 16213470483.81,
      "sell_value_thb": 15476572129.28,
      "net_value_thb": 736898354.5299988,
      "percent_buy_value": 28.744221107249796,
      "percent_sell_value": 27.43780313477871
    }
  },
  "rolling_5d_net_mb": {
    "foreign": -5210.072899950001,
    "individual": 11014.42311811,
    "institution": -3174.86960248,
    "proprietary": -2629.4806156800023
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: GULF ฿1197M, DELTA ฿677M, KBANK ฿510M, KTB ฿372M, PTT ฿275M

```json
{
  "date": "2026-11-23T00:00:00+07:00",
  "top20": [
    {
      "symbol": "GULF",
      "short_value": 1197282500.0,
      "short_volume": null
    },
    {
      "symbol": "DELTA",
      "short_value": 676890600.0,
      "short_volume": null
    },
    {
      "symbol": "KBANK",
      "short_value": 509691600.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 372021820.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 274787760.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 265582150.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 233681550.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 229448500.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 210367590.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 200760020.0,
      "short_volume": null
    },
    {
      "symbol": "CPN",
      "short_value": 182750450.0,
      "short_volume": null
    },
    {
      "symbol": "BH",
      "short_value": 172169600.0,
      "short_volume": null
    },
    {
      "symbol": "AMATA",
      "short_value": 171867320.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 170011520.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 160483970.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 160073975.0,
      "short_volume": null
    },
    {
      "symbol": "WHA",
      "short_value": 146525530.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 137836900.0,
      "short_volume": null
    },
    {
      "symbol": "MINT",
      "short_value": 122956955.0,
      "short_volume": null
    },
    {
      "symbol": "SCC",
      "short_value": 106846600.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: BDMS +฿324M, BH +฿172M, DELTA +฿145M, BCH +฿128M, HANA +฿127M. NVDR net SELL top: GULF ฿-1258M, KTB ฿-184M, PTTEP ฿-162M, KBANK ฿-149M, ADVANC ฿-116M

```json
{
  "date": "2026-11-23",
  "top_buy": [
    {
      "symbol": "BDMS",
      "buy_value": 744140142.16,
      "sell_value": 419953352.75,
      "net_value": 324186789.40999997,
      "total_value": 1164093494.9099998,
      "percent_of_underlying": 31.999170972456835
    },
    {
      "symbol": "BH",
      "buy_value": 329183600.0,
      "sell_value": 156990110.0,
      "net_value": 172193490.0,
      "total_value": 486173710.0,
      "percent_of_underlying": 18.628908133295276
    },
    {
      "symbol": "DELTA",
      "buy_value": 1128400624.0,
      "sell_value": 983676542.0,
      "net_value": 144724082.0,
      "total_value": 2112077166.0,
      "percent_of_underlying": 29.00661561409404
    },
    {
      "symbol": "BCH",
      "buy_value": 141913890.0,
      "sell_value": 13755180.0,
      "net_value": 128158710.0,
      "total_value": 155669070.0,
      "percent_of_underlying": 29.756400635284198
    },
    {
      "symbol": "HANA",
      "buy_value": 355617670.0,
      "sell_value": 228322280.0,
      "net_value": 127295390.0,
      "total_value": 583939950.0,
      "percent_of_underlying": 13.278308363791197
    },
    {
      "symbol": "CPALL",
      "buy_value": 720829860.0,
      "sell_value": 600866690.9200001,
      "net_value": 119963169.07999992,
      "total_value": 1321696550.92,
      "percent_of_underlying": 30.335832460302544
    },
    {
      "symbol": "BBL",
      "buy_value": 425461052.0,
      "sell_value": 306705857.0,
      "net_value": 118755195.0,
      "total_value": 732166909.0,
      "percent_of_underlying": 23.764281348418272
    },
    {
      "symbol": "TRUE",
      "buy_value": 566770700.0,
      "sell_value": 449444575.0,
      "net_value": 117326125.0,
      "total_value": 1016215275.0,
      "percent_of_underlying": 53.07049729075259
    },
    {
      "symbol": "IVL",
      "buy_value": 213557152.3,
      "sell_value": 97250985.0,
      "net_value": 116306167.30000001,
      "total_value": 310808137.3,
      "percent_of_underlying": 27.29417720323736
    },
    {
      "symbol": "CPAXT",
      "buy_value": 95266505.0,
      "sell_value": 10385225.0,
      "net_value": 84881280.0,
      "total_value": 105651730.0,
      "percent_of_underlying": 26.24977133040814
    }
  ],
  "top_sell": [
    {
      "symbol": "GULF",
      "buy_value": 600099500.0,
      "sell_value": 1857871392.5,
      "net_value": -1257771892.5,
      "total_value": 2457970892.5,
      "percent_of_underlying": 33.88291141966233
    },
    {
  
```
