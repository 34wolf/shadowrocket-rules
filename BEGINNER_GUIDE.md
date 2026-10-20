# Beginner Guide

## Safety first

The `input` folder is private and ignored by Git. Never drag `input/lz.conf` into GitHub or include its contents in screenshots.

## Public files

Only reviewed rules, scripts, documentation, tests, workflow, and generated output are public.

## Personal rules

Review one candidate line at a time. Confirm both that it is yours and that its full text is safe to publish before adding it to `custom_rules.conf`.

## Automatic updates

A green Actions check means tests and the build succeeded. A red cross means the previous working output remains available while the failure is investigated.

## 公司内网站点打不开时

先在 Shadowrocket 的「测试规则」中确认域名命中 DIRECT，并确认首页「全局路由」为「配置」。如果关闭 Shadowrocket 后可以访问，继续检查 DNS 和私有 IP 设置，不能仅凭规则命中就认定连接正常。

本项目的生成器会在 `[General]` 中固定设置：

```conf
dns-direct-system = true
private-ip-answer = true
```

第一项让直连域名使用当前网络的系统 DNS，第二项允许公司内网地址作为 DNS 结果。每日自动更新会保留这两项，不需要在客户端反复手改。需要处于能访问公司网络的环境，配置本身不会提供公司网络访问权限。

2026-10-20 排查记录：直连规则和配置模式均正确，单独打开「私有 IP 应答」未恢复；再开启系统 DNS 直连并重新连接后，公司站点恢复访问。

