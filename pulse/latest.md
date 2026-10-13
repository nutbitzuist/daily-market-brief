---
date: 2026-10-13
generated_at_utc: 2026-10-13T17:40:37Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-10-13

Official SET investor-type: Foreign +฿267M, Individual ฿-1,125M, Institution +฿727M, Proprietary +฿131M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign +฿267M, Individual ฿-1,125M, Institution +฿727M, Proprietary +฿131M

```json
{
  "date": "2026-10-12T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 55934028735.39,
  "investors": {
    "institution": {
      "buy_value_thb": 4125432538.98,
      "sell_value_thb": 3398173969.97,
      "net_value_thb": 727258569.0100002,
      "percent_buy_value": 7.375532627010289,
      "percent_sell_value": 6.075324890409588
    },
    "proprietary": {
      "buy_value_thb": 3610507652.22,
      "sell_value_thb": 3479674950.82,
      "net_value_thb": 130832701.39999962,
      "percent_buy_value": 6.454939388150307,
      "percent_sell_value": 6.2210340100504435
    },
    "foreign": {
      "buy_value_thb": 32713922992.81,
      "sell_value_thb": 32447025668.96,
      "net_value_thb": 266897323.8500023,
      "percent_buy_value": 58.486620278277194,
      "percent_sell_value": 58.009455786671154
    },
    "individual": {
      "buy_value_thb": 15484165551.38,
      "sell_value_thb": 16609154145.64,
      "net_value_thb": -1124988594.2600002,
      "percent_buy_value": 27.68290770656221,
      "percent_sell_value": 29.694185312868814
    }
  },
  "rolling_5d_net_mb": {
    "foreign": -6980.567400060001,
    "individual": 5551.4379268600005,
    "institution": 2476.07559366,
    "proprietary": -1046.94612046
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: DELTA ฿377M, SCB ฿293M, AOT ฿193M, PTTEP ฿139M, KTB ฿130M

```json
{
  "date": "2026-10-12T00:00:00+07:00",
  "top20": [
    {
      "symbol": "DELTA",
      "short_value": 376523100.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 293465300.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 192922325.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 139010300.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 129750650.0,
      "short_volume": null
    },
    {
      "symbol": "GULF",
      "short_value": 99086250.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 85572640.0,
      "short_volume": null
    },
    {
      "symbol": "TOP",
      "short_value": 76421575.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 59954400.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 59771250.0,
      "short_volume": null
    },
    {
      "symbol": "BH",
      "short_value": 58402300.0,
      "short_volume": null
    },
    {
      "symbol": "MINT",
      "short_value": 58267920.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 55783500.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 49166000.0,
      "short_volume": null
    },
    {
      "symbol": "MTC",
      "short_value": 47782025.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 47751930.0,
      "short_volume": null
    },
    {
      "symbol": "KBANK",
      "short_value": 45929900.0,
      "short_volume": null
    },
    {
      "symbol": "HMPRO",
      "short_value": 44149760.0,
      "short_volume": null
    },
    {
      "symbol": "KCE",
      "short_value": 40860225.0,
      "short_volume": null
    },
    {
      "symbol": "SPRC",
      "short_value": 36005300.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: SCC +฿1161M, KBANK +฿788M, PTTEP +฿320M, ADVANC +฿266M, AOT +฿224M. NVDR net SELL top: TRUE ฿-372M, SCB ฿-217M, TOP ฿-189M, PTT ฿-148M, CCET ฿-148M

```json
{
  "date": "2026-10-13",
  "top_buy": [
    {
      "symbol": "SCC",
      "buy_value": 1737539600.0,
      "sell_value": 576619800.0,
      "net_value": 1160919800.0,
      "total_value": 2314159400.0,
      "percent_of_underlying": 30.361028643221044
    },
    {
      "symbol": "KBANK",
      "buy_value": 1398397300.0,
      "sell_value": 609913230.0,
      "net_value": 788484070.0,
      "total_value": 2008310530.0,
      "percent_of_underlying": 29.879444404310647
    },
    {
      "symbol": "PTTEP",
      "buy_value": 945422900.0,
      "sell_value": 625083100.0,
      "net_value": 320339800.0,
      "total_value": 1570506000.0,
      "percent_of_underlying": 33.80653827774446
    },
    {
      "symbol": "ADVANC",
      "buy_value": 537343437.0,
      "sell_value": 271688920.0,
      "net_value": 265654517.0,
      "total_value": 809032357.0,
      "percent_of_underlying": 27.010634934354165
    },
    {
      "symbol": "AOT",
      "buy_value": 542056250.0,
      "sell_value": 318357875.0,
      "net_value": 223698375.0,
      "total_value": 860414125.0,
      "percent_of_underlying": 27.185836071193794
    },
    {
      "symbol": "KTB",
      "buy_value": 922370375.0,
      "sell_value": 772734500.0,
      "net_value": 149635875.0,
      "total_value": 1695104875.0,
      "percent_of_underlying": 33.70044148237672
    },
    {
      "symbol": "CPALL",
      "buy_value": 309166743.0,
      "sell_value": 181846009.0,
      "net_value": 127320734.0,
      "total_value": 491012752.0,
      "percent_of_underlying": 28.04438651978933
    },
    {
      "symbol": "KKP",
      "buy_value": 191141150.0,
      "sell_value": 93785150.0,
      "net_value": 97356000.0,
      "total_value": 284926300.0,
      "percent_of_underlying": 32.44038432411635
    },
    {
      "symbol": "BDMS",
      "buy_value": 343015468.2,
      "sell_value": 254547540.0,
      "net_value": 88467928.19999999,
      "total_value": 597563008.2,
      "percent_of_underlying": 32.504896625936254
    },
    {
      "symbol": "BCP",
      "buy_value": 265920525.0,
      "sell_value": 203037400.0,
      "net_value": 62883125.0,
      "total_value": 468957925.0,
      "percent_of_underlying": 34.19303326689931
    }
  ],
  "top_sell": [
    {
      "symbol": "TRUE",
      "buy_value": 899029851.0,
      "sell_value": 1270950315.0,
      "net_value": -371920464.0,
      "total_value": 2169980166.0,
      "percent_of_underlying": 63.831390756571665
    },
    {
      "symbol": "SCB",
    
```
