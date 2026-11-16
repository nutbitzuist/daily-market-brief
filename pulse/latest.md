---
date: 2026-11-16
generated_at_utc: 2026-11-16T22:31:02Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-16

Official SET investor-type: Foreign +฿1,200M, Individual ฿-728M, Institution ฿-81M, Proprietary ฿-391M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign +฿1,200M, Individual ฿-728M, Institution ฿-81M, Proprietary ฿-391M

```json
{
  "date": "2026-11-16T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 65271792032.05,
  "investors": {
    "institution": {
      "buy_value_thb": 3353969414.54,
      "sell_value_thb": 3435163210.26,
      "net_value_thb": -81193795.72000027,
      "percent_buy_value": 5.138466878453592,
      "percent_sell_value": 5.262860269828739
    },
    "proprietary": {
      "buy_value_thb": 14369357163.14,
      "sell_value_thb": 14760151536.34,
      "net_value_thb": -390794373.20000076,
      "percent_buy_value": 22.014650917021406,
      "percent_sell_value": 22.61336953808839
    },
    "foreign": {
      "buy_value_thb": 30710626203.24,
      "sell_value_thb": 29510281606.4,
      "net_value_thb": 1200344596.8400002,
      "percent_buy_value": 47.050380029646426,
      "percent_sell_value": 45.21138563486927
    },
    "individual": {
      "buy_value_thb": 16837839251.13,
      "sell_value_thb": 17566195679.05,
      "net_value_thb": -728356427.9200001,
      "percent_buy_value": 25.796502174878576,
      "percent_sell_value": 26.912384557213596
    }
  },
  "rolling_5d_net_mb": {
    "foreign": 7236.448598709999,
    "individual": -7780.1671316500015,
    "institution": 2508.9900190699996,
    "proprietary": -1965.271486130001
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: KBANK ฿1095M, KTB ฿781M, PTT ฿613M, DELTA ฿480M, SCB ฿373M

```json
{
  "date": "2026-11-16T00:00:00+07:00",
  "top20": [
    {
      "symbol": "KBANK",
      "short_value": 1094742000.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 780897640.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 612868370.0,
      "short_volume": null
    },
    {
      "symbol": "DELTA",
      "short_value": 480438350.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 373498400.0,
      "short_volume": null
    },
    {
      "symbol": "GULF",
      "short_value": 366523200.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 312449870.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 306869700.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 295118450.0,
      "short_volume": null
    },
    {
      "symbol": "CPF",
      "short_value": 253102785.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 246626310.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 216463600.0,
      "short_volume": null
    },
    {
      "symbol": "TOP",
      "short_value": 174650250.0,
      "short_volume": null
    },
    {
      "symbol": "SCC",
      "short_value": 171101000.0,
      "short_volume": null
    },
    {
      "symbol": "KCE",
      "short_value": 152494200.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 119668700.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 96654870.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 93946140.0,
      "short_volume": null
    },
    {
      "symbol": "TLI",
      "short_value": 93662340.0,
      "short_volume": null
    },
    {
      "symbol": "IVL",
      "short_value": 85513485.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: CPALL +฿593M, SCB +฿519M, BH +฿259M, EGCO +฿219M, BDMS +฿159M. NVDR net SELL top: KBANK ฿-676M, KTB ฿-437M, CPF ฿-314M, HANA ฿-186M, BBL ฿-155M

```json
{
  "date": "2026-11-16",
  "top_buy": [
    {
      "symbol": "CPALL",
      "buy_value": 1154109453.0,
      "sell_value": 561341570.0,
      "net_value": 592767883.0,
      "total_value": 1715451023.0,
      "percent_of_underlying": 35.78317285585529
    },
    {
      "symbol": "SCB",
      "buy_value": 957165763.5,
      "sell_value": 438641550.0,
      "net_value": 518524213.5,
      "total_value": 1395807313.5,
      "percent_of_underlying": 30.531214948311096
    },
    {
      "symbol": "BH",
      "buy_value": 411386786.0,
      "sell_value": 152666450.0,
      "net_value": 258720336.0,
      "total_value": 564053236.0,
      "percent_of_underlying": 28.557517642737487
    },
    {
      "symbol": "EGCO",
      "buy_value": 313875200.0,
      "sell_value": 94401300.0,
      "net_value": 219473900.0,
      "total_value": 408276500.0,
      "percent_of_underlying": 33.407649434409656
    },
    {
      "symbol": "BDMS",
      "buy_value": 732644779.0,
      "sell_value": 573416555.4,
      "net_value": 159228223.60000002,
      "total_value": 1306061334.4,
      "percent_of_underlying": 25.822415426676486
    },
    {
      "symbol": "ADVANC",
      "buy_value": 705700338.0,
      "sell_value": 549824600.0,
      "net_value": 155875738.0,
      "total_value": 1255524938.0,
      "percent_of_underlying": 43.79576724615884
    },
    {
      "symbol": "AOT",
      "buy_value": 388597643.0,
      "sell_value": 236102800.0,
      "net_value": 152494843.0,
      "total_value": 624700443.0,
      "percent_of_underlying": 38.75260028864048
    },
    {
      "symbol": "TRUE",
      "buy_value": 687202822.0,
      "sell_value": 535033760.0,
      "net_value": 152169062.0,
      "total_value": 1222236582.0,
      "percent_of_underlying": 56.65881738416222
    },
    {
      "symbol": "GULF",
      "buy_value": 647292504.5,
      "sell_value": 529078975.0,
      "net_value": 118213529.5,
      "total_value": 1176371479.5,
      "percent_of_underlying": 31.157348738532853
    },
    {
      "symbol": "TISCO",
      "buy_value": 222664500.0,
      "sell_value": 110905050.0,
      "net_value": 111759450.0,
      "total_value": 333569550.0,
      "percent_of_underlying": 38.81285429060161
    }
  ],
  "top_sell": [
    {
      "symbol": "KBANK",
      "buy_value": 935374972.0,
      "sell_value": 1611426372.0,
      "net_value": -676051400.0,
      "total_value": 2546801344.0,
      "percent_of_underlying": 27.978953331897067
    },
    {
      "symbol": "KTB",

```
