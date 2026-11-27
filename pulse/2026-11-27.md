---
date: 2026-11-27
generated_at_utc: 2026-11-27T22:30:58Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-27

Official SET investor-type: Foreign ฿-39M, Individual ฿-1,030M, Institution +฿975M, Proprietary +฿94M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign ฿-39M, Individual ฿-1,030M, Institution +฿975M, Proprietary +฿94M

```json
{
  "date": "2026-11-27T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 52376837597.66,
  "investors": {
    "institution": {
      "buy_value_thb": 4065543968.83,
      "sell_value_thb": 3090068312.94,
      "net_value_thb": 975475655.8899999,
      "percent_buy_value": 7.762102783027956,
      "percent_sell_value": 5.899684774168291
    },
    "proprietary": {
      "buy_value_thb": 11329446837.36,
      "sell_value_thb": 11235795172.7,
      "net_value_thb": 93651664.65999985,
      "percent_buy_value": 21.630643156405753,
      "percent_sell_value": 21.45183956887457
    },
    "foreign": {
      "buy_value_thb": 23265280959.81,
      "sell_value_thb": 23303993015.89,
      "net_value_thb": -38712056.07999802,
      "percent_buy_value": 44.419025712330146,
      "percent_sell_value": 44.49293635271163
    },
    "individual": {
      "buy_value_thb": 13716565831.66,
      "sell_value_thb": 14746981096.13,
      "net_value_thb": -1030415264.4699993,
      "percent_buy_value": 26.188228348236137,
      "percent_sell_value": 28.155539304245504
    }
  },
  "rolling_5d_net_mb": {
    "foreign": -8388.648038239999,
    "individual": 12256.500440070002,
    "institution": -4556.03157465,
    "proprietary": 688.1791728199997
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: DELTA ฿687M, KBANK ฿663M, GULF ฿500M, KTB ฿399M, PTT ฿301M

```json
{
  "date": "2026-11-27T00:00:00+07:00",
  "top20": [
    {
      "symbol": "DELTA",
      "short_value": 687036000.0,
      "short_volume": null
    },
    {
      "symbol": "KBANK",
      "short_value": 663281000.0,
      "short_volume": null
    },
    {
      "symbol": "GULF",
      "short_value": 499948625.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 398998960.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 301219170.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 278068700.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 255403810.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 253560010.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 239957650.0,
      "short_volume": null
    },
    {
      "symbol": "TOP",
      "short_value": 213662450.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 192650480.0,
      "short_volume": null
    },
    {
      "symbol": "BH",
      "short_value": 183512000.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 178087850.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 157683295.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 148944300.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 124018000.0,
      "short_volume": null
    },
    {
      "symbol": "TISCO",
      "short_value": 123884800.0,
      "short_volume": null
    },
    {
      "symbol": "KCE",
      "short_value": 114870650.0,
      "short_volume": null
    },
    {
      "symbol": "SCC",
      "short_value": 107322200.0,
      "short_volume": null
    },
    {
      "symbol": "MINT",
      "short_value": 107319045.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: KKP +฿334M, KTB +฿234M, AOT +฿149M, ADVANC +฿114M, CPAXT +฿94M. NVDR net SELL top: KBANK ฿-475M, TOP ฿-308M, SCB ฿-251M, KCE ฿-162M, PTTGC ฿-132M

```json
{
  "date": "2026-11-27",
  "top_buy": [
    {
      "symbol": "KKP",
      "buy_value": 574833200.0,
      "sell_value": 240576700.0,
      "net_value": 334256500.0,
      "total_value": 815409900.0,
      "percent_of_underlying": 29.83341487914487
    },
    {
      "symbol": "KTB",
      "buy_value": 691779406.2,
      "sell_value": 457337790.0,
      "net_value": 234441616.20000005,
      "total_value": 1149117196.2,
      "percent_of_underlying": 31.80331503593052
    },
    {
      "symbol": "AOT",
      "buy_value": 576323535.25,
      "sell_value": 427618600.0,
      "net_value": 148704935.25,
      "total_value": 1003942135.25,
      "percent_of_underlying": 29.012684861909264
    },
    {
      "symbol": "ADVANC",
      "buy_value": 328062793.0,
      "sell_value": 213701800.0,
      "net_value": 114360993.0,
      "total_value": 541764593.0,
      "percent_of_underlying": 32.7650818462701
    },
    {
      "symbol": "CPAXT",
      "buy_value": 134538832.0,
      "sell_value": 40911720.0,
      "net_value": 93627112.0,
      "total_value": 175450552.0,
      "percent_of_underlying": 19.103392567682885
    },
    {
      "symbol": "PTT",
      "buy_value": 520969314.4,
      "sell_value": 436110980.0,
      "net_value": 84858334.39999998,
      "total_value": 957080294.4,
      "percent_of_underlying": 30.041386853474055
    },
    {
      "symbol": "LH",
      "buy_value": 102169696.0,
      "sell_value": 54613878.0,
      "net_value": 47555818.0,
      "total_value": 156783574.0,
      "percent_of_underlying": 27.4945325159201
    },
    {
      "symbol": "CRC",
      "buy_value": 95958090.0,
      "sell_value": 50333020.0,
      "net_value": 45625070.0,
      "total_value": 146291110.0,
      "percent_of_underlying": 20.3447258511209
    },
    {
      "symbol": "HMPRO",
      "buy_value": 74719376.0,
      "sell_value": 32665528.0,
      "net_value": 42053848.0,
      "total_value": 107384904.0,
      "percent_of_underlying": 30.697188938672813
    },
    {
      "symbol": "BEM",
      "buy_value": 81911324.0,
      "sell_value": 43024961.4,
      "net_value": 38886362.6,
      "total_value": 124936285.4,
      "percent_of_underlying": 22.876574254949222
    }
  ],
  "top_sell": [
    {
      "symbol": "KBANK",
      "buy_value": 899848200.0,
      "sell_value": 1375131901.0,
      "net_value": -475283701.0,
      "total_value": 2274980101.0,
      "percent_of_underlying": 39.01727389814326
    },
    {
      "symbol": "TOP",
      "buy_value
```
