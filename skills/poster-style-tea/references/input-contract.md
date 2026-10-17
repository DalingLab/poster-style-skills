# 输入契约与 Brief

先建立素材角色，再谈风格。角色错误会导致商品被重绘、竞品内容泄漏或文字事实被擅自补写。

## 素材角色

| 角色 | 可以控制 | 不可以控制 |
| --- | --- | --- |
| `STYLE_REF` | 布局、标题行为、商品占比、色彩关系、材质、装饰密度 | 新商品身份、品牌、文案、价格、配方 |
| `PRODUCT_ASSET` | 杯型、包装、标签、数量、分层、颜色、装饰、朝向 | 参考图的品牌与场景语义 |
| `BRAND_ASSET` | Logo、标准字、品牌色、授权图形 | 自动推导未提供的品牌规范 |
| `INGREDIENT_REF` | 已确认原料的外观与色彩 | 自动证明配方、产地、功效或杯中含量 |
| `COPY_SHEET` | 需要逐字呈现的文字 | 模型自行补写的促销或事实信息 |

如果一张图片同时包含商品和品牌资产，在同一个素材对象中使用 `roles` 数组，并在 `notes` 说明哪些区域分别是真源，例如：

```json
{"label": "Image 2", "roles": ["PRODUCT_ASSET", "BRAND_ASSET"], "notes": "杯体是商品真源，杯身 Logo 是品牌真源"}
```

## Brief 字段

正式成片使用以下字段；未知值为空，不用占位营销话术代替：

```json
{
  "mode": "publish-ready",
  "assets": [
    {"label": "Image 1", "roles": ["STYLE_REF"]},
    {"label": "Image 2", "roles": ["PRODUCT_ASSET"]},
    {"label": "Image 3", "roles": ["BRAND_ASSET"]}
  ],
  "product_name": "",
  "copy_status": "",
  "title_layout": "",
  "copy_layout": "",
  "product_description": "",
  "category": "milk-tea",
  "temperature": "cold",
  "visible_layers": [],
  "confirmed_ingredients": [],
  "confirmed_claims": [],
  "origin": "",
  "campaign_goal": "new-launch",
  "audience": "",
  "channel": "social-portrait",
  "aspect_ratio": "3:4",
  "exact_copy": [],
  "price": "",
  "promotion_terms": "",
  "style_direction": "",
  "must_preserve": [],
  "forbidden": []
}
```

## 信息门禁

- 进入生成提示词前，`publish-ready` 必须存在 `PRODUCT_ASSET`、商品名和商品描述。未提供品名时，先由 Agent 依参考槽位拟写，填入 `product_name`，并在 `copy_status` 标注“创意拟名”；不把缺品名当作默认阻塞条件。
- `title_layout` 记录行数、断行与字体量感；`copy_layout` 记录各文字槽位的位置、字高、占宽、容量与最终文案。参考图提供空间约束，不提供新商品的事实。
- 产品名、slogan 和配套小字缺省时主动拟写，用户已提供的精确文案优先保留；拟写不授权虚构配方、价格等事实。
- `concept` 可以没有商品图，但必须在交付中标注“概念视觉，商品外观非真实依据”。
- 价格与促销条件必须成对核对；有折扣但没有适用条件时先标记为待确认。
- `confirmed_claims` 仅收录用户已确认且允许展示的卖点。配方字段不自动变成广告文案。
- 门店、日期、产地、认证、营养和健康描述均属于事实字段，不推断。
- 所有 `exact_copy` 在画面中默认只出现一次；重复是错误而不是装饰手段。

## 多参考图

指定哪张参考图分别控制布局、字体、商品处理、配色和纹理。互相矛盾时选择一个主参考，其余只作为局部参考；不要平均融合所有风格。
