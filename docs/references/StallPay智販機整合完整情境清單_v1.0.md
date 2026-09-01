# StallPay 智販機整合完整情境清單

**文件版本：** v1.0  
**產品權威基線：** `pingoapple88/stallpay-v2@f883fa9e617b41e8e0885ad821975f56bb6ae99f`  
**範圍：** StallPay 前線銷售、付款後履約、智販機控制、取貨、現場例外、設備狀態與上游交接  
**正式設備狀態：** `[TODO: 待天來設備 owner、API v2.7 文件、受控環境與實機驗證]`

## 一、責任邊界

StallPay 是**前線銷售與履約層**，負責消費者商品展示、QR／LIFF 操作、購物車、訂單、付款流程協調、取貨資格、取貨碼、設備操作意圖、設備結果呈現、叫號、現場異常與補償意圖。設備供應商能力必須包在 `IVendingMachineProvider`；StallPay 核心流程不得直接綁定天來專屬 API。[1]

ERP Core 是**後端財務與庫存事實層**，負責主價格、正式庫存總帳、交易 Ledger、支付勾稽、電子發票、退款勾稽與正式財務輸出。StallPay 只把訂單、付款結果、設備結果、取貨結果、取消、退款意圖與人工調整結果，以版本化 API、簽章 Webhook 或可靠事件交給 ERP，不直接讀寫 ERP 資料庫。[1]

| 標記 | 定義 |
|---|---|
| `EXISTING` | 權威基線已有程式或明確流程 |
| `PARTIAL` | 有介面、資料模型或其中一段，但尚未形成完整可用流程 |
| `PLANNED` | StallPay 應做，但目前基線尚未完成 |
| `BLOCKED` | 受設備 owner、API 文件、測試機、正式金鑰或中央 Gate 阻塞 |
| `OTHER_OWNER` | 正式事實或審核由 ERP、支付、發票、會員或設備 owner 負責 |

## 二、五條主要端到端旅程

| Journey | 完整流程 | StallPay 角色 |
|---|---|---|
| `J1` 現場智販機購買 | 掃 QR／開啟頁面 → 選商品 → server 查價 → 建訂單 → 付款 → 驗證付款 → 發出設備操作 → 出貨 → 顯示結果 → 寫 audit／事件 | 主責 |
| `J2` 線上訂購、店家製作、機台取餐 | 線上選餐 → 付款 → 建／找會員 → 計算格位 → 綁定格位 → 通知店家製作 → 店家巡補上架 → 確認所有格位完成 → 發取貨 QR → 顧客到機台取餐 | 主責前線與履約；正式庫存由 ERP |
| `J3` 預訂／會員券取貨 | 會員識別 → 查券／餘額 → 選據點與日期 → 驗證營業日與截止時間 → 扣券或付款 → 建預訂 → 到店核銷 → 取餐號／取貨碼 → 設備履約 | 主責；會員主檔透過 Adapter |
| `J4` 定期訂閱取貨 | 訂閱到期 → 冪等檢查 → 自動扣款 → 備貨工單 → 產取貨資格 → 通知 → 實際取貨 → 取貨後才列入設備營收／結算 | StallPay 協調；正式扣款受支付 Gate |
| `J5` 格口出租／寄物自取 | 建格口租約 → 商家寄物 → 產取貨碼 → 通知買家 → 買家驗證 → 開格／取物 → 完成或逾期 → 月租帳單 | 延伸情境；設備控制仍走 Provider |

## 三、完整情境矩陣

### A. 租戶、門店、機台與憑證

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| A01 | 建立智販機主檔 | 保存 `company_id`／`store_id`、`machine_code`、名稱、地點、櫃型、溫區與 Provider 類型 | `EXISTING` |
| A02 | 一個門店綁定一台機台 | 以 server-side tenant scope 建立綁定 | `EXISTING` |
| A03 | 一個門店綁定多台機台 | 列表、選擇、同步與報表都要按機台分流 | `EXISTING／PARTIAL` |
| A04 | 同一機台不可跨門店重複綁定 | 唯一約束與 ownership 驗證 | `PARTIAL`；目前主要約束是 store+machine |
| A05 | 解除綁定 | 軟停用，不刪歷史訂單、銷售、取貨與 audit | `EXISTING` |
| A06 | 重新啟用機台 | 重新核對 ownership、憑證與資料範圍 | `EXISTING／PARTIAL` |
| A07 | 機台停用 | 停止新訂單／新取貨操作，保留唯讀查詢 | `PLANNED` |
| A08 | 機台位置變更 | 更新地點並留下變更 audit | `PARTIAL` |
| A09 | 機台櫃型／溫區設定 | 定義常溫、冷藏、冷凍、加熱及上下限 | `EXISTING` |
| A10 | 每門店獨立天來 company／Token | per-store／per-machine 管理，不得全域混用 | `EXISTING／需治理複核` |
| A11 | Token 加密保存 | 寫入前加密；查詢與 UI 不回傳 Token | `EXISTING` |
| A12 | Token 輪替 | 新舊版本切換、失敗回滾、audit | `PLANNED` |
| A13 | Base URL 分環境 | sandbox／測試機／正式環境外部化並 fail-closed | `BLOCKED`；目前正式分類未核准 |
| A14 | 機台 owner 交接 | 保留歷史事實，新的操作權限自生效日開始 | `PLANNED／OWNER_TBD` |
| A15 | RBAC | 店員只操作所屬門店；管理員才能綁定、停用或改設定 | `PARTIAL`；router 有 store scope，細權限仍需驗證 |

### B. 機台、商品、貨道與格口 Mapping

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| B01 | 讀取機台清單 | 取得 `machine_code`／名稱／櫃數，不接受前端自報 ownership | `PARTIAL／BLOCKED`；Client 有方法，正式唯讀探索未核准 |
| B02 | 讀取商品主檔 | 取得 `commodity_code`、名稱、規格、圖片與原始價格 | `PARTIAL／BLOCKED` |
| B03 | 讀取機台商品 Mapping | 取得 `machine_code + layer + commodity_code` | `PARTIAL／BLOCKED` |
| B04 | A1～I4 共 36 格 Mapping | 建立格位編碼、狀態與商品綁定 | `PLANNED`；精確天來 layer 規則待文件確認 |
| B05 | 兩組機台 72 格 Mapping | 每組保有獨立 machine/module scope | `PLANNED` |
| B06 | 單品占一格 | 找第一個符合溫區、尺寸與狀態的空格 | `PLANNED` |
| B07 | 單品占多格 | 依商品數量／包裝計算所需格數並原子保留 | `PLANNED` |
| B08 | 多品拆格 | 對每個品項分配一格或多格，保存 order-item-slot 關係 | `PLANNED` |
| B09 | 優先連續格位 | 需要兩格時優先 A2+A3 等連續格 | `PLANNED` |
| B10 | 無連續格但有零散格 | 依政策允許拆分，或回傳不可履約 | `PLANNED` |
| B11 | 不同溫區不可混放 | 冷藏、冷凍、加熱與常溫商品只能分配相容格位 | `PARTIAL`；已有溫區 config，缺分配引擎 |
| B12 | 格口維修中 | 排除不可用格位，不可配置新訂單 | `PLANNED` |
| B13 | 格口已保留 | 不可被另一訂單再次分配 | `PLANNED` |
| B14 | 格口已上架 | 等待指定會員取貨，不可轉給其他訂單 | `PLANNED` |
| B15 | 格口逾時釋放 | 先對帳是否已上架／已取貨，再釋放 | `PLANNED` |
| B16 | 商品 Mapping 不存在 | fail-closed，進 `manual_review`，不可猜 commodity_code | `PLANNED／BLOCKED` |
| B17 | 商品 Mapping 重複或矛盾 | 停止配置，交人工確認 | `PLANNED` |
| B18 | 商品停用／停售 | 前台隱藏；既有訂單依補償規則處理 | `PARTIAL` |
| B19 | 商品售罄 | 阻止建立新訂單，提供替代商品／取貨點 | `PARTIAL` |
| B20 | Mapping 版本變更 | 訂單保存當時 mapping snapshot，不回寫歷史 | `PLANNED` |

### C. 顧客、會員與資格

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| C01 | QR 開啟 LIFF／Web | 從 QR 解析 opaque store／machine reference | `EXISTING／PARTIAL` |
| C02 | LINE 登入顧客 | 取得 LINE 身分並綁定門店情境 | `EXISTING` |
| C03 | 新顧客建立會員 | 以手機 E.164 為錨，LINE ID 為屬性 | `EXISTING` |
| C04 | 舊會員自動識別 | LINE ID 找既有會員，失敗回手動認證 | `EXISTING` |
| C05 | OTP 驗證 | 依 ENV／政策啟用，失敗不可建立敏感綁定 | `EXISTING／PARTIAL` |
| C06 | 多國電話格式 | 支援台灣、日本、泰國、美國、印尼 | `EXISTING` |
| C07 | 個資同意 | DOB 等非必要資料須明確同意；未同意仍能走必要流程 | `EXISTING／PARTIAL` |
| C08 | 會員與天來 code 同步 | 建立／更新 `tenlifeCode`，不得跨租戶重用 | `EXISTING／PARTIAL` |
| C09 | 會員專用 QR | 產生不可預測、可失效、可輪替的 QR／barcode | `PARTIAL` |
| C10 | 會員 QR 遺失／外洩 | 撤銷舊碼、產新碼、所有操作 audit | `PLANNED` |
| C11 | 會員解除 LINE 綁定 | 保留交易與會員歷史，只解除登入屬性 | `EXISTING` |
| C12 | 匿名散客 | 可現場購買；只進交易對帳，不自動綁會員或賺點 | `EXISTING` |
| C13 | 會員權益不足 | 不產取貨資格，導向正常付款或顯示 blocked | `EXISTING／PARTIAL` |
| C14 | 門店未啟用智販機權益 | 不觸發天來券／設備履約 | `EXISTING` |

### D. 商品展示、購物車與價格

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| D01 | 顯示機台可售商品 | 只顯示目前 machine/store 可售 SKU | `PARTIAL` |
| D02 | server-side pricing | 前端只送 SKU／quantity；價格由伺服器查詢與重算 | `EXISTING` |
| D03 | client forged price | 忽略／拒絕前端價格，留下 audit | `EXISTING` |
| D04 | 商品價格版本 | 訂單保存價格版本與計價時間 | `PARTIAL` |
| D05 | ERP 主價格更新 | StallPay 接收版本化價格更新並更新快取 | `PLANNED／OTHER_OWNER` |
| D06 | 即時促銷價格 | 前台顯示優惠價、原價、有效期與來源 | `PARTIAL` |
| D07 | 近效期自動降價 | 依活欄位階梯計算，冪等更新並通知 | `EXISTING／正式設備更新 BLOCKED` |
| D08 | 降價失敗 | 保留舊價、標示同步失敗，不得前後價不一致後仍成交 | `PLANNED` |
| D09 | 購物車新增／刪除／改數量 | 每次送出重新查價與庫存／配額 | `EXISTING／PARTIAL` |
| D10 | 重複 SKU | 正規化為單一 SKU 數量或拒絕歧義 payload | `EXISTING` |
| D11 | 無效 SKU | 拒絕，不接受自由文字當正式商品識別 | `EXISTING` |
| D12 | 數量為零／負數／超上限 | 拒絕並返回可修正提示 | `EXISTING` |
| D13 | 購物車價格變動 | 顯示新價格並要求重新確認 | `PLANNED` |
| D14 | 多機台拆單 | 依可用格位／商品 Mapping 拆成子履約單 | `PLANNED` |
| D15 | 空菜單 | 顯示 empty／blocked fallback，不把空資料當系統成功可購買 | `EXISTING／PARTIAL` |

### E. 配額、庫存與預留

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| E01 | 查詢機台即時庫存 | 透過 Provider 唯讀查詢，不直接綁天來 API | `PARTIAL／BLOCKED` |
| E02 | 庫存為推算值 | UI 明示 estimated，不能當 ERP 正式庫存 | `EXISTING` |
| E03 | 商品足量 | 允許進入下單／配額預留 | `PARTIAL` |
| E04 | 商品不足 | 阻止下單或只允許可供數量 | `PARTIAL` |
| E05 | 完全售罄 | 回 `sold_out`，提供替代商品／據點 | `EXISTING／PARTIAL` |
| E06 | 預訂配額原子扣減 | 以 DB transaction／唯一約束防超賣 | `EXISTING` |
| E07 | 單一取貨點配額不足 | 回剩餘量與替代取貨點 | `EXISTING` |
| E08 | 全通路總量超額 | 回滾本次扣減 | `EXISTING` |
| E09 | 重複預留 | 同 idempotency key 回既有結果，不重扣 | `PLANNED／部分服務已有冪等` |
| E10 | 預留逾時 | 對帳後釋放，避免已付款訂單被釋放 | `PLANNED` |
| E11 | 取消訂單釋放配額 | 依訂單狀態與設備結果決定是否可釋放 | `PLANNED` |
| E12 | 出貨完成扣減意圖 | StallPay 發履約成功事件；ERP 原子更新正式庫存 | `PLANNED／OTHER_OWNER` |
| E13 | 設備庫存與 ERP 不一致 | 建差異記錄，進 reconciliation／manual review | `PLANNED` |
| E14 | 低庫存告警 | 依 ENV／DB 閾值、機台與商品每日去重 | `EXISTING／正式資料 BLOCKED` |
| E15 | 補貨工單 | 建 pending→in_progress→done，指派人員與品項 | `PARTIAL`；schema 存在，完整 workflow 待補 |
| E16 | 補錯商品 | 掃描商品與預定 mapping 不一致即阻擋 | `PLANNED` |
| E17 | 補錯數量 | 超容量／超工單量時阻擋並 audit | `PLANNED` |
| E18 | 重複補貨 | 已滿或工單已完成時拒絕 | `PLANNED` |

### F. 訂單、付款與取貨資格

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| F01 | 建立智販機訂單 | server-owned company/store/machine、SKU、價格、數量與 UTC | `EXISTING／PARTIAL` |
| F02 | operation idempotency | 同 key 同 payload 回舊結果；同 key 不同 payload fail-closed | `EXISTING` |
| F03 | 付款前重新查價 | 避免購物車舊價成交 | `PLANNED` |
| F04 | LINE Pay | 透過既有 `IPaymentProvider` | `EXISTING Provider／正式 Gate` |
| F05 | 綠界信用卡 | 透過既有 `IPaymentProvider` | `EXISTING Provider／正式 Gate` |
| F06 | Apple Pay | 透過 Adapter aggregation | `PARTIAL／owner TODO` |
| F07 | Intella Scan2Pay | 透過既有 Adapter | `EXISTING Provider／正式 Gate` |
| F08 | 機台現場現金 | 匿名 Sales；StallPay 匯入對帳，不綁會員 | `EXISTING／PARTIAL` |
| F09 | 悠遊卡／票證 | 解析為機台 Sales payment detail | `EXISTING／PARTIAL` |
| F10 | 混合支付 | 合併兩段 payment detail，保留原始明細 | `PARTIAL` |
| F11 | 付款成功 | 才能建立設備履約資格／取貨資格 | `PLANNED`；券流程已有事件型實作 |
| F12 | 付款失敗 | 不配置／不出貨，允許安全重試付款 | `EXISTING／PARTIAL` |
| F13 | 付款 unknown | 不出貨；查詢 provider 狀態後再決定 | `PLANNED` |
| F14 | Webhook 重送 | 簽章、時效、冪等與 payload 一致性檢查 | `EXISTING／PARTIAL` |
| F15 | 付款成功但資格建立失敗 | 訂單進 `manual_review`／`compensation_pending` | `PLANNED` |
| F16 | 會員券支付／扣券 | 先驗券、確認 ACTIVE 與數量，再原子扣券 | `EXISTING` |
| F17 | 券不存在／已使用 | 拒絕並顯示可修正狀態 | `EXISTING` |
| F18 | 券數量不足 | 導向一般付款或修改數量 | `EXISTING` |
| F19 | 部分核銷 | 扣部分 quantity，券維持 ACTIVE | `EXISTING` |
| F20 | 全量核銷 | quantity 歸零並改為 REDEEMED | `EXISTING` |
| F21 | 付款後取消 | 先確認設備是否未操作，再發取消／補償意圖 | `PLANNED` |
| F22 | 電子發票狀態 | StallPay 顯示 provider-neutral 狀態；正式開立由發票／ERP owner | `PARTIAL／OTHER_OWNER` |

### G. 線上訂餐、備餐、格位配置與上架

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| G01 | 付款後判斷新舊會員 | 新會員建檔並透過 Adapter 同步設備會員識別 | `PARTIAL` |
| G02 | 計算餐點占格數 | 依數量、尺寸、包裝與溫區計算 | `PLANNED` |
| G03 | 查指定機台剩餘格位 | 使用權威 machine-slot mapping | `BLOCKED` |
| G04 | 原子綁定訂單與格位 | 一次保留所有格位；任一失敗則全部回滾 | `PLANNED` |
| G05 | 單訂單多格 | 保存每格品項、數量與 readiness | `PLANNED` |
| G06 | 多機台拆分 | 每個子單有 machine、slots 與獨立履約狀態 | `PLANNED` |
| G07 | 通知店家新訂單 | 顯示餐點、數量、格位、截止時間與特殊需求 | `EXISTING／PARTIAL` |
| G08 | 店家接受訂單 | pending→accepted，留下 operator／UTC／audit | `PLANNED` |
| G09 | 店家拒絕訂單 | 付款後拒絕進補償；付款前直接取消 | `PLANNED` |
| G10 | 店家開始製作 | accepted→preparing | `EXISTING（取餐票流程）／智販機格位未接` |
| G11 | 製作完成 | preparing→ready_for_stocking | `PARTIAL` |
| G12 | 巡補人員登入 | RBAC 限制可操作的機台／格位／供應商 | `PLANNED` |
| G13 | 掃描商品條碼 | 驗證 commodity、order item 與 slot mapping | `PLANNED` |
| G14 | 上架一格成功 | 更新該格 readiness，不提早通知整單完成 | `PLANNED` |
| G15 | 多格部分上架 | 保持 `partially_stocked`；不可發完整取貨通知 | `PLANNED` |
| G16 | 全部格位上架 | 所需格位全部 confirmed 後改 `ready_for_pickup` | `PLANNED` |
| G17 | 上架錯格 | 拒絕或要求移回正確格位，留下 audit | `PLANNED` |
| G18 | 上架商品不符 | 進 blocked／manual review | `PLANNED` |
| G19 | 上架數量不足 | 保持部分完成，通知店家補齊 | `PLANNED` |
| G20 | 上架逾時 | 通知店家／客服；依政策取消或補償 | `PLANNED` |
| G21 | 舊訂單內容變更 | 取消舊設備訂單／格位保留後，以新 operation 建完整新訂單 | `PLANNED` |
| G22 | 同會員重複送單 | 依 idempotency／order version 返回既有單，不重複占格 | `PLANNED` |

### H. 取貨碼、QR 與通知

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| H01 | 付款後產取貨資格 | 以 order 為冪等單位，不重複產碼 | `EXISTING／PARTIAL` |
| H02 | 一件商品一張券 | quantity 逐張產券 | `EXISTING` |
| H03 | 一張碼開多格 | 權限內綁多格，操作回執需逐格回報 | `PLANNED` |
| H04 | 多商品多碼 | 可逐品項取貨並追蹤剩餘資格 | `EXISTING／PARTIAL` |
| H05 | 標準 QR 顯示 | 條碼資料轉標準 QR，避免在 URL 暴露秘密 | `PARTIAL` |
| H06 | 取貨碼有效期 | 由活欄位計算，UI 顯示 UTC 轉在地時間 | `EXISTING` |
| H07 | LINE 發送 | 透過 `INotificationProvider`／Adapter 推播 | `EXISTING／正式 Gate` |
| H08 | App／Email／SMS 發送 | 同一 notification contract 的不同 Adapter | `PLANNED` |
| H09 | 通知失敗 | 不回滾已付款訂單；保存資格並提供重新取得入口 | `PLANNED` |
| H10 | 通知重送 | 使用同一資格，不產新碼 | `PLANNED` |
| H11 | Ready 通知 | 只在全部所需格位 ready 後發送 | `PLANNED` |
| H12 | 取貨提醒 | 依 12h／20h 等活欄位提醒 | `EXISTING` |
| H13 | 逾期通知 | 顯示不可取貨與後續處置 | `PARTIAL` |
| H14 | 會員 QR 長期碼 | 作為身份認證；每次訂單仍需 server 驗證 entitlement | `PARTIAL` |
| H15 | 一次性訂單碼 | 成功取貨後立即失效，防止重播 | `PLANNED` |

### I. 設備開門／出貨執行

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| I01 | 驗證 order／pickup token | server 驗證訂單、會員、機台、格位、有效期與狀態 | `PLANNED` |
| I02 | 掃碼取貨 | 相機／掃描器讀碼後送 StallPay 驗證 | `PLANNED／BLOCKED` |
| I03 | 手動輸入取貨碼 | 限速、防暴力破解、遮罩顯示 | `PLANNED` |
| I04 | App／LIFF 點擊開門 | 需二次確認機台 proximity／操作資格 | `PLANNED` |
| I05 | 開單一格門 | 呼叫 `IVendingMachineProvider.open_slot` 類能力 | `PLANNED／BLOCKED`；目前介面沒有此方法 |
| I06 | 一次開多格 | 逐格 operation receipt；部分成功可追蹤 | `PLANNED／BLOCKED` |
| I07 | 螺旋貨道出貨 | 呼叫 `dispense` 並等待感測器結果 | `PLANNED／BLOCKED` |
| I08 | 履帶／升降機出貨 | Provider 映射不同硬體流程，domain 不感知 SDK | `PLANNED／BLOCKED` |
| I09 | 開門指令 accepted | 只代表設備接受，不代表顧客已取貨 | `PLANNED` |
| I10 | dispensing | 顯示處理中，禁止再次送出 | `PLANNED` |
| I11 | dispensed／door_opened | 記錄明確成功、UTC、operation_ref 與設備回執 | `PLANNED／BLOCKED` |
| I12 | 顧客關門 | 若有門磁，記錄 door_closed；無感測器則標 unknown | `PLANNED／BLOCKED` |
| I13 | 取貨完成 | 成功設備事實＋必要人工／感測確認後改 picked_up | `PLANNED` |
| I14 | 多格全部成功 | 整單 completed，發 Order_Completed 相容事件 | `PLANNED` |
| I15 | 多格部分成功 | 保持 partial_fulfillment，未成功格進補償流程 | `PLANNED` |
| I16 | 同 operation 重送 | 回既有 receipt，不重複開門／出貨 | `PLANNED` |
| I17 | 不同 payload 共用 idempotency key | fail-closed 並 audit | `PLANNED` |
| I18 | 設備結果查詢 | `get_dispense_status`／`get_operation_status` | `PLANNED／BLOCKED`；目前介面缺少 |
| I19 | 設備結果回報 | 版本化 callback／poll result 驗簽後更新狀態 | `PLANNED／BLOCKED` |
| I20 | 取消尚未送出指令 | 明確未送出才可安全取消 | `PLANNED` |
| I21 | 已送出指令不可直接取消 | 先查狀態／對帳，避免貨已出仍退款 | `PLANNED` |
| I22 | 燈光／格口提示 | 透過 Provider 控制，作為取貨輔助 | `PLANNED／BLOCKED` |
| I23 | 顧客未拿商品但門已開 | 依感測器或人工確認，不自動判定已取 | `PLANNED` |
| I24 | 顧客拿錯格商品 | 保存影像／感測／操作證據，進人工處理 | `PLANNED／設備能力 TODO` |

> **核心缺口：** 目前 `IVendingMachineProvider` 僅定義商品、Sales、設備狀態、廣告與折扣；尚未定義 `reserve`、`open_slot`、`dispense`、`get_operation_status`、`cancel_operation` 或 `reconcile_operation`。天來 Client 目前也只含查詢、券與銷售相關端點，沒有已核准的開門／出貨端點，因此 I05～I24 不可宣稱正式完成。[2] [3]

### J. 設備與履約異常

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| J01 | 機台離線於送出前 | 明確未送出可標 retryable；仍使用同一冪等鍵 | `PLANNED` |
| J02 | 送出後連線中斷 | 狀態轉 `unknown／needs_reconciliation`，禁止自動重送 | `PLANNED` |
| J03 | 請求 timeout | 不等於未出貨；先查設備結果 | `PLANNED` |
| J04 | 設備 busy | 顯示等待或受控重試，不建立第二 operation | `PLANNED` |
| J05 | 格口卡住／jam | 進 `jammed`，不可自動再開其他格 | `PLANNED` |
| J06 | 商品卡貨 | 區分明確未出、部分移動、結果未知 | `PLANNED` |
| J07 | 感測器矛盾 | 進 `manual_review`，不可猜已出貨 | `PLANNED` |
| J08 | 門未開 | 若設備明確回失敗，建立補償意圖 | `PLANNED` |
| J09 | 門已開但未關 | 告警店員／顧客，暫停同格新操作 | `PLANNED` |
| J10 | 開錯格 | 立即告警、停止後續格、人工盤點 | `PLANNED` |
| J11 | 出錯商品 | 保存實際 commodity／slot 證據，進客服補償 | `PLANNED` |
| J12 | 少出一件 | 整單 partial，不可直接標 completed | `PLANNED` |
| J13 | 多出一件 | 記錄庫存差異與風險事件 | `PLANNED` |
| J14 | 機台回重複成功 | 以 operation_ref 去重，不重複扣庫存或發事件 | `PLANNED` |
| J15 | 回應格式錯誤 | fail-closed、遮罩 raw payload、進 manual review | `PLANNED` |
| J16 | API state／message 語意不明 | 停止重試，要求 owner 確認 | `BLOCKED` |
| J17 | company scope 不一致 | 拒絕所有資料與控制操作，安全事件 audit | `BLOCKED／PLANNED` |
| J18 | machine_code 不屬於門店 | 403／blocked，不發設備命令 | `PLANNED` |
| J19 | commodity_code 不在該機台 | 阻止出貨，進 mapping 修正 | `PLANNED` |
| J20 | 取貨碼過期 | 不開門；顯示逾期處理入口 | `EXISTING／設備未接` |
| J21 | 取貨碼已使用 | 阻止重播並顯示原完成紀錄 | `PLANNED` |
| J22 | 取貨碼被其他帳號使用 | 阻止並建立資安 audit | `PLANNED` |
| J23 | 顧客掃錯機台 | 提示正確機台／地點，不跨機操作 | `PLANNED` |
| J24 | 店家未上架 | 不發可取貨通知，不允許開門 | `PLANNED` |
| J25 | 多格未全部 ready | 保持 blocked，不允許整單取貨 | `PLANNED` |
| J26 | 支付成功但無空格 | 立即進人工處理／退款意圖或改機 | `PLANNED` |
| J27 | 支付成功但出貨失敗 | 建 `compensation_pending`，不由設備 Adapter 直接退款 | `PLANNED／OTHER_OWNER` |
| J28 | 支付成功且結果 unknown | 凍結退款與重送，先 reconciliation | `PLANNED` |
| J29 | 明確未出貨 | 可建立退款／替代商品／人工聯絡意圖 | `PLANNED` |
| J30 | 明確已出貨 | 關閉出貨補償，不可重複出貨／退款 | `PLANNED` |
| J31 | 部分出貨 | 只補償未履約部分，金額以 server order snapshot 計算 | `PLANNED` |
| J32 | 退款成功但 ERP 未入帳 | 保留 reconciliation pending | `OTHER_OWNER／PLANNED` |
| J33 | ERP 已扣庫存但設備失敗 | 發 release／reconcile intent，不直接改 ERP DB | `OTHER_OWNER／PLANNED` |
| J34 | 網路長時間中斷 | 離線 UI 顯示唯讀／受控操作；高風險命令 fail-closed | `PLANNED` |
| J35 | 復網重送佇列 | 先查 operation 狀態，再決定是否送出 | `PLANNED` |
| J36 | 單機失敗 | 不應中斷其他機台的同步／監控 | `EXISTING（同步）` |
| J37 | 全批次失敗 | 告警、保留 checkpoint、下輪從安全位置重啟 | `PARTIAL` |

### K. 取餐號、備餐與現場人工操作

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| K01 | server-issued 取餐號 | 前端不可指定或偽造 queue number | `EXISTING` |
| K02 | 建立取餐票 | 保存會員、品項、數量、門店、有效期與 audit | `EXISTING` |
| K03 | 同券重送 | 回既有 ticket，不重複核銷或出號 | `EXISTING` |
| K04 | 待備清單 | 依門店列 pending／preparing | `EXISTING` |
| K05 | pending→preparing | 店員開始備餐 | `EXISTING` |
| K06 | pending／preparing→ready | 備妥並通知顧客 | `EXISTING` |
| K07 | ready→picked_up | 完成取貨 | `EXISTING` |
| K08 | pending／preparing／ready→expired | 到期未取 | `EXISTING` |
| K09 | 非法狀態跳轉 | 拒絕並寫 invalid_transition audit | `EXISTING` |
| K10 | ticket 不存在 | 顯示 not found，不建立替代 ticket | `EXISTING` |
| K11 | 店員代客核銷 | 現場 kiosk 驗券、出號與 audit | `EXISTING` |
| K12 | 預訂確認 | 店員 PENDING→CONFIRMED | `EXISTING` |
| K13 | 預訂完成 | CONFIRMED→COMPLETED | `EXISTING` |
| K14 | 當日統計 | 分預訂與取餐票狀態計數 | `EXISTING` |
| K15 | 人工調整 | 必須有 reason、operator、UTC 與 audit reference | `PLANNED／PARTIAL` |

### L. 預訂、取消與定期取貨

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| L01 | 查據點預訂能力 | 顯示可預訂品項、營業日、截止時間與取貨時段 | `EXISTING` |
| L02 | 非會員預訂 | 要求先認證會員 | `EXISTING` |
| L03 | 據點不支援預訂 | blocked，不建立訂單 | `EXISTING` |
| L04 | 非營業日 | 拒絕並提示可用日期 | `EXISTING` |
| L05 | 超過截止時間 | 拒絕並顯示政策 | `EXISTING` |
| L06 | 一般預訂 | 建 PENDING 記錄並通知 | `EXISTING` |
| L07 | 智販機取貨預訂 | `pickupMethod=vending`，後續需 machine／slot allocation | `EXISTING／PARTIAL` |
| L08 | 提貨券足夠 | 扣券建立預訂 | `EXISTING` |
| L09 | 提貨券不足 | 導向正常商品／付款頁 | `EXISTING` |
| L10 | 查詢我的預訂 | 只回本人 PENDING／CONFIRMED | `EXISTING` |
| L11 | 取消 PENDING 預訂 | 驗證本人後取消並通知 | `EXISTING` |
| L12 | 已確認／已完成不可自行取消 | 交人工或補償流程 | `EXISTING／PARTIAL` |
| L13 | 建立定期取貨訂閱 | 頻率、數量、機台、商品、付款方式均為活欄位 | `EXISTING（服務層）` |
| L14 | 到期自動扣款 | 同期冪等，不重複扣款 | `EXISTING／正式 Gate` |
| L15 | 扣款成功 | 建備貨工單並走取貨資格流程 | `EXISTING／正式 Gate` |
| L16 | 扣款失敗 | 計次、通知、受控重試 | `EXISTING` |
| L17 | 超過最大失敗次數 | 狀態 `payment_failed`／暫停 | `EXISTING` |
| L18 | 訂閱暫停／取消 | 不再處理後續週期，保留歷史 | `EXISTING／PARTIAL` |
| L19 | 發資格但未取貨 | 不列入實際設備履約營收 | `EXISTING（規則）` |

### M. 效期、食安、促銷與報損

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| M01 | 查詢溫度 | 逐機台、逐溫區保存時間與數值 | `PARTIAL／BLOCKED` |
| M02 | 無溫度感測器 | 回 null／unsupported，不偽造溫度 | `EXISTING` |
| M03 | 溫度過高 | 依溫區閾值告警 | `EXISTING／正式資料 BLOCKED` |
| M04 | 溫度過低 | 依溫區閾值告警 | `EXISTING／正式資料 BLOCKED` |
| M05 | 溫度查詢失敗 | 不阻斷庫存監控，但寫 audit | `EXISTING` |
| M06 | 冷鏈歷史 | machine+timestamp 冪等保存，供食安追溯 | `EXISTING（服務 contract）` |
| M07 | 低庫存通知 | alertKey 去重後推播 | `EXISTING` |
| M08 | 近效期商品 | 依距到期天數套用階梯折扣 | `EXISTING` |
| M09 | 同日重跑變價 | 不重複調整 | `EXISTING` |
| M10 | 已套更低價格 | 不把價格往回調高 | `EXISTING` |
| M11 | 促銷通知會員 | 依政策選擇對象與 Adapter | `PARTIAL／owner TODO` |
| M12 | 商品到期 | 停售／下架 | `EXISTING（服務層）` |
| M13 | 過期商品報損 | 保存數量、成本、原因與 audit | `EXISTING` |
| M14 | 過期券作廢 | 依政策進處置；正式供應商語意待確認 | `PARTIAL／BLOCKED` |
| M15 | 冷藏／冷凍／常溫未取 | 依政策回補可售配額 | `EXISTING（規則）` |
| M16 | 加熱品未取 | 報廢，不回補可售 | `EXISTING（規則）` |
| M17 | 取貨前 12h／20h 提醒 | 冪等通知 | `EXISTING` |
| M18 | 逾期退點／退款／部分退款／沒收 | 政策活欄位；正式退款由支付 owner | `EXISTING（意圖）／正式 Gate` |
| M19 | 處置重跑 | 不重複退、不重複回補、不重複報廢 | `EXISTING` |

### N. 銷售同步、對帳與事件

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| N01 | 定時拉 Sales | 因無已核准 Webhook，依活欄位輪詢 | `EXISTING／正式 Gate` |
| N02 | 日期區間限制 | 拆分查詢，避免超過供應商限制 | `PARTIAL` |
| N03 | saleID 去重 | 同 sale 不重複入帳 | `EXISTING` |
| N04 | 金額元轉分位 | Provider 內轉換為 integer minor units | `EXISTING` |
| N05 | 台北時間轉 UTC | 原始時間加時區後保存 UTC | `EXISTING` |
| N06 | 外層 API state 失敗 | 明確拋 provider error，不當空資料 | `EXISTING` |
| N07 | 交易 state 成功／失敗 | 原樣保留，交上層判定 | `EXISTING` |
| N08 | 單機同步失敗 | 其他機台繼續處理 | `EXISTING` |
| N09 | 已完成日期重跑 | 跳過，不重複對帳 | `EXISTING` |
| N10 | 憑券取貨配對 Sales | 用 tenlifeSaleId／pickup ledger 配對 | `EXISTING` |
| N11 | 匿名散客 Sales | 只進對帳，不綁會員／不賺點 | `EXISTING` |
| N12 | 會員取貨賺點 | 以線上付款／取貨成本為基數，不用天來可能為 0 的券金額 | `EXISTING` |
| N13 | 券核銷無 Sales | 記 discrepancy；可能是正常 type=1 行為，仍需說明 | `EXISTING` |
| N14 | 有 Sales 無取貨 | `sale_no_pickup`，進調查 | `PLANNED／資料型別已定義` |
| N15 | 有取貨無付款 | `pickup_no_payment`，高風險告警 | `PLANNED／資料型別已定義` |
| N16 | 金額不一致 | `amount_mismatch`，不得自動結清 | `EXISTING／PARTIAL` |
| N17 | 訂單完成事件 | 沿用 v1.8 `Order_Completed`，UUID-v4、UTC、minor units、HMAC | `EXISTING backend contract` |
| N18 | 訂單取消／退款事件 | 沿用既有核心事件，不新增第五事件 | `PARTIAL` |
| N19 | 設備結果事件 | 需版本化 payload、operation_ref、狀態、錯誤、audit | `PLANNED` |
| N20 | ERP 通知失敗 | outbox／重送／冪等；不得直接寫 ERP DB | `PLANNED` |

### O. 多供應商、商業模式與格口出租

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| O01 | 一台機台多供應商 | 每個商品按 machine+commodity 找供應商歸屬 | `EXISTING（服務層）` |
| O02 | 自有商品 | 無 mapping 時歸機台主，但需政策確認 | `EXISTING（規則）` |
| O03 | 供應商 Mapping 缺失 | 記 audit，不可靜默誤歸屬 | `EXISTING／需業務確認` |
| O04 | 銷售拆分冪等 | saleId 已處理時不重複 | `EXISTING` |
| O05 | 分潤／服務費為活欄位 | 不寫死比例 | `EXISTING（規則）／中央 Gate` |
| O06 | 自有機台模式 | 無月租／抽成 | `EXISTING` |
| O07 | 承租模式 | 固定月租 | `EXISTING` |
| O08 | 分潤模式 | 實際履約營收乘活欄位比例 | `EXISTING` |
| O09 | 租金＋分潤模式 | 同時套用兩項活欄位 | `EXISTING` |
| O10 | 模式變更 | 新增生效版本，不重算歷史 | `EXISTING` |
| O11 | 機台月結 | 同月冪等、不重複入帳 | `EXISTING（規則）` |
| O12 | 帳平檢查 | 各方加總等於總營收；差異進人工檢查 | `EXISTING` |
| O13 | 只用實際取貨營收 | 發券未取不列分潤基數 | `EXISTING（規則）` |
| O14 | 格口出租 | 一格同租期不可重複租 | `EXISTING（服務層）` |
| O15 | 格口寄物 | 商家放貨、保存取貨碼與買家聯絡識別 | `EXISTING（服務層）` |
| O16 | 寄物取貨碼重複 | 冪等拒絕 | `EXISTING` |
| O17 | 格口租約到期／終止 | 停止新寄物，處理未取物品 | `PARTIAL` |
| O18 | 格口月租帳單 | 同格同月不重複出帳 | `EXISTING（服務層）` |
| O19 | 正式撥款／發票 | 交財務／發票 owner，不由 StallPay 自行完成 | `OTHER_OWNER／BLOCKED` |

### P. 後台、報表、客服與稽核

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| P01 | 機台清單 | 顯示門店內機台、狀態、位置與最後同步時間 | `EXISTING` |
| P02 | 機台銷售列表 | store+machine scope，限制筆數 | `EXISTING` |
| P03 | 設備狀態頁 | online／offline／unknown、溫度、last sync | `PARTIAL` |
| P04 | 貨道／庫存頁 | 顯示商品、格位、推算庫存與資料時間 | `PARTIAL／BLOCKED` |
| P05 | 訂單履約頁 | 訂單、付款、備餐、格位、設備 operation、取貨狀態同頁追蹤 | `PLANNED` |
| P06 | 異常工作台 | offline、timeout、jam、partial、unknown、manual review | `PLANNED` |
| P07 | 補償工作台 | 只建立退款／替代商品／聯絡意圖，正式執行交 owner | `PLANNED` |
| P08 | 巡補工作台 | 工單、掃碼、上架、錯格、完成 | `PLANNED` |
| P09 | 日報 | 彙整 StallPay、天來散客、憑券取貨、Top 3、低庫存與溫度告警 | `EXISTING（規則）` |
| P10 | 月報／營收報表 | 散客＋會員取貨、機台、供應商與差異 | `EXISTING（規則）` |
| P11 | 對帳差異告警 | 不一致時通知 owner，不自動抹平 | `EXISTING／PARTIAL` |
| P12 | 客服查詢 | 以 order／phone hash／operation_ref 查詢，遮罩 PII | `PLANNED` |
| P13 | 人工補單 | 必須有 reason、operator、RBAC、UTC、audit；不得覆寫原始事實 | `PLANNED` |
| P14 | 人工標記設備結果 | 僅在可驗證證據下調整，保存前後狀態 | `PLANNED` |
| P15 | 匯出稽核證據 | 訂單、付款、取貨、設備回執、通知與補償可追溯 | `PARTIAL` |
| P16 | 五語系 | zh-Hant-TW、en-US、th-TH、ja-JP、id-ID | `PARTIAL` |
| P17 | 手機／桌機／Kiosk | 顧客手機優先，店員後台支援桌機／平板 | `PARTIAL` |
| P18 | 無障礙 | keyboard、ARIA、focus、status live region | `PLANNED／T1 integration evidence TODO` |
| P19 | 服務健康檢查 | Provider、DB、outbox、last sync，不執行高風險動作 | `PLANNED` |
| P20 | 監控告警 | error rate、sync lag、unknown aging、庫存／溫度告警 | `PARTIAL` |

### Q. 資安、隱私與治理

| ID | 情境 | StallPay 必須處理 | 責任／目前狀態 |
|---|---|---|---|
| Q01 | company／store scope | 每個查詢與命令都由 server context 決定 | `EXISTING／需全路由複核` |
| Q02 | machine scope | 機台必須屬於當前 store | `EXISTING／PARTIAL` |
| Q03 | slot／commodity scope | 格位與商品須屬於指定 machine | `PLANNED` |
| Q04 | PII 最小化 | 手機、LINE ID、生日等只收必要資料 | `PARTIAL` |
| Q05 | PII 遮罩 | 報表與 log 不輸出完整手機、Token、卡號 | `PARTIAL` |
| Q06 | 秘密外部化 | Token、Base URL、閾值、費率不得硬寫 | `PARTIAL`；目前 Tenlife Client 有預設 Base URL，正式使用前須修正／核准 |
| Q07 | 簽章驗證 | 驗證參數排序、簽章、時效與防重播 | `EXISTING（client signing）／callback 未完成` |
| Q08 | Raw payload 保存 | 可保存對帳必要欄位，但需遮罩秘密與 PII | `PARTIAL` |
| Q09 | UTC | domain 保存 UTC；顯示層轉在地時間 | `EXISTING／PARTIAL` |
| Q10 | Minor Units | 核心金額為整數分位；供應商原生元由 Adapter 轉換 | `EXISTING` |
| Q11 | Idempotency | 訂單、付款、券、設備操作、同步、報表、結算均需鍵值 | `EXISTING／設備操作待補` |
| Q12 | Audit | 所有狀態變更、拒絕、人工調整、補償意圖均記錄 | `EXISTING／PARTIAL` |
| Q13 | Fail-closed | scope、狀態、文件或設備結果不明時禁止高風險動作 | `PLANNED／治理要求` |
| Q14 | Provider 可替換 | domain 只依賴 `IVendingMachineProvider` | `EXISTING` |
| Q15 | 正式環境 Gate | 未核准 owner、Base URL、Token、測試機前不得實際操作 | `BLOCKED` |

## 四、目前基線已開發的主要部分

實際核對 `stallpay-v2@f883fa9e...` 後，可以確認已有以下資產，但這些資產不等於正式天來環境或實機通過：[2] [3]

| 類別 | 已有資產 | 判定 |
|---|---|---|
| Provider 抽象 | `IVendingMachineProvider` | 已有商品、Sales、設備狀態、廣告、折扣介面；缺開門／出貨 operation contract |
| 天來 Client | `Machine.aspx`、`Commodity.aspx`、`MachineCommodity.aspx`、`Coupon.aspx`、`ActiveCoupon.aspx`、`Sales.aspx`、`MachineTemperature.aspx` | 程式存在；正式 v2.7 文件、Base URL、owner、company scope 與受控實測仍阻塞 |
| 機台管理 | list／bind／unbind／listSales／upsertConsumer | 已有 store-scoped router 與 DB service |
| 憑證保護 | Token 加密保存、不回傳到機台列表 | 已有；正式 secret lifecycle 仍需治理複核 |
| 銷售同步 | Sales 輪詢、saleID 去重、元轉分位、UTC、單機失敗隔離 | 已有測試 |
| 會員與取貨 | LINE／手機會員、券餘額、部分／全量核銷、server-issued 取餐號 | 已有 |
| 預訂 | 設定、營業日、截止時間、券扣抵、查詢、取消 | 已有 |
| 取餐票狀態 | pending／preparing／ready／picked_up／expired | 已有 |
| 庫存／冷鏈 | snapshot、低庫存、溫區歷史、告警與 audit contract | 服務層已有；正式資料與端點驗證阻塞 |
| 效期 | 提醒、逾期、回補／報廢、退點／退款意圖 | 規則引擎已有；正式退款不能宣稱完成 |
| 訂閱取貨 | 定期扣款協調、備貨工單、發取貨資格、失敗計次 | 服務層已有；正式付款 Gate |
| 多供應商 | 商品歸屬、銷售分配、月結與帳平 | 規則層已有；正式比例與撥款由業務／財務 owner |
| 格口出租 | 租約、寄物、取貨碼、月租帳單 | 服務層已有 |
| 開門／出貨控制 | 無已核准 Provider 方法與天來端點 | **尚未完成；正式實機 BLOCKED** |

## 五、應優先補齊的 StallPay 智販機 P0～P2 範圍

| 優先級 | 必須完成的情境 | 原因 |
|---|---|---|
| `P0` | 權威 machine／commodity／machine-commodity 唯讀 mapping | 沒有真實 mapping 就不能安全配置商品、格位或取貨 |
| `P0` | `IVendingMachineProvider` 的 reserve／open／dispense／status／reconcile operation contract | 現有介面無法承載實際履約控制 |
| `P0` | payment success → operation → device receipt → completed／unknown／failed 狀態機 | 防止付款成功後重複出貨或錯誤退款 |
| `P0` | tenant／store／machine／slot／commodity 全鏈 scope | 防止跨租戶與開錯格 |
| `P0` | idempotency、timeout 後查詢、unknown 禁止重送 | 智販機最重要的安全條件 |
| `P0` | 多格部分成功、卡貨、斷線、感測器矛盾與 manual review | 真實履約一定會遇到的例外 |
| `P0` | 正式 owner、API v2.7 文件、Base URL 分類與指定測試機 | 未滿足前不得連接實機 |
| `P1` | 線上訂餐→算格→備餐→巡補上架→全格 ready→發 QR | 完成完整線上訂餐、設備取餐商業流程 |
| `P1` | 庫存／溫度／低庫存／冷鏈告警 | 智慧農業、食品販售與食安必要 |
| `P1` | Sales／取貨／付款／庫存三方對帳 | 確保交易與設備事實一致 |
| `P1` | 補償意圖與 ERP／支付 owner 交接 | 付款後設備失敗不可遺漏 |
| `P2` | 多供應商、格口出租、定期取貨、近效期促銷 | 擴充營運模式與收入來源 |
| `P2` | 日報、月報、供應商結算與客服工作台 | 形成可維運的商業產品 |

## 六、不可由 StallPay 自行宣稱完成的項目

正式支付、正式退款、正式電子發票、ERP 正式入帳、正式庫存扣減、正式供應商撥款、天來生產 Base URL、真實 company scope、真實 Token、開門／出貨 API、實機秒數、溫度感測器、門磁、攝影機與硬體安全能力，在取得 owner、文件、受控環境及可追溯測試證據前，都必須維持 `[TODO: 待人工確認]` 或 `BLOCKED`。目前 T7／CC 唯讀探索也因 `OWNER_TBD`、v2.7 第 10 節文件與 Base URL 未核准而停止，尚未取得真實 machine／commodity mapping。[4]

## References

[1]: [MerchCore平台：前後台責任裁決與邊界定義(v1.1).md](../../upload/MerchCore平台：前後台責任裁決與邊界定義(v1.1).md)  
[2]: [vendingMachineProvider.ts](../../work/stallpay-v2-scenario-audit/server/_core/vendingMachineProvider.ts)  
[3]: [tenlifeClient.ts](../../work/stallpay-v2-scenario-audit/server/vending/providers/tenlife/tenlifeClient.ts)  
[4]: [T7_TIANLAI_V27_READ_ONLY_DISCOVERY_REPORT_2026-08-31.md](T7_TIANLAI_V27_READ_ONLY_DISCOVERY_REPORT_2026-08-31.md)  
[5]: [pickupTicketService.ts](../../work/stallpay-v2-scenario-audit/server/liff/pickupTicketService.ts)  
[6]: [LiffPickup.tsx](../../work/stallpay-v2-scenario-audit/client/src/pages/LiffPickup.tsx)  
[7]: [inventoryMonitor.ts](../../work/stallpay-v2-scenario-audit/server/vending/cron/inventoryMonitor.ts)  
[8]: [salesSyncReconcile.ts](../../work/stallpay-v2-scenario-audit/server/vending/cron/salesSyncReconcile.ts)  
[9]: [revenueReport.ts](../../work/stallpay-v2-scenario-audit/server/vending/cron/revenueReport.ts)
