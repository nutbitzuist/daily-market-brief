---
date: 2026-11-25
generated_at_utc: 2026-11-25T22:31:08Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-25

Official SET investor-type: Foreign ฿-1,180M, Individual +฿5,557M, Institution ฿-3,168M, Proprietary ฿-1,209M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign ฿-1,180M, Individual +฿5,557M, Institution ฿-3,168M, Proprietary ฿-1,209M

```json
{
  "date": "2026-11-25T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 66937719946.2,
  "investors": {
    "institution": {
      "buy_value_thb": 2388969880.09,
      "sell_value_thb": 5556814900.68,
      "net_value_thb": -3167845020.59,
      "percent_buy_value": 3.568944209647553,
      "percent_sell_value": 8.301470240017425
    },
    "proprietary": {
      "buy_value_thb": 14361606011.12,
      "sell_value_thb": 15570541401.23,
      "net_value_thb": -1208935390.1099987,
      "percent_buy_value": 21.455176577067288,
      "percent_sell_value": 23.26123658490989
    },
    "foreign": {
      "buy_value_thb": 27647438721.46,
      "sell_value_thb": 28827363171.8,
      "net_value_thb": -1179924450.3400002,
      "percent_buy_value": 41.30322745334191,
      "percent_sell_value": 43.06594726406797
    },
    "individual": {
      "buy_value_thb": 22539705333.53,
      "sell_value_thb": 16983000472.49,
      "net_value_thb": 5556704861.039999,
      "percent_buy_value": 33.67265175994326,
      "percent_sell_value": 25.371345911004713
    }
  },
  "rolling_5d_net_mb": {
    "foreign": -10628.632280760003,
    "individual": 14735.231606410003,
    "institution": -2541.5810813100006,
    "proprietary": -1565.0182443400001
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: GULF ฿1256M, KTB ฿806M, KBANK ฿631M, DELTA ฿600M, KKP ฿447M

```json
{
  "date": "2026-11-25T00:00:00+07:00",
  "top20": [
    {
      "symbol": "GULF",
      "short_value": 1255850950.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 805850290.0,
      "short_volume": null
    },
    {
      "symbol": "KBANK",
      "short_value": 631127500.0,
      "short_volume": null
    },
    {
      "symbol": "DELTA",
      "short_value": 599588100.0,
      "short_volume": null
    },
    {
      "symbol": "KKP",
      "short_value": 446636050.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 445974450.0,
      "short_volume": null
    },
    {
      "symbol": "TRUE",
      "short_value": 352974715.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 352616500.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 313786725.0,
      "short_volume": null
    },
    {
      "symbol": "AMATA",
      "short_value": 293289110.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 204808600.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 204396925.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 198831990.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 197697070.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 196899500.0,
      "short_volume": null
    },
    {
      "symbol": "TTB",
      "short_value": 192428440.0,
      "short_volume": null
    },
    {
      "symbol": "SCC",
      "short_value": 175490500.0,
      "short_volume": null
    },
    {
      "symbol": "TOP",
      "short_value": 164120125.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 153312700.0,
      "short_volume": null
    },
    {
      "symbol": "TISCO",
      "short_value": 142773100.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: ADVANC +฿308M, BDMS +฿231M, SCC +฿226M, DELTA +฿156M, CPAXT +฿141M. NVDR net SELL top: KBANK ฿-635M, KTB ฿-592M, PTT ฿-529M, GULF ฿-492M, KKP ฿-395M

```json
{
  "date": "2026-11-25",
  "top_buy": [
    {
      "symbol": "ADVANC",
      "buy_value": 763357664.0,
      "sell_value": 455323860.0,
      "net_value": 308033804.0,
      "total_value": 1218681524.0,
      "percent_of_underlying": 28.281406635799133
    },
    {
      "symbol": "BDMS",
      "buy_value": 565936075.7,
      "sell_value": 334560671.0,
      "net_value": 231375404.70000005,
      "total_value": 900496746.7,
      "percent_of_underlying": 29.307577680656518
    },
    {
      "symbol": "SCC",
      "buy_value": 383907900.0,
      "sell_value": 157675998.0,
      "net_value": 226231902.0,
      "total_value": 541583898.0,
      "percent_of_underlying": 30.378304567175878
    },
    {
      "symbol": "DELTA",
      "buy_value": 1148820026.0,
      "sell_value": 993279350.0,
      "net_value": 155540676.0,
      "total_value": 2142099376.0,
      "percent_of_underlying": 28.6461748112472
    },
    {
      "symbol": "CPAXT",
      "buy_value": 227774210.0,
      "sell_value": 87184727.25,
      "net_value": 140589482.75,
      "total_value": 314958937.25,
      "percent_of_underlying": 27.446454107098237
    },
    {
      "symbol": "CPALL",
      "buy_value": 569394636.5,
      "sell_value": 433156195.0,
      "net_value": 136238441.5,
      "total_value": 1002550831.5,
      "percent_of_underlying": 22.416114402911347
    },
    {
      "symbol": "IVL",
      "buy_value": 194092360.0,
      "sell_value": 65316760.0,
      "net_value": 128775600.0,
      "total_value": 259409120.0,
      "percent_of_underlying": 26.333950303204603
    },
    {
      "symbol": "CPN",
      "buy_value": 232067900.0,
      "sell_value": 108936775.0,
      "net_value": 123131125.0,
      "total_value": 341004675.0,
      "percent_of_underlying": 32.15642511086102
    },
    {
      "symbol": "GUNKUL",
      "buy_value": 148480042.0,
      "sell_value": 45554664.0,
      "net_value": 102925378.0,
      "total_value": 194034706.0,
      "percent_of_underlying": 20.107029447071863
    },
    {
      "symbol": "KCE",
      "buy_value": 290099750.0,
      "sell_value": 195994775.0,
      "net_value": 94104975.0,
      "total_value": 486094525.0,
      "percent_of_underlying": 19.979279412538368
    }
  ],
  "top_sell": [
    {
      "symbol": "KBANK",
      "buy_value": 594255200.0,
      "sell_value": 1229687284.0,
      "net_value": -635432084.0,
      "total_value": 1823942484.0,
      "percent_of_underlying": 24.901311060556186
    },
    {
      "symbol": "KTB"
```
