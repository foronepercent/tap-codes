# TapTap 兑换码扫描器

定时扫描 [TapTap 官方帖](https://www.taptap.cn/app/521534/topic?type=official) 中的兑换码，将有效期内的新码通过 PushPlus 推送到微信。

## 原理

| 组件 | 说明 |
|------|------|
| GitHub Actions | 每天 08:00 / 20:00 自动触发（cron），支持手动触发 |
| TapTap WebAPI | 取官方帖列表 → 取正文 → 滑动窗口识别兑换码 |
| Server酱 | 免费微信推送（扫码关注公众号，每天5条） |
| actions/cache | 去重缓存，避免重复推送 |

## 使用

1. 在 GitHub 仓库 Settings → Secrets and variables → Actions 添加：
   - `SERVERCHAN_KEY`：你的 Server酱 SendKey（打开 sct.ftqq.com → 微信扫码 → 消息通道 → SendKey）

2. 手动触发测试：仓库 Actions → TapTap 兑换码扫描 → Run workflow

3. 自动执行：每天 UTC 00:00（北京 08:00）和 UTC 12:00（北京 20:00）

## 本地测试

```bash
pip install -r requirements.txt
python scanner.py           # 扫描（需 PUSHPLUS_TOKEN 环境变量）
python test_extractor.py    # 运行单元测试
```