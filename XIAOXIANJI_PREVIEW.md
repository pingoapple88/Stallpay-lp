# 校鮮集食品團購企業展示原型

## 原型範圍

本分支將「校鮮集」作為食品團購企業展示的候選名稱，面向企業管理者示範北部 100 所國中小教職員工團購的管理情境。100 所、會員數、訂單數、金額與流程健康度均為合成展示數據，不代表正式服務成果；正式公司名稱、平台網址與營運數據均為 `[TODO: 待人工確認]`。

頁面包含多校與校點管理、會員分群、商品與團購檔期、訂單與配送／取貨、對帳中心，以及 Order AI、MerchLoop、StallPay 的 LINE 互動概念展示。v0.2 新增「個別合作社 LINE 工作台」，可切換北區員生合作社、校園員生合作社、單位福利合作社，以及教職員工／在校學生兩種服務對象，展示各自的 LINE 對話、選單、資格邊界與三產品流程。頁面不呼叫外部 API、不收集會員資料、不建立訂單，也不保存付款資訊。

## 本機預覽

不需要安裝 Node.js 或外部 CDN。可直接執行：

```bash
python3 -m http.server 8091
```

瀏覽器開啟 `http://127.0.0.1:8091/`。若要使用容器，先複製 `.env.example` 為 `.env`，再執行：

```bash
docker compose up --build
```

預設會在 `http://127.0.0.1:8080/` 提供靜態頁面。

## Cloudflare Pages Preview

Cloudflare Pages 專案可使用既有 `wrangler.jsonc` 的 `dist` 輸出目錄。建置命令為：

```bash
python3 scripts/build_cloudflare_pages.py --output dist
```

輸出目錄為 `dist`。Git 分支 Preview 應指向本分支：

```text
feat/xiaoxianji-enterprise-prototype
```

本次未在原始碼中放入 Cloudflare token、帳號 ID 或其他正式憑證。若 Cloudflare Pages 尚未綁定 GitHub 儲存庫，請由具備 Cloudflare 帳號權限的維運人員在 Pages 專案設定中建立 GitHub Preview；正式自有網域、Cloudflare project 與部署 owner 為 `[TODO: 待人工確認]`。

## 產品與 LINE 邊界

Order AI 在本頁只展示「訊息整理、信心閾值與人工確認」的產品概念；MerchLoop 展示會員分群、福利與通知偏好；StallPay 展示 QR／LIFF、取貨編號與狀態通知概念。正式實作應由平台中立的 Adapter 接口隔離外部服務，並由核准的 `ILLMProvider`、`INotificationProvider` 與其他 provider 介面負責替換，不在這個靜態原型中建立正式連線。

## 驗證結果

HTML parser、inline JavaScript `node --check`、禁用詞檢查與瀏覽器桌面版驗證均已執行。瀏覽器驗證確認首屏、平台 tab、FAQ 展開／收合、英文／繁體中文切換、個別合作社切換、教職員／學生切換與展示邊界提醒可用；完整紀錄見 `QA_BROWSER_NOTES.md`。
