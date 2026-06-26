# StallPay 經銷夥伴系統：後端 API 與 Schema 實作規格書

這份規格書定義了 StallPay 經銷夥伴體系（Dealer System）的後端實作細節，供後端開發人員（或 Claude）直接實作。

## 一、系統設計原則

1. **單一入口**：所有經銷商都必須從 L1 開始申請，由 Owner 審核後開立，後續由 Owner 調整層級。
2. **防呆隔離**：L2/L3/L4 無法產生 L1 邀請碼給攤主，攤主推薦 QR 與經銷邀請碼完全分開。
3. **無縫歸屬**：攤主透過推薦 QR 或優惠碼開通時，系統自動將其歸屬至對應的 L1 經銷商。

---

## 二、資料庫 Schema 設計 (Drizzle ORM)

請在 `drizzle/schema.ts` 中新增以下資料表，並更新 `stores` 表。

### 1. 新增表：`dealers` (經銷商帳號)

```typescript
export const dealers = mysqlTable("dealers", {
  id: varchar("id", { length: 64 }).primaryKey(), // e.g., dlr_xxxxx
  userId: varchar("user_id", { length: 64 }).notNull(), // 關聯到 users.id
  level: enum("level", ["L1", "L2", "L3", "L4"]).default("L1").notNull(),
  refCode: varchar("ref_code", { length: 32 }).notNull().unique(), // L1 推薦攤主的專屬碼，例如 L1_A3F9K2
  parentDealerId: varchar("parent_dealer_id", { length: 64 }), // 上層經銷商 ID (L1 屬於 L2，L2 屬於 L3...)
  status: enum("status", ["active", "suspended"]).default("active").notNull(),
  city: varchar("city", { length: 32 }),
  scale: varchar("scale", { length: 32 }),
  area: varchar("area", { length: 128 }),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});
```

### 2. 新增表：`dealer_applications` (L1 申請記錄)

```typescript
export const dealerApplications = mysqlTable("dealer_applications", {
  id: varchar("id", { length: 64 }).primaryKey(),
  name: varchar("name", { length: 64 }).notNull(),
  phone: varchar("phone", { length: 32 }).notNull(),
  city: varchar("city", { length: 32 }),
  scale: varchar("scale", { length: 32 }),
  area: varchar("area", { length: 128 }),
  note: text("note"),
  inviteCode: varchar("invite_code", { length: 32 }), // 來源邀請碼
  status: enum("status", ["pending", "approved", "rejected"]).default("pending").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});
```

### 3. 新增表：`dealer_invites` (邀請碼/優惠碼管理)

```typescript
export const dealerInvites = mysqlTable("dealer_invites", {
  id: varchar("id", { length: 64 }).primaryKey(),
  code: varchar("code", { length: 32 }).notNull().unique(), // e.g., INV_XXXX, HOPE2026
  type: enum("type", ["invite_l1", "promo_stall"]).notNull(), // invite_l1: 邀請 L1, promo_stall: 攤主優惠
  createdBy: varchar("created_by", { length: 64 }).notNull(), // 產生者的 user_id (通常是 Owner 或 L3/L4)
  assignedDealerId: varchar("assigned_dealer_id", { length: 64 }), // 優惠碼歸屬的 L1 (若有)
  title: varchar("title", { length: 64 }), // 優惠名稱 (僅 promo_stall 有效)
  description: varchar("description", { length: 255 }), // 優惠說明 (僅 promo_stall 有效)
  maxUses: int("max_uses"), // null 表示無上限
  usedCount: int("used_count").default(0).notNull(),
  expiresAt: timestamp("expires_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});
```

### 4. 更新表：`stores` (攤位)

在現有的 `stores` 表中新增以下欄位：

```typescript
  referredByDealerCode: varchar("referred_by_dealer_code", { length: 32 }), // 來源推薦碼 (L1 的 refCode)
  promoCode: varchar("promo_code", { length: 32 }), // 來源優惠碼
  channel: enum("channel", ["direct", "dealer", "promo"]).default("direct").notNull(),
  attributionLockedUntil: timestamp("attribution_locked_until"), // 歸屬鎖定到期時間
```

---

## 三、API 端點實作 (tRPC Routers)

請在 `server/routers/dealer.ts` 中實作以下 API，並掛載到主 router。

### 1. 公開端點 (Public Procedures)

這三支 API 供 `partner.html` 頁面載入時呼叫，不需登入。

#### `dealer.getRefInfo`
- **輸入**：`ref` (string)
- **邏輯**：查詢 `dealers` 表，比對 `refCode`。
- **輸出**：
  ```json
  { "valid": true, "dealerName": "龍哥", "dealerCity": "高雄市", "level": "L1" }
  ```
  若無效回傳 `{ "valid": false }`。

#### `dealer.getInviteInfo`
- **輸入**：`invite` (string)
- **邏輯**：查詢 `dealer_invites` 表，條件 `code = invite` 且 `type = 'invite_l1'` 且未過期、未達使用上限。
- **輸出**：`{ "valid": true }` 或 `{ "valid": false }`。

#### `dealer.getPromoInfo`
- **輸入**：`promo` (string)
- **邏輯**：查詢 `dealer_invites` 表，條件 `code = promo` 且 `type = 'promo_stall'` 且未過期、未達使用上限。
- **輸出**：
  ```json
  { "valid": true, "title": "希望廣場限定優惠", "description": "開通即享前 200 筆免費" }
  ```

#### `dealer.submitApplication`
- **輸入**：`name`, `phone`, `city`, `scale`, `area`, `note`, `inviteCode`
- **邏輯**：
  1. 驗證 `inviteCode` 有效性。
  2. 寫入 `dealer_applications` 表，狀態為 `pending`。
  3. (Optional) 發送 LINE Notify 通知 Owner。
- **輸出**：`{ "success": true }`

#### `dealer.submitStallInquiry`
- **輸入**：`name`, `phone`, `stallName`, `location`, `refCode` (可選), `promoCode` (可選), `channel`
- **邏輯**：
  1. 此 API 主要用於收集攤主資料（若未完成後續註冊，仍可人工聯絡）。
  2. 寫入 `stall_inquiries` 表 (需建立，或寫入 logs)。
- **輸出**：`{ "success": true }`

---

### 2. 需登入端點 (Protected Procedures)

#### `dealer.bindAttribution`
- **時機**：攤主在 APP 完成 onboarding 建立 store 時呼叫。
- **邏輯**：
  1. 檢查傳入的 `refCode` 或 `promoCode`。
  2. 更新 `stores` 表的 `referredByDealerCode`、`promoCode`、`channel`。
  3. 設定 `attributionLockedUntil` 為現在時間 + 24 個月。

#### `dealer.getMyRefCode` (限 L1~L4)
- **邏輯**：回傳當前登入者的 `dealers.refCode`，用於產生推薦 QR。

#### `dealer.createInviteCode` (限 L3, L4, Owner)
- **輸入**：`type` ('invite_l1'), `expiresInDays`
- **邏輯**：
  1. 檢查權限：僅 L3, L4, Owner 可執行。
  2. 產生亂數 `code`，寫入 `dealer_invites`。
- **輸出**：產生的邀請碼。

#### `dealer.createPromoCode` (限 Owner)
- **輸入**：`code`, `title`, `description`, `assignedDealerId`
- **邏輯**：寫入 `dealer_invites`，`type` 為 `promo_stall`。

#### `dealer.approveApplication` (限 Owner)
- **輸入**：`applicationId`
- **邏輯**：
  1. 將 `dealer_applications.status` 改為 `approved`。
  2. 建立對應的 `users` 帳號 (若無)，設定 role 為 `dealer`。
  3. 建立 `dealers` 記錄，`level` 設為 `L1`，產生 `refCode`。

---

## 四、RBAC 權限設計重點

1. **攤主推薦 QR**：L1, L2, L3, L4 皆可產生，且**必須是一次性或短效期**（前端產生時帶上 token）。
2. **L1 邀請碼**：僅 L3, L4, Owner 可產生。L2 絕對不可產生。
3. **層級調整**：僅 Owner 可調整任何經銷商的 `level`。
4. **審核權限**：目前所有 `dealer_applications` 皆由 Owner 審核。

---

## 五、實作建議順序

1. 建立並 migrate Schema。
2. 實作公開端點，確保 `partner.html` 可正常運作並顯示資料。
3. 實作 `submitApplication`，讓經銷申請流程打通。
4. 修改現有的 `store` 建立邏輯，支援 `bindAttribution`。
5. 實作後台管理介面 API (`approveApplication`, `createInviteCode` 等)。
