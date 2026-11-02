# 字体

风格里用的字体都登记在 `assets/fonts.json`。在风格的 `fonts` 里写字体 id 就能用，一个角色可以给一串 id，前面的优先：

```python
"fonts": {"display": ["zcool-kuhei", "noto-sans-sc"], "body": "noto-sans-sc", "num": "archivo", "mono": "jetbrains-mono"}
```

每个角色会变成 CSS 变量 `--f-<角色>`（如 `--f-display`）。构建时只把用到的字裁出来放进工程，所以中文字体再大也不拖慢渲染。全部样张见 [`gallery/fonts.html`](../gallery/fonts.html)。

## 目录

### 黑体

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `noto-sans-sc` | 正文 / 标题黑体（思源黑体，可变 100–900） | 财经、科技、通用 | OFL |
| `lxgw-neo-xihei` | 新晰黑（清爽黑体） | 清新、通用、科技 | IPA |
| `alibaba-puhuiti` | 正文/标题黑体 | 电商、通用、科技 | 免费商用（不随仓库分发） |
| `harmonyos-sans` | 界面黑体 | 科技、界面 | 免费商用（不随仓库分发） |
| `misans` | 可变黑体 | 科技、界面、通用 | 免费商用（不随仓库分发） |

### 宋体

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `noto-serif-sc` | 标题 / 引语宋体（思源宋体，可变 200–900） | 杂志、电影、国风、财经 | OFL |
| `zcool-xiaowei` | 站酷小薇（文艺宋体标题） | 文艺、杂志、复古 | OFL |

### 楷体与手写

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `lxgw-wenkai` | 文楷（楷书骨架的正文字体） | 温暖、国风、笔记 | OFL |
| `long-cang` | 龙藏体（行楷手写） | 手写、笔记、温暖 | OFL |
| `lxgw-marker` | 霞鹜漫黑（马克笔手写黑体） | 白板、便签、拼贴标签 | OFL |

### 毛笔

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `ma-shan-zheng` | 马善政楷书（毛笔楷） | 国风、书法 | OFL |
| `zhi-mang-xing` | 毛笔行书 | 国风、书法、手写 | OFL |
| `liu-jian-mao-cao` | 毛笔草书 | 国风、书法、狂放 | OFL |

### 圆体与可爱

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `zcool-kuaile` | 站酷快乐体（圆润可爱） | 可爱、童趣、轻松 | OFL |
| `zcool-qingke` | 站酷庆科黄油体（粗圆标题） | 可爱、潮流、游戏 | OFL |

### 标题展示

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `smiley-sans` | 得意黑（斜体标题） | 潮流、科技、年轻 | OFL |
| `zcool-gaoduanhei` | 标题黑体 | 高级、杂志、科技 | 免费商用（不随仓库分发） |
| `zcool-kuhei` | 粗标题黑体 | 冲击、潮流、游戏 | 免费商用（不随仓库分发） |
| `alibaba-puhuiti-heavy` | 特粗标题 | 电商、冲击 | 免费商用（不随仓库分发） |
| `harmonyos-sans-black` | 界面特粗 | 科技、冲击 | 免费商用（不随仓库分发） |

### 英文衬线

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `playfair` | Playfair Display（高反差衬线） | 杂志、奢华、电影 | OFL |
| `playfair-italic` | Playfair Display Italic | 杂志、奢华 | OFL |
| `fraunces` | Fraunces（软衬线，可变 SOFT/WONK） | 温暖、复古、杂志 | OFL |
| `eb-garamond` | EB Garamond（古典书籍衬线） | 书卷、复古、国风 | OFL |
| `eb-garamond-italic` | EB Garamond Italic | 书卷、复古 | OFL |
| `dm-serif` | DM Serif Display（粗衬线标题） | 杂志、电影 | OFL |
| `libre-caslon` | 英文书籍衬线 | 书卷、报纸 | OFL |
| `old-standard` | 英文古典衬线 | 复古、报纸、档案 | OFL |

### 英文无衬线

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `inter` | Inter（界面无衬线，可变） | 科技、通用、财经 | OFL |
| `space-grotesk` | Space Grotesk（几何怪趣无衬线） | 科技、潮流 | OFL |
| `archivo` | Archivo（可变宽度，窄体数字很好用） | 财经、杂志、数据 | OFL |
| `barlow-cond` | Barlow Condensed Bold（窄体数字） | 数据、运动、科技 | OFL |
| `barlow-cond-black` | Barlow Condensed Black（特粗窄体） | 数据、冲击 | OFL |
| `roboto-cond` | 英文窄体 | 新闻、数据 | OFL |

### 英文展示

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `oswald` | Oswald（窄体标题） | 新闻、冲击 | OFL |
| `anton` | Anton（特粗窄体海报字） | 冲击、海报、运动 | OFL |
| `bebas` | Bebas Neue（全大写海报字） | 电影、海报 | OFL |
| `permanent-marker` | Permanent Marker（马克笔手写） | 手绘、街头、拼贴 | Apache |
| `caveat` | Caveat（自然手写，可变） | 手绘、笔记 | OFL |
| `kalam` | Kalam Bold（圆珠笔手写） | 手绘、笔记 | OFL |
| `archivo-black` | 英文特粗 | 冲击、海报、拼贴 | OFL |
| `abril-fatface` | 英文杂志粗衬线 | 杂志、复古、拼贴 | OFL |
| `unifraktur` | 哥特黑字体 | 复古、报头、暗黑 | OFL |
| `patrick-hand` | 英文手写 | 手绘、童趣、白板 | OFL |

### 等宽与像素

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `jetbrains-mono` | JetBrains Mono（代码等宽，可变） | 科技、代码、数据 | OFL |
| `ibm-plex-mono` | IBM Plex Mono（等宽） | 科技、报告 | OFL |
| `space-mono` | Space Mono（复古等宽） | 复古、科技 | OFL |
| `special-elite` | Special Elite（打字机） | 复古、档案、调查 | Apache |
| `courier-prime` | Courier Prime（打字机等宽） | 档案、剧本 | OFL |
| `vt323` | VT323（终端点阵） | 复古、游戏、终端 | OFL |
| `press-start-2p` | 像素字体 | 游戏、像素、复古 | OFL |
| `fusion-pixel` | 缝合像素 12px（中文像素字，用 12 的整数倍字号） | 游戏、像素、复古 | OFL |

### 其他文字

| id | 是什么 | 适合 | 许可 |
|---|---|---|---|
| `noto-sans-jp` | 日文黑体（思源黑体 JP，可选） | 通用 | OFL（可选） |
| `noto-sans-kr` | 韩文黑体（思源黑体 KR，可选） | 通用 | OFL（可选） |
| `noto-sans-tc` | 繁体黑体（思源黑体 TC，可选） | 通用 | OFL（可选） |
| `noto-serif-jp` | 日文宋体（思源宋体 JP，可选） | 杂志、电影 | OFL（可选） |
| `noto-serif-kr` | 韩文宋体（思源宋体 KR，可选） | 杂志、电影 | OFL（可选） |
| `noto-sans-arabic` | 阿拉伯文无衬线（可选） | 通用 | OFL（可选） |
| `noto-naskh-arabic` | 阿拉伯文誊抄体 Naskh（可选） | 书卷、引语 | OFL（可选） |
| `noto-sans-hebrew` | 希伯来文无衬线（可选） | 通用 | OFL（可选） |

## 按情绪搭配

「风格」一栏写的是现在在用的风格；标「适合」的是推荐给对应风格的组合。

| 情绪 | 标题（display） | 正文（body） | 数字 / 英文 / 等宽 | 风格 | 要点 |
|---|---|---|---|---|---|
| 财经刊 | noto-sans-sc（900） | noto-sans-sc | archivo（窄体数字）· jetbrains-mono | press、poster | 大字黑体 + 窄体数字，数据多也不挤 |
| 纸媒高级 | noto-serif-sc | noto-sans-sc | libre-caslon · ibm-plex-mono | doc、atlas | 宋体标题 + 书籍衬线做英文小字 |
| 科技产品 | inter + noto-sans-sc | misans 或 noto-sans-sc | jetbrains-mono | screen、hud、studio | 界面感强，数字用 inter 的等宽数字 |
| 科技潮流 | smiley-sans | lxgw-neo-xihei | space-grotesk · space-mono | chrome3d、iso3d（适合） | 得意黑的斜体给速度感 |
| 爆款冲击 | zcool-kuhei 或 alibaba-puhuiti-heavy | noto-sans-sc | anton · barlow-cond-black | reel、带货类 | 粗黑 + 特粗窄体，一屏一个重点 |
| 电商带货 | alibaba-puhuiti-heavy | alibaba-puhuiti | oswald · barlow-cond | deal_card 动效 | 价格数字用窄体，原价划线用细体 |
| 国风书法 | ma-shan-zheng 或 zhi-mang-xing | noto-serif-sc | eb-garamond-italic | ink、papercut（适合） | 毛笔只用在标题和一两个关键词 |
| 武侠狂草 | liu-jian-mao-cao | noto-serif-sc（900） | old-standard | ink（适合） | 草书认读难，只用两三个字的大标题 |
| 温暖笔记 | lxgw-wenkai | lxgw-wenkai | fraunces（SOFT）· caveat | sketch（适合） | 文楷正文 + 软衬线英文 |
| 手绘白板 | lxgw-marker | lxgw-marker | patrick-hand · kalam | sketch（适合） | 马克笔手写，像在白板上边讲边写 |
| 可爱童趣 | zcool-kuaile | zcool-kuaile | zcool-qingke · patrick-hand | flat（适合） | 圆润字配圆角图形 |
| 文艺杂志 | zcool-xiaowei | noto-serif-sc | playfair-italic · dm-serif | zine（适合） | 小薇宋做大标题，意大利斜体做英文眉题 |
| 高级极简 | zcool-gaoduanhei | lxgw-neo-xihei | inter（细）· ibm-plex-mono | poster 的冷白页 | 细长黑体 + 大留白 |
| 复古报纸 | noto-serif-sc（900） | noto-serif-sc | old-standard · unifraktur（报头） | zine、doc | 哥特体只用在报头 |
| 档案调查 | noto-serif-sc | noto-sans-sc | courier-prime · special-elite | doc、引用类动效（cite_*） | 打字机字体做批注和编号 |
| 电影片名 | noto-serif-sc（900） | noto-sans-sc | bebas · playfair-italic | doc、atlas | 全大写窄体做英文片名 |
| 游戏像素 | fusion-pixel | fusion-pixel | press-start-2p · vt323 | pixel（适合） | 中文用缝合像素，字号只取 12 / 24 才清晰 |
| 终端黑客 | jetbrains-mono | lxgw-neo-xihei | vt323 | screen | 绿色等宽 + 扫描线 |
| 拼贴朋克 | zcool-kuhei | noto-sans-sc | archivo-black · abril-fatface · permanent-marker | zine（适合） | 不同字体混排像剪下来的字；手写批注用 lxgw-marker |
| Y2K 镀铬 | harmonyos-sans-black | harmonyos-sans | space-grotesk · bebas | chrome3d（适合） | 粗黑体最适合做金属、渐变描边 |
| 清新生活 | lxgw-neo-xihei | lxgw-neo-xihei | fraunces（SOFT）· caveat | flat（适合） | 新晰黑比思源黑更轻 |
| 数据新闻 | harmonyos-sans | noto-sans-sc | roboto-cond · jetbrains-mono | hud、图表类动效 | 窄体做坐标轴和图例 |
| 剪纸年味 | zcool-qingke | noto-serif-sc | abril-fatface | papercut（适合） | 粗圆字像剪出来的形状 |
| 多语言 | noto-sans-sc | noto-sans-jp / kr / tc | noto-sans-arabic · noto-sans-hebrew | 任何风格（meta.lang） | 日韩繁阿希字体是可选的，没装时回退系统字体 |

## 许可

- **OFL 1.1 / Apache 2.0 / IPA**：可以商用、改造、随项目分发（不能单独卖字体本身）。
- **免费商用（非开源许可）**：`zcool-gaoduanhei`、`zcool-kuhei`、`alibaba-puhuiti`、`alibaba-puhuiti-heavy`、`harmonyos-sans`、`harmonyos-sans-black`、`misans`。成片里可以用，但字体文件**不随仓库分发**（`fonts.json` 里标了 `"redistribute": false`），需要自己到官方下载；商用前以官方许可原文为准。
- 本仓库**不打包任何字体文件**。构建时按 `fonts.json` 的文件名到这些地方找：`assets/fonts/`、`$H9_FONT_DIRS`、`$H9_MEDIA/fonts`、系统字体目录。找不到会打印下载地址，并回退到 `fallback` 里写的系统字体。
- 标「可选」的日文、韩文、繁体、阿拉伯文、希伯来文字体没装时，会回退到系统字体，字能显示，字形不是最佳。

## 加一款字体

1. 确认许可：OFL / Apache / IPA，或官方写明免费商用的。电商平台上卖的「开源字体」多半是倒卖，只从官方渠道下载。
2. 把字体文件放进 `assets/fonts/`（或你的 `$H9_MEDIA/fonts` 下任意子目录），附上许可原文。
3. 在 `assets/fonts.json` 里加一条：

```json
"my-font": {"file": "MyFont-Bold.ttf", "weight": "700", "fallback": "'PingFang SC',sans-serif", "license": "OFL-1.1",
            "url": "官方地址", "cat": "标题展示", "role": "一句话说明", "mood": ["潮流"], "script": "sc", "redistribute": true}
```

   可变字体把 `weight` 写成范围（`"100 900"`）。免费商用但不能再分发的，`redistribute` 写 `false`。
4. 重新生成样张：`python3 assets/previews/fonts/make_specimens.py`（会同时更新 `gallery/fonts.html` 的数据）。
5. 在风格的 `fonts` 里用新 id，构建一次，确认没有打印「not found」。

还没收录的候选字体（含官方地址、许可和大小）见 [`research/fonts_wishlist.md`](../research/fonts_wishlist.md)。
