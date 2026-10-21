# 2026-10-21 忍3新增原图清单

本批次共增加 **15 张实际下载的图片**（角色立绘 8、武器 7），所有下方「文件」均为仓库内原始图片，而非指向外部网站的缩略图。每张已经记录实际文件大小、像素宽高、SHA-256 与来源地址；通过 GitHub 文件 API 复查路径存在。

## 新角色、流派与皮肤

| 角色/立绘 | 本地原图 | 图片分辨率 | 资料来源 |
|---|---|---:|---|
| 贺新焰·双焰小椒 | [查看文件](../assets/characters/2026-10-expansion/character_2026_shuangyan_hexinyan.png) | 620×780 | [BWIKI](<https://wiki.biligame.com/nmd3/贺新焰>) |
| 夜叉·隼白 | [查看文件](../assets/characters/skins/skin_043_hayabusa.png) | 620×780 | [BWIKI](<https://wiki.biligame.com/nmd3/%E5%A4%9C%E5%8F%89%C2%B7%E9%9A%BC%E7%99%BD>) |
| 极刃·血影 | [查看文件](../assets/characters/skins/skin_047_bloodshadow.png) | 620×780 | [BWIKI](<https://wiki.biligame.com/nmd3/%E6%9E%81%E5%88%83%C2%B7%E8%A1%80%E5%BD%B1>) |
| 双焰·小椒 | [查看文件](../assets/characters/skins/skin_080_shuangyan.png) | 620×780 | [BWIKI](<https://wiki.biligame.com/nmd3/%E5%8F%8C%E7%84%B0%C2%B7%E5%B0%8F%E6%A4%92>) |
| 雷兽·阿力 | [查看文件](../assets/characters/skins/skin_090_ali_thunder.png) | 620×780 | [BWIKI](<https://wiki.biligame.com/nmd3/%E9%9B%B7%E5%85%BD%C2%B7%E9%98%BF%E5%8A%9B>) |
| 不知火·舞 | [查看文件](../assets/characters/skins/skin_091_mai.png) | 620×780 | [BWIKI](<https://wiki.biligame.com/nmd3/%E4%B8%8D%E7%9F%A5%E7%81%AB%C2%B7%E8%88%9E>) |
| 神炎·小椒 | [查看文件](../assets/characters/skins/skin_089_xiaojiao_shenyan.png) | 620×780 | [BWIKI](<https://wiki.biligame.com/nmd3/%E7%A5%9E%E7%82%8E%C2%B7%E5%B0%8F%E6%A4%92>) |
| 乘霄·戌时 | [查看文件](../assets/characters/skins/skin_092_chengxiao.png) | 620×780 | [BWIKI](<https://wiki.biligame.com/nmd3/%E4%B9%98%E9%9C%84%C2%B7%E6%88%8C%E6%97%B6>) |

## 新武器及幻化

| 武器或幻化 | 本地原图 | 图片分辨率 | 资料来源 |
|---|---|---:|---|
| 伏溟九渊 | [查看文件](../assets/weapons/2026-10-expansion/weapon_2026_fuming_jiuyuan.png) | 555×555 | [BWIKI](<https://wiki.biligame.com/nmd3/伏溟九渊>) |
| 尽滅·共逐风 | [查看文件](../assets/weapons/2026-10-expansion/weapon_2026_jinmie_feng.png) | 555×555 | [BWIKI](<https://wiki.biligame.com/nmd3/尽滅>) |
| 风月含袖·流泠 | [查看文件](../assets/weapons/2026-10-expansion/weapon_2026_fengyue_liuling.png) | 555×555 | [BWIKI](<https://wiki.biligame.com/nmd3/风月含袖>) |
| 巨阙·缚日 | [查看文件](../assets/weapons/2026-10-expansion/weapon_2026_juque_furi.png) | 555×555 | [BWIKI](<https://wiki.biligame.com/nmd3/巨阙·缚日>) |
| 怒鲤双生·寂鲤并蒂 | [查看文件](../assets/weapons/2026-10-expansion/weapon_2026_nuli_jibi.png) | 555×555 | [BWIKI](<https://wiki.biligame.com/nmd3/怒鲤双生>) |
| 百雷·拂晓·龙泓 | [查看文件](../assets/weapons/2026-10-expansion/weapon_2026_bailei_longhong.png) | 555×555 | [BWIKI](<https://wiki.biligame.com/nmd3/百雷·拂晓>) |
| 百炼 | [查看文件](../assets/weapons/wiki/wiki_weapon_102_bailian.png) | 520×520 | [BWIKI](<https://wiki.biligame.com/nmd3/%E7%99%BE%E7%82%BC>) |

## 自动扩充和待处理事项

- [角色皮肤采集目标](../catalog/wiki_illustration_targets.json)：已将乘霄·戌时与外观、风铭·戌时皮肤、双焰·小椒、银枭/伊鹤新增服饰等加入候选；只有检测到明确的「立绘」图片、下载并通过校验后才入库。
- [武器采集目标](../catalog/wiki_weapon_targets.json)：包括新武器**焚天**、百炼、破雾·贯羽、尽滅、伏溟九渊等。**焚天**有官方上线资料，但本轮未取得经验证原图，因此不计入上述成果。
- [武器采集程序](../scripts/discover_wiki_weapons.py) 和 [自动采集流程](../.github/workflows/expand-weapons.yml) 会记录无法获取的目标；未成功的不会伪装成已下载。
- [素材 JSON](../catalog/assets.json) 的 `download_status=downloaded` 表示图片已通过脚本下载格式检查并保存，`not_downloaded` 仅是候选。
- [下载入口](../index.html) 只展示已下载文件。仍需人工逐图检查内容是否适合后续分层制作、是否存在被截断身体或水印；格式/像素校验不等于逐张视觉质检。

**版权说明：** 本仓库属于非官方个人视觉资料索引，游戏立绘、武器图片及宣传图的版权归权利方所有；在确认权利范围前不可据此声称可商用或自由转载。
