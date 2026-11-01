# `deal_card` · 

<img src="../../assets/previews/fx/deal_card.webp" width="480" alt="deal_card 横屏"> <img src="../../assets/previews/fx/deal_card_v.webp" width="160" alt="deal_card 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 类型 |
| 适合的句子 | 带货、价格对比、限时优惠 |
| 建议时长 | 4.5–6 秒 |
| 参数 | `at`, `countdown`, `countdown_label`, `coupon`, `cur`, `image`, `note`, `price`, `product`, `stock`, `sub`, `tags`, `title`, `unit`, `was` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | Envato Infographics「Modern Price Tags & Counters」 |

```json
{
 "scene": "fx",
 "fx": "deal_card",
 "theme": "paper",
 "topic": "商业拆解",
 "product": "冰鲜柠檬水 · 大杯",
 "sub": "下单后 15 分钟可取",
 "price": "4",
 "was": "6",
 "unit": "/杯",
 "tags": [
  "限时",
  "第二杯半价"
 ],
 "coupon": [
  "满 20 减 3",
  "立即领"
 ],
 "countdown": "00:59:59",
 "stock": [
  23,
  100
 ],
 "note": "示意",
 "line": "门店里一杯柠檬水，*只要 4 块*。",
 "src": "示意：原价、券与库存为演示数据",
 "t": "@关键词"
}
```

**已知坑**：原价、券、库存如果不是真的就写 note: 示意；countdown 是演示倒计时，不代表真实活动。
