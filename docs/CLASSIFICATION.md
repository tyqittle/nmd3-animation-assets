# 忍3素材分类规范 v2（2026-10-21）

本规范用于 [网页素材图鉴](../index.html)、[JSON主索引](../catalog/assets.json)、[CSV索引](../catalog/assets.csv) 及后续自动采集。**分类依据来源标题、角色页和资源用途，不冒充已经逐张人工看图。** `visual_review=pending` 标明尚待内容复核。

## 分类原则

大类是 **category**，细类是 **subcategory**。一个忍者角色可以包含多个流派、皮肤和参考动作；一个武器系列可以包含本体和幻化。资源文件在 `assets/` 内的位置为**历史存放路径**，不再拿目录名当分类依据；这样修分类不会让已经收藏的原图 URL 404。

| 大类 | category | 细分类 subcategory | 规则 |
|---|---|---|---|
| 忍者角色 | characters | base_portrait（基础立绘） | 忍者本体 |
| 忍者角色 | characters | style_portrait（流派立绘） | 同一忍者的战斗流派/初始流派外观，并不等于购买的皮肤 |
| 忍者角色 | characters | costume_portrait（角色皮肤） | 时装、节庆衣装、明确的额外外观 |
| 忍者角色 | characters | pose_reference（动作参考） | 攻击、跳跃等姿势图，不独立创建角色 |
| 忍者角色 | characters | alternate_portrait / character_reference / unreviewed_portrait | 不同版本、宣传素材或身份待确认的候选 |
| 武器 | weapons | weapon_art | 本体武器图 |
| 武器 | weapons | weapon_appearance | 武器外观、外装、幻化；仍属武器 |
| Boss与怪物 | bosses | boss_art | 非可操作敌人与Boss |
| 场景参考 | scenes | scene_reference | 具有场景表现价值；不承诺“无角色、无文字” |
| 壁纸与构图 | wallpapers | wallpaper_composite | 壁纸、角色+场景合成画面、场景构图参考 |
| 活动宣传 | promos | event_promo | 周年庆、纪念、版本宣传等主视觉 |
| 战斗特效 | effects | skill_effect_reference | 忍术截图、技能表现、战斗特效 |

**示例：**
- `雷兽·阿力`、`神炎·小椒`、`乘霄·戌时`：归属各自忍者的**流派立绘**，不是看见“皮肤”二字就全部标记为服装。
- `贺新焰·双焰小椒`、`神乐·琳·巫女`：归属人物的**角色皮肤/时装**。
- `百雷·拂晓·龙泓`、`怒鲤双生·寂鲤并蒂`：**武器幻化**；不能叫 `skin_illustration` 角色皮肤。
- `樱火·荧·樱火忍术展示`：属于**战斗特效参考**；没有静态立绘属性。
- `七周年·神炎铸赤心`：属于**活动宣传**，而非可直接复用的空场景。
- `青绿水墨鸟居`：标为**场景参考**，是否纯净要人工看图确认。

## 元数据约束

- `id` 唯一且稳定；不根据分类改变原始文件 ID。
- `name` 保存实际物件名称，`character` 应是**人物主体**（如“小椒”），而非“神炎·小椒”这样的流派名称。
- `weapon_family` 保存武器系列，以便检索幻化。
- `subcategory` 必须与顶级 `category` 对应，任何未知类型都必须**显式待复核**，不能偷偷默认为角色皮肤。
- `source_page` 和 `local_path` 分别是外部来源、已下载仓库文件。逻辑分类发生变化时，**不挪动二进制图片文件**。
- `download_status=downloaded` 才能在图鉴展示，待采集候选不能计入实图总数。
- `visual_review=pending` 是分类内容还没经过逐张目检；不要把脚本验证图片格式等同于内容准确。
- 原站图片可能有版权限制；保存索引不意味着拥有再分发或商用授权。

## 后续采集要求

`catalog/wiki_illustration_targets.json` 的每项明确 `asset_type`。自动发现程序 `scripts/discover_wiki_art.py` 以该字段存储 `subcategory`，**不得继续把所有忍者外观标为 `skin_illustration`**。来源不明确的放到 `unreviewed_portrait`。

武器发现程序从真实图页下载图片，按 `weapon_art` 归类；如果后续引入新幻化目标，必须明确设置 `asset_type=weapon_appearance`，并绑定 `weapon_family`。更新元数据后运行：

```bash
python scripts/validate_taxonomy.py
python scripts/audit_assets.py
```

网页的“较高清”仅按像素最大边筛选，分类不等于画质或可编辑分层质量。实际制作MV/动画前请进一步审核**角色是否完整、背景是否可用、图像是否含水印和错误对应**。
