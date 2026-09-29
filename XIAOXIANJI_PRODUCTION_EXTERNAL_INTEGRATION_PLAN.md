# 校鮮集 Production 外部服務串接規劃

**文件性質：**Production readiness 與外部服務串接計畫，不是正式採購、法律、稅務或服務商承諾。

## 建議的第一個串接順序

建議先從「物流 sandbox」開始，再進入金流 sandbox，原因是物流託運單可以先驗證訂單、地址／取貨 scope、標籤、狀態回傳與冪等，而不會一開始就產生扣款、退款或財務申報風險。實際服務商與是否先做物流，仍須由 owner 核准。

## 六道 Production gate

### Gate 0：責任與服務商確認

確認法人／營業主體、服務區域、物流或金流服務商、付款／發票責任、資料 owner、客訴與退款責任。所有未確認項目標示 `[TODO: 待人工確認]`。

### Gate 1：Contract freeze

凍結校鮮集自己的 adapter contract：request／response、錯誤分類、timeout、retry、idempotency、webhook 驗證、狀態機、audit 與 PII 遮罩。不得把服務商 raw payload 直接暴露給 domain layer。

### Gate 2：Sandbox isolation

以獨立 sandbox credential、sandbox database、sandbox webhook、synthetic fixture 與 isolated UAT 執行。Production URL、token、secret、正式客戶資料不可進入測試環境。

### Gate 3：Failure and replay test

至少驗證 timeout、5xx、重送、亂序 webhook、部分成功、未知狀態、重複託運單／付款、scope mismatch、人工介入與補償流程。所有狀態變更寫入 append-only audit。

### Gate 4：Owner approval

由校鮮集 owner 核准服務商、資料欄位、保存期限、費用、退款／取消規則、webhook 公開入口、監控、備份與事件通報。approval reference 必須寫入 integration registration。

### Gate 5：受控 Production rollout

先以單一組織／單一校點／低風險測試範圍啟用，保留 kill switch、人工覆核、交易上限、告警與 rollback。沒有 owner approval、idempotency、webhook 與 secret reference 時不可啟用 Production。

## 建議先做的物流 sandbox 驗收

1. 建立校鮮集 `ShipmentDraft`。
2. 透過 `ILogisticsProvider` 送出 sandbox label request。
3. 將服務商回應映射為 provider-neutral `ShipmentLabelResult`。
4. 接收 sandbox webhook，驗證簽章與冪等。
5. 模擬 timeout、重送、未知狀態與取消。
6. 確認不會重複建立託運單、不會重複計費、不會誤改訂單完成狀態。
7. 完成 owner review 後才建立 production registration。

## 金流應排在物流之後的原因

金流會引入扣款、退款、支付爭議、對帳、發票與個資風險。應先完成付款責任、退款責任、發票責任、對帳 owner、交易上限、風險控管與人工覆核，再接 sandbox。任何支付結果不明都必須 fail-closed，不能因 timeout 自動判定成功。

## 目前已完成的程式基線

- `ILogisticsProvider`。
- mock 託運單草稿與 label preview API。
- `ExternalIntegrationRegistration`。
- sandbox／production 分離。
- owner approval、credential reference、webhook、idempotency readiness gate。
- `external_integrations` migration。
- readiness focused tests。

## 仍待 owner 決策

- `[TODO: 待人工確認]` 第一個正式物流服務商。
- `[TODO: 待人工確認]` 第一個正式金流服務商。
- `[TODO: 待人工確認]` 正式法人／開票主體。
- `[TODO: 待人工確認]` 正式部署平台與 secret manager。
- `[TODO: 待人工確認]` webhook 網域與事件通報窗口。
- `[TODO: 待人工確認]` 正式 rollout 的組織／校點範圍。
