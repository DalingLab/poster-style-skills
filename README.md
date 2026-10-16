# DalingLab Poster Style Skills

用参考海报建立设计约束，再为新主题、新商品和新活动制作视觉。

作者与维护者：**[DalingLab](https://github.com/DalingLab)** · 版本 **1.0.0** · MIT License

这是一组中文 Agent Skills。每个文件夹都包含完整说明和参考资源，可单独安装；不依赖其余四个 skill。它们负责指导具备相应能力的 Agent，不是独立生图软件，也不附带模型密钥。

## 五个版本

| Skill | 适用任务 | 专项重点 |
| --- | --- | --- |
| [poster-style-general](skills/poster-style-general/SKILL.md) | 跨行业海报、活动与文化视觉 | 设计参数、主题变化、版式适配 |
| [poster-style-food](skills/poster-style-food/SKILL.md) | 餐厅、茶饮、咖啡、烘焙与食品 | 食欲、配料、器皿与真实包装 |
| [poster-style-beauty](skills/poster-style-beauty/SKILL.md) | 护肤、彩妆、香氛与洗护 | 包装、色号、质地与已确认卖点 |
| [poster-style-tech](skills/poster-style-tech/SKILL.md) | 硬件、软件、AI 工具与 SaaS | 产品结构、真实 UI 与功能价值 |
| [poster-style-retail](skills/poster-style-retail/SKILL.md) | 门店促销、电商、会员与多商品活动 | 价格对应、优惠条件与购买入口 |

按任务的主导问题选版本：食品新品主视觉选 food；食品多件满减活动若主要难点是价格与规则，选 retail。通用版用于没有对应行业或跨题材迁移的任务。

## 能交付什么

- **海报制作**：使用可用图片工具出图并复核。
- **风格拆解**：只给设计记录、迁移优先级和适配建议。
- **提示词模板**：给变量表与一整段可复制提示词，不自动调用生图。

共同方法包括素材角色分配、版面比例、标题层级、主体关系、色彩职责，以及先核对事实再评价设计。密集中文、准确包装、真实 UI 和价格条件优先采用素材合成与确定性排版。

## 安装到 Codex

下载本仓库后，将需要的完整 skill 文件夹复制到 `~/.codex/skills/`。例如安装餐饮版：

```bash
git clone https://github.com/DalingLab/poster-style-skills.git
mkdir -p ~/.codex/skills
cp -R poster-style-skills/skills/poster-style-food ~/.codex/skills/
```

安装全部五个：

```bash
mkdir -p ~/.codex/skills
cp -R poster-style-skills/skills/poster-style-* ~/.codex/skills/
```

若已有同名 skill，先备份原目录再替换，不要把旧参考文件混进新版本。重新打开会话后调用对应名称。其他支持 Agent Skills 的环境，按该环境约定安装完整文件夹。

## 快速开始

```text
$poster-style-food
图 1 是版式与质感参考，图 2 是我的真实商品图。
为我的桂花拿铁做新品海报，标题“桂花拿铁”，比例 9:16。
配料仅使用我提供的资料，未给价格，不展示价格。
```

```text
$poster-style-tech
只拆解这张参考海报，并说明如何适配我的软件发布主题，先不要生图。
```

每个 skill 的 `references/prompt-examples.md` 中都有三种调用示例、变量说明和完整模板。

## 素材与能力

分析参考海报需要图片查看能力，直接制作需要图片生成能力；精确文字合成需要可用排版工具。工具不可用时会明确交付提示词或待排版视觉，不假称完成了图片。

提供真实商品、品牌资产、人物或界面时，请说明哪些内容必须保留。价格、配料、功效、参数和活动信息以已确认资料为准。示例文案不代表真实商品宣传。

## 文件结构

```text
skills/poster-style-{general,food,beauty,tech,retail}/
  SKILL.md
  agents/openai.yaml
  references/design-map.md
  references/sector-guide.md
  references/review-guide.md
  references/prompt-examples.md
  LICENSE
```

## 验证范围

版本发布前检查了五个 skill 的元数据、引用路径、独立目录完整性与模板内容。未把未执行的图片生成称为实测；不同模型的实际出图效果需在具体参考素材上复核。

## License

[MIT](LICENSE) · Copyright (c) 2026 DalingLab
