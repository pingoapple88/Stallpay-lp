# iMin Falcon 1／F1 公開資料查核

查核日期：2026-09-09

## 官方產品頁

來源：https://www.imin.com/product/falcon-1/

官方頁面將產品名稱列為 **Falcon 1**，可作為使用者所稱 iMin F1 的候選對應型號，但正式採購與型號仍需人工確認。官方公開資訊包含：80mm × 80mm 熱感印表機、最高 250mm/s 列印速度與自動切刀；支援 NFC 與 QR code 掃描；10.1 吋、1280 × 800 顯示器；Android 11 series；八核心處理器；2GB+16GB 或 4GB+32GB 記憶體組合；Wi-Fi、Bluetooth 5.0、4G、GPS；0.3M 固定焦距相機，支援 1D／2D 掃描；另有多種週邊連接埠。

## 官方 SDK 文件

來源：https://oss-sg.imin.sg/docs/en/SDK.html

官方 SDK 文件說明 iMin POS 可使用 `IminDeviceLibrary:3.0.0`，透過 `DeviceManager.initialize()` 初始化，並取得裝置資訊、型號、品牌、序號、雙螢幕、硬體、網路、軟體、顯示器、記憶體與儲存資訊。實際使用前必須確認設備初始化成功。這表示正式整合可透過獨立的 `IHardwareDeviceProvider`／設備 Adapter 封裝，不應把 iMin SDK 直接寫入核心訂單或庫存邏輯。

## 官方印表機文件

來源：https://oss-sg.imin.sg/docs/en/Printer.html

官方文件說明第三方 App 可連接 iMin 內建印表機；Falcon 1 在列出的 USB 連線支援機型中。文件也提供 Android SDK、Web print 與 JavaScript API 方向，並列出 QR code、barcode、圖片、文字、表格等列印能力。正式實作仍需依實際 OS、韌體、機型與 SDK 版本確認。

## 官方 FAQ

來源：https://www.imin.com/faq/

官方 FAQ 表示第三方 App 可參考 iMin 官方 API 文件整合；iMin Printer Plugin 可供支援的網頁 POS 使用；第三方 APK 可透過 USB 或下載方式安裝。以上僅證明存在官方整合途徑，不代表校鮮集已取得設備權限、支付資格、設備管理權或正式開櫃 API。

## 原型定位

校鮮集原型可把 Falcon 1／iMin F1 作為「智販機／取貨設備選項」展示：掃描 1D／2D 取貨碼、確認訂單、列印取貨單／QR、回報設備事件。正式版本仍需人工確認實際型號、Android／韌體版本、SDK、設備管理、網路、支付、庫存扣減、開櫃協議、資安與維運 owner。所有設備操作應透過 Adapter，並在失敗時 fail-closed，不直接標記取貨完成或重複扣款。
