---
date: 2026-11-17
generated_at_utc: 2026-11-17T22:30:43Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-17

Official SET investor-type: Foreign ฿-997M, Individual +฿3,880M, Institution ฿-1,083M, Proprietary ฿-1,800M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign ฿-997M, Individual +฿3,880M, Institution ฿-1,083M, Proprietary ฿-1,800M

```json
{
  "date": "2026-11-17T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 86593621562.86,
  "investors": {
    "institution": {
      "buy_value_thb": 4212939544.27,
      "sell_value_thb": 5296336505.59,
      "net_value_thb": -1083396961.3200002,
      "percent_buy_value": 4.865184603939616,
      "percent_sell_value": 6.116312506626468
    },
    "proprietary": {
      "buy_value_thb": 18703185533.24,
      "sell_value_thb": 20502875803.65,
      "net_value_thb": -1799690270.4099998,
      "percent_buy_value": 21.598802770551632,
      "percent_sell_value": 23.6771201314944
    },
    "foreign": {
      "buy_value_thb": 38887794280.42,
      "sell_value_thb": 39884581523.24,
      "net_value_thb": -996787242.8199997,
      "percent_buy_value": 44.90838190915781,
      "percent_sell_value": 46.05949122278828
    },
    "individual": {
      "buy_value_thb": 24789702204.93,
      "sell_value_thb": 20909827730.38,
      "net_value_thb": 3879874474.549999,
      "percent_buy_value": 28.62763071635094,
      "percent_sell_value": 24.147076139090853
    }
  },
  "rolling_5d_net_mb": {
    "foreign": 5557.877415199997,
    "individual": -1656.8716980200004,
    "institution": -451.75081820000077,
    "proprietary": -3449.2548989800007
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: PTT ฿742M, DELTA ฿684M, GULF ฿681M, KTB ฿582M, KBANK ฿566M

```json
{
  "date": "2026-11-17T00:00:00+07:00",
  "top20": [
    {
      "symbol": "PTT",
      "short_value": 741569340.0,
      "short_volume": null
    },
    {
      "symbol": "DELTA",
      "short_value": 683508850.0,
      "short_volume": null
    },
    {
      "symbol": "GULF",
      "short_value": 680869750.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 582001170.0,
      "short_volume": null
    },
    {
      "symbol": "KBANK",
      "short_value": 565813200.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 420680300.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 364202950.0,
      "short_volume": null
    },
    {
      "symbol": "WHA",
      "short_value": 354964428.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 283305150.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 249603080.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 231696240.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 201039775.0,
      "short_volume": null
    },
    {
      "symbol": "SCC",
      "short_value": 168219100.0,
      "short_volume": null
    },
    {
      "symbol": "KCE",
      "short_value": 165399475.0,
      "short_volume": null
    },
    {
      "symbol": "TOP",
      "short_value": 165050000.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 152297310.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 151611850.0,
      "short_volume": null
    },
    {
      "symbol": "CPF",
      "short_value": 113831685.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 111300825.0,
      "short_volume": null
    },
    {
      "symbol": "IVL",
      "short_value": 110417305.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: BDMS +฿1081M, CPALL +฿631M, KCE +฿519M, ADVANC +฿426M, BH +฿308M. NVDR net SELL top: PTT ฿-1059M, KBANK ฿-505M, WHA ฿-409M, PTTEP ฿-406M, GULF ฿-308M

```json
{
  "date": "2026-11-17",
  "top_buy": [
    {
      "symbol": "BDMS",
      "buy_value": 1791223970.0,
      "sell_value": 709845330.0,
      "net_value": 1081378640.0,
      "total_value": 2501069300.0,
      "percent_of_underlying": 26.058295371954085
    },
    {
      "symbol": "CPALL",
      "buy_value": 1688485200.0,
      "sell_value": 1057743974.52,
      "net_value": 630741225.48,
      "total_value": 2746229174.52,
      "percent_of_underlying": 29.862290911962344
    },
    {
      "symbol": "KCE",
      "buy_value": 658952053.5,
      "sell_value": 140254100.0,
      "net_value": 518697953.5,
      "total_value": 799206153.5,
      "percent_of_underlying": 17.110481587827536
    },
    {
      "symbol": "ADVANC",
      "buy_value": 1061450020.0,
      "sell_value": 635006667.0,
      "net_value": 426443353.0,
      "total_value": 1696456687.0,
      "percent_of_underlying": 28.075632200372095
    },
    {
      "symbol": "BH",
      "buy_value": 513433950.0,
      "sell_value": 205645650.0,
      "net_value": 307788300.0,
      "total_value": 719079600.0,
      "percent_of_underlying": 32.86347330410894
    },
    {
      "symbol": "TRUE",
      "buy_value": 1169796825.0,
      "sell_value": 932374965.85,
      "net_value": 237421859.14999998,
      "total_value": 2102171790.85,
      "percent_of_underlying": 55.301222563571024
    },
    {
      "symbol": "SCB",
      "buy_value": 763772200.0,
      "sell_value": 561465592.0,
      "net_value": 202306608.0,
      "total_value": 1325237792.0,
      "percent_of_underlying": 31.709863873412516
    },
    {
      "symbol": "DELTA",
      "buy_value": 1377012872.0,
      "sell_value": 1248385478.5,
      "net_value": 128627393.5,
      "total_value": 2625398350.5,
      "percent_of_underlying": 32.7169654162919
    },
    {
      "symbol": "KKP",
      "buy_value": 295627350.0,
      "sell_value": 201165300.0,
      "net_value": 94462050.0,
      "total_value": 496792650.0,
      "percent_of_underlying": 38.64228211739074
    },
    {
      "symbol": "CHG",
      "buy_value": 94776337.0,
      "sell_value": 11044554.0,
      "net_value": 83731783.0,
      "total_value": 105820891.0,
      "percent_of_underlying": 21.11145735555905
    }
  ],
  "top_sell": [
    {
      "symbol": "PTT",
      "buy_value": 2014998767.0,
      "sell_value": 3074049750.0,
      "net_value": -1059050983.0,
      "total_value": 5089048517.0,
      "percent_of_underlying": 34.018872970076515
    },
    {
      "symbol": 
```
