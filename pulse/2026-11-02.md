---
date: 2026-11-02
generated_at_utc: 2026-11-02T22:34:59Z
model_used: deterministic-fallback/openrouter-unavailable
trackers_ok: 3/3
---

# 🇹🇭 Thai Market Pulse — 2026-11-02

Official SET investor-type: Foreign +฿995M, Individual +฿449M, Institution ฿-113M, Proprietary ฿-1,332M.

## 1. SET Investor-Type Flow
Official SET investor type: Foreign +฿995M, Individual +฿449M, Institution ฿-113M, Proprietary ฿-1,332M

```json
{
  "date": "2026-11-02T00:00:00+07:00",
  "source": "https://www.set.or.th/api/set/market/SET/investor-type",
  "total_value_thb": 55798723168.05,
  "investors": {
    "institution": {
      "buy_value_thb": 3424045462.7,
      "sell_value_thb": 3537079983.29,
      "net_value_thb": -113034520.59000015,
      "percent_buy_value": 6.13642260663876,
      "percent_sell_value": 6.33899806745992
    },
    "proprietary": {
      "buy_value_thb": 3579770213.22,
      "sell_value_thb": 4911448648.07,
      "net_value_thb": -1331678434.85,
      "percent_buy_value": 6.4155056065328635,
      "percent_sell_value": 8.802080709406384
    },
    "foreign": {
      "buy_value_thb": 33777230278.58,
      "sell_value_thb": 32782014855.04,
      "net_value_thb": 995215423.5400009,
      "percent_buy_value": 60.534055908147785,
      "percent_sell_value": 58.750474910169224
    },
    "individual": {
      "buy_value_thb": 15017677213.55,
      "sell_value_thb": 14568179681.65,
      "net_value_thb": 449497531.8999996,
      "percent_buy_value": 26.914015878680583,
      "percent_sell_value": 26.108446312964464
    }
  },
  "rolling_5d_net_mb": {
    "foreign": -2077.4946355899965,
    "individual": 3907.611883199997,
    "institution": -343.78535629,
    "proprietary": -1486.3318913199992
  },
  "history_size": 30
}
```

## 2. SET Short-Sale Ranking
Top short value: DELTA ฿360M, PTTEP ฿289M, SCC ฿190M, KBANK ฿112M, TOP ฿94M

```json
{
  "date": "2026-11-02T00:00:00+07:00",
  "top20": [
    {
      "symbol": "DELTA",
      "short_value": 359574300.0,
      "short_volume": null
    },
    {
      "symbol": "PTTEP",
      "short_value": 289297000.0,
      "short_volume": null
    },
    {
      "symbol": "SCC",
      "short_value": 189553900.0,
      "short_volume": null
    },
    {
      "symbol": "KBANK",
      "short_value": 111812300.0,
      "short_volume": null
    },
    {
      "symbol": "TOP",
      "short_value": 93942550.0,
      "short_volume": null
    },
    {
      "symbol": "PTT",
      "short_value": 91757950.0,
      "short_volume": null
    },
    {
      "symbol": "AOT",
      "short_value": 85184050.0,
      "short_volume": null
    },
    {
      "symbol": "KTB",
      "short_value": 82653050.0,
      "short_volume": null
    },
    {
      "symbol": "BBL",
      "short_value": 75750250.0,
      "short_volume": null
    },
    {
      "symbol": "GULF",
      "short_value": 68038200.0,
      "short_volume": null
    },
    {
      "symbol": "PTTGC",
      "short_value": 60620800.0,
      "short_volume": null
    },
    {
      "symbol": "KKP",
      "short_value": 59630050.0,
      "short_volume": null
    },
    {
      "symbol": "BH",
      "short_value": 57469100.0,
      "short_volume": null
    },
    {
      "symbol": "ADVANC",
      "short_value": 55048100.0,
      "short_volume": null
    },
    {
      "symbol": "SCB",
      "short_value": 53167750.0,
      "short_volume": null
    },
    {
      "symbol": "KCE",
      "short_value": 43875725.0,
      "short_volume": null
    },
    {
      "symbol": "CPALL",
      "short_value": 33687500.0,
      "short_volume": null
    },
    {
      "symbol": "BDMS",
      "short_value": 32498760.0,
      "short_volume": null
    },
    {
      "symbol": "BA",
      "short_value": 29135090.0,
      "short_volume": null
    },
    {
      "symbol": "CPF",
      "short_value": 22303490.0,
      "short_volume": null
    }
  ],
  "biggest_movers_dod": []
}
```

## 3. NVDR Daily Flow
NVDR net BUY top: TRUE +฿324M, CPALL +฿236M, GULF +฿230M, HANA +฿157M, TOP +฿125M. NVDR net SELL top: PTTEP ฿-277M, KTB ฿-262M, BBL ฿-249M, SCC ฿-208M, KKP ฿-197M

```json
{
  "date": "2026-11-02",
  "top_buy": [
    {
      "symbol": "TRUE",
      "buy_value": 1137545330.0,
      "sell_value": 813696830.0,
      "net_value": 323848500.0,
      "total_value": 1951242160.0,
      "percent_of_underlying": 59.41759106391212
    },
    {
      "symbol": "CPALL",
      "buy_value": 482572100.0,
      "sell_value": 246288200.0,
      "net_value": 236283900.0,
      "total_value": 728860300.0,
      "percent_of_underlying": 32.72581117014069
    },
    {
      "symbol": "GULF",
      "buy_value": 745697425.0,
      "sell_value": 515756209.0,
      "net_value": 229941216.0,
      "total_value": 1261453634.0,
      "percent_of_underlying": 31.11362377567642
    },
    {
      "symbol": "HANA",
      "buy_value": 296705725.0,
      "sell_value": 139780425.0,
      "net_value": 156925300.0,
      "total_value": 436486150.0,
      "percent_of_underlying": 22.136040105474645
    },
    {
      "symbol": "TOP",
      "buy_value": 465532891.0,
      "sell_value": 340755175.0,
      "net_value": 124777716.0,
      "total_value": 806288066.0,
      "percent_of_underlying": 35.26161575032837
    },
    {
      "symbol": "BDMS",
      "buy_value": 510037338.5,
      "sell_value": 410795640.0,
      "net_value": 99241698.5,
      "total_value": 920832978.5,
      "percent_of_underlying": 32.29031346611637
    },
    {
      "symbol": "BH",
      "buy_value": 274599250.0,
      "sell_value": 181863700.0,
      "net_value": 92735550.0,
      "total_value": 456462950.0,
      "percent_of_underlying": 25.830979828303075
    },
    {
      "symbol": "TTB",
      "buy_value": 166850425.44,
      "sell_value": 80527404.3,
      "net_value": 86323021.14,
      "total_value": 247377829.74,
      "percent_of_underlying": 26.863494299527446
    },
    {
      "symbol": "COM7",
      "buy_value": 157813175.0,
      "sell_value": 72653550.0,
      "net_value": 85159625.0,
      "total_value": 230466725.0,
      "percent_of_underlying": 30.574221963114674
    },
    {
      "symbol": "KCE",
      "buy_value": 345830250.0,
      "sell_value": 271719742.75,
      "net_value": 74110507.25,
      "total_value": 617549992.75,
      "percent_of_underlying": 18.76613691125687
    }
  ],
  "top_sell": [
    {
      "symbol": "PTTEP",
      "buy_value": 967601845.5,
      "sell_value": 1244549850.0,
      "net_value": -276948004.5,
      "total_value": 2212151695.5,
      "percent_of_underlying": 27.27350496320253
    },
    {
      "symbol": "KTB",
      "buy_value"
```
