# Customer Experience Touchpoints - Fishbone Analysis

## 🐟 Fishbone Diagram (Ishikawa)

```
                                    ┌─────────────────────────────────────────────────────────────────┐
                                    │           CUSTOMER EXPERIENCE - YAKINIKU RESTAURANT            │
                                    └─────────────────────────────────────────────────────────────────┘

        PRE-VISIT                           ARRIVAL                              DINING                           POST-VISIT
            │                                   │                                   │                                   │
            │                                   │                                   │                                   │
    ┌───────┴───────┐                   ┌───────┴───────┐                   ┌───────┴───────┐                   ┌───────┴───────┐
    │               │                   │               │                   │               │                   │               │
    ▼               ▼                   ▼               ▼                   ▼               ▼                   ▼               ▼

┌─────────┐   ┌─────────┐         ┌─────────┐   ┌─────────┐         ┌─────────┐   ┌─────────┐         ┌─────────┐   ┌─────────┐
│Discovery│   │ Booking │         │Check-in │   │ Seating │         │Ordering │   │ Service │         │ Payment │   │ Loyalty │
└────┬────┘   └────┬────┘         └────┬────┘   └────┬────┘         └────┬────┘   └────┬────┘         └────┬────┘   └────┬────┘
     │             │                   │             │                   │             │                   │             │
     ▼             ▼                   ▼             ▼                   ▼             ▼                   ▼             ▼
┌─────────┐   ┌─────────┐         ┌─────────┐   ┌─────────┐         ┌─────────┐   ┌─────────┐         ┌─────────┐   ┌─────────┐
│• Website│   │• Online │         │• Kiosk  │   │• Table  │         │• iPad   │   │• Kitchen│         │• POS    │   │• Follow │
│• SNS    │   │  Form   │         │• QR Code│   │  Guide  │         │  Menu   │   │  Speed  │         │• Receipt│   │  up     │
│• Google │   │• Phone  │         │• Staff  │   │• VIP    │         │• Staff  │   │• Quality│         │• Split  │   │• Review │
│• Ads    │   │• Chat AI│         │  Greet  │   │  Room   │         │  Suggest│   │  Check  │         │  Bill   │   │• Points │
└─────────┘   └─────────┘         └─────────┘   └─────────┘         └─────────┘   └─────────┘         └─────────┘   └─────────┘
     │             │                   │             │                   │             │                   │             │
     └──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘                   └──────┬──────┘
            │                                 │                                 │                                 │
            ▼                                 ▼                                 ▼                                 ▼
      ┌───────────┐                     ┌───────────┐                     ┌───────────┐                     ┌───────────┐
      │  🌐 WEB   │                     │📱 CHECKIN │                     │🍖 TABLE   │                     │💳 POS     │
      │   APP    │                     │   KIOSK   │                     │  ORDER    │                     │  SYSTEM   │
      └───────────┘                     └───────────┘                     └───────────┘                     └───────────┘


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                                    CUSTOMER JOURNEY
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                                          ▼
                          ┌─────────────────────────────────────────────────────────────────┐
                          │                    😊 SATISFIED CUSTOMER                        │
                          │              (Repeat Visit + Positive Review)                   │
                          └─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Detailed Touchpoint Analysis

### 1️⃣ PRE-VISIT (前来店)

```
                              PRE-VISIT TOUCHPOINTS
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
        ┌──────────┐           ┌──────────┐           ┌──────────┐
        │ DISCOVER │           │ RESEARCH │           │  DECIDE  │
        └────┬─────┘           └────┬─────┘           └────┬─────┘
             │                      │                      │
     ┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐
     │               │      │               │      │               │
     ▼               ▼      ▼               ▼      ▼               ▼
┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Google  │   │Instagram│ │ Website │ │ Reviews │ │ Booking │ │   AI    │
│  Maps   │   │  /LINE  │ │  Menu   │ │ Tabelog │ │  Form   │ │  Chat   │
└─────────┘   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
     │               │           │           │           │           │
     └───────┬───────┘           └─────┬─────┘           └─────┬─────┘
             │                         │                       │
             ▼                         ▼                       ▼
        ┌─────────┐              ┌─────────┐              ┌─────────┐
        │  apps/  │              │  apps/  │              │ backend/│
        │   web   │              │   web   │              │  /chat  │
        └─────────┘              └─────────┘              └─────────┘
```

| Touchpoint | App/System | Pain Points | Opportunities |
|------------|------------|-------------|---------------|
| 🔍 Search/Discovery | Google, SNS | 情報が見つからない | SEO最適化, SNS活用 |
| 📖 Menu Browsing | `apps/web` | 画像がない、価格不明 | 高画質写真、詳細説明 |
| 💬 AI Chat | `backend/chat` | 回答が遅い/不正確 | GPT-4活用、FAQ学習 |
| 📅 Online Booking | `apps/web` | 空席確認が面倒 | リアルタイム空席表示 |
| 📞 Phone Booking | Staff | 営業時間外対応不可 | AI音声予約 |

---

### 2️⃣ ARRIVAL (来店時)

```
                              ARRIVAL TOUCHPOINTS
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
        ┌──────────┐           ┌──────────┐           ┌──────────┐
        │  ARRIVE  │           │ CHECK-IN │           │  SEATED  │
        └────┬─────┘           └────┬─────┘           └────┬─────┘
             │                      │                      │
     ┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐
     │               │      │               │      │               │
     ▼               ▼      ▼               ▼      ▼               ▼
┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Exterior │   │ Parking │ │  Kiosk  │ │  Staff  │ │  Table  │ │   VIP   │
│ Signage │   │  Space  │ │Check-in │ │ Greet   │ │ Assign  │ │Treatment│
└─────────┘   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
     │               │           │           │           │           │
     └───────────────┘           └─────┬─────┘           └─────┬─────┘
                                       │                       │
                                       ▼                       ▼
                                  ┌─────────┐            ┌──────────┐
                                  │  apps/  │            │ backend/ │
                                  │ checkin │            │ /tables  │
                                  └─────────┘            └──────────┘
```

| Touchpoint | App/System | Pain Points | Opportunities |
|------------|------------|-------------|---------------|
| 🏠 Physical Arrival | - | 場所がわかりにくい | Google Maps連携 |
| 📱 Self Check-in | `apps/checkin` | 操作が難しい | シンプルUI, QR対応 |
| 👋 Staff Greeting | Staff | 待ち時間が長い | 予約確認の自動化 |
| 🪑 Table Assignment | `backend/tables` | 希望席でない | AI最適化配席 |
| ⭐ VIP Recognition | `backend/customers` | VIP対応漏れ | 自動VIPアラート |

---

### 3️⃣ DINING (食事中)

```
                              DINING TOUCHPOINTS
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       │                              │                              │
       ▼                              ▼                              ▼
 ┌───────────┐                 ┌───────────┐                 ┌───────────┐
 │  ORDERING │                 │  COOKING  │                 │  SERVING  │
 └─────┬─────┘                 └─────┬─────┘                 └─────┬─────┘
       │                             │                             │
┌──────┴──────┐               ┌──────┴──────┐               ┌──────┴──────┐
│             │               │             │               │             │
▼             ▼               ▼             ▼               ▼             ▼
┌───────┐ ┌───────┐       ┌───────┐ ┌───────┐       ┌───────┐ ┌───────┐
│ iPad  │ │ Staff │       │Kitchen│ │Quality│       │ Serve │ │ Refill│
│ Order │ │Suggest│       │Display│ │ Check │       │ Timing│ │Request│
└───┬───┘ └───┬───┘       └───┬───┘ └───┬───┘       └───┬───┘ └───┬───┘
    │         │               │         │               │         │
    ▼         ▼               ▼         ▼               ▼         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   apps/table-   │       │   apps/kitchen  │       │   WebSocket     │
│     order       │       │                 │       │   Real-time     │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

| Touchpoint | App/System | Pain Points | Opportunities |
|------------|------------|-------------|---------------|
| 📱 iPad Ordering | `apps/table-order` | 操作がわからない | 直感的UI, 写真メニュー |
| 🍖 Menu Selection | `apps/table-order` | 選びにくい | AIおすすめ, アレルギー表示 |
| 👨‍🍳 Kitchen Display | `apps/kitchen` | 注文漏れ | リアルタイム表示, 優先順位 |
| ⏱️ Wait Time | WebSocket | 待ち時間不明 | 進捗表示, 予想時間 |
| 🔔 Additional Orders | `apps/table-order` | 呼び出しが面倒 | ワンタップ追加注文 |
| 💡 Recommendations | AI | 好みがわからない | 顧客履歴学習, ペアリング提案 |

---

### 4️⃣ POST-VISIT (退店後)

```
                             POST-VISIT TOUCHPOINTS
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
        ┌──────────┐           ┌──────────┐           ┌──────────┐
        │ PAYMENT  │           │ FEEDBACK │           │ LOYALTY  │
        └────┬─────┘           └────┬─────┘           └────┬─────┘
             │                      │                      │
     ┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐
     │               │      │               │      │               │
     ▼               ▼      ▼               ▼      ▼               ▼
┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│   POS   │   │  Split  │ │ Survey  │ │ Review  │ │ Points  │ │  Next   │
│ Payment │   │  Bill   │ │  Form   │ │ Request │ │ Balance │ │ Booking │
└─────────┘   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
     │               │           │           │           │           │
     └───────┬───────┘           └─────┬─────┘           └─────┬─────┘
             │                         │                       │
             ▼                         ▼                       ▼
        ┌─────────┐              ┌─────────┐              ┌─────────┐
        │  apps/  │              │ backend/│              │ backend/│
        │   pos   │              │customers│              │ /promo  │
        └─────────┘              └─────────┘              └─────────┘
```

| Touchpoint | App/System | Pain Points | Opportunities |
|------------|------------|-------------|---------------|
| 💳 Payment | `apps/pos` | 会計が遅い | セルフ会計, QR決済 |
| 📄 Receipt | `apps/pos` | 紙がかさばる | 電子レシート |
| ⭐ Review Request | Email/LINE | 面倒くさい | 簡単ワンクリック評価 |
| 🎁 Points/Rewards | `backend/promotions` | ポイント確認できない | アプリでリアルタイム |
| 📧 Follow-up | Email/LINE | スパム感 | パーソナライズDM |

---

## 🎯 System Mapping to Touchpoints

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           YAKINIKU SYSTEM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  CUSTOMER-FACING                      STAFF-FACING           BACKEND            │
│  ┌─────────────────┐                  ┌─────────────┐       ┌─────────────┐    │
│  │                 │                  │             │       │             │    │
│  │   apps/web      │◄────REST────────►│   apps/     │◄─────►│  FastAPI    │    │
│  │  (Booking,Chat) │                  │  dashboard  │       │  Backend    │    │
│  │                 │                  │             │       │             │    │
│  └─────────────────┘                  └─────────────┘       └──────┬──────┘    │
│          │                                   ▲                     │           │
│          │                                   │                     │           │
│          ▼                            WebSocket                    ▼           │
│  ┌─────────────────┐                         │              ┌─────────────┐    │
│  │                 │                         │              │             │    │
│  │  apps/checkin   │◄────────────────────────┤              │  PostgreSQL │    │
│  │  (Self Kiosk)   │                         │              │  Database   │    │
│  │                 │                         │              │             │    │
│  └─────────────────┘                         │              └─────────────┘    │
│          │                                   │                                 │
│          │                                   │                                 │
│          ▼                                   │                                 │
│  ┌─────────────────┐              ┌─────────────────┐                         │
│  │                 │              │                 │                         │
│  │ apps/table-order│◄──WebSocket──┤  apps/kitchen   │                         │
│  │  (iPad Menu)    │              │  (KDS Display)  │                         │
│  │                 │              │                 │                         │
│  └─────────────────┘              └─────────────────┘                         │
│          │                                                                     │
│          │                                                                     │
│          ▼                                                                     │
│  ┌─────────────────┐                                                          │
│  │                 │                                                          │
│  │    apps/pos     │                                                          │
│  │  (Checkout)     │                                                          │
│  │                 │                                                          │
│  └─────────────────┘                                                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📈 Customer Journey Map

```
Emotion   😊                                    😊
Level     │     ╭───╮                     ╭───╮ │
          │    ╱     ╲         ╭───╮     ╱     ╲│
          │   ╱       ╲       ╱     ╲   ╱       ╲
      😐  │──╱─────────╲─────╱───────╲─╱─────────│
          │ ╱           ╲   ╱         ╲          │
          │╱             ╲ ╱           ╲         │
          │               ╳             ╲        │
      😔  │              ╱ ╲             ╲       │
          └──────────────────────────────────────┘

          Discovery  Booking  Check-in  Order  Wait  Eat  Pay  Leave

          ▲ Peaks (Moments of Delight):
          • Easy online booking with AI chat
          • Smooth self check-in
          • Delicious food served hot
          • Quick payment

          ▼ Valleys (Pain Points):
          • Long wait for table
          • Confusing ordering system
          • Slow food delivery
          • Complex payment process
```

---

## 🔄 Touchpoint Integration Flow

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│  CUSTOMER  │    │   CHECK    │    │   TABLE    │    │    POS     │
│  WEBSITE   │───►│    IN      │───►│   ORDER    │───►│  PAYMENT   │
└─────┬──────┘    └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
      │                 │                 │                 │
      ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND API                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐│
│  │Bookings │  │Customers│  │ Orders  │  │ Tables  │  │Payments││
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └────────┘│
└─────────────────────────────────────────────────────────────────┘
      │                 │                 │                 │
      ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DASHBOARD                                  │
│  Real-time monitoring of all customer touchpoints               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📊 Bookings │ 👥 Customers │ 🍽️ Orders │ 🪑 Tables │ 💰 Sales ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     KITCHEN DISPLAY                              │
│  Order queue with real-time updates                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Action Items by Priority

### 🔴 High Priority (Immediate Impact)
1. **Table Order UX** - Simplify iPad ordering interface
2. **Wait Time Display** - Show estimated cooking time
3. **VIP Alert System** - Auto-notify staff of VIP arrivals
4. **Payment Speed** - Enable QR code payment

### 🟡 Medium Priority (Near-term)
5. **AI Recommendations** - Suggest dishes based on history
6. **Self Check-in** - QR code for faster check-in
7. **Kitchen Optimization** - Priority queue algorithm
8. **Review Automation** - Post-visit feedback request

### 🟢 Lower Priority (Long-term)
9. **Loyalty Program** - Points and rewards system
10. **Voice Ordering** - AI-powered voice commands
11. **AR Menu** - Augmented reality dish preview
12. **Predictive Booking** - AI suggests optimal times

---

## 📊 KPIs per Touchpoint

| Phase | Touchpoint | KPI | Target |
|-------|-----------|-----|--------|
| Pre-visit | Website | Bounce Rate | < 40% |
| Pre-visit | Booking | Conversion Rate | > 15% |
| Arrival | Check-in | Wait Time | < 2 min |
| Dining | Ordering | Time to First Order | < 3 min |
| Dining | Kitchen | Avg Cook Time | < 8 min |
| Dining | Service | Refill Response | < 1 min |
| Post-visit | Payment | Checkout Time | < 3 min |
| Post-visit | Review | Review Rate | > 20% |

---

*Document created: 2026-02-05*
*Version: 1.0*
