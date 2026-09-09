# 校鮮集食品團購企業展示原型

## 原型範圍

本分支將「校鮮集」作為食品團購企業展示的候選名稱，面向企業管理者示範北部 100 所國中小教職員工團購的管理情境。100 所、會員數、訂單數、金額與流程健康度均為合成展示數據，不代表正式服務成果；正式公司名稱、平台網址與營運數據均為 `[TODO: 待人工確認]`。頁尾製作／服務提供者標示為「捷州資訊」。

頁面包含多校與校點管理、會員分群、商品與團購檔期、訂單與配送／取貨、ERP 財務對帳、多校庫存，以及 Order AI、MerchLoop、StallPay 的 LINE 互動概念展示。v0.6 新增「捷州資訊」高可見度頁尾服務提供者列；v0.5 新增教職員福利點數與回饋金自動結算對帳、iMin Falcon 1／F1 收銀與發票列印硬體互動，以及智販機／取物櫃／冷藏設備異常觸發後端任務與 LINE 通知的可重播流程。頁面不呼叫外部 API、不收集會員資料、不建立訂單，也不保存付款資訊。

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

ERP 對帳畫面展示合作社、校點與檔期的應收／已收／待核對／異常狀態；多校庫存畫面展示 SKU、低庫存與跨校調撥概念。成功資料流中的「扣減」是庫存數量扣減，不是金融付款扣款；正式付款、退款與帳務入帳應由獨立 Payment／Finance Adapter 處理。福利模組只展示點數計算、回饋金資格鎖定、退貨窗口與合作社批次事件，不代表正式福利資格、稅務或入帳規則。智販機、取物櫃與 iMin Falcon 1／F1 僅作為取貨／收銀設備選項與互動模擬，不代表正式設備、場地、支付、發票、SDK、開櫃或維運接點已確認。設備異常流程以 EventBus 解耦設備、庫存、任務與 LINE 通知，正式接收者、閾值與補貨 SLA 待確認。Order AI 遇到低信心、商品不唯一或校點衝突時，應停止自動建單，保留事件紀錄並交由合作社窗口確認。

### iMin Falcon 1／F1 公開資料邊界

本原型以使用者所稱「iMin F1」對應公開產品名稱「iMin Falcon 1」作為候選設備；正式型號仍待人工確認。iMin 官方產品頁列出 80mm 熱感印表機、QR／1D／2D 掃描、NFC、Android 11、Wi-Fi、Bluetooth、4G、GPS 與多種連接埠。iMin 官方 SDK 文件與印表機文件提供裝置資訊、初始化、內建印表機、QR／條碼與 Web／JavaScript 列印的整合方向；正式版本仍需依實際設備、韌體、SDK、設備管理、支付與開櫃協議確認。

公開參考：[iMin Falcon 1 官方產品頁](https://www.imin.com/product/falcon-1/)、[iMin SDK 文件](https://oss-sg.imin.sg/docs/en/SDK.html)、[iMin Printer 文件](https://oss-sg.imin.sg/docs/en/Printer.html)、[iMin FAQ](https://www.imin.com/faq/)。

## 驗證結果

HTML parser、inline JavaScript `node --check`、禁用詞檢查與瀏覽器桌面版驗證均已執行。瀏覽器驗證確認首屏、ERP 財務與多校庫存儀表板、福利結算播放、iMin F1 收銀／發票列印流程、設備異常至 LINE 通知流程、Order AI 成功資料流播放、iMin F1／智販機／取物櫃設備切換與取貨回寫模擬、平台 tab、FAQ 展開／收合、英文／繁體中文切換、個別合作社切換、教職員／學生切換與展示邊界提醒可用；完整紀錄見 `QA_BROWSER_NOTES.md`。
