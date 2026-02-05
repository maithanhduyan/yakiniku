-- ============================================
-- Yakiniku.io Platform - Complete Seed Data
-- Generated: 2026-02-05
-- Chain: ç„¼è‚‰ã‚¸ãƒŠãƒ³ (Yakiniku JIAN)
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
-- æœ¬åº— (Head Office) - Kawasaki Hirama
('branch-001', 'hirama', 'ç„¼è‚‰ã‚¸ãƒŠãƒ³ å¹³é–“æœ¬åº—', 'hirama', '044-555-0001', 'ã€’211-0012 ç¥žå¥ˆå·çœŒå·å´Žå¸‚ä¸­åŽŸåŒºä¸­ä¸¸å­571-13 ãƒŸãƒ¤ã‚¿ãƒžãƒ³ã‚·ãƒ§ãƒ³101', '#d4af37', '#1a1a1a', '17:00', '23:00', '22:30', '[2]', 40, 1, datetime('now')),
-- æ–°å®¿åº— - Shinjuku (B1 basement)
('branch-002', 'shinjuku', 'ç„¼è‚‰ã‚¸ãƒŠãƒ³ æ–°å®¿åº—', 'shinjuku', '03-5555-0002', 'ã€’160-0023 æ±äº¬éƒ½æ–°å®¿åŒºè¥¿æ–°å®¿1ä¸ç›®13-8 æœæ—¥æ–°å®¿ãƒ“ãƒ« B1F', '#d4af37', '#1a1a1a', '11:30', '23:30', '23:00', '[]', 60, 1, datetime('now')),
-- å…«é‡æ´²åº— - Yaesu (Tokyo Station area)
('branch-003', 'yaesu', 'ç„¼è‚‰ã‚¸ãƒŠãƒ³ å…«é‡æ´²åº—', 'yaesu', '03-5555-0003', 'ã€’103-0028 æ±äº¬éƒ½ä¸­å¤®åŒºå…«é‡æ´²1ä¸ç›®5-10 ãƒˆãƒ¼ã‚¤ãƒ³å…«é‡æ´²ãƒ“ãƒ« 1F', '#d4af37', '#1a1a1a', '11:00', '22:00', '21:30', '[0]', 35, 1, datetime('now')),
-- å“å·åº— - Shinagawa
('branch-004', 'shinagawa', 'ç„¼è‚‰ã‚¸ãƒŠãƒ³ å“å·åº—', 'shinagawa', '03-5555-0004', 'ã€’141-0043 æ±äº¬éƒ½å“å·åŒºäºŒè‘‰1ä¸ç›®16-17', '#d4af37', '#1a1a1a', '17:00', '23:00', '22:30', '[1]', 45, 1, datetime('now')),
-- æ¨ªæµœåº— - Yokohama Kannai
('branch-005', 'yokohama', 'ç„¼è‚‰ã‚¸ãƒŠãƒ³ æ¨ªæµœé–¢å†…åº—', 'yokohama', '045-555-0005', 'ã€’231-0013 ç¥žå¥ˆå·çœŒæ¨ªæµœå¸‚ä¸­åŒºä½å‰ç”º5ä¸ç›®65-2 ã‚¢ã‚½ãƒ«ãƒ†ã‚£ 1F', '#d4af37', '#1a1a1a', '17:00', '24:00', '23:30', '[2]', 50, 1, datetime('now'));

-- ============ STAFF (6-8 per branch = ~35 total) ============
-- å¹³é–“æœ¬åº— Staff (8äºº)
INSERT INTO staff (id, employee_id, branch_code, name, name_kana, phone, email, role, pin_code, is_active, hire_date, created_at) VALUES
('staff-001', 'J001', 'hirama', 'å±±ç”° å¤ªéƒŽ', 'ãƒ¤ãƒžãƒ€ ã‚¿ãƒ­ã‚¦', '090-1111-0001', 'yamada@jp', 'admin', '111111', 1, '2020-04-01', datetime('now')),
('staff-002', 'J002', 'hirama', 'ä½è—¤ èŠ±å­', 'ã‚µãƒˆã‚¦ ãƒãƒŠã‚³', '090-1111-0002', 'sato@jp', 'manager', '222222', 1, '2020-04-01', datetime('now')),
('staff-003', 'J003', 'hirama', 'ç”°ä¸­ ä¸€éƒŽ', 'ã‚¿ãƒŠã‚« ã‚¤ãƒãƒ­ã‚¦', '090-1111-0003', 'tanaka@jp', 'cashier', '333333', 1, '2021-06-15', datetime('now')),
('staff-004', 'J004', 'hirama', 'éˆ´æœ¨ ç¾Žå’²', 'ã‚¹ã‚ºã‚­ ãƒŸã‚µã‚­', '090-1111-0004', 'suzuki@jp', 'waiter', '444444', 1, '2022-01-10', datetime('now')),
('staff-005', 'J005', 'hirama', 'é«˜æ©‹ å¥å¤ª', 'ã‚¿ã‚«ãƒã‚· ã‚±ãƒ³ã‚¿', '090-1111-0005', 'takahashi@jp', 'waiter', '555555', 1, '2022-03-20', datetime('now')),
('staff-006', 'J006', 'hirama', 'ä¼Šè—¤ ã•ãã‚‰', 'ã‚¤ãƒˆã‚¦ ã‚µã‚¯ãƒ©', '090-1111-0006', 'ito@jp', 'kitchen', '666666', 1, '2023-04-01', datetime('now')),
('staff-007', 'J007', 'hirama', 'æ¸¡è¾º å¤§è¼”', 'ãƒ¯ã‚¿ãƒŠãƒ™ ãƒ€ã‚¤ã‚¹ã‚±', '090-1111-0007', 'watanabe@jp', 'kitchen', '777777', 1, '2021-08-01', datetime('now')),
('staff-008', 'J008', 'hirama', 'ä¸­æ‘ çœŸç”±ç¾Ž', 'ãƒŠã‚«ãƒ ãƒ© ãƒžãƒ¦ãƒŸ', '090-1111-0008', 'nakamura@jp', 'receptionist', '888888', 1, '2022-07-15', datetime('now')),

-- æ–°å®¿åº— Staff (8äºº)
('staff-011', 'S001', 'shinjuku', 'å°æž— ç¿”å¤ª', 'ã‚³ãƒãƒ¤ã‚· ã‚·ãƒ§ã‚¦ã‚¿', '090-2111-0001', 'kobayashi@shinjuku.jp', 'admin', '111111', 1, '2021-04-01', datetime('now')),
('staff-012', 'S002', 'shinjuku', 'åŠ è—¤ æ„›', 'ã‚«ãƒˆã‚¦ ã‚¢ã‚¤', '090-2111-0002', 'kato@shinjuku.jp', 'manager', '222222', 1, '2021-04-01', datetime('now')),
('staff-013', 'S003', 'shinjuku', 'å‰ç”° éš†', 'ãƒ¨ã‚·ãƒ€ ã‚¿ã‚«ã‚·', '090-2111-0003', 'yoshida@shinjuku.jp', 'cashier', '333333', 1, '2022-01-10', datetime('now')),
('staff-014', 'S004', 'shinjuku', 'å±±å£ ç¾Žå„ª', 'ãƒ¤ãƒžã‚°ãƒ ãƒŸãƒ¦ã‚¦', '090-2111-0004', 'yamaguchi@shinjuku.jp', 'waiter', '444444', 1, '2022-06-01', datetime('now')),
('staff-015', 'S005', 'shinjuku', 'æ¾æœ¬ å¤§åœ°', 'ãƒžãƒ„ãƒ¢ãƒˆ ãƒ€ã‚¤ãƒ', '090-2111-0005', 'matsumoto@shinjuku.jp', 'waiter', '555555', 1, '2023-01-15', datetime('now')),
('staff-016', 'S006', 'shinjuku', 'äº•ä¸Š çµè¡£', 'ã‚¤ãƒŽã‚¦ã‚¨ ãƒ¦ã‚¤', '090-2111-0006', 'inoue@shinjuku.jp', 'waiter', '666666', 1, '2023-04-01', datetime('now')),
('staff-017', 'S007', 'shinjuku', 'æœ¨æ‘ æ‹“ä¹Ÿ', 'ã‚­ãƒ ãƒ© ã‚¿ã‚¯ãƒ¤', '090-2111-0007', 'kimura@shinjuku.jp', 'kitchen', '777777', 1, '2021-08-01', datetime('now')),
('staff-018', 'S008', 'shinjuku', 'æž— ç¾Žç©‚', 'ãƒãƒ¤ã‚· ãƒŸãƒ›', '090-2111-0008', 'hayashi@shinjuku.jp', 'kitchen', '888888', 1, '2022-03-01', datetime('now')),

-- å…«é‡æ´²åº— Staff (6äºº)
('staff-021', 'Y001', 'yaesu', 'æ¸…æ°´ èª ', 'ã‚·ãƒŸã‚º ãƒžã‚³ãƒˆ', '090-3111-0001', 'shimizu@yaesu.jp', 'admin', '111111', 1, '2022-04-01', datetime('now')),
('staff-022', 'Y002', 'yaesu', 'æ£®ç”° ã•ã‚„ã‹', 'ãƒ¢ãƒªã‚¿ ã‚µãƒ¤ã‚«', '090-3111-0002', 'morita@yaesu.jp', 'manager', '222222', 1, '2022-04-01', datetime('now')),
('staff-023', 'Y003', 'yaesu', 'å²¡ç”° æµ©äºŒ', 'ã‚ªã‚«ãƒ€ ã‚³ã‚¦ã‚¸', '090-3111-0003', 'okada@yaesu.jp', 'cashier', '333333', 1, '2022-08-01', datetime('now')),
('staff-024', 'Y004', 'yaesu', 'å‰ç”° å‡›', 'ãƒžã‚¨ãƒ€ ãƒªãƒ³', '090-3111-0004', 'maeda@yaesu.jp', 'waiter', '444444', 1, '2023-01-10', datetime('now')),
('staff-025', 'Y005', 'yaesu', 'è—¤äº• å¥', 'ãƒ•ã‚¸ã‚¤ ã‚±ãƒ³', '090-3111-0005', 'fujii@yaesu.jp', 'waiter', '555555', 1, '2023-04-01', datetime('now')),
('staff-026', 'Y006', 'yaesu', 'æ‘ä¸Š äºœç¾Ž', 'ãƒ ãƒ©ã‚«ãƒŸ ã‚¢ãƒŸ', '090-3111-0006', 'murakami@yaesu.jp', 'kitchen', '666666', 1, '2022-06-01', datetime('now')),

-- å“å·åº— Staff (6äºº)
('staff-031', 'G001', 'shinagawa', 'å¤ªç”° å‹‡æ°—', 'ã‚ªã‚ªã‚¿ ãƒ¦ã‚¦ã‚­', '090-4111-0001', 'ota@shinagawa.jp', 'admin', '111111', 1, '2022-10-01', datetime('now')),
('staff-032', 'G002', 'shinagawa', 'çŸ³äº• éº»è¡£', 'ã‚¤ã‚·ã‚¤ ãƒžã‚¤', '090-4111-0002', 'ishii@shinagawa.jp', 'manager', '222222', 1, '2022-10-01', datetime('now')),
('staff-033', 'G003', 'shinagawa', 'å¾Œè—¤ ç¿”', 'ã‚´ãƒˆã‚¦ ã‚·ãƒ§ã‚¦', '090-4111-0003', 'goto@shinagawa.jp', 'cashier', '333333', 1, '2023-01-15', datetime('now')),
('staff-034', 'G004', 'shinagawa', 'å‚æœ¬ å½©ä¹ƒ', 'ã‚µã‚«ãƒ¢ãƒˆ ã‚¢ãƒ¤ãƒŽ', '090-4111-0004', 'sakamoto@shinagawa.jp', 'waiter', '444444', 1, '2023-04-01', datetime('now')),
('staff-035', 'G005', 'shinagawa', 'é•·è°·å· è“®', 'ãƒã‚»ã‚¬ãƒ¯ ãƒ¬ãƒ³', '090-4111-0005', 'hasegawa@shinagawa.jp', 'waiter', '555555', 1, '2023-07-01', datetime('now')),
('staff-036', 'G006', 'shinagawa', 'è¿‘è—¤ ç¾Žæœˆ', 'ã‚³ãƒ³ãƒ‰ã‚¦ ãƒŸãƒ…ã‚­', '090-4111-0006', 'kondo@shinagawa.jp', 'kitchen', '666666', 1, '2023-01-01', datetime('now')),

-- æ¨ªæµœåº— Staff (6äºº)
('staff-041', 'K001', 'yokohama', 'æ–Žè—¤ å¤§æ¨¹', 'ã‚µã‚¤ãƒˆã‚¦ ãƒ€ã‚¤ã‚­', '090-5111-0001', 'saito@yokohama.jp', 'admin', '111111', 1, '2023-04-01', datetime('now')),
('staff-042', 'K002', 'yokohama', 'é è—¤ çœŸç†', 'ã‚¨ãƒ³ãƒ‰ã‚¦ ãƒžãƒª', '090-5111-0002', 'endo@yokohama.jp', 'manager', '222222', 1, '2023-04-01', datetime('now')),
('staff-043', 'K003', 'yokohama', 'åŽŸç”° èˆªå¹³', 'ãƒãƒ©ãƒ€ ã‚³ã‚¦ãƒ˜ã‚¤', '090-5111-0003', 'harada@yokohama.jp', 'cashier', '333333', 1, '2023-06-01', datetime('now')),
('staff-044', 'K004', 'yokohama', 'ä¸­å³¶ è‘µ', 'ãƒŠã‚«ã‚¸ãƒž ã‚¢ã‚ªã‚¤', '090-5111-0004', 'nakajima@yokohama.jp', 'waiter', '444444', 1, '2023-08-01', datetime('now')),
('staff-045', 'K005', 'yokohama', 'å°é‡Ž é™½å¤ª', 'ã‚ªãƒŽ ãƒ¨ã‚¦ã‚¿', '090-5111-0005', 'ono@yokohama.jp', 'waiter', '555555', 1, '2024-01-15', datetime('now')),
('staff-046', 'K006', 'yokohama', 'ç«¹å†… å„ªèŠ±', 'ã‚¿ã‚±ã‚¦ãƒ ãƒ¦ã‚¦ã‚«', '090-5111-0006', 'takeuchi@yokohama.jp', 'kitchen', '666666', 1, '2023-10-01', datetime('now'));

-- ============ TABLES (per branch) ============
-- å¹³é–“æœ¬åº— Tables (8 tables, 40 seats max)
INSERT INTO tables (id, branch_code, table_number, name, min_capacity, max_capacity, table_type, floor, zone, has_window, is_smoking, is_wheelchair_accessible, has_baby_chair, status, is_active, priority, notes, created_at) VALUES
('table-j01', 'hirama', 'T1', 'ãƒ†ãƒ¼ãƒ–ãƒ«1', 2, 4, 'regular', 1, 'A', 0, 0, 1, 1, 'available', 1, 0, 'å…¥å£è¿‘ã', datetime('now')),
('table-j02', 'hirama', 'T2', 'ãƒ†ãƒ¼ãƒ–ãƒ«2', 2, 4, 'regular', 1, 'A', 1, 0, 1, 0, 'available', 1, 0, 'çª“éš›å¸­', datetime('now')),
('table-j03', 'hirama', 'T3', 'ãƒ†ãƒ¼ãƒ–ãƒ«3', 2, 4, 'regular', 1, 'A', 1, 0, 1, 1, 'available', 1, 0, 'çª“éš›å¸­', datetime('now')),
('table-j04', 'hirama', 'T4', 'ãƒ†ãƒ¼ãƒ–ãƒ«4', 2, 4, 'regular', 1, 'B', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-j05', 'hirama', 'T5', 'ãƒ†ãƒ¼ãƒ–ãƒ«5', 2, 4, 'regular', 1, 'B', 0, 0, 1, 0, 'available', 1, 0, 'ãƒ‡ãƒ¢ç”¨ãƒ†ãƒ¼ãƒ–ãƒ«', datetime('now')),
('table-j06', 'hirama', 'T6', 'ãƒ†ãƒ¼ãƒ–ãƒ«6', 4, 6, 'regular', 1, 'B', 0, 0, 1, 1, 'available', 1, 0, 'å¤§äººæ•°å‘ã‘', datetime('now')),
('table-j07', 'hirama', 'VIP1', 'å€‹å®¤VIP', 4, 8, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, 'å®Œå…¨å€‹å®¤ãƒ»æŽ¥å¾…å‘ã‘', datetime('now')),
('table-j08', 'hirama', 'VIP2', 'åŠå€‹å®¤', 4, 6, 'private', 1, 'VIP', 0, 0, 1, 1, 'available', 1, 5, 'åŠå€‹å®¤ãƒ»å®¶æ—å‘ã‘', datetime('now')),

-- æ–°å®¿åº— Tables (11 tables, 60 seats max) - B1éšŽ
('table-s01', 'shinjuku', 'A1', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼1', 1, 2, 'counter', -1, 'Counter', 0, 0, 1, 0, 'available', 1, 0, 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼å¸­', datetime('now')),
('table-s02', 'shinjuku', 'A2', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼2', 1, 2, 'counter', -1, 'Counter', 0, 0, 1, 0, 'available', 1, 0, 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼å¸­', datetime('now')),
('table-s03', 'shinjuku', 'A3', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼3', 1, 2, 'counter', -1, 'Counter', 0, 0, 1, 0, 'available', 1, 0, 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼å¸­', datetime('now')),
('table-s04', 'shinjuku', 'B1', 'ãƒ†ãƒ¼ãƒ–ãƒ«1', 2, 4, 'regular', -1, 'Main', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-s05', 'shinjuku', 'B2', 'ãƒ†ãƒ¼ãƒ–ãƒ«2', 2, 4, 'regular', -1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-s06', 'shinjuku', 'B3', 'ãƒ†ãƒ¼ãƒ–ãƒ«3', 2, 4, 'regular', -1, 'Main', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-s07', 'shinjuku', 'B4', 'ãƒ†ãƒ¼ãƒ–ãƒ«4', 2, 4, 'regular', -1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-s08', 'shinjuku', 'C1', 'ãƒœãƒƒã‚¯ã‚¹å¸­1', 4, 6, 'regular', -1, 'Box', 0, 0, 1, 1, 'available', 1, 3, 'ãƒœãƒƒã‚¯ã‚¹å¸­', datetime('now')),
('table-s09', 'shinjuku', 'C2', 'ãƒœãƒƒã‚¯ã‚¹å¸­2', 4, 6, 'regular', -1, 'Box', 0, 0, 1, 0, 'available', 1, 3, 'ãƒœãƒƒã‚¯ã‚¹å¸­', datetime('now')),
('table-s10', 'shinjuku', 'VIP', 'å€‹å®¤', 6, 10, 'private', -1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, 'å®Œå…¨å€‹å®¤ãƒ»æŽ¥å¾…å‘ã‘', datetime('now')),
('table-s11', 'shinjuku', 'P1', 'ãƒ‘ãƒ¼ãƒ†ã‚£å¸­', 8, 12, 'regular', -1, 'Party', 0, 0, 1, 1, 'available', 1, 5, 'å®´ä¼šå‘ã‘', datetime('now')),

-- å…«é‡æ´²åº— Tables (7 tables, 35 seats max) - 1F
('table-y01', 'yaesu', 'T1', 'ãƒ†ãƒ¼ãƒ–ãƒ«1', 2, 4, 'regular', 1, 'Main', 1, 0, 1, 0, 'available', 1, 0, 'çª“éš›', datetime('now')),
('table-y02', 'yaesu', 'T2', 'ãƒ†ãƒ¼ãƒ–ãƒ«2', 2, 4, 'regular', 1, 'Main', 1, 0, 1, 1, 'available', 1, 0, 'çª“éš›', datetime('now')),
('table-y03', 'yaesu', 'T3', 'ãƒ†ãƒ¼ãƒ–ãƒ«3', 2, 4, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-y04', 'yaesu', 'T4', 'ãƒ†ãƒ¼ãƒ–ãƒ«4', 2, 4, 'regular', 1, 'Main', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-y05', 'yaesu', 'T5', 'ãƒ†ãƒ¼ãƒ–ãƒ«5', 4, 6, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-y06', 'yaesu', 'T6', 'ãƒ†ãƒ¼ãƒ–ãƒ«6', 4, 6, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-y07', 'yaesu', 'VIP', 'å€‹å®¤', 4, 7, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, 'å•†è«‡å‘ã‘å€‹å®¤', datetime('now')),

-- å“å·åº— Tables (9 tables, 45 seats max)
('table-g01', 'shinagawa', 'T1', 'ãƒ†ãƒ¼ãƒ–ãƒ«1', 2, 4, 'regular', 1, 'A', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-g02', 'shinagawa', 'T2', 'ãƒ†ãƒ¼ãƒ–ãƒ«2', 2, 4, 'regular', 1, 'A', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-g03', 'shinagawa', 'T3', 'ãƒ†ãƒ¼ãƒ–ãƒ«3', 2, 4, 'regular', 1, 'A', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-g04', 'shinagawa', 'T4', 'ãƒ†ãƒ¼ãƒ–ãƒ«4', 2, 4, 'regular', 1, 'B', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-g05', 'shinagawa', 'T5', 'ãƒ†ãƒ¼ãƒ–ãƒ«5', 4, 6, 'regular', 1, 'B', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-g06', 'shinagawa', 'T6', 'ãƒ†ãƒ¼ãƒ–ãƒ«6', 4, 6, 'regular', 1, 'B', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-g07', 'shinagawa', 'VIP1', 'å€‹å®¤1', 4, 8, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, 'å€‹å®¤', datetime('now')),
('table-g08', 'shinagawa', 'VIP2', 'å€‹å®¤2', 4, 6, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, 'å€‹å®¤', datetime('now')),
('table-g09', 'shinagawa', 'Terrace', 'ãƒ†ãƒ©ã‚¹å¸­', 2, 4, 'terrace', 1, 'Terrace', 1, 1, 0, 0, 'available', 1, 0, 'ãƒšãƒƒãƒˆå¯ãƒ»å–«ç…™å¯', datetime('now')),

-- æ¨ªæµœåº— Tables (10 tables, 50 seats max)
('table-k01', 'yokohama', 'T1', 'ãƒ†ãƒ¼ãƒ–ãƒ«1', 2, 4, 'regular', 1, 'Main', 1, 0, 1, 1, 'available', 1, 0, 'çª“éš›', datetime('now')),
('table-k02', 'yokohama', 'T2', 'ãƒ†ãƒ¼ãƒ–ãƒ«2', 2, 4, 'regular', 1, 'Main', 1, 0, 1, 0, 'available', 1, 0, 'çª“éš›', datetime('now')),
('table-k03', 'yokohama', 'T3', 'ãƒ†ãƒ¼ãƒ–ãƒ«3', 2, 4, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-k04', 'yokohama', 'T4', 'ãƒ†ãƒ¼ãƒ–ãƒ«4', 2, 4, 'regular', 1, 'Main', 0, 0, 1, 1, 'available', 1, 0, NULL, datetime('now')),
('table-k05', 'yokohama', 'T5', 'ãƒ†ãƒ¼ãƒ–ãƒ«5', 4, 6, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-k06', 'yokohama', 'T6', 'ãƒ†ãƒ¼ãƒ–ãƒ«6', 4, 6, 'regular', 1, 'Main', 0, 0, 1, 0, 'available', 1, 0, NULL, datetime('now')),
('table-k07', 'yokohama', 'VIP1', 'å€‹å®¤A', 4, 8, 'private', 1, 'VIP', 0, 0, 1, 0, 'available', 1, 10, 'æŽ˜ã‚Šã”ãŸã¤å€‹å®¤', datetime('now')),
('table-k08', 'yokohama', 'VIP2', 'å€‹å®¤B', 4, 6, 'private', 1, 'VIP', 0, 0, 1, 1, 'available', 1, 8, 'å€‹å®¤', datetime('now')),
('table-k09', 'yokohama', 'P1', 'å®´ä¼šå¸­1', 6, 10, 'regular', 1, 'Party', 0, 0, 1, 0, 'available', 1, 5, 'å®´ä¼šå‘ã‘', datetime('now')),
('table-k10', 'yokohama', 'C1', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼', 1, 2, 'counter', 1, 'Counter', 0, 0, 1, 0, 'available', 1, 0, 'ãŠã²ã¨ã‚Šæ§˜å‘ã‘', datetime('now'));

-- ============ MENU ITEMS (shared across all branches) ============
-- è‚‰é¡ž (Meat)
INSERT INTO menu_items (id, branch_code, name, name_en, description, category, subcategory, price, image_url, is_available, is_popular, is_spicy, is_vegetarian, allergens, prep_time_minutes, display_order, created_at) VALUES
-- å¹³é–“æœ¬åº—ãƒ¡ãƒ‹ãƒ¥ãƒ¼ (other branches inherit same menu)
('menu-001', 'hirama', 'å’Œç‰›ä¸Šãƒãƒ©ãƒŸ', 'Premium Harami', 'å£ã®ä¸­ã§ã»ã©ã‘ã‚‹æŸ”ã‚‰ã‹ã•ã¨æ¿ƒåŽšãªå‘³ã‚ã„ã€‚å½“åº—è‡ªæ…¢ã®ä¸€å“', 'meat', 'beef', 1800, '/images/menu/harami.jpg', 1, 1, 0, 0, '', 5, 1, datetime('now')),
('menu-002', 'hirama', 'åŽšåˆ‡ã‚Šä¸Šã‚¿ãƒ³å¡©', 'Thick Sliced Beef Tongue', 'è´…æ²¢ãªåŽšåˆ‡ã‚Šã€‚æ­¯ã”ãŸãˆã¨è‚‰æ±ãŒæº¢ã‚Œã¾ã™', 'meat', 'beef', 2200, '/images/menu/tan.jpg', 1, 1, 0, 0, '', 6, 2, datetime('now')),
('menu-003', 'hirama', 'ç‰¹é¸ã‚«ãƒ«ãƒ“', 'Premium Kalbi', 'éœœé™ã‚ŠãŒç¾Žã—ã„æœ€é«˜ç´šã‚«ãƒ«ãƒ“', 'meat', 'beef', 1800, '/images/menu/kalbi.jpg', 1, 1, 0, 0, '', 5, 3, datetime('now')),
('menu-004', 'hirama', 'ã‚«ãƒ«ãƒ“', 'Kalbi', 'å®šç•ªã®äººæ°—ãƒ¡ãƒ‹ãƒ¥ãƒ¼ã€‚ã‚¸ãƒ¥ãƒ¼ã‚·ãƒ¼ãªå‘³ã‚ã„', 'meat', 'beef', 1500, '/images/menu/kalbi_regular.jpg', 1, 0, 0, 0, '', 5, 4, datetime('now')),
('menu-005', 'hirama', 'ä¸Šãƒ­ãƒ¼ã‚¹', 'Premium Sirloin', 'èµ¤èº«ã®æ—¨å‘³ãŒæ¥½ã—ã‚ã‚‹ä¸Šè³ªãªãƒ­ãƒ¼ã‚¹', 'meat', 'beef', 1700, '/images/menu/rosu.jpg', 1, 0, 0, 0, '', 5, 5, datetime('now')),
('menu-006', 'hirama', 'ãƒ­ãƒ¼ã‚¹', 'Sirloin', 'ã‚ã£ã•ã‚Šã¨ã—ãŸèµ¤èº«ã®ç¾Žå‘³ã—ã•', 'meat', 'beef', 1400, '/images/menu/rosu_regular.jpg', 1, 0, 0, 0, '', 5, 6, datetime('now')),
('menu-007', 'hirama', 'ãƒ›ãƒ«ãƒ¢ãƒ³ç››ã‚Šåˆã‚ã›', 'Offal Assortment', 'æ–°é®®ãªãƒ›ãƒ«ãƒ¢ãƒ³ã‚’ãŸã£ã·ã‚Šã€‚ãƒŸãƒŽãƒ»ãƒãƒãƒŽã‚¹ãƒ»ã‚·ãƒžãƒãƒ§ã‚¦', 'meat', 'offal', 1400, '/images/menu/horumon.jpg', 1, 0, 0, 0, '', 7, 7, datetime('now')),
('menu-008', 'hirama', 'ç‰¹é¸ç››ã‚Šåˆã‚ã›', 'Special Assortment', 'æœ¬æ—¥ã®ãŠã™ã™ã‚å¸Œå°‘éƒ¨ä½ã‚’è´…æ²¢ã«ç››ã‚Šåˆã‚ã›', 'meat', 'beef', 4500, '/images/menu/tokusenmori.jpg', 1, 1, 0, 0, '', 8, 8, datetime('now')),
('menu-009', 'hirama', 'è±šã‚«ãƒ«ãƒ“', 'Pork Kalbi', 'ç”˜ã¿ã®ã‚ã‚‹è±šãƒãƒ©è‚‰', 'meat', 'pork', 900, '/images/menu/buta_kalbi.jpg', 1, 0, 0, 0, '', 5, 9, datetime('now')),
('menu-010', 'hirama', 'é¶ã‚‚ã‚‚', 'Chicken Thigh', 'æŸ”ã‚‰ã‹ãã‚¸ãƒ¥ãƒ¼ã‚·ãƒ¼ãªé¶ã‚‚ã‚‚è‚‰', 'meat', 'chicken', 800, '/images/menu/tori_momo.jpg', 1, 0, 0, 0, '', 5, 10, datetime('now')),

-- é£²ã¿ç‰© (Drinks)
('menu-011', 'hirama', 'ç”Ÿãƒ“ãƒ¼ãƒ«', 'Draft Beer', 'ã‚­ãƒ³ã‚­ãƒ³ã«å†·ãˆãŸç”Ÿãƒ“ãƒ¼ãƒ«ï¼ˆä¸­ï¼‰', 'drinks', 'beer', 600, '/images/menu/beer.jpg', 1, 0, 0, 0, '', 1, 1, datetime('now')),
('menu-012', 'hirama', 'ç“¶ãƒ“ãƒ¼ãƒ«', 'Bottled Beer', 'ã‚¢ã‚µãƒ’ã‚¹ãƒ¼ãƒ‘ãƒ¼ãƒ‰ãƒ©ã‚¤', 'drinks', 'beer', 650, '/images/menu/beer_bottle.jpg', 1, 0, 0, 0, '', 1, 2, datetime('now')),
('menu-013', 'hirama', 'ãƒã‚¤ãƒœãƒ¼ãƒ«', 'Highball', 'ã™ã£ãã‚Šçˆ½ã‚„ã‹ãªã‚¦ã‚¤ã‚¹ã‚­ãƒ¼ã‚½ãƒ¼ãƒ€', 'drinks', 'whisky', 500, '/images/menu/highball.jpg', 1, 0, 0, 0, '', 1, 3, datetime('now')),
('menu-014', 'hirama', 'ãƒ¬ãƒ¢ãƒ³ã‚µãƒ¯ãƒ¼', 'Lemon Sour', 'è‡ªå®¶è£½ãƒ¬ãƒ¢ãƒ³ã‚µãƒ¯ãƒ¼ã€‚ãŸã£ã·ã‚Šé£²ã¿ã‚„ã™ã„', 'drinks', 'sour', 500, '/images/menu/lemon_sour.jpg', 1, 0, 0, 0, '', 1, 4, datetime('now')),
('menu-015', 'hirama', 'æ¢…é…’ã‚µãƒ¯ãƒ¼', 'Plum Wine Sour', 'ç”˜é…¸ã£ã±ã„æ¢…é…’ã‚½ãƒ¼ãƒ€å‰²ã‚Š', 'drinks', 'sour', 550, '/images/menu/umeshu.jpg', 1, 0, 0, 0, '', 1, 5, datetime('now')),
('menu-016', 'hirama', 'ãƒžãƒƒã‚³ãƒª', 'Makgeolli', 'éŸ“å›½ã®ä¼çµ±é…’ã€‚ã¾ã‚ã‚„ã‹ãªç”˜ã¿', 'drinks', 'korean', 600, '/images/menu/makgeolli.jpg', 1, 0, 0, 0, '', 1, 6, datetime('now')),
('menu-017', 'hirama', 'ç„¼é…Žï¼ˆèŠ‹ï¼‰', 'Sweet Potato Shochu', 'æœ¬æ ¼èŠ‹ç„¼é…Žã€‚ãƒ­ãƒƒã‚¯ãƒ»æ°´å‰²ã‚Šãƒ»ãŠæ¹¯å‰²ã‚Š', 'drinks', 'shochu', 500, '/images/menu/shochu.jpg', 1, 0, 0, 0, '', 1, 7, datetime('now')),
('menu-018', 'hirama', 'ã‚¦ãƒ¼ãƒ­ãƒ³èŒ¶', 'Oolong Tea', 'ã‚½ãƒ•ãƒˆãƒ‰ãƒªãƒ³ã‚¯', 'drinks', 'soft', 300, '/images/menu/oolong.jpg', 1, 0, 0, 0, '', 1, 8, datetime('now')),
('menu-019', 'hirama', 'ã‚³ãƒ¼ãƒ©', 'Cola', 'ã‚³ã‚«ãƒ»ã‚³ãƒ¼ãƒ©', 'drinks', 'soft', 300, '/images/menu/cola.jpg', 1, 0, 0, 0, '', 1, 9, datetime('now')),
('menu-020', 'hirama', 'ã‚ªãƒ¬ãƒ³ã‚¸ã‚¸ãƒ¥ãƒ¼ã‚¹', 'Orange Juice', '100%æžœæ±ã‚ªãƒ¬ãƒ³ã‚¸ã‚¸ãƒ¥ãƒ¼ã‚¹', 'drinks', 'soft', 350, '/images/menu/orange.jpg', 1, 0, 0, 0, '', 1, 10, datetime('now')),

-- ã‚µãƒ©ãƒ€ (Salad)
('menu-021', 'hirama', 'ãƒãƒ§ãƒ¬ã‚®ã‚µãƒ©ãƒ€', 'Korean Salad', 'éŸ“å›½é¢¨ãƒ”ãƒªè¾›ã‚µãƒ©ãƒ€ã€‚ã”ã¾æ²¹ãŒé¦™ã‚‹', 'salad', '', 600, '/images/menu/choregi.jpg', 1, 0, 1, 1, '', 3, 1, datetime('now')),
('menu-022', 'hirama', 'ã‚·ãƒ¼ã‚¶ãƒ¼ã‚µãƒ©ãƒ€', 'Caesar Salad', 'ãƒ‘ãƒ«ãƒ¡ã‚¶ãƒ³ãƒãƒ¼ã‚ºãŸã£ã·ã‚Š', 'salad', '', 700, '/images/menu/caesar.jpg', 1, 0, 0, 1, 'milk', 3, 2, datetime('now')),
('menu-023', 'hirama', 'ãƒŠãƒ ãƒ«ç››ã‚Šåˆã‚ã›', 'Namul Assortment', '3ç¨®ã®ãƒŠãƒ ãƒ«ï¼ˆã‚‚ã‚„ã—ãƒ»ã»ã†ã‚Œã‚“è‰ãƒ»å¤§æ ¹ï¼‰', 'salad', '', 500, '/images/menu/namul.jpg', 1, 0, 0, 1, '', 3, 3, datetime('now')),
('menu-024', 'hirama', 'ã‚­ãƒ ãƒç››ã‚Šåˆã‚ã›', 'Kimchi Assortment', 'ç™½èœãƒ»ã‚«ã‚¯ãƒ†ã‚­ãƒ»ã‚ªã‚¤ã‚­ãƒ ãƒ', 'salad', '', 550, '/images/menu/kimchi.jpg', 1, 0, 1, 1, '', 2, 4, datetime('now')),

-- ã”é£¯ãƒ»éºº (Rice & Noodles)
('menu-025', 'hirama', 'ãƒ©ã‚¤ã‚¹', 'Rice', 'å›½ç”£ã‚³ã‚·ãƒ’ã‚«ãƒªä½¿ç”¨', 'rice', '', 200, '/images/menu/rice.jpg', 1, 0, 0, 1, '', 2, 1, datetime('now')),
('menu-026', 'hirama', 'å¤§ç››ã‚Šãƒ©ã‚¤ã‚¹', 'Large Rice', 'å›½ç”£ã‚³ã‚·ãƒ’ã‚«ãƒªå¤§ç››ã‚Š', 'rice', '', 300, '/images/menu/rice_large.jpg', 1, 0, 0, 1, '', 2, 2, datetime('now')),
('menu-027', 'hirama', 'çŸ³ç„¼ãƒ“ãƒ“ãƒ³ãƒ', 'Stone Pot Bibimbap', 'ç†±ã€…ã®çŸ³é‹ã§æä¾›ã€‚ãŠã“ã’ãŒç¾Žå‘³ã—ã„', 'rice', '', 1200, '/images/menu/bibimbap.jpg', 1, 1, 1, 0, 'egg', 8, 3, datetime('now')),
('menu-028', 'hirama', 'å†·éºº', 'Cold Noodles', 'éŸ“å›½å†·éººã€‚ã•ã£ã±ã‚Šã¨ã—ãŸå‘³ã‚ã„', 'rice', '', 900, '/images/menu/reimen.jpg', 1, 0, 0, 0, 'wheat', 5, 4, datetime('now')),
('menu-029', 'hirama', 'ã‚«ãƒ«ãƒ“ã‚¯ãƒƒãƒ‘', 'Kalbi Rice Soup', 'ã‚«ãƒ«ãƒ“å…¥ã‚Šã®éŸ“å›½é¢¨ã‚¹ãƒ¼ãƒ—ã”é£¯', 'rice', '', 950, '/images/menu/kuppa.jpg', 1, 0, 1, 0, '', 6, 5, datetime('now')),

-- ã‚µã‚¤ãƒ‰ãƒ¡ãƒ‹ãƒ¥ãƒ¼ (Side Menu)
('menu-030', 'hirama', 'ã‚ã‹ã‚ã‚¹ãƒ¼ãƒ—', 'Seaweed Soup', 'éŸ“å›½é¢¨ã‚ã‹ã‚ã‚¹ãƒ¼ãƒ—', 'side', '', 350, '/images/menu/wakame.jpg', 1, 0, 0, 1, '', 3, 1, datetime('now')),
('menu-031', 'hirama', 'ãƒ†ãƒ¼ãƒ«ã‚¹ãƒ¼ãƒ—', 'Oxtail Soup', 'ã‚³ãƒ©ãƒ¼ã‚²ãƒ³ãŸã£ã·ã‚Šç‰›ãƒ†ãƒ¼ãƒ«ã‚¹ãƒ¼ãƒ—', 'side', '', 800, '/images/menu/tail_soup.jpg', 1, 0, 0, 0, '', 10, 2, datetime('now')),
('menu-032', 'hirama', 'æžè±†', 'Edamame', 'å¡©èŒ¹ã§æžè±†', 'side', '', 350, '/images/menu/edamame.jpg', 1, 0, 0, 1, '', 2, 3, datetime('now')),
('menu-033', 'hirama', 'éŸ“å›½æµ·è‹”', 'Korean Seaweed', 'ã”ã¾æ²¹é¦™ã‚‹éŸ“å›½æµ·è‹”', 'side', '', 300, '/images/menu/nori.jpg', 1, 0, 0, 1, '', 1, 4, datetime('now')),
('menu-034', 'hirama', 'ãƒãƒ‚ãƒŸ', 'Korean Pancake', 'æµ·é®®ãƒãƒ‚ãƒŸã€‚å¤–ã¯ã‚«ãƒªã£ã¨ä¸­ã¯ã‚‚ã£ã¡ã‚Š', 'side', '', 850, '/images/menu/chijimi.jpg', 1, 0, 0, 0, 'wheat|egg|seafood', 10, 5, datetime('now')),

-- ãƒ‡ã‚¶ãƒ¼ãƒˆ (Dessert)
('menu-035', 'hirama', 'ãƒãƒ‹ãƒ©ã‚¢ã‚¤ã‚¹', 'Vanilla Ice Cream', 'æ¿ƒåŽšãƒãƒ‹ãƒ©ã‚¢ã‚¤ã‚¹ã‚¯ãƒªãƒ¼ãƒ ', 'dessert', '', 400, '/images/menu/vanilla_ice.jpg', 1, 0, 0, 1, 'milk', 1, 1, datetime('now')),
('menu-036', 'hirama', 'æä»è±†è…', 'Almond Tofu', 'æ‰‹ä½œã‚Šæä»è±†è…ã€‚ãªã‚ã‚‰ã‹ãªå£å½“ãŸã‚Š', 'dessert', '', 450, '/images/menu/annin.jpg', 1, 0, 0, 1, 'milk', 1, 2, datetime('now')),
('menu-037', 'hirama', 'ã‚·ãƒ£ãƒ¼ãƒ™ãƒƒãƒˆ', 'Sherbet', 'ãƒžãƒ³ã‚´ãƒ¼ã‚·ãƒ£ãƒ¼ãƒ™ãƒƒãƒˆ', 'dessert', '', 400, '/images/menu/sherbet.jpg', 1, 0, 0, 1, '', 1, 3, datetime('now')),

-- ã‚»ãƒƒãƒˆãƒ¡ãƒ‹ãƒ¥ãƒ¼ (Set Menu)
('menu-038', 'hirama', 'ç„¼è‚‰å®šé£Ÿ', 'Yakiniku Set', 'ã‚«ãƒ«ãƒ“ãƒ»ãƒ­ãƒ¼ã‚¹ãƒ»ãƒ©ã‚¤ã‚¹ãƒ»ã‚¹ãƒ¼ãƒ—ãƒ»ã‚µãƒ©ãƒ€', 'set', '', 1800, '/images/menu/teishoku.jpg', 1, 1, 0, 0, '', 15, 1, datetime('now')),
('menu-039', 'hirama', 'ä¸Šç„¼è‚‰å®šé£Ÿ', 'Premium Yakiniku Set', 'ä¸Šã‚«ãƒ«ãƒ“ãƒ»ä¸Šãƒ­ãƒ¼ã‚¹ãƒ»ãƒ©ã‚¤ã‚¹ãƒ»ã‚¹ãƒ¼ãƒ—ãƒ»ã‚µãƒ©ãƒ€', 'set', '', 2500, '/images/menu/teishoku_premium.jpg', 1, 0, 0, 0, '', 15, 2, datetime('now')),
('menu-040', 'hirama', 'å¥³å­ä¼šã‚³ãƒ¼ã‚¹', 'Ladies Course', 'ã‚µãƒ©ãƒ€ãƒ»ãŠè‚‰5ç¨®ãƒ»ãƒ‡ã‚¶ãƒ¼ãƒˆãƒ»ãƒ‰ãƒªãƒ³ã‚¯ä»˜ã', 'set', '', 3500, '/images/menu/ladies_course.jpg', 1, 0, 0, 0, '', 20, 3, datetime('now'));

-- ============ GLOBAL CUSTOMERS (50 customers) ============
INSERT INTO global_customers (id, phone, name, email, created_at) VALUES
('cust-001', '090-2000-0001', 'ä½ã€…æœ¨ ç¾Žå’²', 'sasaki.misaki@email.jp', '2024-01-15 10:30:00'),
('cust-002', '090-2000-0002', 'æœ¨æ‘ å¥å¤ª', 'kimura.kenta@email.jp', '2024-01-20 14:45:00'),
('cust-003', '090-2000-0003', 'å±±æœ¬ çœŸç”±ç¾Ž', 'yamamoto.mayumi@email.jp', '2024-02-01 11:20:00'),
('cust-004', '090-2000-0004', 'äº•ä¸Š å¤§è¼”', 'inoue.daisuke@email.jp', '2024-02-05 18:00:00'),
('cust-005', '090-2000-0005', 'æž— ã•ãã‚‰', 'hayashi.sakura@email.jp', '2024-02-10 12:30:00'),
('cust-006', '090-2000-0006', 'æ¸…æ°´ ç¿”å¤ª', 'shimizu.shota@email.jp', '2024-02-15 19:15:00'),
('cust-007', '090-2000-0007', 'æ¾æœ¬ æ„›', 'matsumoto.ai@email.jp', '2024-02-20 17:00:00'),
('cust-008', '090-2000-0008', 'æ£®ç”° ä¸€éƒŽ', 'morita.ichiro@email.jp', '2024-03-01 13:45:00'),
('cust-009', '090-2000-0009', 'å°å· èŠ±å­', 'ogawa.hanako@email.jp', '2024-03-05 16:30:00'),
('cust-010', '090-2000-0010', 'è—¤ç”° å¤ªéƒŽ', 'fujita.taro@email.jp', '2024-03-10 11:00:00'),
('cust-011', '090-2000-0011', 'å²¡ç”° ç¾Žå„ª', 'okada.miyu@email.jp', '2024-03-15 20:00:00'),
('cust-012', '090-2000-0012', 'å¾Œè—¤ åº·å¹³', 'goto.kohei@email.jp', '2024-03-20 15:30:00'),
('cust-013', '090-2000-0013', 'å‚æœ¬ çµè¡£', 'sakamoto.yui@email.jp', '2024-03-25 12:00:00'),
('cust-014', '090-2000-0014', 'é•·è°·å· èª ', 'hasegawa.makoto@email.jp', '2024-04-01 18:45:00'),
('cust-015', '090-2000-0015', 'çŸ³äº• å½©ä¹ƒ', 'ishii.ayano@email.jp', '2024-04-05 14:15:00'),
('cust-016', '090-2000-0016', 'å‰ç”° éš†å¤ª', 'maeda.ryuta@email.jp', '2024-04-10 19:30:00'),
('cust-017', '090-2000-0017', 'è—¤äº• ç¾Žç©‚', 'fujii.miho@email.jp', '2024-04-15 11:45:00'),
('cust-018', '090-2000-0018', 'æ‘ä¸Š æµ©äºŒ', 'murakami.koji@email.jp', '2024-04-20 16:00:00'),
('cust-019', '090-2000-0019', 'å¤ªç”° éº»è¡£', 'ota.mai@email.jp', '2024-04-25 13:30:00'),
('cust-020', '090-2000-0020', 'é‡‘å­ æ‹“æµ·', 'kaneko.takumi@email.jp', '2024-05-01 17:15:00'),
('cust-021', '090-2000-0021', 'ä¸­å³¶ å„ªå­', 'nakajima.yuko@email.jp', '2024-05-05 10:00:00'),
('cust-022', '090-2000-0022', 'åŽŸç”° ç›´æ¨¹', 'harada.naoki@email.jp', '2024-05-10 14:30:00'),
('cust-023', '090-2000-0023', 'å°é‡Ž åƒå°‹', 'ono.chihiro@email.jp', '2024-05-15 19:00:00'),
('cust-024', '090-2000-0024', 'ç«¹å†… å‹‡æ°—', 'takeuchi.yuki@email.jp', '2024-05-20 12:45:00'),
('cust-025', '090-2000-0025', 'å®®å´Ž è‘µ', 'miyazaki.aoi@email.jp', '2024-05-25 15:15:00'),
('cust-026', '090-2000-0026', 'è¿‘è—¤ é›„å¤§', 'kondo.yudai@email.jp', '2024-06-01 18:30:00'),
('cust-027', '090-2000-0027', 'çŸ³å· ç¾Žæœˆ', 'ishikawa.mizuki@email.jp', '2024-06-05 11:00:00'),
('cust-028', '090-2000-0028', 'æ–Žè—¤ è“®', 'saito.ren@email.jp', '2024-06-10 16:45:00'),
('cust-029', '090-2000-0029', 'ä¸Šé‡Ž ä¸ƒæµ·', 'ueno.nanami@email.jp', '2024-06-15 13:15:00'),
('cust-030', '090-2000-0030', 'æ¨ªå±± æ‚ äºº', 'yokoyama.yuto@email.jp', '2024-06-20 17:30:00'),
('cust-031', '090-2000-0031', 'å¤§é‡Ž å‡›', 'ono.rin@email.jp', '2024-06-25 10:45:00'),
('cust-032', '090-2000-0032', 'å‰æ‘ é¢¯å¤ª', 'yoshimura.sota@email.jp', '2024-07-01 14:00:00'),
('cust-033', '090-2000-0033', 'æ± ç”° é™½èœ', 'ikeda.hina@email.jp', '2024-07-05 19:15:00'),
('cust-034', '090-2000-0034', 'ç¦ç”° æ¨¹', 'fukuda.itsuki@email.jp', '2024-07-10 12:30:00'),
('cust-035', '090-2000-0035', 'è¥¿æ‘ æ¥“', 'nishimura.kaede@email.jp', '2024-07-15 15:45:00'),
('cust-036', '090-2000-0036', 'å±±å£ æµ·æ–—', 'yamaguchi.kaito@email.jp', '2024-07-20 18:00:00'),
('cust-037', '090-2000-0037', 'ä¸­å· å¿ƒæ˜¥', 'nakagawa.koharu@email.jp', '2024-07-25 11:15:00'),
('cust-038', '090-2000-0038', 'é‡Žæ‘ é™¸', 'nomura.riku@email.jp', '2024-08-01 16:30:00'),
('cust-039', '090-2000-0039', 'æ¾ç”° ç¾Žæ¡œ', 'matsuda.mio@email.jp', '2024-08-05 13:45:00'),
('cust-040', '090-2000-0040', 'èŠæ±  å¤§ç¿”', 'kikuchi.hiroto@email.jp', '2024-08-10 17:00:00'),
('cust-041', '090-2000-0041', 'å’Œç”° èŽ‰å­', 'wada.riko@email.jp', '2024-08-15 10:30:00'),
('cust-042', '090-2000-0042', 'ä¹…ä¿ æ¹Š', 'kubo.minato@email.jp', '2024-08-20 14:45:00'),
('cust-043', '090-2000-0043', 'å¢—ç”° ç´¬', 'masuda.tsumugi@email.jp', '2024-08-25 19:00:00'),
('cust-044', '090-2000-0044', 'æ²³é‡Ž æœé™½', 'kawano.asahi@email.jp', '2024-09-01 12:15:00'),
('cust-045', '090-2000-0045', 'æ‰å±± èŠ½ä¾', 'sugiyama.mei@email.jp', '2024-09-05 15:30:00'),
('cust-046', '090-2000-0046', 'å†…ç”° æ‚ çœŸ', 'uchida.yuma@email.jp', '2024-09-10 18:45:00'),
('cust-047', '090-2000-0047', 'æ°¸äº• æŸšè‘‰', 'nagai.yuzuha@email.jp', '2024-09-15 11:00:00'),
('cust-048', '090-2000-0048', 'ä»Šäº• å¥å¤ª', 'imai.sota@email.jp', '2024-09-20 16:15:00'),
('cust-049', '090-2000-0049', 'å°å³¶ ç’ƒå­', 'kojima.riko@email.jp', '2024-09-25 13:30:00'),
('cust-050', '090-2000-0050', 'æµ…é‡Ž å¾‹', 'asano.ritsu@email.jp', '2024-10-01 17:45:00');

-- ============ BRANCH CUSTOMERS (distributed across branches with sentiment) ============
-- å¹³é–“æœ¬åº— Customers (VIPs included)
INSERT INTO branch_customers (id, global_customer_id, branch_code, visit_count, last_visit, is_vip, notes, created_at) VALUES
('bc-001', 'cust-001', 'hirama', 15, '2026-01-20 19:30:00', 1, 'å¸¸é€£æ§˜ã€‚ã„ã¤ã‚‚ã‚¿ãƒ³å¡©ã‚’æ³¨æ–‡ã•ã‚Œã‚‹ [positive]', datetime('now')),
('bc-002', 'cust-002', 'hirama', 8, '2025-11-15 18:00:00', 0, 'ãŠå­æ§˜é€£ã‚Œã§æ¥åº—ã€‚å€‹å®¤å¸Œæœ› [positive]', datetime('now')),
('bc-003', 'cust-003', 'hirama', 3, '2025-10-01 20:00:00', 0, 'åˆå›žå‰²å¼•åˆ©ç”¨ [neutral]', datetime('now')),
('bc-004', 'cust-004', 'hirama', 22, '2026-02-01 19:00:00', 1, 'VIPã€‚ç‰¹åˆ¥ãªãŠç¥ã„ã§ã‚ˆãåˆ©ç”¨ [very_positive]', datetime('now')),
('bc-005', 'cust-005', 'hirama', 12, '2026-01-15 20:30:00', 1, 'è‚‰ã®ç„¼ãåŠ æ¸›ã«ã“ã ã‚ã‚‹ã€‚ãƒ¬ã‚¢å¸Œæœ› [positive]', datetime('now')),
('bc-006', 'cust-006', 'hirama', 5, '2025-09-20 19:00:00', 0, 'ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼ï¼ˆç”²æ®»é¡žï¼‰ã‚ã‚Š [neutral]', datetime('now')),
('bc-007', 'cust-007', 'hirama', 18, '2026-01-25 18:30:00', 1, 'ãƒ¯ã‚¤ãƒ³å¥½ãã€‚è¨˜å¿µæ—¥åˆ©ç”¨å¤šã— [very_positive]', datetime('now')),
('bc-008', 'cust-008', 'hirama', 10, '2025-11-30 20:00:00', 1, 'å¤§äººæ•°å®´ä¼šã§ã‚ˆãäºˆç´„ [positive]', datetime('now')),
('bc-009', 'cust-009', 'hirama', 1, '2025-06-01 18:00:00', 0, 'æ–™ç†ã®æä¾›ãŒé…ã„ã¨ã‚¯ãƒ¬ãƒ¼ãƒ  [negative]', datetime('now')),
('bc-010', 'cust-010', 'hirama', 7, '2025-10-15 19:00:00', 0, 'é™ã‹ãªå¸­å¸Œæœ›ã€‚ãƒ‡ãƒ¼ãƒˆåˆ©ç”¨ [positive]', datetime('now')),

-- æ–°å®¿åº— Customers
('bc-011', 'cust-011', 'shinjuku', 20, '2026-02-01 19:30:00', 1, 'ä¼šç¤¾ã®æŽ¥å¾…ã§ã‚ˆãåˆ©ç”¨ã€‚ä¸Šè³ªãªè‚‰å¸Œæœ› [very_positive]', datetime('now')),
('bc-012', 'cust-012', 'shinjuku', 9, '2025-11-10 19:00:00', 0, 'å†™çœŸæ’®å½±å¥½ãã€‚ã‚¤ãƒ³ã‚¹ã‚¿æŠ•ç¨¿ [positive]', datetime('now')),
('bc-013', 'cust-013', 'shinjuku', 25, '2026-01-20 20:30:00', 1, 'å‰µæ¥­æ™‚ã‹ã‚‰ã®å¸¸é€£æ§˜ã€‚æœ€é«˜ç´šã‚³ãƒ¼ã‚¹ [very_positive]', datetime('now')),
('bc-014', 'cust-014', 'shinjuku', 6, '2025-10-05 19:00:00', 0, 'ç¦ç…™å¸­å¸Œæœ›ã€‚åŒ‚ã„ã«æ•æ„Ÿ [positive]', datetime('now')),
('bc-015', 'cust-015', 'shinjuku', 11, '2025-12-10 19:30:00', 1, 'èª•ç”Ÿæ—¥ã‚±ãƒ¼ã‚­æŒã¡è¾¼ã¿è¨±å¯æ¸ˆ [positive]', datetime('now')),
('bc-016', 'cust-016', 'shinjuku', 4, '2025-09-15 20:00:00', 0, 'é£²ã¿æ”¾é¡Œãƒ—ãƒ©ãƒ³å¥½ã [neutral]', datetime('now')),
('bc-017', 'cust-017', 'shinjuku', 8, '2025-11-01 18:30:00', 0, 'å­ä¾›ç”¨ãƒ¡ãƒ‹ãƒ¥ãƒ¼æ³¨æ–‡ [positive]', datetime('now')),
('bc-018', 'cust-018', 'shinjuku', 15, '2026-01-25 20:00:00', 1, 'ã‚¯ãƒªã‚¹ãƒžã‚¹æ¯Žå¹´äºˆç´„ã€‚ãƒ­ãƒžãƒ³ãƒãƒƒã‚¯ãªå¸­å¸Œæœ› [very_positive]', datetime('now')),
('bc-019', 'cust-019', 'shinjuku', 7, '2025-10-20 19:30:00', 0, 'ãƒ›ãƒ«ãƒ¢ãƒ³å°‚é–€ã€‚é€šãªæ³¨æ–‡ [positive]', datetime('now')),
('bc-020', 'cust-020', 'shinjuku', 19, '2026-02-05 20:00:00', 1, 'ãƒ¯ã‚¤ãƒ³ä¼šå¹¹äº‹ã€‚å¤§å£æ³¨æ–‡ [very_positive]', datetime('now')),

-- å…«é‡æ´²åº— Customers (ãƒ“ã‚¸ãƒã‚¹å®¢å¤šã‚)
('bc-021', 'cust-021', 'yaesu', 30, '2026-02-03 12:30:00', 1, 'ãƒ©ãƒ³ãƒå¸¸é€£ã€‚å•†è«‡åˆ©ç”¨å¤šæ•° [very_positive]', datetime('now')),
('bc-022', 'cust-022', 'yaesu', 15, '2026-01-15 13:00:00', 1, 'æŽ¥å¾…åˆ©ç”¨ã€‚é ˜åŽæ›¸å¿…è¦ [positive]', datetime('now')),
('bc-023', 'cust-023', 'yaesu', 8, '2025-12-20 12:00:00', 0, 'ãƒ©ãƒ³ãƒã‚»ãƒƒãƒˆæ„›ç”¨ [positive]', datetime('now')),
('bc-024', 'cust-024', 'yaesu', 5, '2025-11-10 18:30:00', 0, 'å‡ºå¼µã§æ±äº¬é§…åˆ©ç”¨æ™‚ã«æ¥åº— [neutral]', datetime('now')),
('bc-025', 'cust-025', 'yaesu', 12, '2026-01-30 19:00:00', 1, 'å–å¼•å…ˆã¨ã®ä¼šé£Ÿå ´æ‰€ã¨ã—ã¦å›ºå®š [very_positive]', datetime('now')),
('bc-026', 'cust-026', 'yaesu', 3, '2025-10-05 12:30:00', 0, 'æ€¥ã„ã§ã„ã‚‹ã“ã¨ãŒå¤šã„ [neutral]', datetime('now')),
('bc-027', 'cust-027', 'yaesu', 7, '2025-12-10 18:00:00', 0, 'å€‹å®¤ã§å•†è«‡ [positive]', datetime('now')),
('bc-028', 'cust-028', 'yaesu', 20, '2026-02-01 12:00:00', 1, 'æ¯Žé€±é‡‘æ›œãƒ©ãƒ³ãƒå¸¸é€£ [very_positive]', datetime('now')),

-- å“å·åº— Customers
('bc-031', 'cust-031', 'shinagawa', 10, '2025-12-25 19:00:00', 1, 'å®¶æ—é€£ã‚Œã§æ¥åº—ã€‚å­ä¾›ç”¨æ¤…å­å¿…è¦ [positive]', datetime('now')),
('bc-032', 'cust-032', 'shinagawa', 6, '2025-11-20 20:00:00', 0, 'ãƒ†ãƒ©ã‚¹å¸­å¸Œæœ›ã€‚ãƒšãƒƒãƒˆåŒä¼´ [positive]', datetime('now')),
('bc-033', 'cust-033', 'shinagawa', 15, '2026-01-10 18:30:00', 1, 'åœ°å…ƒå¸¸é€£ã€‚é€±æœ«åˆ©ç”¨ [very_positive]', datetime('now')),
('bc-034', 'cust-034', 'shinagawa', 4, '2025-10-15 19:30:00', 0, 'ã‚«ãƒƒãƒ—ãƒ«åˆ©ç”¨ã€‚é™ã‹ãªå¸­å¸Œæœ› [positive]', datetime('now')),
('bc-035', 'cust-035', 'shinagawa', 8, '2025-12-05 20:00:00', 0, 'ã‚¹ãƒãƒ¼ãƒ„è¦³æˆ¦å¸Œæœ› [positive]', datetime('now')),
('bc-036', 'cust-036', 'shinagawa', 2, '2025-08-20 19:00:00', 0, 'è¿‘æ‰€ã«å¼•ã£è¶Šã—ã¦ããŸ [neutral]', datetime('now')),
('bc-037', 'cust-037', 'shinagawa', 12, '2026-01-20 18:00:00', 1, 'èª•ç”Ÿæ—¥ä¼šå¸¸é€£ [positive]', datetime('now')),
('bc-038', 'cust-038', 'shinagawa', 5, '2025-11-05 19:30:00', 0, 'ä»•äº‹å¸°ã‚Šã«ä¸€äººç„¼è‚‰ [positive]', datetime('now')),

-- æ¨ªæµœåº— Customers
('bc-041', 'cust-041', 'yokohama', 18, '2026-01-30 19:00:00', 1, 'æ¨ªæµœåœ¨ä½VIPã€‚æ¯Žæœˆæ¥åº— [very_positive]', datetime('now')),
('bc-042', 'cust-042', 'yokohama', 10, '2025-12-15 20:30:00', 1, 'å¿˜å¹´ä¼šå¹¹äº‹ã€‚å¤§äººæ•°äºˆç´„ [positive]', datetime('now')),
('bc-043', 'cust-043', 'yokohama', 6, '2025-11-25 19:30:00', 0, 'æŽ˜ã‚Šã”ãŸã¤å€‹å®¤å¸Œæœ› [positive]', datetime('now')),
('bc-044', 'cust-044', 'yokohama', 3, '2025-10-10 18:00:00', 0, 'åˆæ¥åº—ã€‚å‹äººç´¹ä»‹ [neutral]', datetime('now')),
('bc-045', 'cust-045', 'yokohama', 14, '2026-02-01 20:00:00', 1, 'æ·±å¤œå–¶æ¥­æ™‚é–“å¸¯å¸¸é€£ [positive]', datetime('now')),
('bc-046', 'cust-046', 'yokohama', 8, '2025-12-20 19:00:00', 0, 'é–¢å†…é§…è¿‘ã„ã®ã§ä¾¿åˆ©ã¨è©•ä¾¡ [positive]', datetime('now')),
('bc-047', 'cust-047', 'yokohama', 5, '2025-11-10 18:30:00', 0, 'å®´ä¼šåˆ©ç”¨ã€‚å¹¹äº‹ [neutral]', datetime('now')),
('bc-048', 'cust-048', 'yokohama', 22, '2026-02-03 21:00:00', 1, 'é…ã„æ™‚é–“å¸¯ã®å¸¸é€£ã€‚æ·±å¤œã¾ã§é£²ã‚€ [very_positive]', datetime('now'));

-- ============ SAMPLE BOOKINGS (Today's bookings for demo) ============
INSERT INTO bookings (id, branch_code, guest_name, guest_phone, guest_email, date, time, guests, note, status, source, created_at) VALUES
-- å¹³é–“æœ¬åº— Today's Bookings
('book-001', 'hirama', 'ä½ã€…æœ¨ ç¾Žå’²', '090-2000-0001', 'sasaki.misaki@email.jp', date('now'), '18:00', 4, 'ãŠèª•ç”Ÿæ—¥ã‚±ãƒ¼ã‚­æŒã¡è¾¼ã¿å¸Œæœ›ã€‚çª“éš›å¸­å¸Œæœ›', 'confirmed', 'web', datetime('now')),
('book-002', 'hirama', 'æœ¨æ‘ å¥å¤ª', '090-2000-0002', 'kimura.kenta@email.jp', date('now'), '18:30', 2, NULL, 'confirmed', 'web', datetime('now')),
('book-003', 'hirama', 'äº•ä¸Š å¤§è¼”', '090-2000-0004', 'inoue.daisuke@email.jp', date('now'), '19:00', 6, 'æŽ¥å¾…åˆ©ç”¨ã€‚å€‹å®¤å¸Œæœ›ã€‚é ˜åŽæ›¸å¿…è¦', 'confirmed', 'phone', datetime('now')),
('book-004', 'hirama', 'æž— ã•ãã‚‰', '090-2000-0005', 'hayashi.sakura@email.jp', date('now'), '19:30', 3, 'ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼ï¼šç”²æ®»é¡ž', 'confirmed', 'web', datetime('now')),
('book-005', 'hirama', 'æ¾æœ¬ æ„›', '090-2000-0007', 'matsumoto.ai@email.jp', date('now'), '20:00', 4, 'è¨˜å¿µæ—¥åˆ©ç”¨ã€‚çª“éš›å¸­å¸Œæœ›', 'pending', 'chat', datetime('now')),
('book-006', 'hirama', 'æ£®ç”° ä¸€éƒŽ', '090-2000-0008', 'morita.ichiro@email.jp', date('now'), '20:30', 8, 'å¿˜å¹´ä¼šã€‚å€‹å®¤å¸Œæœ›', 'confirmed', 'phone', datetime('now')),

-- æ–°å®¿åº— Today's Bookings
('book-011', 'shinjuku', 'å²¡ç”° ç¾Žå„ª', '090-2000-0011', 'okada.miyu@email.jp', date('now'), '18:00', 2, 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼å¸­å¸Œæœ›', 'confirmed', 'web', datetime('now')),
('book-012', 'shinjuku', 'å‚æœ¬ çµè¡£', '090-2000-0013', 'sakamoto.yui@email.jp', date('now'), '19:00', 4, 'InstagramæŠ•ç¨¿äºˆå®š', 'confirmed', 'web', datetime('now')),
('book-013', 'shinjuku', 'é•·è°·å· èª ', '090-2000-0014', 'hasegawa.makoto@email.jp', date('now'), '19:30', 6, 'ä¼šç¤¾ã®é£²ã¿ä¼šã€‚ãƒœãƒƒã‚¯ã‚¹å¸­å¸Œæœ›', 'confirmed', 'phone', datetime('now')),
('book-014', 'shinjuku', 'é‡‘å­ æ‹“æµ·', '090-2000-0020', 'kaneko.takumi@email.jp', date('now'), '20:00', 10, 'å®´ä¼šã€‚é£²ã¿æ”¾é¡Œä»˜ã', 'confirmed', 'phone', datetime('now')),

-- å…«é‡æ´²åº— Today's Bookings (ãƒ©ãƒ³ãƒå¤šã‚)
('book-021', 'yaesu', 'ä¸­å³¶ å„ªå­', '090-2000-0021', 'nakajima.yuko@email.jp', date('now'), '12:00', 2, 'ãƒ©ãƒ³ãƒãƒŸãƒ¼ãƒ†ã‚£ãƒ³ã‚°', 'confirmed', 'web', datetime('now')),
('book-022', 'yaesu', 'åŽŸç”° ç›´æ¨¹', '090-2000-0022', 'harada.naoki@email.jp', date('now'), '12:30', 4, 'å•†è«‡ã€‚å€‹å®¤å¸Œæœ›ã€‚é™ã‹ãªå¸­', 'confirmed', 'phone', datetime('now')),
('book-023', 'yaesu', 'ç«¹å†… å‹‡æ°—', '090-2000-0024', 'takeuchi.yuki@email.jp', date('now'), '13:00', 2, NULL, 'pending', 'web', datetime('now')),
('book-024', 'yaesu', 'è¿‘è—¤ é›„å¤§', '090-2000-0026', 'kondo.yudai@email.jp', date('now'), '18:30', 6, 'å–å¼•å…ˆã¨ã®ä¼šé£Ÿã€‚å€‹å®¤å¸Œæœ›', 'confirmed', 'phone', datetime('now')),

-- å“å·åº— Today's Bookings
('book-031', 'shinagawa', 'å¤§é‡Ž å‡›', '090-2000-0031', 'ono.rin@email.jp', date('now'), '18:00', 4, 'å­ä¾›2åã€‚ã‚­ãƒƒã‚ºãƒã‚§ã‚¢å¿…è¦', 'confirmed', 'web', datetime('now')),
('book-032', 'shinagawa', 'æ± ç”° é™½èœ', '090-2000-0033', 'ikeda.hina@email.jp', date('now'), '19:00', 2, 'ãƒšãƒƒãƒˆåŒä¼´ã€‚ãƒ†ãƒ©ã‚¹å¸­å¸Œæœ›', 'confirmed', 'chat', datetime('now')),
('book-033', 'shinagawa', 'è¥¿æ‘ æ¥“', '090-2000-0035', 'nishimura.kaede@email.jp', date('now'), '19:30', 5, 'ã‚¹ãƒãƒ¼ãƒ„è¦³æˆ¦ã—ãŸã„', 'confirmed', 'web', datetime('now')),

-- æ¨ªæµœåº— Today's Bookings
('book-041', 'yokohama', 'å’Œç”° èŽ‰å­', '090-2000-0041', 'wada.riko@email.jp', date('now'), '18:30', 6, 'æŽ˜ã‚Šã”ãŸã¤å€‹å®¤å¸Œæœ›', 'confirmed', 'phone', datetime('now')),
('book-042', 'yokohama', 'å¢—ç”° ç´¬', '090-2000-0043', 'masuda.tsumugi@email.jp', date('now'), '19:00', 4, 'çª“éš›å¸­å¸Œæœ›', 'confirmed', 'web', datetime('now')),
('book-043', 'yokohama', 'å†…ç”° æ‚ çœŸ', '090-2000-0046', 'uchida.yuma@email.jp', date('now'), '20:00', 8, 'åŒçª“ä¼šã€‚å®´ä¼šå¸­å¸Œæœ›', 'pending', 'phone', datetime('now')),
('book-044', 'yokohama', 'æµ…é‡Ž å¾‹', '090-2000-0050', 'asano.ritsu@email.jp', date('now'), '21:30', 2, 'æ·±å¤œã¾ã§é£²ã¿ãŸã„', 'confirmed', 'chat', datetime('now'));

-- ============ END OF SEED DATA ============
--
-- Summary:
-- - 5 Branches: JIAN (æœ¬åº—), shinjuku, yaesu, shinagawa, yokohama
-- - 34 Staff members (6-8 per branch)
-- - 45 Tables total (7-11 per branch)
-- - 40 Menu items (shared menu from JIAN branch)
-- - 50 Global customers
-- - 48 Branch customer records
-- - 22 Sample bookings for today
--
-- To seed: sqlite3 yakiniku.db < seed.sql
-- ============================================
