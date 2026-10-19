from pathlib import Path
p=Path('README.md');old=p.read_text(encoding='utf-8-sig');prefix='# 最新成片：P(doom) — LINE ARCHITECTURE\n\n当前交付：output_v4/Pdoom_Line_Architecture_1080p.mp4\n\n制作说明与复现入口：v4/README.md。此版本全部代码绘制，34段独立线条空间与文字结构，原音轨无重压缩。\n\n以下为较早版本记录：\n\n'
if not old.startswith('# 最新成片'):p.write_text(prefix+old,encoding='utf-8')
p=Path('v4/README.md');s=p.read_text(encoding='utf-8-sig');s+='\n## 最终检查\n\n- 全片完整解码通过。\n- 原始AAC音频码流SHA256完全一致。\n- 558个演唱画幅抽查样本，当前唱句未超出画幅。\n- 12fps动态诊断未检测到演唱段内超过0.5秒的近静止。\n- 强鼓附近有对应的可检测画面波动；该项仅用于节奏诊断，不作为艺术效果高低的客观证明。\n- 对照检查与连续样片已覆盖开场、副歌、左转、破围、GPU剪切等段落。\n'
p.write_text(s,encoding='utf-8')
