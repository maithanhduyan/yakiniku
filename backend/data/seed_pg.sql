-- ============================================
-- Yakiniku Jinan - PostgreSQL Seed Data
-- ============================================
-- Generated from CSV core data files
-- Compatible with PostgreSQL 15+
-- Schema-matched with actual database models
-- ============================================

-- Clear existing data (in correct order due to foreign keys)
TRUNCATE TABLE customer_preferences CASCADE;
TRUNCATE TABLE chat_messages CASCADE;
TRUNCATE TABLE chat_insights CASCADE;
TRUNCATE TABLE bookings CASCADE;
TRUNCATE TABLE branch_customers CASCADE;
TRUNCATE TABLE global_customers CASCADE;
TRUNCATE TABLE menu_items CASCADE;
TRUNCATE TABLE tables CASCADE;
TRUNCATE TABLE staff CASCADE;
TRUNCATE TABLE branches CASCADE;

-- ============================================
-- 1. BRANCHES (5 branches)
-- Schema: id, code, name, subdomain, phone, address, theme_primary_color,
--         theme_bg_color, logo_url, opening_time, closing_time, last_order_time,
--         closed_days, max_capacity, features, is_active, created_at
-- ============================================
INSERT INTO branches (id, code, name, subdomain, phone, address, opening_time, closing_time, max_capacity, is_active) VALUES
('branch-jinan', 'jinan', '焼肉ジナン 平間本店', 'jinan', '044-520-3729', '川崎市中原区中丸子571-13', '17:00:00', '24:00:00', 50, true),
('branch-shinjuku', 'shinjuku', '焼肉ジナン 新宿店', 'shinjuku', '03-5909-7729', '新宿区西新宿1-13-8 B1F', '17:00:00', '01:00:00', 80, true),
('branch-yaesu', 'yaesu', '焼肉ジナン 八重洲店', 'yaesu', '03-3271-7729', '中央区八重洲1-5-10 1F', '11:30:00', '23:00:00', 40, true),
('branch-shinagawa', 'shinagawa', '焼肉ジナン 品川店', 'shinagawa', '03-6417-7729', '品川区二葉1-16-17', '17:00:00', '24:00:00', 50, true),
('branch-yokohama', 'yokohama', '焼肉ジナン 横浜関内店', 'yokohama', '045-264-7729', '横浜市中区住吉町5-65-2 1F', '17:00:00', '24:00:00', 60, true);

-- ============================================
-- 2. STAFF (34 staff across 5 branches)
-- ============================================
INSERT INTO staff (id, employee_id, branch_code, name, name_kana, phone, email, role, pin_code, is_active, hire_date) VALUES
-- Jinan (10 staff)
('staff-001', 'S001', 'jinan', '山田 太郎', 'ヤマダ タロウ', '090-1111-0001', 'yamada@yakiniku-jp', 'admin', '111111', true, '2020-04-01'),
('staff-002', 'S002', 'jinan', '佐藤 花子', 'サトウ ハナコ', '090-1111-0002', 'sato@yakiniku-jp', 'admin', '222222', true, '2020-04-01'),
('staff-003', 'S003', 'jinan', '田中 一郎', 'タナカ イチロウ', '090-1111-0003', 'tanaka@yakiniku-jp', 'manager', '333333', true, '2021-06-15'),
('staff-004', 'S004', 'jinan', '鈴木 美咲', 'スズキ ミサキ', '090-1111-0004', 'suzuki@yakiniku-jp', 'cashier', '444444', true, '2022-01-10'),
('staff-005', 'S005', 'jinan', '高橋 健太', 'タカハシ ケンタ', '090-1111-0005', 'takahashi@yakiniku-jp', 'waiter', '555555', true, '2022-03-20'),
('staff-006', 'S006', 'jinan', '伊藤 さくら', 'イトウ サクラ', '090-1111-0006', 'ito@yakiniku-jp', 'waiter', '666666', true, '2023-04-01'),
('staff-007', 'S007', 'jinan', '渡辺 大輔', 'ワタナベ ダイスケ', '090-1111-0007', 'watanabe@yakiniku-jp', 'kitchen', '777777', true, '2021-08-01'),
('staff-008', 'S008', 'jinan', '中村 真由美', 'ナカムラ マユミ', '090-1111-0008', 'nakamura@yakiniku-jp', 'kitchen', '888888', true, '2022-07-15'),
('staff-009', 'S009', 'jinan', '小林 翔太', 'コバヤシ ショウタ', '090-1111-0009', 'kobayashi@yakiniku-jp', 'receptionist', '999999', true, '2023-09-01'),
('staff-010', 'S010', 'jinan', '加藤 愛', 'カトウ アイ', '090-1111-0010', 'kato@yakiniku-jp', 'waiter', '000000', true, '2024-01-15'),
-- Shinjuku (7 staff)
('staff-011', 'S011', 'shinjuku', '松本 大介', 'マツモト ダイスケ', '090-2222-0001', 'matsumoto@yakiniku-jp', 'admin', '111112', true, '2022-03-15'),
('staff-012', 'S012', 'shinjuku', '井上 明美', 'イノウエ アケミ', '090-2222-0002', 'inoue@yakiniku-jp', 'manager', '222223', true, '2022-04-01'),
('staff-013', 'S013', 'shinjuku', '木村 誠', 'キムラ マコト', '090-2222-0003', 'kimura@yakiniku-jp', 'cashier', '333334', true, '2022-06-01'),
('staff-014', 'S014', 'shinjuku', '林 優子', 'ハヤシ ユウコ', '090-2222-0004', 'hayashi@yakiniku-jp', 'waiter', '444445', true, '2022-08-15'),
('staff-015', 'S015', 'shinjuku', '清水 拓也', 'シミズ タクヤ', '090-2222-0005', 'shimizu@yakiniku-jp', 'waiter', '555556', true, '2023-01-10'),
('staff-016', 'S016', 'shinjuku', '山口 彩香', 'ヤマグチ アヤカ', '090-2222-0006', 'yamaguchi@yakiniku-jp', 'kitchen', '666667', true, '2022-05-01'),
('staff-017', 'S017', 'shinjuku', '森 健二', 'モリ ケンジ', '090-2222-0007', 'mori@yakiniku-jp', 'kitchen', '777778', true, '2023-03-01'),
-- Yaesu (5 staff)
('staff-018', 'S018', 'yaesu', '池田 直樹', 'イケダ ナオキ', '090-3333-0001', 'ikeda@yakiniku-jp', 'admin', '111113', true, '2023-06-01'),
('staff-019', 'S019', 'yaesu', '橋本 美穂', 'ハシモト ミホ', '090-3333-0002', 'hashimoto@yakiniku-jp', 'manager', '222224', true, '2023-06-15'),
('staff-020', 'S020', 'yaesu', '阿部 翔', 'アベ ショウ', '090-3333-0003', 'abe@yakiniku-jp', 'cashier', '333335', true, '2023-07-01'),
('staff-021', 'S021', 'yaesu', '石川 恵理', 'イシカワ エリ', '090-3333-0004', 'ishikawa@yakiniku-jp', 'waiter', '444446', true, '2023-08-01'),
('staff-022', 'S022', 'yaesu', '前田 龍一', 'マエダ リュウイチ', '090-3333-0005', 'maeda@yakiniku-jp', 'kitchen', '555557', true, '2023-09-01'),
-- Shinagawa (5 staff)
('staff-023', 'S023', 'shinagawa', '藤原 剛', 'フジワラ ツヨシ', '090-4444-0001', 'fujiwara@yakiniku-jp', 'admin', '111114', true, '2023-09-01'),
('staff-024', 'S024', 'shinagawa', '岡田 さやか', 'オカダ サヤカ', '090-4444-0002', 'okada@yakiniku-jp', 'manager', '222225', true, '2023-09-15'),
('staff-025', 'S025', 'shinagawa', '後藤 亮太', 'ゴトウ リョウタ', '090-4444-0003', 'goto@yakiniku-jp', 'cashier', '333336', true, '2023-10-01'),
('staff-026', 'S026', 'shinagawa', '遠藤 真理', 'エンドウ マリ', '090-4444-0004', 'endo@yakiniku-jp', 'waiter', '444447', true, '2023-11-01'),
('staff-027', 'S027', 'shinagawa', '青木 大地', 'アオキ ダイチ', '090-4444-0005', 'aoki@yakiniku-jp', 'kitchen', '555558', true, '2023-12-01'),
-- Yokohama (7 staff)
('staff-028', 'S028', 'yokohama', '坂本 隼人', 'サカモト ハヤト', '090-5555-0001', 'sakamoto@yakiniku-jp', 'admin', '111115', true, '2024-01-15'),
('staff-029', 'S029', 'yokohama', '吉田 麻衣', 'ヨシダ マイ', '090-5555-0002', 'yoshida@yakiniku-jp', 'manager', '222226', true, '2024-01-20'),
('staff-030', 'S030', 'yokohama', '原田 悠斗', 'ハラダ ユウト', '090-5555-0003', 'harada@yakiniku-jp', 'cashier', '333337', true, '2024-02-01'),
('staff-031', 'S031', 'yokohama', '千葉 琴音', 'チバ コトネ', '090-5555-0004', 'chiba@yakiniku-jp', 'waiter', '444448', true, '2024-02-15'),
('staff-032', 'S032', 'yokohama', '野村 蓮', 'ノムラ レン', '090-5555-0005', 'nomura@yakiniku-jp', 'waiter', '555559', true, '2024-03-01'),
('staff-033', 'S033', 'yokohama', '菅原 桃子', 'スガワラ モモコ', '090-5555-0006', 'sugawara@yakiniku-jp', 'kitchen', '666668', true, '2024-03-15'),
('staff-034', 'S034', 'yokohama', '新井 康介', 'アライ コウスケ', '090-5555-0007', 'arai@yakiniku-jp', 'kitchen', '777779', true, '2024-04-01');

-- ============================================
-- 3. TABLES (47 tables across 5 branches)
-- Schema: id, branch_code, table_number, name, min_capacity, max_capacity,
--         table_type, floor, zone, has_window, is_smoking, is_wheelchair_accessible,
--         has_baby_chair, status, is_active, priority, notes
-- ============================================
INSERT INTO tables (id, branch_code, table_number, name, max_capacity, table_type, zone, has_window, is_active, notes) VALUES
-- Jinan (9 tables)
('table-jinan-01', 'jinan', 'A1', 'テーブルA1', 4, 'table', 'floor', true, true, '窓際'),
('table-jinan-02', 'jinan', 'A2', 'テーブルA2', 4, 'table', 'floor', false, true, NULL),
('table-jinan-03', 'jinan', 'A3', 'テーブルA3', 4, 'table', 'floor', false, true, NULL),
('table-jinan-04', 'jinan', 'A4', 'テーブルA4', 6, 'table', 'floor', false, true, '大きめテーブル'),
('table-jinan-05', 'jinan', 'B1', 'カウンターB1', 2, 'counter', 'counter', false, true, 'カウンター席'),
('table-jinan-06', 'jinan', 'B2', 'カウンターB2', 2, 'counter', 'counter', false, true, 'カウンター席'),
('table-jinan-07', 'jinan', 'B3', 'カウンターB3', 2, 'counter', 'counter', false, true, 'カウンター席'),
('table-jinan-08', 'jinan', 'C1', '個室C1', 8, 'private', 'private', false, true, '個室・掘りごたつ'),
('table-jinan-09', 'jinan', 'C2', 'VIP個室C2', 10, 'private', 'private', false, true, 'VIP個室・カラオケ付'),
-- Shinjuku (12 tables)
('table-shinjuku-01', 'shinjuku', 'A1', 'テーブルA1', 4, 'table', 'floor', true, true, '窓際'),
('table-shinjuku-02', 'shinjuku', 'A2', 'テーブルA2', 4, 'table', 'floor', false, true, NULL),
('table-shinjuku-03', 'shinjuku', 'A3', 'テーブルA3', 4, 'table', 'floor', false, true, NULL),
('table-shinjuku-04', 'shinjuku', 'A4', 'テーブルA4', 4, 'table', 'floor', false, true, NULL),
('table-shinjuku-05', 'shinjuku', 'A5', 'テーブルA5', 6, 'table', 'floor', false, true, '角席'),
('table-shinjuku-06', 'shinjuku', 'B1', 'カウンターB1', 2, 'counter', 'counter', false, true, NULL),
('table-shinjuku-07', 'shinjuku', 'B2', 'カウンターB2', 2, 'counter', 'counter', false, true, NULL),
('table-shinjuku-08', 'shinjuku', 'B3', 'カウンターB3', 2, 'counter', 'counter', false, true, NULL),
('table-shinjuku-09', 'shinjuku', 'B4', 'カウンターB4', 2, 'counter', 'counter', false, true, NULL),
('table-shinjuku-10', 'shinjuku', 'C1', '個室C1', 8, 'private', 'private', false, true, '個室'),
('table-shinjuku-11', 'shinjuku', 'C2', 'VIP個室C2', 10, 'private', 'private', false, true, 'VIP個室'),
('table-shinjuku-12', 'shinjuku', 'C3', '宴会個室C3', 14, 'private', 'private', false, true, '宴会個室'),
-- Yaesu (8 tables)
('table-yaesu-01', 'yaesu', 'A1', 'テーブルA1', 4, 'table', 'floor', true, true, '窓際・ビジネス向け'),
('table-yaesu-02', 'yaesu', 'A2', 'テーブルA2', 4, 'table', 'floor', false, true, NULL),
('table-yaesu-03', 'yaesu', 'A3', 'テーブルA3', 4, 'table', 'floor', false, true, NULL),
('table-yaesu-04', 'yaesu', 'B1', 'カウンターB1', 2, 'counter', 'counter', false, true, 'ランチ人気'),
('table-yaesu-05', 'yaesu', 'B2', 'カウンターB2', 2, 'counter', 'counter', false, true, NULL),
('table-yaesu-06', 'yaesu', 'B3', 'カウンターB3', 2, 'counter', 'counter', false, true, NULL),
('table-yaesu-07', 'yaesu', 'C1', '商談個室C1', 6, 'private', 'private', false, true, '商談向け個室'),
('table-yaesu-08', 'yaesu', 'C2', '接待個室C2', 8, 'private', 'private', false, true, '接待向け個室'),
-- Shinagawa (8 tables)
('table-shinagawa-01', 'shinagawa', 'A1', 'テーブルA1', 4, 'table', 'floor', false, true, NULL),
('table-shinagawa-02', 'shinagawa', 'A2', 'テーブルA2', 4, 'table', 'floor', false, true, NULL),
('table-shinagawa-03', 'shinagawa', 'A3', 'テーブルA3', 4, 'table', 'floor', true, true, '窓際'),
('table-shinagawa-04', 'shinagawa', 'A4', 'テーブルA4', 6, 'table', 'floor', false, true, NULL),
('table-shinagawa-05', 'shinagawa', 'B1', 'カウンターB1', 2, 'counter', 'counter', false, true, NULL),
('table-shinagawa-06', 'shinagawa', 'B2', 'カウンターB2', 2, 'counter', 'counter', false, true, NULL),
('table-shinagawa-07', 'shinagawa', 'C1', '個室C1', 8, 'private', 'private', false, true, '個室'),
('table-shinagawa-08', 'shinagawa', 'C2', '宴会個室C2', 10, 'private', 'private', false, true, '宴会個室'),
-- Yokohama (10 tables)
('table-yokohama-01', 'yokohama', 'A1', 'テーブルA1', 4, 'table', 'floor', true, true, '海が見える'),
('table-yokohama-02', 'yokohama', 'A2', 'テーブルA2', 4, 'table', 'floor', true, true, '海が見える'),
('table-yokohama-03', 'yokohama', 'A3', 'テーブルA3', 4, 'table', 'floor', false, true, NULL),
('table-yokohama-04', 'yokohama', 'A4', 'テーブルA4', 4, 'table', 'floor', false, true, NULL),
('table-yokohama-05', 'yokohama', 'A5', 'テーブルA5', 6, 'table', 'floor', false, true, '角席'),
('table-yokohama-06', 'yokohama', 'B1', 'カウンターB1', 2, 'counter', 'counter', false, true, NULL),
('table-yokohama-07', 'yokohama', 'B2', 'カウンターB2', 2, 'counter', 'counter', false, true, NULL),
('table-yokohama-08', 'yokohama', 'B3', 'カウンターB3', 2, 'counter', 'counter', false, true, NULL),
('table-yokohama-09', 'yokohama', 'C1', '個室C1', 8, 'private', 'private', false, true, '個室'),
('table-yokohama-10', 'yokohama', 'C2', '大宴会個室C2', 12, 'private', 'private', false, true, '大宴会個室');

-- ============================================
-- 4. MENU ITEMS (41 items for jinan branch)
-- Schema: id, branch_code, name, name_en, description, category, subcategory,
--         display_order, price, tax_rate, image_url, prep_time_minutes, kitchen_note,
--         is_available, is_popular, is_spicy, is_vegetarian, allergens
-- ============================================
INSERT INTO menu_items (id, branch_code, name, name_en, description, category, subcategory, price, display_order, is_available, is_popular, is_spicy, is_vegetarian, allergens, prep_time_minutes, kitchen_note) VALUES
('menu-001', 'jinan', '和牛上ハラミ', 'Premium Harami', '口の中でほどける柔らかさと濃厚な味わい。当店自慢の一品', 'meat', 'beef', 1800, 1, true, true, false, false, NULL, 5, '焼き加減はレアがおすすめ'),
('menu-002', 'jinan', '厚切り上タン塩', 'Thick Sliced Beef Tongue', '贅沢な厚切り。歯ごたえと肉汁が溢れます', 'meat', 'beef', 2200, 2, true, true, false, false, NULL, 6, '厚切りのため中心まで火を通す'),
('menu-003', 'jinan', '特選カルビ', 'Premium Kalbi', '霜降りが美しい最高級カルビ', 'meat', 'beef', 1800, 3, true, true, false, false, NULL, 5, NULL),
('menu-004', 'jinan', 'カルビ', 'Kalbi', '定番の人気メニュー。ジューシーな味わい', 'meat', 'beef', 1500, 4, true, false, false, false, NULL, 5, NULL),
('menu-005', 'jinan', '上ロース', 'Premium Sirloin', '赤身の旨味が楽しめる上質なロース', 'meat', 'beef', 1700, 5, true, false, false, false, NULL, 5, NULL),
('menu-006', 'jinan', 'ロース', 'Sirloin', 'あっさりとした赤身の美味しさ', 'meat', 'beef', 1400, 6, true, false, false, false, NULL, 5, NULL),
('menu-007', 'jinan', 'ホルモン盛り合わせ', 'Offal Assortment', '新鮮なホルモンをたっぷり。ミノ・ハチノス・シマチョウ', 'meat', 'offal', 1400, 7, true, false, false, false, NULL, 7, '新鮮なうちに提供'),
('menu-008', 'jinan', '特選盛り合わせ', 'Special Assortment', '本日のおすすめ希少部位を贅沢に盛り合わせ', 'meat', 'beef', 4500, 8, true, true, false, false, NULL, 8, '4種盛り'),
('menu-009', 'jinan', '豚カルビ', 'Pork Kalbi', '甘みのある豚バラ肉', 'meat', 'pork', 900, 9, true, false, false, false, NULL, 5, NULL),
('menu-010', 'jinan', '鶏もも', 'Chicken Thigh', '柔らかくジューシーな鶏もも肉', 'meat', 'chicken', 800, 10, true, false, false, false, NULL, 5, NULL),
('menu-011', 'jinan', '生ビール', 'Draft Beer', 'キンキンに冷えた生ビール（中）', 'drinks', 'beer', 600, 1, true, false, false, false, NULL, 1, NULL),
('menu-012', 'jinan', '瓶ビール', 'Bottled Beer', 'アサヒスーパードライ', 'drinks', 'beer', 650, 2, true, false, false, false, NULL, 1, NULL),
('menu-013', 'jinan', 'ハイボール', 'Highball', 'すっきり爽やかなウイスキーソーダ', 'drinks', 'whisky', 500, 3, true, false, false, false, NULL, 1, NULL),
('menu-014', 'jinan', 'レモンサワー', 'Lemon Sour', '自家製レモンサワー。さっぱり飲みやすい', 'drinks', 'sour', 500, 4, true, false, false, false, NULL, 1, NULL),
('menu-015', 'jinan', '梅酒サワー', 'Plum Wine Sour', '甘酸っぱい梅酒ソーダ割り', 'drinks', 'sour', 550, 5, true, false, false, false, NULL, 1, NULL),
('menu-016', 'jinan', 'マッコリ', 'Makgeolli', '韓国の伝統酒。まろやかな甘さ', 'drinks', 'korean', 600, 6, true, false, false, false, NULL, 1, NULL),
('menu-017', 'jinan', '焼酎（芋）', 'Sweet Potato Shochu', '本格芋焼酎。ロック・水割り・お湯割り', 'drinks', 'shochu', 500, 7, true, false, false, false, NULL, 1, NULL),
('menu-018', 'jinan', 'ウーロン茶', 'Oolong Tea', 'ソフトドリンク', 'drinks', 'soft', 300, 8, true, false, false, false, NULL, 1, NULL),
('menu-019', 'jinan', 'コーラ', 'Cola', 'コカ・コーラ', 'drinks', 'soft', 300, 9, true, false, false, false, NULL, 1, NULL),
('menu-020', 'jinan', 'オレンジジュース', 'Orange Juice', '100%フレッシュジュース', 'drinks', 'soft', 400, 10, true, false, false, false, NULL, 1, NULL),
('menu-021', 'jinan', 'キムチ盛り合わせ', 'Kimchi Assortment', '白菜・大根・きゅうりの3種盛り', 'side', 'korean', 500, 1, true, false, true, true, NULL, 2, NULL),
('menu-022', 'jinan', 'ナムル盛り合わせ', 'Namul Assortment', 'ほうれん草・もやし・ぜんまいの3種', 'side', 'korean', 500, 2, true, false, false, true, NULL, 3, NULL),
('menu-023', 'jinan', 'チョレギサラダ', 'Choregi Salad', 'シャキシャキ野菜のごま油ドレッシング', 'side', 'salad', 600, 3, true, false, false, true, 'ごま', 3, NULL),
('menu-024', 'jinan', '石焼ビビンバ', 'Stone-grilled Bibimbap', 'おこげが香ばしい定番〆メニュー', 'rice', 'korean', 1200, 1, true, true, false, false, '卵', 10, 'おこげを作る'),
('menu-025', 'jinan', '冷麺', 'Cold Noodles', '弾力ある麺と爽やかなスープ', 'noodle', 'korean', 900, 2, true, false, false, false, '小麦・卵', 5, '夏季限定'),
('menu-026', 'jinan', 'カルビクッパ', 'Kalbi Soup with Rice', '旨味たっぷりのスープにご飯を添えて', 'rice', 'korean', 1000, 3, true, false, false, false, NULL, 8, NULL),
('menu-027', 'jinan', 'ライス', 'Rice', '国産コシヒカリ', 'rice', 'japanese', 300, 4, true, false, false, true, NULL, 2, NULL),
('menu-028', 'jinan', 'わかめスープ', 'Seaweed Soup', '優しい味わいの定番スープ', 'soup', 'korean', 400, 1, true, false, false, true, NULL, 3, NULL),
('menu-029', 'jinan', 'たまごスープ', 'Egg Soup', 'ふわふわ卵のやさしいスープ', 'soup', 'japanese', 400, 2, true, false, false, false, '卵', 3, NULL),
('menu-030', 'jinan', 'テールスープ', 'Oxtail Soup', 'じっくり煮込んだ本格派', 'soup', 'korean', 800, 3, true, false, false, false, NULL, 5, '朝から仕込み'),
('menu-031', 'jinan', 'バニラアイス', 'Vanilla Ice Cream', '濃厚バニラアイス', 'dessert', 'ice', 400, 1, true, false, false, false, '乳', 1, NULL),
('menu-032', 'jinan', '抹茶アイス', 'Matcha Ice Cream', '京都産宇治抹茶使用', 'dessert', 'ice', 450, 2, true, false, false, false, '乳', 1, NULL),
('menu-033', 'jinan', 'シャーベット3種', 'Sorbet Trio', 'ゆず・マンゴー・ライチ', 'dessert', 'ice', 500, 3, true, false, false, true, NULL, 1, NULL),
('menu-034', 'jinan', '杏仁豆腐', 'Almond Jelly', 'なめらかな食感の本格杏仁', 'dessert', 'chinese', 450, 4, true, false, false, false, 'アーモンド・乳', 2, NULL),
('menu-035', 'jinan', '焼肉弁当（上）', 'Premium Yakiniku Bento', '上カルビ・上ロース・ナムル・キムチ', 'bento', 'takeout', 1800, 1, true, true, false, false, NULL, 15, 'テイクアウト用'),
('menu-036', 'jinan', '焼肉弁当（並）', 'Regular Yakiniku Bento', 'カルビ・ロース・ナムル・キムチ', 'bento', 'takeout', 1200, 2, true, false, false, false, NULL, 12, 'テイクアウト用'),
('menu-037', 'jinan', 'タン塩弁当', 'Beef Tongue Bento', '厚切りタン塩・ナムル・サラダ', 'bento', 'takeout', 1500, 3, true, false, false, false, NULL, 12, 'テイクアウト用'),
('menu-038', 'jinan', '飲み放題（90分）', 'All-You-Can-Drink 90min', 'ビール・サワー・焼酎・ソフトドリンク', 'course', 'drink', 1500, 1, true, false, false, false, NULL, 0, '要予約'),
('menu-039', 'jinan', '飲み放題（120分）', 'All-You-Can-Drink 120min', 'ビール・サワー・焼酎・ソフトドリンク', 'course', 'drink', 2000, 2, true, false, false, false, NULL, 0, '要予約'),
('menu-040', 'jinan', '贅沢コース', 'Luxury Course', '前菜・特選5種盛り・〆・デザート', 'course', 'food', 8000, 3, true, true, false, false, NULL, 0, '要予約・2名様より'),
('menu-041', 'jinan', '宴会コース', 'Party Course', '前菜・焼肉盛り合わせ・〆・デザート+飲み放題', 'course', 'food', 5500, 4, true, false, false, false, NULL, 0, '要予約・4名様より');

-- ============================================
-- 5. GLOBAL CUSTOMERS (100 customers)
-- ============================================
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
('cust-020', '090-2000-0020', '原田 翔', 'harada.sho@email.jp', '2024-05-01 10:00:00'),
('cust-021', '090-2000-0021', '中島 由美子', 'nakajima.yumiko@email.jp', '2024-05-05 15:00:00'),
('cust-022', '090-2000-0022', '石田 陽子', 'ishida.yoko@email.jp', '2024-05-10 18:30:00'),
('cust-023', '090-2000-0023', '山口 達也', 'yamaguchi.tatsuya@email.jp', '2024-05-15 12:15:00'),
('cust-024', '090-2000-0024', '松田 恵', 'matsuda.megumi@email.jp', '2024-05-20 17:00:00'),
('cust-025', '090-2000-0025', '井田 拓真', 'ida.takuma@email.jp', '2024-05-25 14:30:00'),
('cust-026', '090-2000-0026', '中山 愛', 'nakayama.ai@email.jp', '2024-06-01 11:00:00'),
('cust-027', '090-2000-0027', '小野 健司', 'ono.kenji@email.jp', '2024-06-05 16:45:00'),
('cust-028', '090-2000-0028', '高田 美香', 'takada.mika@email.jp', '2024-06-10 13:00:00'),
('cust-029', '090-2000-0029', '福田 誠一', 'fukuda.seiichi@email.jp', '2024-06-15 19:00:00'),
('cust-030', '090-2000-0030', '西村 健', 'nishimura.ken@email.jp', '2024-06-20 10:30:00'),
('cust-031', '090-2000-0031', '三浦 彩', 'miura.aya@email.jp', '2024-06-25 15:15:00'),
('cust-032', '090-2000-0032', '藤本 大地', 'fujimoto.daichi@email.jp', '2024-07-01 12:45:00'),
('cust-033', '090-2000-0033', '岩田 美咲', 'iwata.misaki@email.jp', '2024-07-05 18:00:00'),
('cust-034', '090-2000-0034', '中田 良平', 'nakata.ryohei@email.jp', '2024-07-10 14:30:00'),
('cust-035', '090-2000-0035', '横山 さやか', 'yokoyama.sayaka@email.jp', '2024-07-15 11:15:00'),
('cust-036', '090-2000-0036', '上野 剛', 'ueno.tsuyoshi@email.jp', '2024-07-20 17:30:00'),
('cust-037', '090-2000-0037', '金子 美優', 'kaneko.miyu@email.jp', '2024-07-25 13:45:00'),
('cust-038', '090-2000-0038', '大野 康介', 'ohno.kosuke@email.jp', '2024-08-01 10:15:00'),
('cust-039', '090-2000-0039', '小山 真理', 'koyama.mari@email.jp', '2024-08-05 16:00:00'),
('cust-040', '090-2000-0040', '野口 拓也', 'noguchi.takuya@email.jp', '2024-08-10 12:30:00'),
('cust-041', '090-2000-0041', '菅原 恵子', 'sugawara.keiko@email.jp', '2024-08-15 19:15:00'),
('cust-042', '090-2000-0042', '新井 翔太', 'arai.shota@email.jp', '2024-08-20 15:00:00'),
('cust-043', '090-2000-0043', '千葉 麻衣', 'chiba.mai@email.jp', '2024-08-25 11:30:00'),
('cust-044', '090-2000-0044', '佐野 大輔', 'sano.daisuke@email.jp', '2024-09-01 18:00:00'),
('cust-045', '090-2000-0045', '渡部 由美', 'watabe.yumi@email.jp', '2024-09-05 14:15:00'),
('cust-046', '090-2000-0046', '北村 健一', 'kitamura.kenichi@email.jp', '2024-09-10 10:45:00'),
('cust-047', '090-2000-0047', '斎藤 美香', 'saito.mika@email.jp', '2024-09-15 17:00:00'),
('cust-048', '090-2000-0048', '安藤 誠', 'ando.makoto@email.jp', '2024-09-20 13:30:00'),
('cust-049', '090-2000-0049', '河野 彩乃', 'kono.ayano@email.jp', '2024-09-25 20:00:00'),
('cust-050', '090-2000-0050', '内田 浩二', 'uchida.koji@email.jp', '2024-10-01 16:15:00'),
('cust-051', '090-2000-0051', '宮本 優子', 'miyamoto.yuko@email.jp', '2024-10-05 12:00:00'),
('cust-052', '090-2000-0052', '島田 太郎', 'shimada.taro@email.jp', '2024-10-10 18:45:00'),
('cust-053', '090-2000-0053', '森本 真由', 'morimoto.mayu@email.jp', '2024-10-15 15:30:00'),
('cust-054', '090-2000-0054', '柴田 健太', 'shibata.kenta@email.jp', '2024-10-20 11:00:00'),
('cust-055', '090-2000-0055', '久保 愛', 'kubo.ai@email.jp', '2024-10-25 17:45:00'),
('cust-056', '090-2000-0056', '平野 一郎', 'hirano.ichiro@email.jp', '2024-11-01 14:00:00'),
('cust-057', '090-2000-0057', '松永 美咲', 'matsunaga.misaki@email.jp', '2024-11-05 10:30:00'),
('cust-058', '090-2000-0058', '福島 達也', 'fukushima.tatsuya@email.jp', '2024-11-10 16:45:00'),
('cust-059', '090-2000-0059', '大橋 恵', 'ohashi.megumi@email.jp', '2024-11-15 13:15:00'),
('cust-060', '090-2000-0060', '吉村 拓真', 'yoshimura.takuma@email.jp', '2024-11-20 19:30:00'),
('cust-061', '090-2000-0061', '川島 由美子', 'kawashima.yumiko@email.jp', '2024-11-25 15:45:00'),
('cust-062', '090-2000-0062', '杉山 健司', 'sugiyama.kenji@email.jp', '2024-12-01 12:00:00'),
('cust-063', '090-2000-0063', '今井 美香', 'imai.mika@email.jp', '2024-12-05 18:15:00'),
('cust-064', '090-2000-0064', '田村 誠一', 'tamura.seiichi@email.jp', '2024-12-10 14:30:00'),
('cust-065', '090-2000-0065', '本田 彩', 'honda.aya@email.jp', '2024-12-15 11:00:00'),
('cust-066', '090-2000-0066', '谷口 大地', 'taniguchi.daichi@email.jp', '2024-12-20 17:15:00'),
('cust-067', '090-2000-0067', '武田 麻衣', 'takeda.mai@email.jp', '2024-12-25 13:45:00'),
('cust-068', '090-2000-0068', '永井 良平', 'nagai.ryohei@email.jp', '2025-01-01 20:00:00'),
('cust-069', '090-2000-0069', '西田 さやか', 'nishida.sayaka@email.jp', '2025-01-05 16:30:00'),
('cust-070', '090-2000-0070', '栗原 剛', 'kurihara.tsuyoshi@email.jp', '2025-01-10 12:45:00'),
('cust-071', '090-2000-0071', '山下 美優', 'yamashita.miyu@email.jp', '2025-01-15 19:00:00'),
('cust-072', '090-2000-0072', '竹内 康介', 'takeuchi.kosuke@email.jp', '2025-01-20 15:15:00'),
('cust-073', '090-2000-0073', '近藤 真理', 'kondo.mari@email.jp', '2025-01-25 11:30:00'),
('cust-074', '090-2000-0074', '石原 翔太', 'ishihara.shota@email.jp', '2025-02-01 18:00:00'),
('cust-075', '090-2000-0075', '増田 恵子', 'masuda.keiko@email.jp', '2025-02-05 14:15:00'),
('cust-076', '090-2000-0076', '望月 大輔', 'mochizuki.daisuke@email.jp', '2025-02-10 10:45:00'),
('cust-077', '090-2000-0077', '片山 由美', 'katayama.yumi@email.jp', '2025-02-15 17:00:00'),
('cust-078', '090-2000-0078', '秋山 健一', 'akiyama.kenichi@email.jp', '2025-02-20 13:30:00'),
('cust-079', '090-2000-0079', '内山 美香', 'uchiyama.mika@email.jp', '2025-02-25 20:00:00'),
('cust-080', '090-2000-0080', '早川 誠', 'hayakawa.makoto@email.jp', '2025-03-01 16:15:00'),
('cust-081', '090-2000-0081', '土井 彩乃', 'doi.ayano@email.jp', '2025-03-05 12:30:00'),
('cust-082', '090-2000-0082', '堀田 浩二', 'hotta.koji@email.jp', '2025-03-10 18:45:00'),
('cust-083', '090-2000-0083', '矢野 優子', 'yano.yuko@email.jp', '2025-03-15 15:00:00'),
('cust-084', '090-2000-0084', '浜田 太郎', 'hamada.taro@email.jp', '2025-03-20 11:15:00'),
('cust-085', '090-2000-0085', '星野 真由', 'hoshino.mayu@email.jp', '2025-03-25 17:30:00'),
('cust-086', '090-2000-0086', '村田 健太', 'murata.kenta@email.jp', '2025-04-01 13:45:00'),
('cust-087', '090-2000-0087', '宮崎 愛', 'miyazaki.ai@email.jp', '2025-04-05 20:15:00'),
('cust-088', '090-2000-0088', '関口 一郎', 'sekiguchi.ichiro@email.jp', '2025-04-10 16:30:00'),
('cust-089', '090-2000-0089', '丸山 美咲', 'maruyama.misaki@email.jp', '2025-04-15 12:45:00'),
('cust-090', '090-2000-0090', '平田 達也', 'hirata.tatsuya@email.jp', '2025-04-20 19:00:00'),
('cust-091', '090-2000-0091', '奥村 恵', 'okumura.megumi@email.jp', '2025-04-25 15:15:00'),
('cust-092', '090-2000-0092', '古川 拓真', 'furukawa.takuma@email.jp', '2025-05-01 11:30:00'),
('cust-093', '090-2000-0093', '飯田 由美子', 'iida.yumiko@email.jp', '2025-05-05 18:00:00'),
('cust-094', '090-2000-0094', '松井 健司', 'matsui.kenji@email.jp', '2025-05-10 14:15:00'),
('cust-095', '090-2000-0095', '水野 美香', 'mizuno.mika@email.jp', '2025-05-15 10:45:00'),
('cust-096', '090-2000-0096', '荒木 誠一', 'araki.seiichi@email.jp', '2025-05-20 17:00:00'),
('cust-097', '090-2000-0097', '大久保 彩', 'okubo.aya@email.jp', '2025-05-25 13:30:00'),
('cust-098', '090-2000-0098', '野田 大地', 'noda.daichi@email.jp', '2025-06-01 20:00:00'),
('cust-099', '090-2000-0099', '須藤 麻衣', 'sudo.mai@email.jp', '2025-06-05 16:15:00'),
('cust-100', '090-2000-0100', '宮田 良平', 'miyata.ryohei@email.jp', '2025-06-10 12:30:00');

-- ============================================
-- 6. BRANCH CUSTOMERS (relationships)
-- ============================================
INSERT INTO branch_customers (id, global_customer_id, branch_code, visit_count, last_visit, is_vip, notes) VALUES
-- Jinan branch (30 customers)
('bc-001', 'cust-001', 'jinan', 15, '2025-12-20 19:30:00', true, '常連様。いつもタン塩を注文される'),
('bc-002', 'cust-002', 'jinan', 8, '2025-11-15 18:00:00', false, 'お子様連れで来店。個室希望'),
('bc-003', 'cust-003', 'jinan', 3, '2025-10-01 20:00:00', false, '初回割引利用'),
('bc-004', 'cust-004', 'jinan', 22, '2026-01-10 19:00:00', true, 'VIP。特別なお祝いでよく利用'),
('bc-005', 'cust-005', 'jinan', 1, '2025-08-05 18:30:00', false, '一度きりの来店'),
('bc-006', 'cust-006', 'jinan', 12, '2025-12-01 20:30:00', true, '肉の焼き加減にこだわる。レア希望'),
('bc-007', 'cust-007', 'jinan', 5, '2025-09-20 19:00:00', false, 'アレルギー（甲殻類）あり'),
('bc-008', 'cust-008', 'jinan', 18, '2026-01-25 18:30:00', true, 'ワイン好き。記念日利用多し'),
('bc-009', 'cust-009', 'jinan', 2, '2025-07-10 19:30:00', false, 'クーポン利用のみ'),
('bc-010', 'cust-010', 'jinan', 10, '2025-11-30 20:00:00', true, '大人数宴会でよく予約'),
('bc-011', 'cust-011', 'jinan', 1, '2025-06-01 18:00:00', false, '料理の提供が遅いとクレーム'),
('bc-012', 'cust-012', 'jinan', 7, '2025-10-15 19:00:00', false, '静かな席希望。デート利用'),
('bc-013', 'cust-013', 'jinan', 4, '2025-09-05 18:30:00', false, '辛いもの好き'),
('bc-014', 'cust-014', 'jinan', 20, '2026-02-01 19:30:00', true, '会社の接待でよく利用。上質な肉希望'),
('bc-015', 'cust-015', 'jinan', 3, '2025-08-20 20:00:00', false, 'ベジタリアン向けメニュー希望'),
('bc-016', 'cust-016', 'jinan', 1, '2025-07-15 18:00:00', false, '予約時間に遅刻。30分待ち'),
('bc-017', 'cust-017', 'jinan', 9, '2025-11-10 19:00:00', false, '写真撮影好き。インスタ投稿'),
('bc-018', 'cust-018', 'jinan', 25, '2026-01-20 20:30:00', true, '創業時からの常連様。最高級コース'),
('bc-019', 'cust-019', 'jinan', 2, '2025-08-01 18:30:00', false, '価格について質問多い'),
('bc-020', 'cust-020', 'jinan', 6, '2025-10-05 19:00:00', false, '禁煙席希望。匂いに敏感'),
('bc-021', 'cust-021', 'jinan', 1, '2025-06-20 18:00:00', false, 'サービスに不満。二度と来ないと発言'),
('bc-022', 'cust-022', 'jinan', 11, '2025-12-10 19:30:00', true, '誕生日ケーキ持ち込み許可済'),
('bc-023', 'cust-023', 'jinan', 4, '2025-09-15 20:00:00', false, '飲み放題プラン好き'),
('bc-024', 'cust-024', 'jinan', 8, '2025-11-01 18:30:00', false, '子供用メニュー注文'),
('bc-025', 'cust-025', 'jinan', 2, '2025-07-25 19:00:00', false, '前回の会計ミスで返金対応済'),
('bc-026', 'cust-026', 'jinan', 15, '2025-12-25 20:00:00', true, 'クリスマス毎年予約。ロマンチックな席希望'),
('bc-027', 'cust-027', 'jinan', 1, '2025-06-10 18:00:00', false, 'メニューが分かりにくいとフィードバック'),
('bc-028', 'cust-028', 'jinan', 7, '2025-10-20 19:30:00', false, 'ホルモン専門。通な注文'),
('bc-029', 'cust-029', 'jinan', 3, '2025-08-15 18:30:00', false, '早めの時間帯希望。高齢者同伴'),
('bc-030', 'cust-030', 'jinan', 19, '2026-01-15 20:00:00', true, 'ワイン会幹事。大口注文'),
-- Shinjuku branch (10 customers)
('bc-031', 'cust-002', 'shinjuku', 5, '2025-11-20 19:00:00', false, '子供連れで訪問'),
('bc-032', 'cust-012', 'shinjuku', 8, '2025-12-15 18:30:00', true, 'カップル利用多い'),
('bc-033', 'cust-017', 'shinjuku', 12, '2026-01-05 20:00:00', true, 'SNS投稿有名人'),
('bc-034', 'cust-039', 'shinjuku', 6, '2025-10-30 19:30:00', false, '女子会グループ'),
('bc-035', 'cust-044', 'shinjuku', 15, '2026-01-20 18:00:00', true, '法人様利用'),
('bc-036', 'cust-050', 'shinjuku', 3, '2025-09-10 19:00:00', false, '初来店'),
('bc-037', 'cust-055', 'shinjuku', 7, '2025-11-25 20:30:00', false, 'ドリンク多め'),
('bc-038', 'cust-060', 'shinjuku', 10, '2025-12-20 19:00:00', true, '金曜夜常連'),
('bc-039', 'cust-065', 'shinjuku', 2, '2025-08-15 18:30:00', false, '偶然の来店'),
('bc-040', 'cust-070', 'shinjuku', 18, '2026-01-25 20:00:00', true, 'VIP個室常連'),
-- Yaesu branch (7 customers - business focus)
('bc-041', 'cust-003', 'yaesu', 8, '2025-12-01 12:30:00', true, 'ランチ常連'),
('bc-042', 'cust-007', 'yaesu', 4, '2025-10-20 18:00:00', false, 'アレルギー対応必要'),
('bc-043', 'cust-014', 'yaesu', 12, '2025-12-15 19:00:00', true, '接待利用多い'),
('bc-044', 'cust-036', 'yaesu', 6, '2025-11-10 19:30:00', false, '外国人ゲスト同伴'),
('bc-045', 'cust-048', 'yaesu', 3, '2025-09-25 12:00:00', false, 'ランチ初利用'),
('bc-046', 'cust-062', 'yaesu', 9, '2025-12-20 18:30:00', true, 'ビジネス常連'),
('bc-047', 'cust-075', 'yaesu', 2, '2025-08-30 12:30:00', false, '一回限り'),
-- Shinagawa branch (6 customers)
('bc-048', 'cust-032', 'shinagawa', 7, '2025-11-15 18:00:00', false, 'スポーツ選手'),
('bc-049', 'cust-037', 'shinagawa', 5, '2025-10-25 17:30:00', false, 'ファミリー'),
('bc-050', 'cust-045', 'shinagawa', 10, '2025-12-10 19:00:00', true, '記念日利用'),
('bc-051', 'cust-058', 'shinagawa', 3, '2025-09-05 18:30:00', false, '初来店'),
('bc-052', 'cust-072', 'shinagawa', 8, '2025-11-30 20:00:00', true, '常連様'),
('bc-053', 'cust-085', 'shinagawa', 2, '2025-08-20 19:00:00', false, '偶然の来店'),
-- Yokohama branch (8 customers)
('bc-054', 'cust-040', 'yokohama', 12, '2025-12-15 19:00:00', true, '年末年始常連'),
('bc-055', 'cust-050', 'yokohama', 8, '2025-11-20 18:30:00', true, 'VIP様'),
('bc-056', 'cust-056', 'yokohama', 5, '2025-10-10 19:30:00', false, '大家族'),
('bc-057', 'cust-066', 'yokohama', 10, '2026-01-05 18:00:00', true, '新年会幹事'),
('bc-058', 'cust-074', 'yokohama', 4, '2025-09-20 20:00:00', false, 'スポーツ観戦'),
('bc-059', 'cust-080', 'yokohama', 6, '2025-11-05 19:00:00', false, 'カップル'),
('bc-060', 'cust-090', 'yokohama', 3, '2025-10-25 18:30:00', false, '初来店'),
('bc-061', 'cust-095', 'yokohama', 7, '2025-12-01 20:00:00', false, 'リピーター');

-- ============================================
-- 7. CUSTOMER PREFERENCES
-- ============================================
INSERT INTO customer_preferences (id, branch_customer_id, preference, category, note, confidence, source) VALUES
('pref-001', 'bc-001', '厚切りタン塩', 'meat', '毎回必ず注文', 1.0, 'manual'),
('pref-002', 'bc-001', '窓際席希望', 'seating', '景色を楽しみたい', 1.0, 'booking'),
('pref-003', 'bc-002', '個室希望', 'seating', '子供が騒ぐため', 1.0, 'booking'),
('pref-004', 'bc-002', '子供用椅子必要', 'facility', '3歳のお子様', 1.0, 'manual'),
('pref-005', 'bc-004', '最高級和牛コース', 'meat', '接待・記念日用', 1.0, 'manual'),
('pref-006', 'bc-004', 'シャンパン好き', 'drinks', 'お祝い時に注文', 0.9, 'chat'),
('pref-007', 'bc-006', 'レア焼き', 'cooking', '生に近い状態が好き', 1.0, 'manual'),
('pref-008', 'bc-006', 'ハラミ', 'meat', '脂身少なめが好み', 1.0, 'chat'),
('pref-009', 'bc-007', '甲殻類アレルギー', 'allergy', 'エビ・カニNG', 1.0, 'manual'),
('pref-010', 'bc-008', '赤ワイン好き', 'drinks', 'ボルドー系希望', 1.0, 'manual'),
('pref-011', 'bc-008', '記念日利用', 'occasion', '年に3回程度', 0.85, 'chat'),
('pref-012', 'bc-010', '大人数宴会', 'occasion', '10名以上でよく予約', 1.0, 'booking'),
('pref-013', 'bc-010', '飲み放題プラン', 'drinks', '必ず利用', 1.0, 'manual'),
('pref-014', 'bc-012', '静かな席', 'seating', 'カップルでデート', 1.0, 'booking'),
('pref-015', 'bc-013', 'キムチ追加', 'side', '辛いもの好き', 0.8, 'chat'),
('pref-016', 'bc-014', '接待利用', 'occasion', '会社経費', 1.0, 'manual'),
('pref-017', 'bc-014', '上質な部位のみ', 'meat', '予算は気にしない', 1.0, 'manual'),
('pref-018', 'bc-017', '写真撮影OK', 'other', 'インスタ投稿', 0.9, 'chat'),
('pref-019', 'bc-018', '創業時から常連', 'loyalty', '特別対応必要', 1.0, 'manual'),
('pref-020', 'bc-018', 'VIPルーム', 'seating', 'プライバシー重視', 1.0, 'booking'),
('pref-021', 'bc-020', '禁煙席', 'seating', '匂いに敏感', 1.0, 'booking'),
('pref-022', 'bc-022', '持ち込みケーキOK', 'other', '誕生日対応済', 1.0, 'manual'),
('pref-023', 'bc-024', '子供メニュー', 'kids', 'お子様ランチ希望', 1.0, 'manual'),
('pref-024', 'bc-026', 'ロマンチックな席', 'seating', 'カップル席', 1.0, 'booking'),
('pref-025', 'bc-026', 'デザート盛り合わせ', 'dessert', '記念日用', 0.9, 'chat'),
('pref-026', 'bc-028', 'ホルモン系', 'meat', '通なオーダー', 0.85, 'chat'),
('pref-027', 'bc-030', 'ワイン会', 'occasion', '月1回開催', 1.0, 'manual'),
('pref-028', 'bc-030', '個室12名', 'seating', 'ワイン持ち込み可', 1.0, 'booking'),
('pref-029', 'bc-048', 'タンパク質重視', 'diet', 'アスリート食', 1.0, 'manual'),
('pref-030', 'bc-048', 'サラダ大盛り', 'side', '野菜多め', 0.9, 'chat');

-- ============================================
-- 8. BOOKINGS (25 sample bookings)
-- ============================================
INSERT INTO bookings (id, branch_code, branch_customer_id, guest_name, guest_phone, guest_email, date, time, guests, status, note, source) VALUES
('bk-001', 'jinan', 'bc-001', '佐々木 美咲', '090-2000-0001', 'sasaki.misaki@email.jp', '2025-06-20', '19:00', 3, 'confirmed', '厚切りタン塩希望', 'web'),
('bk-002', 'jinan', 'bc-004', '井上 大輔', '090-2000-0004', 'inoue.daisuke@email.jp', '2025-06-20', '19:30', 6, 'confirmed', '接待利用。VIP対応お願いします。シャンパン用意', 'phone'),
('bk-003', 'jinan', 'bc-006', '清水 翔太', '090-2000-0006', 'shimizu.shota@email.jp', '2025-06-20', '18:30', 2, 'confirmed', 'カウンター席希望', 'web'),
('bk-004', 'jinan', 'bc-008', '森田 一郎', '090-2000-0008', 'morita.ichiro@email.jp', '2025-06-21', '19:00', 4, 'confirmed', '記念日ケーキ持ち込み。赤ワイン準備', 'web'),
('bk-005', 'jinan', 'bc-010', '藤田 太郎', '090-2000-0010', 'fujita.taro@email.jp', '2025-06-21', '18:00', 10, 'confirmed', '宴会予約。飲み放題プラン', 'phone'),
('bk-006', 'jinan', 'bc-014', '長谷川 誠', '090-2000-0014', 'hasegawa.makoto@email.jp', '2025-06-22', '19:30', 5, 'confirmed', '会社接待。上質な部位でコース', 'web'),
('bk-007', 'jinan', 'bc-018', '村上 浩二', '090-2000-0018', 'murakami.koji@email.jp', '2025-06-22', '19:00', 2, 'confirmed', '常連様。いつものコース', 'phone'),
('bk-008', 'jinan', 'bc-022', '石田 陽子', '090-2000-0022', 'ishida.yoko@email.jp', '2025-06-23', '18:00', 4, 'pending', '誕生日サプライズ。ケーキ持ち込みOK済', 'web'),
('bk-009', 'jinan', 'bc-026', '中山 愛', '090-2000-0026', 'nakayama.ai@email.jp', '2025-06-23', '19:30', 2, 'confirmed', 'デート利用。ロマンチックな席で', 'chat'),
('bk-010', 'jinan', 'bc-030', '西村 健', '090-2000-0030', 'nishimura.ken@email.jp', '2025-06-24', '19:00', 12, 'confirmed', 'ワイン会。ワイン6本持ち込み', 'phone'),
('bk-011', 'shinjuku', 'bc-031', '木村 健太', '090-2000-0002', 'kimura.kenta@email.jp', '2025-06-20', '18:30', 4, 'confirmed', '子供連れ。個室希望。子供椅子必要', 'web'),
('bk-012', 'shinjuku', 'bc-032', '後藤 康平', '090-2000-0012', 'goto.kohei@email.jp', '2025-06-20', '19:00', 2, 'confirmed', 'デート。窓際席希望', 'web'),
('bk-013', 'shinjuku', 'bc-033', '藤井 美穂', '090-2000-0017', 'fujii.miho@email.jp', '2025-06-21', '20:00', 4, 'confirmed', '写真撮影OK確認済', 'web'),
('bk-014', 'shinjuku', 'bc-034', '女子会グループ', '090-2000-0039', 'group@email.jp', '2025-06-21', '19:00', 6, 'confirmed', '女子会プラン。サラダ多め', 'phone'),
('bk-015', 'shinjuku', 'bc-035', '法人様', '090-2000-0044', 'corp@email.jp', '2025-06-22', '18:30', 14, 'confirmed', '法人宴会。領収書必要', 'phone'),
('bk-016', 'yaesu', 'bc-041', '山本 真由美', '090-2000-0003', 'yamamoto.mayumi@email.jp', '2025-06-20', '12:00', 4, 'confirmed', 'ランチ商談', 'web'),
('bk-017', 'yaesu', 'bc-042', '松本 愛', '090-2000-0007', 'matsumoto.ai@email.jp', '2025-06-20', '19:00', 2, 'confirmed', 'アレルギー注意。甲殻類NG', 'web'),
('bk-018', 'yaesu', 'bc-044', '外国人ゲスト様', '090-2000-0036', 'foreigner@email.jp', '2025-06-21', '19:30', 6, 'pending', '英語対応必要。英語メニュー', 'phone'),
('bk-019', 'shinagawa', 'bc-048', 'アスリート様', '090-2000-0032', 'athlete@email.jp', '2025-06-20', '18:00', 3, 'confirmed', '高タンパク食。サラダ大盛り', 'web'),
('bk-020', 'shinagawa', 'bc-049', 'ファミリー様', '090-2000-0037', 'family@email.jp', '2025-06-21', '17:30', 4, 'confirmed', '赤ちゃん連れ。ベビーカーあり', 'phone'),
('bk-021', 'yokohama', 'bc-054', '年末常連様', '090-2000-0040', 'regular@email.jp', '2025-06-20', '19:00', 4, 'confirmed', '窓際で海を見ながら', 'web'),
('bk-022', 'yokohama', 'bc-055', 'VIP様', '090-2000-0050', 'vip@email.jp', '2025-06-21', '19:30', 8, 'confirmed', '特上盛り合わせ希望。VIP対応', 'phone'),
('bk-023', 'jinan', NULL, '山田 太郎', '090-9999-0001', NULL, '2025-06-20', '20:00', 4, 'confirmed', '新規のお客様', 'walk_in'),
('bk-024', 'jinan', NULL, '田中 花子', '090-9999-0002', NULL, '2025-06-21', '18:30', 2, 'cancelled', 'キャンセル', 'web'),
('bk-025', 'shinjuku', NULL, '新規様', '090-9999-0003', NULL, '2025-06-22', '19:00', 3, 'pending', '確認待ち', 'web');

-- ============================================
-- Summary Statistics
-- ============================================
-- Branches: 5
-- Staff: 34
-- Tables: 47
-- Menu Items: 41
-- Global Customers: 100
-- Branch Customers: 61 (bc-001 to bc-061)
-- Customer Preferences: 30 (pref-001 to pref-030)
-- Bookings: 25 (bk-001 to bk-025)
