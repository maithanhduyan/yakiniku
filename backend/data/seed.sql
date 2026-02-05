-- ============================================
-- Yakiniku Jinan Chain - Complete Seed Data
-- Generated: 2026-02-05
-- Chain: 焼肉ジナン (Yakiniku Jinan)
-- Branches: 5 locations
-- ============================================

-- ============ CLEAR EXISTING DATA ============
DELETE FROM table_assignments;
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM table_sessions;
DELETE FROM bookings;
DELETE FROM customer_preferences;
DELETE FROM branch_customers;
DELETE FROM global_customers;
DELETE FROM staff;
DELETE FROM tables;
DELETE FROM menu_items;
DELETE FROM branches;

-- ============ BRANCHES (5 locations) ============
INSERT INTO branches (id, code, name, subdomain, phone, address, theme_primary_color, theme_bg_color, opening_time, closing_time, last_order_time, closed_days, max_capacity, is_active, created_at) VALUES
-- 本店 (Head Office) - Kawasaki Hirama
('branch-001', 'jinan', '焼肉ジナン 平間本店', 'jinan', '044-555-0001', '〒211-0012 神奈川県川崎市中原区中丸子571-13 ミヤタマンション101', '#d4af37', '#1a1a1a', '17:00', '23:00', '22:30', '[2]', 40, 1, datetime('now')),
-- 新宿店 - Shinjuku (B1 basement)
('branch-002', 'shinjuku', '焼肉ジナン 新宿店', 'shinjuku', '03-5555-0002', '〒160-0023 東京都新宿区西新宿1丁目13-8 朝日新宿ビル B1F', '#d4af37', '#1a1a1a', '11:30', '23:30', '23:00', '[]', 60, 1, datetime('now')),
-- 八重洲店 - Yaesu (Tokyo Station area)
('branch-003', 'yaesu', '焼肉ジナン 八重洲店', 'yaesu', '03-5555-0003', '〒103-0028 東京都中央区八重洲1丁目5-10 トーイン八重洲ビル 1F', '#d4af37', '#1a1a1a', '11:00', '22:00', '21:30', '[0]', 35, 1, datetime('now')),
-- 品川店 - Shinagawa
('branch-004', 'shinagawa', '焼肉ジナン 品川店', 'shinagawa', '03-5555-0004', '〒141-0043 東京都品川区二葉1丁目16-17', '#d4af37', '#1a1a1a', '17:00', '23:00', '22:30', '[1]', 45, 1, datetime('now')),
-- 横浜店 - Yokohama Kannai
('branch-005', 'yokohama', '焼肉ジナン 横浜関内店', 'yokohama', '045-555-0005', '〒231-0013 神奈川県横浜市中区住吉町5丁目65-2 アソルティ 1F', '#d4af37', '#1a1a1a', '17:00', '24:00', '23:30', '[2]', 50, 1, datetime('now'));

-- ============ STAFF (6-8 per branch = ~35 total) ============
-- 平間本店 Staff (8人)
INSERT INTO staff (id, employee_id, branch_code, name, name_kana, phone, email, role, pin_code, is_active, hire_date, created_at) VALUES
('staff-001', 'J001', 'jinan', '山田 太郎', 'ヤマダ タロウ', '090-1111-0001', 'yamada@jp', 'admin', '111111', 1, '2020-04-01', datetime('now')),
('staff-002', 'J002', 'jinan', '佐藤 花子', 'サトウ ハナコ', '090-1111-0002', 'sato@jp', 'manager', '222222', 1, '2020-04-01', datetime('now')),
('staff-003', 'J003', 'jinan', '田中 一郎', 'タナカ イチロウ', '090-1111-0003', 'tanaka@jp', 'cashier', '333333', 1, '2021-06-15', datetime('now')),
('staff-004', 'J004', 'jinan', '鈴木 美咲', 'スズキ ミサキ', '090-1111-0004', 'suzuki@jp', 'waiter', '444444', 1, '2022-01-10', datetime('now')),
('staff-005', 'J005', 'jinan', '高橋 健太', 'タカハシ ケンタ', '090-1111-0005', 'takahashi@jp', 'waiter', '555555', 1, '2022-03-20', datetime('now')),
('staff-006', 'J006', 'jinan', '伊藤 さくら', 'イトウ サクラ', '090-1111-0006', 'ito@jp', 'kitchen', '666666', 1, '2023-04-01', datetime('now')),
('staff-007', 'J007', 'jinan', '渡辺 大輔', 'ワタナベ ダイスケ', '090-1111-0007', 'watanabe@jp', 'kitchen', '777777', 1, '2021-08-01', datetime('now')),
('staff-008', 'J008', 'jinan', '中村 真由美', 'ナカムラ マユミ', '090-1111-0008', 'nakamura@jp', 'receptionist', '888888', 1, '2022-07-15', datetime('now')),

-- 新宿店 Staff (8人)
('staff-011', 'S001', 'shinjuku', '小林 翔太', 'コバヤシ ショウタ', '090-2111-0001', 'kobayashi@shinjuku.jp', 'admin', '111111', 1, '2021-04-01', datetime('now')),
('staff-012', 'S002', 'shinjuku', '加藤 愛', 'カトウ アイ', '090-2111-0002', 'kato@shinjuku.jp', 'manager', '222222', 1, '2021-04-01', datetime('now')),
('staff-013', 'S003', 'shinjuku', '吉田 隆', 'ヨシダ タカシ', '090-2111-0003', 'yoshida@shinjuku.jp', 'cashier', '333333', 1, '2022-01-10', datetime('now')),
('staff-014', 'S004', 'shinjuku', '山口 美優', 'ヤマグチ ミユウ', '090-2111-0004', 'yamaguchi@shinjuku.jp', 'waiter', '444444', 1, '2022-06-01', datetime('now')),
('staff-015', 'S005', 'shinjuku', '松本 大地', 'マツモト ダイチ', '090-2111-0005', 'matsumoto@shinjuku.jp', 'waiter', '555555', 1, '2023-01-15', datetime('now')),
('staff-016', 'S006', 'shinjuku', '井上 結衣', 'イノウエ ユイ', '090-2111-0006', 'inoue@shinjuku.jp', 'waiter', '666666', 1, '2023-04-01', datetime('now')),
('staff-017', 'S007', 'shinjuku', '木村 拓也', 'キムラ タクヤ', '090-2111-0007', 'kimura@shinjuku.jp', 'kitchen', '777777', 1, '2021-08-01', datetime('now')),
('staff-018', 'S008', 'shinjuku', '林 美穂', 'ハヤシ ミホ', '090-2111-0008', 'hayashi@shinjuku.jp', 'kitchen', '888888', 1, '2022-03-01', datetime('now')),

-- 八重洲店 Staff (6人)
('staff-021', 'Y001', 'yaesu', '清水 誠', 'シミズ マコト', '090-3111-0001', 'shimizu@yaesu.jp', 'admin', '111111', 1, '2022-04-01', datetime('now')),
('staff-022', 'Y002', 'yaesu', '森田 さやか', 'モリタ サヤカ', '090-3111-0002', 'morita@yaesu.jp', 'manager', '222222', 1, '2022-04-01', datetime('now')),
('staff-023', 'Y003', 'yaesu', '岡田 浩二', 'オカダ コウジ', '090-3111-0003', 'okada@yaesu.jp', 'cashier', '333333', 1, '2022-08-01', datetime('now')),
('staff-024', 'Y004', 'yaesu', '前田 凛', 'マエダ リン', '090-3111-0004', 'maeda@yaesu.jp', 'waiter', '444444', 1, '2023-01-10', datetime('now')),
('staff-025', 'Y005', 'yaesu', '藤井 健', 'フジイ ケン', '090-3111-0005', 'fujii@yaesu.jp', 'waiter', '555555', 1, '2023-04-01', datetime('now')),
('staff-026', 'Y006', 'yaesu', '村上 亜美', 'ムラカミ アミ', '090-3111-0006', 'murakami@yaesu.jp', 'kitchen', '666666', 1, '2022-06-01', datetime('now')),

-- 品川店 Staff (6人)
('staff-031', 'G001', 'shinagawa', '太田 勇気', 'オオタ ユウキ', '090-4111-0001', 'ota@shinagawa.jp', 'admin', '111111', 1, '2022-10-01', datetime('now')),
('staff-032', 'G002', 'shinagawa', '石井 麻衣', 'イシイ マイ', '090-4111-0002', 'ishii@shinagawa.jp', 'manager', '222222', 1, '2022-10-01', datetime('now')),
('staff-033', 'G003', 'shinagawa', '後藤 翔', 'ゴトウ ショウ', '090-4111-0003', 'goto@shinagawa.jp', 'cashier', '333333', 1, '2023-01-15', datetime('now')),
('staff-034', 'G004', 'shinagawa', '坂本 彩乃', 'サカモト アヤノ', '090-4111-0004', 'sakamoto@shinagawa.jp', 'waiter', '444444', 1, '2023-04-01', datetime('now')),
('staff-035', 'G005', 'shinagawa', '長谷川 蓮', 'ハセガワ レン', '090-4111-0005', 'hasegawa@shinagawa.jp', 'waiter', '555555', 1, '2023-07-01', datetime('now')),
('staff-036', 'G006', 'shinagawa', '近藤 美月', 'コンドウ ミヅキ', '090-4111-0006', 'kondo@shinagawa.jp', 'kitchen', '666666', 1, '2023-01-01', datetime('now')),

-- 横浜店 Staff (6人)
('staff-041', 'K001', 'yokohama', '斎藤 大樹', 'サイトウ ダイキ', '090-5111-0001', 'saito@yokohama.jp', 'admin', '111111', 1, '2023-04-01', datetime('now')),
('staff-042', 'K002', 'yokohama', '遠藤 真理', 'エンドウ マリ', '090-5111-0002', 'endo@yokohama.jp', 'manager', '222222', 1, '2023-04-01', datetime('now')),
('staff-043', 'K003', 'yokohama', '原田 航平', 'ハラダ コウヘイ', '090-5111-0003', 'harada@yokohama.jp', 'cashier', '333333', 1, '2023-06-01', datetime('now')),
('staff-044', 'K004', 'yokohama', '中島 葵', 'ナカジマ アオイ', '090-5111-0004', 'nakajima@yokohama.jp', 'waiter', '444444', 1, '2023-08-01', datetime('now')),
('staff-045', 'K005', 'yokohama', '小野 陽太', 'オノ ヨウタ', '090-5111-0005', 'ono@yokohama.jp', 'waiter', '555555', 1, '2024-01-15', datetime('now')),
('staff-046', 'K006', 'yokohama', '竹内 優花', 'タケウチ ユウカ', '090-5111-0006', 'takeuchi@yokohama.jp', 'kitchen', '666666', 1, '2023-10-01', datetime('now'));

-- ============ TABLES (per branch) ============
-- 平間本店 Tables (8 tables, 40 seats max)
INSERT INTO tables (id, branch_code, table_number, name, min_capacity, max_capacity, table_type, floor, zone, has_window, is_smoking, is_wheelchair_accessible, has_baby_chair, status, is_active, priority, notes, created_at) VALUES
('table-j01', 'jinan', 'T1', 'テーブル1', 2, 4, 'regular', 1, 'A', 0, 0, 1, 1, 'available', 1, 0, '入口近く', datetime('now')),
('table-j02', 'jinan', 'T2', 'テーブル2', 2, 4, 'regular', 1, 'A', 1, 0, 1, 0, 'available', 1, 0, '窓際席', datetime('now')),
('table-j03', 'jinan', 'T3', 'テーブル3', 2, 4, 'regular', 1, 'A', 1, 0, 1, 1, 'available', 1, 0, '窓際席', datetime('now')),
('table-j04', 'jinan', 'T4', 'テーブル4', 2, 4, 'regular', 1, 'B', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-j05', 'jinan', 'T5', 'テーブル5', 2, 4, 'regular', 1, 'B', 0, 0, 1, 0, 'available', 1, 0, 'デモ用テーブル', datetime('now')),
('table-j06', 'jinan', 'T6', 'テーブル6', 4, 6, 'regular', 1, 'B', 0, 0, 1, 1, 'available', 1, 0, '大人数向け', datetime('now')),
('table-j07', 'jinan', 'VIP1', '個室VIP', 4, 8, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, '完全個室・接待向け', datetime('now')),
('table-j08', 'jinan', 'VIP2', '半個室', 4, 6, 'private', 1, 'VIP', 0, 0, 1, 1, 'available', 1, 5, '半個室・家族向け', datetime('now')),

-- 新宿店 Tables (11 tables, 60 seats max) - B1階
('table-s01', 'shinjuku', 'A1', 'カウンター1', 1, 2, 'counter', -1, 'Counter', 0, 0, 1, 0, 'available', 1, 0, 'カウンター席', datetime('now')),
('table-s02', 'shinjuku', 'A2', 'カウンター2', 1, 2, 'counter', -1, 'Counter', 0, 0, 1, 0, 'available', 1, 0, 'カウンター席', datetime('now')),
('table-s03', 'shinjuku', 'A3', 'カウンター3', 1, 2, 'counter', -1, 'Counter', 0, 0, 1, 0, 'available', 1, 0, 'カウンター席', datetime('now')),
('table-s04', 'shinjuku', 'B1', 'テーブル1', 2, 4, 'regular', -1, 'Main', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-s05', 'shinjuku', 'B2', 'テーブル2', 2, 4, 'regular', -1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-s06', 'shinjuku', 'B3', 'テーブル3', 2, 4, 'regular', -1, 'Main', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-s07', 'shinjuku', 'B4', 'テーブル4', 2, 4, 'regular', -1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-s08', 'shinjuku', 'C1', 'ボックス席1', 4, 6, 'regular', -1, 'Box', 0, 0, 1, 1, 'available', 1, 3, 'ボックス席', datetime('now')),
('table-s09', 'shinjuku', 'C2', 'ボックス席2', 4, 6, 'regular', -1, 'Box', 0, 0, 1, 0, 'available', 1, 3, 'ボックス席', datetime('now')),
('table-s10', 'shinjuku', 'VIP', '個室', 6, 10, 'private', -1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, '完全個室・接待向け', datetime('now')),
('table-s11', 'shinjuku', 'P1', 'パーティ席', 8, 12, 'regular', -1, 'Party', 0, 0, 1, 1, 'available', 1, 5, '宴会向け', datetime('now')),

-- 八重洲店 Tables (7 tables, 35 seats max) - 1F
('table-y01', 'yaesu', 'T1', 'テーブル1', 2, 4, 'regular', 1, 'Main', 1, 0, 1, 0, 'available', 1, 0, '窓際', datetime('now')),
('table-y02', 'yaesu', 'T2', 'テーブル2', 2, 4, 'regular', 1, 'Main', 1, 0, 1, 1, 'available', 1, 0, '窓際', datetime('now')),
('table-y03', 'yaesu', 'T3', 'テーブル3', 2, 4, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-y04', 'yaesu', 'T4', 'テーブル4', 2, 4, 'regular', 1, 'Main', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-y05', 'yaesu', 'T5', 'テーブル5', 4, 6, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-y06', 'yaesu', 'T6', 'テーブル6', 4, 6, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-y07', 'yaesu', 'VIP', '個室', 4, 7, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, '商談向け個室', datetime('now')),

-- 品川店 Tables (9 tables, 45 seats max)
('table-g01', 'shinagawa', 'T1', 'テーブル1', 2, 4, 'regular', 1, 'A', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-g02', 'shinagawa', 'T2', 'テーブル2', 2, 4, 'regular', 1, 'A', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-g03', 'shinagawa', 'T3', 'テーブル3', 2, 4, 'regular', 1, 'A', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-g04', 'shinagawa', 'T4', 'テーブル4', 2, 4, 'regular', 1, 'B', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-g05', 'shinagawa', 'T5', 'テーブル5', 4, 6, 'regular', 1, 'B', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-g06', 'shinagawa', 'T6', 'テーブル6', 4, 6, 'regular', 1, 'B', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-g07', 'shinagawa', 'VIP1', '個室1', 4, 8, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, '個室', datetime('now')),
('table-g08', 'shinagawa', 'VIP2', '個室2', 4, 6, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, '個室', datetime('now')),
('table-g09', 'shinagawa', 'Terrace', 'テラス席', 2, 4, 'terrace', 1, 'Terrace', 1, 1, 0, 0, 'available', 1, 0, 'ペット可・喫煙可', datetime('now')),

-- 横浜店 Tables (10 tables, 50 seats max)
('table-k01', 'yokohama', 'T1', 'テーブル1', 2, 4, 'regular', 1, 'Main', 1, 0, 1, 1, 'available', 1, 0, '窓際', datetime('now')),
('table-k02', 'yokohama', 'T2', 'テーブル2', 2, 4, 'regular', 1, 'Main', 1, 0, 1, 0, 'available', 1, 0, '窓際', datetime('now')),
('table-k03', 'yokohama', 'T3', 'テーブル3', 2, 4, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-k04', 'yokohama', 'T4', 'テーブル4', 2, 4, 'regular', 1, 'Main', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-k05', 'yokohama', 'T5', 'テーブル5', 4, 6, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-k06', 'yokohama', 'T6', 'テーブル6', 4, 6, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-k07', 'yokohama', 'VIP1', '個室A', 4, 8, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, '掘りごたつ個室', datetime('now')),
('table-k08', 'yokohama', 'VIP2', '個室B', 4, 6, 'private', 1, 'VIP', 0, 0, 1, 1, 'available', 1, 8, '個室', datetime('now')),
('table-k09', 'yokohama', 'P1', '宴会席1', 6, 10, 'regular', 1, 'Party', 0, 0, 1, 0, 'available', 1, 5, '宴会向け', datetime('now')),
('table-k10', 'yokohama', 'C1', 'カウンター', 1, 2, 'counter', 1, 'Counter', 0, 0, 1, 0, 'available', 1, 0, 'おひとり様向け', datetime('now'));

-- ============ MENU ITEMS (shared across all branches) ============
-- 肉類 (Meat)
INSERT INTO menu_items (id, branch_code, name, name_en, description, category, subcategory, price, image_url, is_available, is_popular, is_spicy, is_vegetarian, allergens, prep_time_minutes, display_order, created_at) VALUES
-- 平間本店メニュー (other branches inherit same menu)
('menu-001', 'jinan', '和牛上ハラミ', 'Premium Harami', '口の中でほどける柔らかさと濃厚な味わい。当店自慢の一品', 'meat', 'beef', 1800, '/images/menu/harami.jpg', 1, 1, 0, 0, '', 5, 1, datetime('now')),
('menu-002', 'jinan', '厚切り上タン塩', 'Thick Sliced Beef Tongue', '贅沢な厚切り。歯ごたえと肉汁が溢れます', 'meat', 'beef', 2200, '/images/menu/tan.jpg', 1, 1, 0, 0, '', 6, 2, datetime('now')),
('menu-003', 'jinan', '特選カルビ', 'Premium Kalbi', '霜降りが美しい最高級カルビ', 'meat', 'beef', 1800, '/images/menu/kalbi.jpg', 1, 1, 0, 0, '', 5, 3, datetime('now')),
('menu-004', 'jinan', 'カルビ', 'Kalbi', '定番の人気メニュー。ジューシーな味わい', 'meat', 'beef', 1500, '/images/menu/kalbi_regular.jpg', 1, 0, 0, 0, '', 5, 4, datetime('now')),
('menu-005', 'jinan', '上ロース', 'Premium Sirloin', '赤身の旨味が楽しめる上質なロース', 'meat', 'beef', 1700, '/images/menu/rosu.jpg', 1, 0, 0, 0, '', 5, 5, datetime('now')),
('menu-006', 'jinan', 'ロース', 'Sirloin', 'あっさりとした赤身の美味しさ', 'meat', 'beef', 1400, '/images/menu/rosu_regular.jpg', 1, 0, 0, 0, '', 5, 6, datetime('now')),
('menu-007', 'jinan', 'ホルモン盛り合わせ', 'Offal Assortment', '新鮮なホルモンをたっぷり。ミノ・ハチノス・シマチョウ', 'meat', 'offal', 1400, '/images/menu/horumon.jpg', 1, 0, 0, 0, '', 7, 7, datetime('now')),
('menu-008', 'jinan', '特選盛り合わせ', 'Special Assortment', '本日のおすすめ希少部位を贅沢に盛り合わせ', 'meat', 'beef', 4500, '/images/menu/tokusenmori.jpg', 1, 1, 0, 0, '', 8, 8, datetime('now')),
('menu-009', 'jinan', '豚カルビ', 'Pork Kalbi', '甘みのある豚バラ肉', 'meat', 'pork', 900, '/images/menu/buta_kalbi.jpg', 1, 0, 0, 0, '', 5, 9, datetime('now')),
('menu-010', 'jinan', '鶏もも', 'Chicken Thigh', '柔らかくジューシーな鶏もも肉', 'meat', 'chicken', 800, '/images/menu/tori_momo.jpg', 1, 0, 0, 0, '', 5, 10, datetime('now')),

-- 飲み物 (Drinks)
('menu-011', 'jinan', '生ビール', 'Draft Beer', 'キンキンに冷えた生ビール（中）', 'drinks', 'beer', 600, '/images/menu/beer.jpg', 1, 0, 0, 0, '', 1, 1, datetime('now')),
('menu-012', 'jinan', '瓶ビール', 'Bottled Beer', 'アサヒスーパードライ', 'drinks', 'beer', 650, '/images/menu/beer_bottle.jpg', 1, 0, 0, 0, '', 1, 2, datetime('now')),
('menu-013', 'jinan', 'ハイボール', 'Highball', 'すっきり爽やかなウイスキーソーダ', 'drinks', 'whisky', 500, '/images/menu/highball.jpg', 1, 0, 0, 0, '', 1, 3, datetime('now')),
('menu-014', 'jinan', 'レモンサワー', 'Lemon Sour', '自家製レモンサワー。たっぷり飲みやすい', 'drinks', 'sour', 500, '/images/menu/lemon_sour.jpg', 1, 0, 0, 0, '', 1, 4, datetime('now')),
('menu-015', 'jinan', '梅酒サワー', 'Plum Wine Sour', '甘酸っぱい梅酒ソーダ割り', 'drinks', 'sour', 550, '/images/menu/umeshu.jpg', 1, 0, 0, 0, '', 1, 5, datetime('now')),
('menu-016', 'jinan', 'マッコリ', 'Makgeolli', '韓国の伝統酒。まろやかな甘み', 'drinks', 'korean', 600, '/images/menu/makgeolli.jpg', 1, 0, 0, 0, '', 1, 6, datetime('now')),
('menu-017', 'jinan', '焼酎（芋）', 'Sweet Potato Shochu', '本格芋焼酎。ロック・水割り・お湯割り', 'drinks', 'shochu', 500, '/images/menu/shochu.jpg', 1, 0, 0, 0, '', 1, 7, datetime('now')),
('menu-018', 'jinan', 'ウーロン茶', 'Oolong Tea', 'ソフトドリンク', 'drinks', 'soft', 300, '/images/menu/oolong.jpg', 1, 0, 0, 0, '', 1, 8, datetime('now')),
('menu-019', 'jinan', 'コーラ', 'Cola', 'コカ・コーラ', 'drinks', 'soft', 300, '/images/menu/cola.jpg', 1, 0, 0, 0, '', 1, 9, datetime('now')),
('menu-020', 'jinan', 'オレンジジュース', 'Orange Juice', '100%果汁オレンジジュース', 'drinks', 'soft', 350, '/images/menu/orange.jpg', 1, 0, 0, 0, '', 1, 10, datetime('now')),

-- サラダ (Salad)
('menu-021', 'jinan', 'チョレギサラダ', 'Korean Salad', '韓国風ピリ辛サラダ。ごま油が香る', 'salad', '', 600, '/images/menu/choregi.jpg', 1, 0, 1, 1, '', 3, 1, datetime('now')),
('menu-022', 'jinan', 'シーザーサラダ', 'Caesar Salad', 'パルメザンチーズたっぷり', 'salad', '', 700, '/images/menu/caesar.jpg', 1, 0, 0, 1, 'milk', 3, 2, datetime('now')),
('menu-023', 'jinan', 'ナムル盛り合わせ', 'Namul Assortment', '3種のナムル（もやし・ほうれん草・大根）', 'salad', '', 500, '/images/menu/namul.jpg', 1, 0, 0, 1, '', 3, 3, datetime('now')),
('menu-024', 'jinan', 'キムチ盛り合わせ', 'Kimchi Assortment', '白菜・カクテキ・オイキムチ', 'salad', '', 550, '/images/menu/kimchi.jpg', 1, 0, 1, 1, '', 2, 4, datetime('now')),

-- ご飯・麺 (Rice & Noodles)
('menu-025', 'jinan', 'ライス', 'Rice', '国産コシヒカリ使用', 'rice', '', 200, '/images/menu/rice.jpg', 1, 0, 0, 1, '', 2, 1, datetime('now')),
('menu-026', 'jinan', '大盛りライス', 'Large Rice', '国産コシヒカリ大盛り', 'rice', '', 300, '/images/menu/rice_large.jpg', 1, 0, 0, 1, '', 2, 2, datetime('now')),
('menu-027', 'jinan', '石焼ビビンバ', 'Stone Pot Bibimbap', '熱々の石鍋で提供。おこげが美味しい', 'rice', '', 1200, '/images/menu/bibimbap.jpg', 1, 1, 1, 0, 'egg', 8, 3, datetime('now')),
('menu-028', 'jinan', '冷麺', 'Cold Noodles', '韓国冷麺。さっぱりとした味わい', 'rice', '', 900, '/images/menu/reimen.jpg', 1, 0, 0, 0, 'wheat', 5, 4, datetime('now')),
('menu-029', 'jinan', 'カルビクッパ', 'Kalbi Rice Soup', 'カルビ入りの韓国風スープご飯', 'rice', '', 950, '/images/menu/kuppa.jpg', 1, 0, 1, 0, '', 6, 5, datetime('now')),

-- サイドメニュー (Side Menu)
('menu-030', 'jinan', 'わかめスープ', 'Seaweed Soup', '韓国風わかめスープ', 'side', '', 350, '/images/menu/wakame.jpg', 1, 0, 0, 1, '', 3, 1, datetime('now')),
('menu-031', 'jinan', 'テールスープ', 'Oxtail Soup', 'コラーゲンたっぷり牛テールスープ', 'side', '', 800, '/images/menu/tail_soup.jpg', 1, 0, 0, 0, '', 10, 2, datetime('now')),
('menu-032', 'jinan', '枝豆', 'Edamame', '塩茹で枝豆', 'side', '', 350, '/images/menu/edamame.jpg', 1, 0, 0, 1, '', 2, 3, datetime('now')),
('menu-033', 'jinan', '韓国海苔', 'Korean Seaweed', 'ごま油香る韓国海苔', 'side', '', 300, '/images/menu/nori.jpg', 1, 0, 0, 1, '', 1, 4, datetime('now')),
('menu-034', 'jinan', 'チヂミ', 'Korean Pancake', '海鮮チヂミ。外はカリっと中はもっちり', 'side', '', 850, '/images/menu/chijimi.jpg', 1, 0, 0, 0, 'wheat|egg|seafood', 10, 5, datetime('now')),

-- デザート (Dessert)
('menu-035', 'jinan', 'バニラアイス', 'Vanilla Ice Cream', '濃厚バニラアイスクリーム', 'dessert', '', 400, '/images/menu/vanilla_ice.jpg', 1, 0, 0, 1, 'milk', 1, 1, datetime('now')),
('menu-036', 'jinan', '杏仁豆腐', 'Almond Tofu', '手作り杏仁豆腐。なめらかな口当たり', 'dessert', '', 450, '/images/menu/annin.jpg', 1, 0, 0, 1, 'milk', 1, 2, datetime('now')),
('menu-037', 'jinan', 'シャーベット', 'Sherbet', 'マンゴーシャーベット', 'dessert', '', 400, '/images/menu/sherbet.jpg', 1, 0, 0, 1, '', 1, 3, datetime('now')),

-- セットメニュー (Set Menu)
('menu-038', 'jinan', '焼肉定食', 'Yakiniku Set', 'カルビ・ロース・ライス・スープ・サラダ', 'set', '', 1800, '/images/menu/teishoku.jpg', 1, 1, 0, 0, '', 15, 1, datetime('now')),
('menu-039', 'jinan', '上焼肉定食', 'Premium Yakiniku Set', '上カルビ・上ロース・ライス・スープ・サラダ', 'set', '', 2500, '/images/menu/teishoku_premium.jpg', 1, 0, 0, 0, '', 15, 2, datetime('now')),
('menu-040', 'jinan', '女子会コース', 'Ladies Course', 'サラダ・お肉5種・デザート・ドリンク付き', 'set', '', 3500, '/images/menu/ladies_course.jpg', 1, 0, 0, 0, '', 20, 3, datetime('now'));

-- ============ GLOBAL CUSTOMERS (50 customers) ============
INSERT INTO global_customers (id, phone, name, email, created_at) VALUES
('cust-001', '090-2000-0001', '佐々木 美咲', 'sasaki.misaki@email.jp', '2024-01-15 10:30:00'),
('cust-002', '090-2000-0002', '木村 健太', 'kimura.kenta@email.jp', '2024-01-20 14:45:00'),
('cust-003', '090-2000-0003', '山本 真由美', 'yamamoto.mayumi@email.jp', '2024-02-01 11:20:00'),
('cust-004', '090-2000-0004', '井上 大輔', 'inoue.daisuke@email.jp', '2024-02-05 18:00:00'),
('cust-005', '090-2000-0005', '林 さくら', 'hayashi.sakura@email.jp', '2024-02-10 12:30:00'),
('cust-006', '090-2000-0006', '清水 翔太', 'shimizu.shota@email.jp', '2024-02-15 19:15:00'),
('cust-007', '090-2000-0007', '松本 愛', 'matsumoto.ai@email.jp', '2024-02-20 17:00:00'),
('cust-008', '090-2000-0008', '森田 一郎', 'morita.ichiro@email.jp', '2024-03-01 13:45:00'),
('cust-009', '090-2000-0009', '小川 花子', 'ogawa.hanako@email.jp', '2024-03-05 16:30:00'),
('cust-010', '090-2000-0010', '藤田 太郎', 'fujita.taro@email.jp', '2024-03-10 11:00:00'),
('cust-011', '090-2000-0011', '岡田 美優', 'okada.miyu@email.jp', '2024-03-15 20:00:00'),
('cust-012', '090-2000-0012', '後藤 康平', 'goto.kohei@email.jp', '2024-03-20 15:30:00'),
('cust-013', '090-2000-0013', '坂本 結衣', 'sakamoto.yui@email.jp', '2024-03-25 12:00:00'),
('cust-014', '090-2000-0014', '長谷川 誠', 'hasegawa.makoto@email.jp', '2024-04-01 18:45:00'),
('cust-015', '090-2000-0015', '石井 彩乃', 'ishii.ayano@email.jp', '2024-04-05 14:15:00'),
('cust-016', '090-2000-0016', '前田 隆太', 'maeda.ryuta@email.jp', '2024-04-10 19:30:00'),
('cust-017', '090-2000-0017', '藤井 美穂', 'fujii.miho@email.jp', '2024-04-15 11:45:00'),
('cust-018', '090-2000-0018', '村上 浩二', 'murakami.koji@email.jp', '2024-04-20 16:00:00'),
('cust-019', '090-2000-0019', '太田 麻衣', 'ota.mai@email.jp', '2024-04-25 13:30:00'),
('cust-020', '090-2000-0020', '金子 拓海', 'kaneko.takumi@email.jp', '2024-05-01 17:15:00'),
('cust-021', '090-2000-0021', '中島 優子', 'nakajima.yuko@email.jp', '2024-05-05 10:00:00'),
('cust-022', '090-2000-0022', '原田 直樹', 'harada.naoki@email.jp', '2024-05-10 14:30:00'),
('cust-023', '090-2000-0023', '小野 千尋', 'ono.chihiro@email.jp', '2024-05-15 19:00:00'),
('cust-024', '090-2000-0024', '竹内 勇気', 'takeuchi.yuki@email.jp', '2024-05-20 12:45:00'),
('cust-025', '090-2000-0025', '宮崎 葵', 'miyazaki.aoi@email.jp', '2024-05-25 15:15:00'),
('cust-026', '090-2000-0026', '近藤 雄大', 'kondo.yudai@email.jp', '2024-06-01 18:30:00'),
('cust-027', '090-2000-0027', '石川 美月', 'ishikawa.mizuki@email.jp', '2024-06-05 11:00:00'),
('cust-028', '090-2000-0028', '斎藤 蓮', 'saito.ren@email.jp', '2024-06-10 16:45:00'),
('cust-029', '090-2000-0029', '上野 七海', 'ueno.nanami@email.jp', '2024-06-15 13:15:00'),
('cust-030', '090-2000-0030', '横山 悠人', 'yokoyama.yuto@email.jp', '2024-06-20 17:30:00'),
('cust-031', '090-2000-0031', '大野 凛', 'ono.rin@email.jp', '2024-06-25 10:45:00'),
('cust-032', '090-2000-0032', '吉村 颯太', 'yoshimura.sota@email.jp', '2024-07-01 14:00:00'),
('cust-033', '090-2000-0033', '池田 陽菜', 'ikeda.hina@email.jp', '2024-07-05 19:15:00'),
('cust-034', '090-2000-0034', '福田 樹', 'fukuda.itsuki@email.jp', '2024-07-10 12:30:00'),
('cust-035', '090-2000-0035', '西村 楓', 'nishimura.kaede@email.jp', '2024-07-15 15:45:00'),
('cust-036', '090-2000-0036', '山口 海斗', 'yamaguchi.kaito@email.jp', '2024-07-20 18:00:00'),
('cust-037', '090-2000-0037', '中川 心春', 'nakagawa.koharu@email.jp', '2024-07-25 11:15:00'),
('cust-038', '090-2000-0038', '野村 陸', 'nomura.riku@email.jp', '2024-08-01 16:30:00'),
('cust-039', '090-2000-0039', '松田 美桜', 'matsuda.mio@email.jp', '2024-08-05 13:45:00'),
('cust-040', '090-2000-0040', '菊池 大翔', 'kikuchi.hiroto@email.jp', '2024-08-10 17:00:00'),
('cust-041', '090-2000-0041', '和田 莉子', 'wada.riko@email.jp', '2024-08-15 10:30:00'),
('cust-042', '090-2000-0042', '久保 湊', 'kubo.minato@email.jp', '2024-08-20 14:45:00'),
('cust-043', '090-2000-0043', '増田 紬', 'masuda.tsumugi@email.jp', '2024-08-25 19:00:00'),
('cust-044', '090-2000-0044', '河野 朝陽', 'kawano.asahi@email.jp', '2024-09-01 12:15:00'),
('cust-045', '090-2000-0045', '杉山 芽依', 'sugiyama.mei@email.jp', '2024-09-05 15:30:00'),
('cust-046', '090-2000-0046', '内田 悠真', 'uchida.yuma@email.jp', '2024-09-10 18:45:00'),
('cust-047', '090-2000-0047', '永井 柚葉', 'nagai.yuzuha@email.jp', '2024-09-15 11:00:00'),
('cust-048', '090-2000-0048', '今井 奏太', 'imai.sota@email.jp', '2024-09-20 16:15:00'),
('cust-049', '090-2000-0049', '小島 璃子', 'kojima.riko@email.jp', '2024-09-25 13:30:00'),
('cust-050', '090-2000-0050', '浅野 律', 'asano.ritsu@email.jp', '2024-10-01 17:45:00');

-- ============ BRANCH CUSTOMERS (distributed across branches with sentiment) ============
-- 平間本店 Customers (VIPs included)
INSERT INTO branch_customers (id, global_customer_id, branch_code, visit_count, last_visit, is_vip, notes, created_at) VALUES
('bc-001', 'cust-001', 'jinan', 15, '2026-01-20 19:30:00', 1, '常連様。いつもタン塩を注文される [positive]', datetime('now')),
('bc-002', 'cust-002', 'jinan', 8, '2025-11-15 18:00:00', 0, 'お子様連れで来店。個室希望 [positive]', datetime('now')),
('bc-003', 'cust-003', 'jinan', 3, '2025-10-01 20:00:00', 0, '初回割引利用 [neutral]', datetime('now')),
('bc-004', 'cust-004', 'jinan', 22, '2026-02-01 19:00:00', 1, 'VIP。特別なお祝いでよく利用 [very_positive]', datetime('now')),
('bc-005', 'cust-005', 'jinan', 12, '2026-01-15 20:30:00', 1, '肉の焼き加減にこだわる。レア希望 [positive]', datetime('now')),
('bc-006', 'cust-006', 'jinan', 5, '2025-09-20 19:00:00', 0, 'アレルギー（甲殻類）あり [neutral]', datetime('now')),
('bc-007', 'cust-007', 'jinan', 18, '2026-01-25 18:30:00', 1, 'ワイン好き。記念日利用多し [very_positive]', datetime('now')),
('bc-008', 'cust-008', 'jinan', 10, '2025-11-30 20:00:00', 1, '大人数宴会でよく予約 [positive]', datetime('now')),
('bc-009', 'cust-009', 'jinan', 1, '2025-06-01 18:00:00', 0, '料理の提供が遅いとクレーム [negative]', datetime('now')),
('bc-010', 'cust-010', 'jinan', 7, '2025-10-15 19:00:00', 0, '静かな席希望。デート利用 [positive]', datetime('now')),

-- 新宿店 Customers
('bc-011', 'cust-011', 'shinjuku', 20, '2026-02-01 19:30:00', 1, '会社の接待でよく利用。上質な肉希望 [very_positive]', datetime('now')),
('bc-012', 'cust-012', 'shinjuku', 9, '2025-11-10 19:00:00', 0, '写真撮影好き。インスタ投稿 [positive]', datetime('now')),
('bc-013', 'cust-013', 'shinjuku', 25, '2026-01-20 20:30:00', 1, '創業時からの常連様。最高級コース [very_positive]', datetime('now')),
('bc-014', 'cust-014', 'shinjuku', 6, '2025-10-05 19:00:00', 0, '禁煙席希望。匂いに敏感 [positive]', datetime('now')),
('bc-015', 'cust-015', 'shinjuku', 11, '2025-12-10 19:30:00', 1, '誕生日ケーキ持ち込み許可済 [positive]', datetime('now')),
('bc-016', 'cust-016', 'shinjuku', 4, '2025-09-15 20:00:00', 0, '飲み放題プラン好き [neutral]', datetime('now')),
('bc-017', 'cust-017', 'shinjuku', 8, '2025-11-01 18:30:00', 0, '子供用メニュー注文 [positive]', datetime('now')),
('bc-018', 'cust-018', 'shinjuku', 15, '2026-01-25 20:00:00', 1, 'クリスマス毎年予約。ロマンチックな席希望 [very_positive]', datetime('now')),
('bc-019', 'cust-019', 'shinjuku', 7, '2025-10-20 19:30:00', 0, 'ホルモン専門。通な注文 [positive]', datetime('now')),
('bc-020', 'cust-020', 'shinjuku', 19, '2026-02-05 20:00:00', 1, 'ワイン会幹事。大口注文 [very_positive]', datetime('now')),

-- 八重洲店 Customers (ビジネス客多め)
('bc-021', 'cust-021', 'yaesu', 30, '2026-02-03 12:30:00', 1, 'ランチ常連。商談利用多数 [very_positive]', datetime('now')),
('bc-022', 'cust-022', 'yaesu', 15, '2026-01-15 13:00:00', 1, '接待利用。領収書必要 [positive]', datetime('now')),
('bc-023', 'cust-023', 'yaesu', 8, '2025-12-20 12:00:00', 0, 'ランチセット愛用 [positive]', datetime('now')),
('bc-024', 'cust-024', 'yaesu', 5, '2025-11-10 18:30:00', 0, '出張で東京駅利用時に来店 [neutral]', datetime('now')),
('bc-025', 'cust-025', 'yaesu', 12, '2026-01-30 19:00:00', 1, '取引先との会食場所として固定 [very_positive]', datetime('now')),
('bc-026', 'cust-026', 'yaesu', 3, '2025-10-05 12:30:00', 0, '急いでいることが多い [neutral]', datetime('now')),
('bc-027', 'cust-027', 'yaesu', 7, '2025-12-10 18:00:00', 0, '個室で商談 [positive]', datetime('now')),
('bc-028', 'cust-028', 'yaesu', 20, '2026-02-01 12:00:00', 1, '毎週金曜ランチ常連 [very_positive]', datetime('now')),

-- 品川店 Customers
('bc-031', 'cust-031', 'shinagawa', 10, '2025-12-25 19:00:00', 1, '家族連れで来店。子供用椅子必要 [positive]', datetime('now')),
('bc-032', 'cust-032', 'shinagawa', 6, '2025-11-20 20:00:00', 0, 'テラス席希望。ペット同伴 [positive]', datetime('now')),
('bc-033', 'cust-033', 'shinagawa', 15, '2026-01-10 18:30:00', 1, '地元常連。週末利用 [very_positive]', datetime('now')),
('bc-034', 'cust-034', 'shinagawa', 4, '2025-10-15 19:30:00', 0, 'カップル利用。静かな席希望 [positive]', datetime('now')),
('bc-035', 'cust-035', 'shinagawa', 8, '2025-12-05 20:00:00', 0, 'スポーツ観戦希望 [positive]', datetime('now')),
('bc-036', 'cust-036', 'shinagawa', 2, '2025-08-20 19:00:00', 0, '近所に引っ越してきた [neutral]', datetime('now')),
('bc-037', 'cust-037', 'shinagawa', 12, '2026-01-20 18:00:00', 1, '誕生日会常連 [positive]', datetime('now')),
('bc-038', 'cust-038', 'shinagawa', 5, '2025-11-05 19:30:00', 0, '仕事帰りに一人焼肉 [positive]', datetime('now')),

-- 横浜店 Customers
('bc-041', 'cust-041', 'yokohama', 18, '2026-01-30 19:00:00', 1, '横浜在住VIP。毎月来店 [very_positive]', datetime('now')),
('bc-042', 'cust-042', 'yokohama', 10, '2025-12-15 20:30:00', 1, '忘年会幹事。大人数予約 [positive]', datetime('now')),
('bc-043', 'cust-043', 'yokohama', 6, '2025-11-25 19:30:00', 0, '掘りごたつ個室希望 [positive]', datetime('now')),
('bc-044', 'cust-044', 'yokohama', 3, '2025-10-10 18:00:00', 0, '初来店。友人紹介 [neutral]', datetime('now')),
('bc-045', 'cust-045', 'yokohama', 14, '2026-02-01 20:00:00', 1, '深夜営業時間帯常連 [positive]', datetime('now')),
('bc-046', 'cust-046', 'yokohama', 8, '2025-12-20 19:00:00', 0, '関内駅近いので便利と評価 [positive]', datetime('now')),
('bc-047', 'cust-047', 'yokohama', 5, '2025-11-10 18:30:00', 0, '宴会利用。幹事 [neutral]', datetime('now')),
('bc-048', 'cust-048', 'yokohama', 22, '2026-02-03 21:00:00', 1, '遅い時間帯の常連。深夜まで飲む [very_positive]', datetime('now'));

-- ============ SAMPLE BOOKINGS (Today's bookings for demo) ============
INSERT INTO bookings (id, branch_code, guest_name, guest_phone, guest_email, date, time, guests, note, status, source, created_at) VALUES
-- 平間本店 Today's Bookings
('book-001', 'jinan', '佐々木 美咲', '090-2000-0001', 'sasaki.misaki@email.jp', date('now'), '18:00', 4, 'お誕生日ケーキ持ち込み希望。窓際席希望', 'confirmed', 'web', datetime('now')),
('book-002', 'jinan', '木村 健太', '090-2000-0002', 'kimura.kenta@email.jp', date('now'), '18:30', 2, NULL, 'confirmed', 'web', datetime('now')),
('book-003', 'jinan', '井上 大輔', '090-2000-0004', 'inoue.daisuke@email.jp', date('now'), '19:00', 6, '接待利用。個室希望。領収書必要', 'confirmed', 'phone', datetime('now')),
('book-004', 'jinan', '林 さくら', '090-2000-0005', 'hayashi.sakura@email.jp', date('now'), '19:30', 3, 'アレルギー：甲殻類', 'confirmed', 'web', datetime('now')),
('book-005', 'jinan', '松本 愛', '090-2000-0007', 'matsumoto.ai@email.jp', date('now'), '20:00', 4, '記念日利用。窓際席希望', 'pending', 'chat', datetime('now')),
('book-006', 'jinan', '森田 一郎', '090-2000-0008', 'morita.ichiro@email.jp', date('now'), '20:30', 8, '忘年会。個室希望', 'confirmed', 'phone', datetime('now')),

-- 新宿店 Today's Bookings
('book-011', 'shinjuku', '岡田 美優', '090-2000-0011', 'okada.miyu@email.jp', date('now'), '18:00', 2, 'カウンター席希望', 'confirmed', 'web', datetime('now')),
('book-012', 'shinjuku', '坂本 結衣', '090-2000-0013', 'sakamoto.yui@email.jp', date('now'), '19:00', 4, 'Instagram投稿予定', 'confirmed', 'web', datetime('now')),
('book-013', 'shinjuku', '長谷川 誠', '090-2000-0014', 'hasegawa.makoto@email.jp', date('now'), '19:30', 6, '会社の飲み会。ボックス席希望', 'confirmed', 'phone', datetime('now')),
('book-014', 'shinjuku', '金子 拓海', '090-2000-0020', 'kaneko.takumi@email.jp', date('now'), '20:00', 10, '宴会。飲み放題付き', 'confirmed', 'phone', datetime('now')),

-- 八重洲店 Today's Bookings (ランチ多め)
('book-021', 'yaesu', '中島 優子', '090-2000-0021', 'nakajima.yuko@email.jp', date('now'), '12:00', 2, 'ランチミーティング', 'confirmed', 'web', datetime('now')),
('book-022', 'yaesu', '原田 直樹', '090-2000-0022', 'harada.naoki@email.jp', date('now'), '12:30', 4, '商談。個室希望。静かな席', 'confirmed', 'phone', datetime('now')),
('book-023', 'yaesu', '竹内 勇気', '090-2000-0024', 'takeuchi.yuki@email.jp', date('now'), '13:00', 2, NULL, 'pending', 'web', datetime('now')),
('book-024', 'yaesu', '近藤 雄大', '090-2000-0026', 'kondo.yudai@email.jp', date('now'), '18:30', 6, '取引先との会食。個室希望', 'confirmed', 'phone', datetime('now')),

-- 品川店 Today's Bookings
('book-031', 'shinagawa', '大野 凛', '090-2000-0031', 'ono.rin@email.jp', date('now'), '18:00', 4, '子供2名。キッズチェア必要', 'confirmed', 'web', datetime('now')),
('book-032', 'shinagawa', '池田 陽菜', '090-2000-0033', 'ikeda.hina@email.jp', date('now'), '19:00', 2, 'ペット同伴。テラス席希望', 'confirmed', 'chat', datetime('now')),
('book-033', 'shinagawa', '西村 楓', '090-2000-0035', 'nishimura.kaede@email.jp', date('now'), '19:30', 5, 'スポーツ観戦したい', 'confirmed', 'web', datetime('now')),

-- 横浜店 Today's Bookings
('book-041', 'yokohama', '和田 莉子', '090-2000-0041', 'wada.riko@email.jp', date('now'), '18:30', 6, '掘りごたつ個室希望', 'confirmed', 'phone', datetime('now')),
('book-042', 'yokohama', '増田 紬', '090-2000-0043', 'masuda.tsumugi@email.jp', date('now'), '19:00', 4, '窓際席希望', 'confirmed', 'web', datetime('now')),
('book-043', 'yokohama', '内田 悠真', '090-2000-0046', 'uchida.yuma@email.jp', date('now'), '20:00', 8, '同窓会。宴会席希望', 'pending', 'phone', datetime('now')),
('book-044', 'yokohama', '浅野 律', '090-2000-0050', 'asano.ritsu@email.jp', date('now'), '21:30', 2, '深夜まで飲みたい', 'confirmed', 'chat', datetime('now'));

-- ============ END OF SEED DATA ============
--
-- Summary:
-- - 5 Branches: jinan (本店), shinjuku, yaesu, shinagawa, yokohama
-- - 34 Staff members (6-8 per branch)
-- - 45 Tables total (7-11 per branch)
-- - 40 Menu items (shared menu from jinan branch)
-- - 50 Global customers
-- - 48 Branch customer records
-- - 22 Sample bookings for today
--
-- To seed: sqlite3 yakiniku.db < seed.sql
-- ============================================
