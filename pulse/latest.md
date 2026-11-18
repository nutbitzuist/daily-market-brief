---
date: 2026-11-18
generated_at_utc: 2026-11-18T22:30:45Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-18

Official SET investor-type: Foreign ฿-34M, Individual +฿1,148M, Institution ฿-1,377M, Proprietary +฿264M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign ฿-34M, Individual +฿1,148M, Institution ฿-1,377M, Proprietary +฿264M

```json
{
  "date": "2026-11-18T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 62110766606.63,
  "investors": {
    "institution": {
      "buy_value_thb": 2817600550.18,
      "sell_value_thb": 4195060249.24,
      "net_value_thb": -1377459699.06,
      "percent_buy_value": 4.536412451684723,
      "percent_sell_value": 6.7541595095884706
    },
    "proprietary": {
      "buy_value_thb": 13983127747.41,
      "sell_value_thb": 13719514569.86,
      "net_value_thb": 263613177.54999924,
      "percent_buy_value": 22.513210690137214,
      "percent_sell_value": 22.08878640437762
    },
    "foreign": {
      "buy_value_thb": 29387164541.29,
      "sell_value_thb": 29421413852.18,
      "net_value_thb": -34249310.88999939,
      "percent_buy_value": 47.31412305278659,
      "percent_sell_value": 47.36926536185985
    },
    "individual": {
      "buy_value_thb": 15922873767.75,
      "sell_value_thb": 14774777935.35,
      "net_value_thb": 1148095832.3999996,
      "percent_buy_value": 25.636253805391476,
      "percent_sell_value": 23.787788724174064
    }
  },
  "rolling_5d_net_mb": {
    "foreign": 6236.27936611,
    "individual": -319.70266379000094,
    "institution": -3224.1859623200007,
    "proprietary": -2692.3907400000007
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: KBANK ฿602M, KTB ฿420M, TRUE ฿369M, SCB ฿349M, BDMS ฿331M

```json
{
  "date": "2026-11-18T00:00:00+07:00",
  "top20": [
    {
      "symbol": "KBANK",
      "short_value": 601650200.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 420137540.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 368778740.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 349297650.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 330731325.0,
      "short_volume": null
    },
    {
      "symbol": "CPF",
      "short_value": 320077350.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 315436490.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 303284900.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 256250350.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 243988410.0,
      "short_volume": null
    },
    {
      "symbol": "DELTA",
      "short_value": 233046200.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 199093530.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 194125025.0,
      "short_volume": null
    },
    {
      "symbol": "GULF",
      "short_value": 185851850.0,
      "short_volume": null
    },
    {
      "symbol": "CPN",
      "short_value": 150681350.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 149959100.0,
      "short_volume": null
    },
    {
      "symbol": "BH",
      "short_value": 147221050.0,
      "short_volume": null
    },
    {
      "symbol": "KCE",
      "short_value": 139419100.0,
      "short_volume": null
    },
    {
      "symbol": "WHA",
      "short_value": 122056180.0,
      "short_volume": null
    },
    {
      "symbol": "MINT",
      "short_value": 120113530.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: GULF +฿523M, BH +฿397M, CPALL +฿230M, ADVANC +฿202M, TRUE +฿122M. NVDR net SELL top: CPF ฿-226M, KTB ฿-211M, KBANK ฿-130M, TTB ฿-124M, PTTGC ฿-123M

```json
{
  "date": "2026-11-18",
  "top_buy": [
    {
      "symbol": "GULF",
      "buy_value": 949394950.0,
      "sell_value": 426760311.5,
      "net_value": 522634638.5,
      "total_value": 1376155261.5,
      "percent_of_underlying": 34.4854780149929
    },
    {
      "symbol": "BH",
      "buy_value": 663369450.0,
      "sell_value": 266801100.0,
      "net_value": 396568350.0,
      "total_value": 930170550.0,
      "percent_of_underlying": 16.70989733494514
    },
    {
      "symbol": "CPALL",
      "buy_value": 680948660.0,
      "sell_value": 450800350.0,
      "net_value": 230148310.0,
      "total_value": 1131749010.0,
      "percent_of_underlying": 26.655979519905227
    },
    {
      "symbol": "ADVANC",
      "buy_value": 551554530.0,
      "sell_value": 349918652.0,
      "net_value": 201635878.0,
      "total_value": 901473182.0,
      "percent_of_underlying": 29.55524199248515
    },
    {
      "symbol": "TRUE",
      "buy_value": 1635534757.45,
      "sell_value": 1513364440.0,
      "net_value": 122170317.45000005,
      "total_value": 3148899197.45,
      "percent_of_underlying": 56.5552664268503
    },
    {
      "symbol": "PLANB",
      "buy_value": 135900362.0,
      "sell_value": 25948320.0,
      "net_value": 109952042.0,
      "total_value": 161848682.0,
      "percent_of_underlying": 14.956465156434437
    },
    {
      "symbol": "KCE",
      "buy_value": 374738122.0,
      "sell_value": 265827712.75,
      "net_value": 108910409.25,
      "total_value": 640565834.75,
      "percent_of_underlying": 18.72170316157293
    },
    {
      "symbol": "HANA",
      "buy_value": 355780390.9,
      "sell_value": 253633111.0,
      "net_value": 102147279.89999998,
      "total_value": 609413501.9,
      "percent_of_underlying": 14.112477403016062
    },
    {
      "symbol": "ICHI",
      "buy_value": 113832160.0,
      "sell_value": 18172130.0,
      "net_value": 95660030.0,
      "total_value": 132004290.0,
      "percent_of_underlying": 27.232600799408967
    },
    {
      "symbol": "BGRIM",
      "buy_value": 156205945.0,
      "sell_value": 63640985.0,
      "net_value": 92564960.0,
      "total_value": 219846930.0,
      "percent_of_underlying": 14.604177616816838
    }
  ],
  "top_sell": [
    {
      "symbol": "CPF",
      "buy_value": 115583162.5,
      "sell_value": 342043025.0,
      "net_value": -226459862.5,
      "total_value": 457626187.5,
      "percent_of_underlying": 29.821184208526198
    },
    {
      "symbol": "KTB"
```
