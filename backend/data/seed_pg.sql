-- ============================================
-- Yakiniku.io Platform - PostgreSQL Seed Data
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
('branch-hirama', 'hirama', 'Yakiniku å¹³é–“æœ¬åº—', 'hirama', '044-520-3729', 'å·å´Žå¸‚ä¸­åŽŸåŒºä¸­ä¸¸å­571-13', '17:00:00', '24:00:00', 50, true),
('branch-shinjuku', 'shinjuku', 'Yakiniku æ–°å®¿åº—', 'shinjuku', '03-5909-7729', 'æ–°å®¿åŒºè¥¿æ–°å®¿1-13-8 B1F', '17:00:00', '01:00:00', 80, true),
('branch-yaesu', 'yaesu', 'Yakiniku å…«é‡æ´²åº—', 'yaesu', '03-3271-7729', 'ä¸­å¤®åŒºå…«é‡æ´²1-5-10 1F', '11:30:00', '23:00:00', 40, true),
('branch-shinagawa', 'shinagawa', 'Yakiniku å“å·åº—', 'shinagawa', '03-6417-7729', 'å“å·åŒºäºŒè’‰1-16-17', '17:00:00', '24:00:00', 50, true),
('branch-yokohama', 'yokohama', 'Yakiniku æ¨ªæµœé–¢å†…åº—', 'yokohama', '045-264-7729', 'æ¨ªæµœå¸‚ä¸­åŒºä½å‰ç”º5-65-2 1F', '17:00:00', '24:00:00', 60, true);

-- ============================================
-- 2. STAFF (34 staff across 5 branches)
-- ============================================
INSERT INTO staff (id, employee_id, branch_code, name, name_kana, phone, email, role, pin_code, is_active, hire_date) VALUES
-- JIAN (10 staff)
('staff-001', 'S001', 'hirama', 'å±±ç”° å¤ªéƒŽ', 'ãƒ¤ãƒžãƒ€ ã‚¿ãƒ­ã‚¦', '090-1111-0001', 'yamada@yakiniku.io', 'admin', '111111', true, '2020-04-01'),
('staff-002', 'S002', 'hirama', 'ä½è—¤ èŠ±å­', 'ã‚µãƒˆã‚¦ ãƒãƒŠã‚³', '090-1111-0002', 'sato@yakiniku.io', 'admin', '222222', true, '2020-04-01'),
('staff-003', 'S003', 'hirama', 'ç”°ä¸­ ä¸€éƒŽ', 'ã‚¿ãƒŠã‚« ã‚¤ãƒãƒ­ã‚¦', '090-1111-0003', 'tanaka@yakiniku.io', 'manager', '333333', true, '2021-06-15'),
('staff-004', 'S004', 'hirama', 'éˆ´æœ¨ ç¾Žå’²', 'ã‚¹ã‚ºã‚­ ãƒŸã‚µã‚­', '090-1111-0004', 'suzuki@yakiniku.io', 'cashier', '444444', true, '2022-01-10'),
('staff-005', 'S005', 'hirama', 'é«˜æ©‹ å¥å¤ª', 'ã‚¿ã‚«ãƒã‚· ã‚±ãƒ³ã‚¿', '090-1111-0005', 'takahashi@yakiniku.io', 'waiter', '555555', true, '2022-03-20'),
('staff-006', 'S006', 'hirama', 'ä¼Šè—¤ ã•ãã‚‰', 'ã‚¤ãƒˆã‚¦ ã‚µã‚¯ãƒ©', '090-1111-0006', 'ito@yakiniku.io', 'waiter', '666666', true, '2023-04-01'),
('staff-007', 'S007', 'hirama', 'æ¸¡è¾º å¤§è¼”', 'ãƒ¯ã‚¿ãƒŠãƒ™ ãƒ€ã‚¤ã‚¹ã‚±', '090-1111-0007', 'watanabe@yakiniku.io', 'kitchen', '777777', true, '2021-08-01'),
('staff-008', 'S008', 'hirama', 'ä¸­æ‘ çœŸç”±ç¾Ž', 'ãƒŠã‚«ãƒ ãƒ© ãƒžãƒ¦ãƒŸ', '090-1111-0008', 'nakamura@yakiniku.io', 'kitchen', '888888', true, '2022-07-15'),
('staff-009', 'S009', 'hirama', 'å°æž— ç¿”å¤ª', 'ã‚³ãƒãƒ¤ã‚· ã‚·ãƒ§ã‚¦ã‚¿', '090-1111-0009', 'kobayashi@yakiniku.io', 'receptionist', '999999', true, '2023-09-01'),
('staff-010', 'S010', 'hirama', 'åŠ è—¤ æ„›', 'ã‚«ãƒˆã‚¦ ã‚¢ã‚¤', '090-1111-0010', 'kato@yakiniku.io', 'waiter', '000000', true, '2024-01-15'),
-- Shinjuku (7 staff)
('staff-011', 'S011', 'shinjuku', 'æ¾æœ¬ å¤§ä»‹', 'ãƒžãƒ„ãƒ¢ãƒˆ ãƒ€ã‚¤ã‚¹ã‚±', '090-2222-0001', 'matsumoto@yakiniku.io', 'admin', '111112', true, '2022-03-15'),
('staff-012', 'S012', 'shinjuku', 'äº•ä¸Š æ˜Žç¾Ž', 'ã‚¤ãƒŽã‚¦ã‚¨ ã‚¢ã‚±ãƒŸ', '090-2222-0002', 'inoue@yakiniku.io', 'manager', '222223', true, '2022-04-01'),
('staff-013', 'S013', 'shinjuku', 'æœ¨æ‘ èª ', 'ã‚­ãƒ ãƒ© ãƒžã‚³ãƒˆ', '090-2222-0003', 'kimura@yakiniku.io', 'cashier', '333334', true, '2022-06-01'),
('staff-014', 'S014', 'shinjuku', 'æž— å„ªå­', 'ãƒãƒ¤ã‚· ãƒ¦ã‚¦ã‚³', '090-2222-0004', 'hayashi@yakiniku.io', 'waiter', '444445', true, '2022-08-15'),
('staff-015', 'S015', 'shinjuku', 'æ¸…æ°´ æ‹“ä¹Ÿ', 'ã‚·ãƒŸã‚º ã‚¿ã‚¯ãƒ¤', '090-2222-0005', 'shimizu@yakiniku.io', 'waiter', '555556', true, '2023-01-10'),
('staff-016', 'S016', 'shinjuku', 'å±±å£ å½©é¦™', 'ãƒ¤ãƒžã‚°ãƒ ã‚¢ãƒ¤ã‚«', '090-2222-0006', 'yamaguchi@yakiniku.io', 'kitchen', '666667', true, '2022-05-01'),
('staff-017', 'S017', 'shinjuku', 'æ£® å¥äºŒ', 'ãƒ¢ãƒª ã‚±ãƒ³ã‚¸', '090-2222-0007', 'mori@yakiniku.io', 'kitchen', '777778', true, '2023-03-01'),
-- Yaesu (5 staff)
('staff-018', 'S018', 'yaesu', 'æ± ç”° ç›´æ¨¹', 'ã‚¤ã‚±ãƒ€ ãƒŠã‚ªã‚­', '090-3333-0001', 'ikeda@yakiniku.io', 'admin', '111113', true, '2023-06-01'),
('staff-019', 'S019', 'yaesu', 'æ©‹æœ¬ ç¾Žç©‚', 'ãƒã‚·ãƒ¢ãƒˆ ãƒŸãƒ›', '090-3333-0002', 'hashimoto@yakiniku.io', 'manager', '222224', true, '2023-06-15'),
('staff-020', 'S020', 'yaesu', 'é˜¿éƒ¨ ç¿”', 'ã‚¢ãƒ™ ã‚·ãƒ§ã‚¦', '090-3333-0003', 'abe@yakiniku.io', 'cashier', '333335', true, '2023-07-01'),
('staff-021', 'S021', 'yaesu', 'çŸ³å· æµç†', 'ã‚¤ã‚·ã‚«ãƒ¯ ã‚¨ãƒª', '090-3333-0004', 'ishikawa@yakiniku.io', 'waiter', '444446', true, '2023-08-01'),
('staff-022', 'S022', 'yaesu', 'å‰ç”° é¾ä¸€', 'ãƒžã‚¨ãƒ€ ãƒªãƒ¥ã‚¦ã‚¤ãƒ', '090-3333-0005', 'maeda@yakiniku.io', 'kitchen', '555557', true, '2023-09-01'),
-- Shinagawa (5 staff)
('staff-023', 'S023', 'shinagawa', 'è—¤åŽŸ å‰›', 'ãƒ•ã‚¸ãƒ¯ãƒ© ãƒ„ãƒ¨ã‚·', '090-4444-0001', 'fujiwara@yakiniku.io', 'admin', '111114', true, '2023-09-01'),
('staff-024', 'S024', 'shinagawa', 'å²¡ç”° ã•ã‚„ã‹', 'ã‚ªã‚«ãƒ€ ã‚µãƒ¤ã‚«', '090-4444-0002', 'okada@yakiniku.io', 'manager', '222225', true, '2023-09-15'),
('staff-025', 'S025', 'shinagawa', 'å¾Œè—¤ äº®å¤ª', 'ã‚´ãƒˆã‚¦ ãƒªãƒ§ã‚¦ã‚¿', '090-4444-0003', 'goto@yakiniku.io', 'cashier', '333336', true, '2023-10-01'),
('staff-026', 'S026', 'shinagawa', 'é è—¤ çœŸç†', 'ã‚¨ãƒ³ãƒ‰ã‚¦ ãƒžãƒª', '090-4444-0004', 'endo@yakiniku.io', 'waiter', '444447', true, '2023-11-01'),
('staff-027', 'S027', 'shinagawa', 'é’æœ¨ å¤§åœ°', 'ã‚¢ã‚ªã‚­ ãƒ€ã‚¤ãƒ', '090-4444-0005', 'aoki@yakiniku.io', 'kitchen', '555558', true, '2023-12-01'),
-- Yokohama (7 staff)
('staff-028', 'S028', 'yokohama', 'å‚æœ¬ éš¼äºº', 'ã‚µã‚«ãƒ¢ãƒˆ ãƒãƒ¤ãƒˆ', '090-5555-0001', 'sakamoto@yakiniku.io', 'admin', '111115', true, '2024-01-15'),
('staff-029', 'S029', 'yokohama', 'å‰ç”° éº»è¡£', 'ãƒ¨ã‚·ãƒ€ ãƒžã‚¤', '090-5555-0002', 'yoshida@yakiniku.io', 'manager', '222226', true, '2024-01-20'),
('staff-030', 'S030', 'yokohama', 'åŽŸç”° æ‚ æ–—', 'ãƒãƒ©ãƒ€ ãƒ¦ã‚¦ãƒˆ', '090-5555-0003', 'harada@yakiniku.io', 'cashier', '333337', true, '2024-02-01'),
('staff-031', 'S031', 'yokohama', 'åƒè‘‰ ç´éŸ³', 'ãƒãƒ ã‚³ãƒˆãƒ', '090-5555-0004', 'chiba@yakiniku.io', 'waiter', '444448', true, '2024-02-15'),
('staff-032', 'S032', 'yokohama', 'é‡Žæ‘ è“®', 'ãƒŽãƒ ãƒ© ãƒ¬ãƒ³', '090-5555-0005', 'nomura@yakiniku.io', 'waiter', '555559', true, '2024-03-01'),
('staff-033', 'S033', 'yokohama', 'è…åŽŸ æ¡ƒå­', 'ã‚¹ã‚¬ãƒ¯ãƒ© ãƒ¢ãƒ¢ã‚³', '090-5555-0006', 'sugawara@yakiniku.io', 'kitchen', '666668', true, '2024-03-15'),
('staff-034', 'S034', 'yokohama', 'æ–°äº• åº·ä»‹', 'ã‚¢ãƒ©ã‚¤ ã‚³ã‚¦ã‚¹ã‚±', '090-5555-0007', 'arai@yakiniku.io', 'kitchen', '777779', true, '2024-04-01');

-- ============================================
-- 3. TABLES (47 tables across 5 branches)
-- Schema: id, branch_code, table_number, name, min_capacity, max_capacity,
--         table_type, floor, zone, has_window, is_smoking, is_wheelchair_accessible,
--         has_baby_chair, status, is_active, priority, notes
-- ============================================
INSERT INTO tables (id, branch_code, table_number, name, max_capacity, table_type, zone, has_window, is_active, notes) VALUES
-- JIAN (9 tables)
('table-JIAN-01', 'hirama', 'A1', 'ãƒ†ãƒ¼ãƒ–ãƒ«A1', 4, 'table', 'floor', true, true, 'çª“éš›'),
('table-JIAN-02', 'hirama', 'A2', 'ãƒ†ãƒ¼ãƒ–ãƒ«A2', 4, 'table', 'floor', false, true, NULL),
('table-JIAN-03', 'hirama', 'A3', 'ãƒ†ãƒ¼ãƒ–ãƒ«A3', 4, 'table', 'floor', false, true, NULL),
('table-JIAN-04', 'hirama', 'A4', 'ãƒ†ãƒ¼ãƒ–ãƒ«A4', 6, 'table', 'floor', false, true, 'å¤§ãã‚ãƒ†ãƒ¼ãƒ–ãƒ«'),
('table-JIAN-05', 'hirama', 'B1', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B1', 2, 'counter', 'counter', false, true, 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼å¸­'),
('table-JIAN-06', 'hirama', 'B2', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B2', 2, 'counter', 'counter', false, true, 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼å¸­'),
('table-JIAN-07', 'hirama', 'B3', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B3', 2, 'counter', 'counter', false, true, 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼å¸­'),
('table-JIAN-08', 'hirama', 'C1', 'å€‹å®¤C1', 8, 'private', 'private', false, true, 'å€‹å®¤ãƒ»æŽ˜ã‚Šã”ãŸã¤'),
('table-JIAN-09', 'hirama', 'C2', 'VIPå€‹å®¤C2', 10, 'private', 'private', false, true, 'VIPå€‹å®¤ãƒ»ã‚«ãƒ©ã‚ªã‚±ä»˜'),
-- Shinjuku (12 tables)
('table-shinjuku-01', 'shinjuku', 'A1', 'ãƒ†ãƒ¼ãƒ–ãƒ«A1', 4, 'table', 'floor', true, true, 'çª“éš›'),
('table-shinjuku-02', 'shinjuku', 'A2', 'ãƒ†ãƒ¼ãƒ–ãƒ«A2', 4, 'table', 'floor', false, true, NULL),
('table-shinjuku-03', 'shinjuku', 'A3', 'ãƒ†ãƒ¼ãƒ–ãƒ«A3', 4, 'table', 'floor', false, true, NULL),
('table-shinjuku-04', 'shinjuku', 'A4', 'ãƒ†ãƒ¼ãƒ–ãƒ«A4', 4, 'table', 'floor', false, true, NULL),
('table-shinjuku-05', 'shinjuku', 'A5', 'ãƒ†ãƒ¼ãƒ–ãƒ«A5', 6, 'table', 'floor', false, true, 'è§’å¸­'),
('table-shinjuku-06', 'shinjuku', 'B1', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B1', 2, 'counter', 'counter', false, true, NULL),
('table-shinjuku-07', 'shinjuku', 'B2', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B2', 2, 'counter', 'counter', false, true, NULL),
('table-shinjuku-08', 'shinjuku', 'B3', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B3', 2, 'counter', 'counter', false, true, NULL),
('table-shinjuku-09', 'shinjuku', 'B4', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B4', 2, 'counter', 'counter', false, true, NULL),
('table-shinjuku-10', 'shinjuku', 'C1', 'å€‹å®¤C1', 8, 'private', 'private', false, true, 'å€‹å®¤'),
('table-shinjuku-11', 'shinjuku', 'C2', 'VIPå€‹å®¤C2', 10, 'private', 'private', false, true, 'VIPå€‹å®¤'),
('table-shinjuku-12', 'shinjuku', 'C3', 'å®´ä¼šå€‹å®¤C3', 14, 'private', 'private', false, true, 'å®´ä¼šå€‹å®¤'),
-- Yaesu (8 tables)
('table-yaesu-01', 'yaesu', 'A1', 'ãƒ†ãƒ¼ãƒ–ãƒ«A1', 4, 'table', 'floor', true, true, 'çª“éš›ãƒ»ãƒ“ã‚¸ãƒã‚¹å‘ã‘'),
('table-yaesu-02', 'yaesu', 'A2', 'ãƒ†ãƒ¼ãƒ–ãƒ«A2', 4, 'table', 'floor', false, true, NULL),
('table-yaesu-03', 'yaesu', 'A3', 'ãƒ†ãƒ¼ãƒ–ãƒ«A3', 4, 'table', 'floor', false, true, NULL),
('table-yaesu-04', 'yaesu', 'B1', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B1', 2, 'counter', 'counter', false, true, 'ãƒ©ãƒ³ãƒäººæ°—'),
('table-yaesu-05', 'yaesu', 'B2', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B2', 2, 'counter', 'counter', false, true, NULL),
('table-yaesu-06', 'yaesu', 'B3', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B3', 2, 'counter', 'counter', false, true, NULL),
('table-yaesu-07', 'yaesu', 'C1', 'å•†è«‡å€‹å®¤C1', 6, 'private', 'private', false, true, 'å•†è«‡å‘ã‘å€‹å®¤'),
('table-yaesu-08', 'yaesu', 'C2', 'æŽ¥å¾…å€‹å®¤C2', 8, 'private', 'private', false, true, 'æŽ¥å¾…å‘ã‘å€‹å®¤'),
-- Shinagawa (8 tables)
('table-shinagawa-01', 'shinagawa', 'A1', 'ãƒ†ãƒ¼ãƒ–ãƒ«A1', 4, 'table', 'floor', false, true, NULL),
('table-shinagawa-02', 'shinagawa', 'A2', 'ãƒ†ãƒ¼ãƒ–ãƒ«A2', 4, 'table', 'floor', false, true, NULL),
('table-shinagawa-03', 'shinagawa', 'A3', 'ãƒ†ãƒ¼ãƒ–ãƒ«A3', 4, 'table', 'floor', true, true, 'çª“éš›'),
('table-shinagawa-04', 'shinagawa', 'A4', 'ãƒ†ãƒ¼ãƒ–ãƒ«A4', 6, 'table', 'floor', false, true, NULL),
('table-shinagawa-05', 'shinagawa', 'B1', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B1', 2, 'counter', 'counter', false, true, NULL),
('table-shinagawa-06', 'shinagawa', 'B2', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B2', 2, 'counter', 'counter', false, true, NULL),
('table-shinagawa-07', 'shinagawa', 'C1', 'å€‹å®¤C1', 8, 'private', 'private', false, true, 'å€‹å®¤'),
('table-shinagawa-08', 'shinagawa', 'C2', 'å®´ä¼šå€‹å®¤C2', 10, 'private', 'private', false, true, 'å®´ä¼šå€‹å®¤'),
-- Yokohama (10 tables)
('table-yokohama-01', 'yokohama', 'A1', 'ãƒ†ãƒ¼ãƒ–ãƒ«A1', 4, 'table', 'floor', true, true, 'æµ·ãŒè¦‹ãˆã‚‹'),
('table-yokohama-02', 'yokohama', 'A2', 'ãƒ†ãƒ¼ãƒ–ãƒ«A2', 4, 'table', 'floor', true, true, 'æµ·ãŒè¦‹ãˆã‚‹'),
('table-yokohama-03', 'yokohama', 'A3', 'ãƒ†ãƒ¼ãƒ–ãƒ«A3', 4, 'table', 'floor', false, true, NULL),
('table-yokohama-04', 'yokohama', 'A4', 'ãƒ†ãƒ¼ãƒ–ãƒ«A4', 4, 'table', 'floor', false, true, NULL),
('table-yokohama-05', 'yokohama', 'A5', 'ãƒ†ãƒ¼ãƒ–ãƒ«A5', 6, 'table', 'floor', false, true, 'è§’å¸­'),
('table-yokohama-06', 'yokohama', 'B1', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B1', 2, 'counter', 'counter', false, true, NULL),
('table-yokohama-07', 'yokohama', 'B2', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B2', 2, 'counter', 'counter', false, true, NULL),
('table-yokohama-08', 'yokohama', 'B3', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼B3', 2, 'counter', 'counter', false, true, NULL),
('table-yokohama-09', 'yokohama', 'C1', 'å€‹å®¤C1', 8, 'private', 'private', false, true, 'å€‹å®¤'),
('table-yokohama-10', 'yokohama', 'C2', 'å¤§å®´ä¼šå€‹å®¤C2', 12, 'private', 'private', false, true, 'å¤§å®´ä¼šå€‹å®¤');

-- ============================================
-- 4. MENU ITEMS (41 items for JIAN branch)
-- Schema: id, branch_code, name, name_en, description, category, subcategory,
--         display_order, price, tax_rate, image_url, prep_time_minutes, kitchen_note,
--         is_available, is_popular, is_spicy, is_vegetarian, allergens
-- ============================================
INSERT INTO menu_items (id, branch_code, name, name_en, description, category, subcategory, price, display_order, is_available, is_popular, is_spicy, is_vegetarian, allergens, prep_time_minutes, kitchen_note) VALUES
('menu-001', 'hirama', 'å’Œç‰›ä¸Šãƒãƒ©ãƒŸ', 'Premium Harami', 'å£ã®ä¸­ã§ã»ã©ã‘ã‚‹æŸ”ã‚‰ã‹ã•ã¨æ¿ƒåŽšãªå‘³ã‚ã„ã€‚å½“åº—è‡ªæ…¢ã®ä¸€å“', 'meat', 'beef', 1800, 1, true, true, false, false, NULL, 5, 'ç„¼ãåŠ æ¸›ã¯ãƒ¬ã‚¢ãŒãŠã™ã™ã‚'),
('menu-002', 'hirama', 'åŽšåˆ‡ã‚Šä¸Šã‚¿ãƒ³å¡©', 'Thick Sliced Beef Tongue', 'è´…æ²¢ãªåŽšåˆ‡ã‚Šã€‚æ­¯ã”ãŸãˆã¨è‚‰æ±ãŒæº¢ã‚Œã¾ã™', 'meat', 'beef', 2200, 2, true, true, false, false, NULL, 6, 'åŽšåˆ‡ã‚Šã®ãŸã‚ä¸­å¿ƒã¾ã§ç«ã‚’é€šã™'),
('menu-003', 'hirama', 'ç‰¹é¸ã‚«ãƒ«ãƒ“', 'Premium Kalbi', 'éœœé™ã‚ŠãŒç¾Žã—ã„æœ€é«˜ç´šã‚«ãƒ«ãƒ“', 'meat', 'beef', 1800, 3, true, true, false, false, NULL, 5, NULL),
('menu-004', 'hirama', 'ã‚«ãƒ«ãƒ“', 'Kalbi', 'å®šç•ªã®äººæ°—ãƒ¡ãƒ‹ãƒ¥ãƒ¼ã€‚ã‚¸ãƒ¥ãƒ¼ã‚·ãƒ¼ãªå‘³ã‚ã„', 'meat', 'beef', 1500, 4, true, false, false, false, NULL, 5, NULL),
('menu-005', 'hirama', 'ä¸Šãƒ­ãƒ¼ã‚¹', 'Premium Sirloin', 'èµ¤èº«ã®æ—¨å‘³ãŒæ¥½ã—ã‚ã‚‹ä¸Šè³ªãªãƒ­ãƒ¼ã‚¹', 'meat', 'beef', 1700, 5, true, false, false, false, NULL, 5, NULL),
('menu-006', 'hirama', 'ãƒ­ãƒ¼ã‚¹', 'Sirloin', 'ã‚ã£ã•ã‚Šã¨ã—ãŸèµ¤èº«ã®ç¾Žå‘³ã—ã•', 'meat', 'beef', 1400, 6, true, false, false, false, NULL, 5, NULL),
('menu-007', 'hirama', 'ãƒ›ãƒ«ãƒ¢ãƒ³ç››ã‚Šåˆã‚ã›', 'Offal Assortment', 'æ–°é®®ãªãƒ›ãƒ«ãƒ¢ãƒ³ã‚’ãŸã£ã·ã‚Šã€‚ãƒŸãƒŽãƒ»ãƒãƒãƒŽã‚¹ãƒ»ã‚·ãƒžãƒãƒ§ã‚¦', 'meat', 'offal', 1400, 7, true, false, false, false, NULL, 7, 'æ–°é®®ãªã†ã¡ã«æä¾›'),
('menu-008', 'hirama', 'ç‰¹é¸ç››ã‚Šåˆã‚ã›', 'Special Assortment', 'æœ¬æ—¥ã®ãŠã™ã™ã‚å¸Œå°‘éƒ¨ä½ã‚’è´…æ²¢ã«ç››ã‚Šåˆã‚ã›', 'meat', 'beef', 4500, 8, true, true, false, false, NULL, 8, '4ç¨®ç››ã‚Š'),
('menu-009', 'hirama', 'è±šã‚«ãƒ«ãƒ“', 'Pork Kalbi', 'ç”˜ã¿ã®ã‚ã‚‹è±šãƒãƒ©è‚‰', 'meat', 'pork', 900, 9, true, false, false, false, NULL, 5, NULL),
('menu-010', 'hirama', 'é¶ã‚‚ã‚‚', 'Chicken Thigh', 'æŸ”ã‚‰ã‹ãã‚¸ãƒ¥ãƒ¼ã‚·ãƒ¼ãªé¶ã‚‚ã‚‚è‚‰', 'meat', 'chicken', 800, 10, true, false, false, false, NULL, 5, NULL),
('menu-011', 'hirama', 'ç”Ÿãƒ“ãƒ¼ãƒ«', 'Draft Beer', 'ã‚­ãƒ³ã‚­ãƒ³ã«å†·ãˆãŸç”Ÿãƒ“ãƒ¼ãƒ«ï¼ˆä¸­ï¼‰', 'drinks', 'beer', 600, 1, true, false, false, false, NULL, 1, NULL),
('menu-012', 'hirama', 'ç“¶ãƒ“ãƒ¼ãƒ«', 'Bottled Beer', 'ã‚¢ã‚µãƒ’ã‚¹ãƒ¼ãƒ‘ãƒ¼ãƒ‰ãƒ©ã‚¤', 'drinks', 'beer', 650, 2, true, false, false, false, NULL, 1, NULL),
('menu-013', 'hirama', 'ãƒã‚¤ãƒœãƒ¼ãƒ«', 'Highball', 'ã™ã£ãã‚Šçˆ½ã‚„ã‹ãªã‚¦ã‚¤ã‚¹ã‚­ãƒ¼ã‚½ãƒ¼ãƒ€', 'drinks', 'whisky', 500, 3, true, false, false, false, NULL, 1, NULL),
('menu-014', 'hirama', 'ãƒ¬ãƒ¢ãƒ³ã‚µãƒ¯ãƒ¼', 'Lemon Sour', 'è‡ªå®¶è£½ãƒ¬ãƒ¢ãƒ³ã‚µãƒ¯ãƒ¼ã€‚ã•ã£ã±ã‚Šé£²ã¿ã‚„ã™ã„', 'drinks', 'sour', 500, 4, true, false, false, false, NULL, 1, NULL),
('menu-015', 'hirama', 'æ¢…é…’ã‚µãƒ¯ãƒ¼', 'Plum Wine Sour', 'ç”˜é…¸ã£ã±ã„æ¢…é…’ã‚½ãƒ¼ãƒ€å‰²ã‚Š', 'drinks', 'sour', 550, 5, true, false, false, false, NULL, 1, NULL),
('menu-016', 'hirama', 'ãƒžãƒƒã‚³ãƒª', 'Makgeolli', 'éŸ“å›½ã®ä¼çµ±é…’ã€‚ã¾ã‚ã‚„ã‹ãªç”˜ã•', 'drinks', 'korean', 600, 6, true, false, false, false, NULL, 1, NULL),
('menu-017', 'hirama', 'ç„¼é…Žï¼ˆèŠ‹ï¼‰', 'Sweet Potato Shochu', 'æœ¬æ ¼èŠ‹ç„¼é…Žã€‚ãƒ­ãƒƒã‚¯ãƒ»æ°´å‰²ã‚Šãƒ»ãŠæ¹¯å‰²ã‚Š', 'drinks', 'shochu', 500, 7, true, false, false, false, NULL, 1, NULL),
('menu-018', 'hirama', 'ã‚¦ãƒ¼ãƒ­ãƒ³èŒ¶', 'Oolong Tea', 'ã‚½ãƒ•ãƒˆãƒ‰ãƒªãƒ³ã‚¯', 'drinks', 'soft', 300, 8, true, false, false, false, NULL, 1, NULL),
('menu-019', 'hirama', 'ã‚³ãƒ¼ãƒ©', 'Cola', 'ã‚³ã‚«ãƒ»ã‚³ãƒ¼ãƒ©', 'drinks', 'soft', 300, 9, true, false, false, false, NULL, 1, NULL),
('menu-020', 'hirama', 'ã‚ªãƒ¬ãƒ³ã‚¸ã‚¸ãƒ¥ãƒ¼ã‚¹', 'Orange Juice', '100%ãƒ•ãƒ¬ãƒƒã‚·ãƒ¥ã‚¸ãƒ¥ãƒ¼ã‚¹', 'drinks', 'soft', 400, 10, true, false, false, false, NULL, 1, NULL),
('menu-021', 'hirama', 'ã‚­ãƒ ãƒç››ã‚Šåˆã‚ã›', 'Kimchi Assortment', 'ç™½èœãƒ»å¤§æ ¹ãƒ»ãã‚…ã†ã‚Šã®3ç¨®ç››ã‚Š', 'side', 'korean', 500, 1, true, false, true, true, NULL, 2, NULL),
('menu-022', 'hirama', 'ãƒŠãƒ ãƒ«ç››ã‚Šåˆã‚ã›', 'Namul Assortment', 'ã»ã†ã‚Œã‚“è‰ãƒ»ã‚‚ã‚„ã—ãƒ»ãœã‚“ã¾ã„ã®3ç¨®', 'side', 'korean', 500, 2, true, false, false, true, NULL, 3, NULL),
('menu-023', 'hirama', 'ãƒãƒ§ãƒ¬ã‚®ã‚µãƒ©ãƒ€', 'Choregi Salad', 'ã‚·ãƒ£ã‚­ã‚·ãƒ£ã‚­é‡Žèœã®ã”ã¾æ²¹ãƒ‰ãƒ¬ãƒƒã‚·ãƒ³ã‚°', 'side', 'salad', 600, 3, true, false, false, true, 'ã”ã¾', 3, NULL),
('menu-024', 'hirama', 'çŸ³ç„¼ãƒ“ãƒ“ãƒ³ãƒ', 'Stone-grilled Bibimbap', 'ãŠã“ã’ãŒé¦™ã°ã—ã„å®šç•ªã€†ãƒ¡ãƒ‹ãƒ¥ãƒ¼', 'rice', 'korean', 1200, 1, true, true, false, false, 'åµ', 10, 'ãŠã“ã’ã‚’ä½œã‚‹'),
('menu-025', 'hirama', 'å†·éºº', 'Cold Noodles', 'å¼¾åŠ›ã‚ã‚‹éººã¨çˆ½ã‚„ã‹ãªã‚¹ãƒ¼ãƒ—', 'noodle', 'korean', 900, 2, true, false, false, false, 'å°éº¦ãƒ»åµ', 5, 'å¤å­£é™å®š'),
('menu-026', 'hirama', 'ã‚«ãƒ«ãƒ“ã‚¯ãƒƒãƒ‘', 'Kalbi Soup with Rice', 'æ—¨å‘³ãŸã£ã·ã‚Šã®ã‚¹ãƒ¼ãƒ—ã«ã”é£¯ã‚’æ·»ãˆã¦', 'rice', 'korean', 1000, 3, true, false, false, false, NULL, 8, NULL),
('menu-027', 'hirama', 'ãƒ©ã‚¤ã‚¹', 'Rice', 'å›½ç”£ã‚³ã‚·ãƒ’ã‚«ãƒª', 'rice', 'japanese', 300, 4, true, false, false, true, NULL, 2, NULL),
('menu-028', 'hirama', 'ã‚ã‹ã‚ã‚¹ãƒ¼ãƒ—', 'Seaweed Soup', 'å„ªã—ã„å‘³ã‚ã„ã®å®šç•ªã‚¹ãƒ¼ãƒ—', 'soup', 'korean', 400, 1, true, false, false, true, NULL, 3, NULL),
('menu-029', 'hirama', 'ãŸã¾ã”ã‚¹ãƒ¼ãƒ—', 'Egg Soup', 'ãµã‚ãµã‚åµã®ã‚„ã•ã—ã„ã‚¹ãƒ¼ãƒ—', 'soup', 'japanese', 400, 2, true, false, false, false, 'åµ', 3, NULL),
('menu-030', 'hirama', 'ãƒ†ãƒ¼ãƒ«ã‚¹ãƒ¼ãƒ—', 'Oxtail Soup', 'ã˜ã£ãã‚Šç…®è¾¼ã‚“ã æœ¬æ ¼æ´¾', 'soup', 'korean', 800, 3, true, false, false, false, NULL, 5, 'æœã‹ã‚‰ä»•è¾¼ã¿'),
('menu-031', 'hirama', 'ãƒãƒ‹ãƒ©ã‚¢ã‚¤ã‚¹', 'Vanilla Ice Cream', 'æ¿ƒåŽšãƒãƒ‹ãƒ©ã‚¢ã‚¤ã‚¹', 'dessert', 'ice', 400, 1, true, false, false, false, 'ä¹³', 1, NULL),
('menu-032', 'hirama', 'æŠ¹èŒ¶ã‚¢ã‚¤ã‚¹', 'Matcha Ice Cream', 'äº¬éƒ½ç”£å®‡æ²»æŠ¹èŒ¶ä½¿ç”¨', 'dessert', 'ice', 450, 2, true, false, false, false, 'ä¹³', 1, NULL),
('menu-033', 'hirama', 'ã‚·ãƒ£ãƒ¼ãƒ™ãƒƒãƒˆ3ç¨®', 'Sorbet Trio', 'ã‚†ãšãƒ»ãƒžãƒ³ã‚´ãƒ¼ãƒ»ãƒ©ã‚¤ãƒ', 'dessert', 'ice', 500, 3, true, false, false, true, NULL, 1, NULL),
('menu-034', 'hirama', 'æä»è±†è…', 'Almond Jelly', 'ãªã‚ã‚‰ã‹ãªé£Ÿæ„Ÿã®æœ¬æ ¼æä»', 'dessert', 'chinese', 450, 4, true, false, false, false, 'ã‚¢ãƒ¼ãƒ¢ãƒ³ãƒ‰ãƒ»ä¹³', 2, NULL),
('menu-035', 'hirama', 'ç„¼è‚‰å¼å½“ï¼ˆä¸Šï¼‰', 'Premium Yakiniku Bento', 'ä¸Šã‚«ãƒ«ãƒ“ãƒ»ä¸Šãƒ­ãƒ¼ã‚¹ãƒ»ãƒŠãƒ ãƒ«ãƒ»ã‚­ãƒ ãƒ', 'bento', 'takeout', 1800, 1, true, true, false, false, NULL, 15, 'ãƒ†ã‚¤ã‚¯ã‚¢ã‚¦ãƒˆç”¨'),
('menu-036', 'hirama', 'ç„¼è‚‰å¼å½“ï¼ˆä¸¦ï¼‰', 'Regular Yakiniku Bento', 'ã‚«ãƒ«ãƒ“ãƒ»ãƒ­ãƒ¼ã‚¹ãƒ»ãƒŠãƒ ãƒ«ãƒ»ã‚­ãƒ ãƒ', 'bento', 'takeout', 1200, 2, true, false, false, false, NULL, 12, 'ãƒ†ã‚¤ã‚¯ã‚¢ã‚¦ãƒˆç”¨'),
('menu-037', 'hirama', 'ã‚¿ãƒ³å¡©å¼å½“', 'Beef Tongue Bento', 'åŽšåˆ‡ã‚Šã‚¿ãƒ³å¡©ãƒ»ãƒŠãƒ ãƒ«ãƒ»ã‚µãƒ©ãƒ€', 'bento', 'takeout', 1500, 3, true, false, false, false, NULL, 12, 'ãƒ†ã‚¤ã‚¯ã‚¢ã‚¦ãƒˆç”¨'),
('menu-038', 'hirama', 'é£²ã¿æ”¾é¡Œï¼ˆ90åˆ†ï¼‰', 'All-You-Can-Drink 90min', 'ãƒ“ãƒ¼ãƒ«ãƒ»ã‚µãƒ¯ãƒ¼ãƒ»ç„¼é…Žãƒ»ã‚½ãƒ•ãƒˆãƒ‰ãƒªãƒ³ã‚¯', 'course', 'drink', 1500, 1, true, false, false, false, NULL, 0, 'è¦äºˆç´„'),
('menu-039', 'hirama', 'é£²ã¿æ”¾é¡Œï¼ˆ120åˆ†ï¼‰', 'All-You-Can-Drink 120min', 'ãƒ“ãƒ¼ãƒ«ãƒ»ã‚µãƒ¯ãƒ¼ãƒ»ç„¼é…Žãƒ»ã‚½ãƒ•ãƒˆãƒ‰ãƒªãƒ³ã‚¯', 'course', 'drink', 2000, 2, true, false, false, false, NULL, 0, 'è¦äºˆç´„'),
('menu-040', 'hirama', 'è´…æ²¢ã‚³ãƒ¼ã‚¹', 'Luxury Course', 'å‰èœãƒ»ç‰¹é¸5ç¨®ç››ã‚Šãƒ»ã€†ãƒ»ãƒ‡ã‚¶ãƒ¼ãƒˆ', 'course', 'food', 8000, 3, true, true, false, false, NULL, 0, 'è¦äºˆç´„ãƒ»2åæ§˜ã‚ˆã‚Š'),
('menu-041', 'hirama', 'å®´ä¼šã‚³ãƒ¼ã‚¹', 'Party Course', 'å‰èœãƒ»ç„¼è‚‰ç››ã‚Šåˆã‚ã›ãƒ»ã€†ãƒ»ãƒ‡ã‚¶ãƒ¼ãƒˆ+é£²ã¿æ”¾é¡Œ', 'course', 'food', 5500, 4, true, false, false, false, NULL, 0, 'è¦äºˆç´„ãƒ»4åæ§˜ã‚ˆã‚Š');

-- ============================================
-- 5. GLOBAL CUSTOMERS (100 customers)
-- ============================================
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
('cust-020', '090-2000-0020', 'åŽŸç”° ç¿”', 'harada.sho@email.jp', '2024-05-01 10:00:00'),
('cust-021', '090-2000-0021', 'ä¸­å³¶ ç”±ç¾Žå­', 'nakajima.yumiko@email.jp', '2024-05-05 15:00:00'),
('cust-022', '090-2000-0022', 'çŸ³ç”° é™½å­', 'ishida.yoko@email.jp', '2024-05-10 18:30:00'),
('cust-023', '090-2000-0023', 'å±±å£ é”ä¹Ÿ', 'yamaguchi.tatsuya@email.jp', '2024-05-15 12:15:00'),
('cust-024', '090-2000-0024', 'æ¾ç”° æµ', 'matsuda.megumi@email.jp', '2024-05-20 17:00:00'),
('cust-025', '090-2000-0025', 'äº•ç”° æ‹“çœŸ', 'ida.takuma@email.jp', '2024-05-25 14:30:00'),
('cust-026', '090-2000-0026', 'ä¸­å±± æ„›', 'nakayama.ai@email.jp', '2024-06-01 11:00:00'),
('cust-027', '090-2000-0027', 'å°é‡Ž å¥å¸', 'ono.kenji@email.jp', '2024-06-05 16:45:00'),
('cust-028', '090-2000-0028', 'é«˜ç”° ç¾Žé¦™', 'takada.mika@email.jp', '2024-06-10 13:00:00'),
('cust-029', '090-2000-0029', 'ç¦ç”° èª ä¸€', 'fukuda.seiichi@email.jp', '2024-06-15 19:00:00'),
('cust-030', '090-2000-0030', 'è¥¿æ‘ å¥', 'nishimura.ken@email.jp', '2024-06-20 10:30:00'),
('cust-031', '090-2000-0031', 'ä¸‰æµ¦ å½©', 'miura.aya@email.jp', '2024-06-25 15:15:00'),
('cust-032', '090-2000-0032', 'è—¤æœ¬ å¤§åœ°', 'fujimoto.daichi@email.jp', '2024-07-01 12:45:00'),
('cust-033', '090-2000-0033', 'å²©ç”° ç¾Žå’²', 'iwata.misaki@email.jp', '2024-07-05 18:00:00'),
('cust-034', '090-2000-0034', 'ä¸­ç”° è‰¯å¹³', 'nakata.ryohei@email.jp', '2024-07-10 14:30:00'),
('cust-035', '090-2000-0035', 'æ¨ªå±± ã•ã‚„ã‹', 'yokoyama.sayaka@email.jp', '2024-07-15 11:15:00'),
('cust-036', '090-2000-0036', 'ä¸Šé‡Ž å‰›', 'ueno.tsuyoshi@email.jp', '2024-07-20 17:30:00'),
('cust-037', '090-2000-0037', 'é‡‘å­ ç¾Žå„ª', 'kaneko.miyu@email.jp', '2024-07-25 13:45:00'),
('cust-038', '090-2000-0038', 'å¤§é‡Ž åº·ä»‹', 'ohno.kosuke@email.jp', '2024-08-01 10:15:00'),
('cust-039', '090-2000-0039', 'å°å±± çœŸç†', 'koyama.mari@email.jp', '2024-08-05 16:00:00'),
('cust-040', '090-2000-0040', 'é‡Žå£ æ‹“ä¹Ÿ', 'noguchi.takuya@email.jp', '2024-08-10 12:30:00'),
('cust-041', '090-2000-0041', 'è…åŽŸ æµå­', 'sugawara.keiko@email.jp', '2024-08-15 19:15:00'),
('cust-042', '090-2000-0042', 'æ–°äº• ç¿”å¤ª', 'arai.shota@email.jp', '2024-08-20 15:00:00'),
('cust-043', '090-2000-0043', 'åƒè‘‰ éº»è¡£', 'chiba.mai@email.jp', '2024-08-25 11:30:00'),
('cust-044', '090-2000-0044', 'ä½é‡Ž å¤§è¼”', 'sano.daisuke@email.jp', '2024-09-01 18:00:00'),
('cust-045', '090-2000-0045', 'æ¸¡éƒ¨ ç”±ç¾Ž', 'watabe.yumi@email.jp', '2024-09-05 14:15:00'),
('cust-046', '090-2000-0046', 'åŒ—æ‘ å¥ä¸€', 'kitamura.kenichi@email.jp', '2024-09-10 10:45:00'),
('cust-047', '090-2000-0047', 'æ–Žè—¤ ç¾Žé¦™', 'saito.mika@email.jp', '2024-09-15 17:00:00'),
('cust-048', '090-2000-0048', 'å®‰è—¤ èª ', 'ando.makoto@email.jp', '2024-09-20 13:30:00'),
('cust-049', '090-2000-0049', 'æ²³é‡Ž å½©ä¹ƒ', 'kono.ayano@email.jp', '2024-09-25 20:00:00'),
('cust-050', '090-2000-0050', 'å†…ç”° æµ©äºŒ', 'uchida.koji@email.jp', '2024-10-01 16:15:00'),
('cust-051', '090-2000-0051', 'å®®æœ¬ å„ªå­', 'miyamoto.yuko@email.jp', '2024-10-05 12:00:00'),
('cust-052', '090-2000-0052', 'å³¶ç”° å¤ªéƒŽ', 'shimada.taro@email.jp', '2024-10-10 18:45:00'),
('cust-053', '090-2000-0053', 'æ£®æœ¬ çœŸç”±', 'morimoto.mayu@email.jp', '2024-10-15 15:30:00'),
('cust-054', '090-2000-0054', 'æŸ´ç”° å¥å¤ª', 'shibata.kenta@email.jp', '2024-10-20 11:00:00'),
('cust-055', '090-2000-0055', 'ä¹…ä¿ æ„›', 'kubo.ai@email.jp', '2024-10-25 17:45:00'),
('cust-056', '090-2000-0056', 'å¹³é‡Ž ä¸€éƒŽ', 'hirano.ichiro@email.jp', '2024-11-01 14:00:00'),
('cust-057', '090-2000-0057', 'æ¾æ°¸ ç¾Žå’²', 'matsunaga.misaki@email.jp', '2024-11-05 10:30:00'),
('cust-058', '090-2000-0058', 'ç¦å³¶ é”ä¹Ÿ', 'fukushima.tatsuya@email.jp', '2024-11-10 16:45:00'),
('cust-059', '090-2000-0059', 'å¤§æ©‹ æµ', 'ohashi.megumi@email.jp', '2024-11-15 13:15:00'),
('cust-060', '090-2000-0060', 'å‰æ‘ æ‹“çœŸ', 'yoshimura.takuma@email.jp', '2024-11-20 19:30:00'),
('cust-061', '090-2000-0061', 'å·å³¶ ç”±ç¾Žå­', 'kawashima.yumiko@email.jp', '2024-11-25 15:45:00'),
('cust-062', '090-2000-0062', 'æ‰å±± å¥å¸', 'sugiyama.kenji@email.jp', '2024-12-01 12:00:00'),
('cust-063', '090-2000-0063', 'ä»Šäº• ç¾Žé¦™', 'imai.mika@email.jp', '2024-12-05 18:15:00'),
('cust-064', '090-2000-0064', 'ç”°æ‘ èª ä¸€', 'tamura.seiichi@email.jp', '2024-12-10 14:30:00'),
('cust-065', '090-2000-0065', 'æœ¬ç”° å½©', 'honda.aya@email.jp', '2024-12-15 11:00:00'),
('cust-066', '090-2000-0066', 'è°·å£ å¤§åœ°', 'taniguchi.daichi@email.jp', '2024-12-20 17:15:00'),
('cust-067', '090-2000-0067', 'æ­¦ç”° éº»è¡£', 'takeda.mai@email.jp', '2024-12-25 13:45:00'),
('cust-068', '090-2000-0068', 'æ°¸äº• è‰¯å¹³', 'nagai.ryohei@email.jp', '2025-01-01 20:00:00'),
('cust-069', '090-2000-0069', 'è¥¿ç”° ã•ã‚„ã‹', 'nishida.sayaka@email.jp', '2025-01-05 16:30:00'),
('cust-070', '090-2000-0070', 'æ —åŽŸ å‰›', 'kurihara.tsuyoshi@email.jp', '2025-01-10 12:45:00'),
('cust-071', '090-2000-0071', 'å±±ä¸‹ ç¾Žå„ª', 'yamashita.miyu@email.jp', '2025-01-15 19:00:00'),
('cust-072', '090-2000-0072', 'ç«¹å†… åº·ä»‹', 'takeuchi.kosuke@email.jp', '2025-01-20 15:15:00'),
('cust-073', '090-2000-0073', 'è¿‘è—¤ çœŸç†', 'kondo.mari@email.jp', '2025-01-25 11:30:00'),
('cust-074', '090-2000-0074', 'çŸ³åŽŸ ç¿”å¤ª', 'ishihara.shota@email.jp', '2025-02-01 18:00:00'),
('cust-075', '090-2000-0075', 'å¢—ç”° æµå­', 'masuda.keiko@email.jp', '2025-02-05 14:15:00'),
('cust-076', '090-2000-0076', 'æœ›æœˆ å¤§è¼”', 'mochizuki.daisuke@email.jp', '2025-02-10 10:45:00'),
('cust-077', '090-2000-0077', 'ç‰‡å±± ç”±ç¾Ž', 'katayama.yumi@email.jp', '2025-02-15 17:00:00'),
('cust-078', '090-2000-0078', 'ç§‹å±± å¥ä¸€', 'akiyama.kenichi@email.jp', '2025-02-20 13:30:00'),
('cust-079', '090-2000-0079', 'å†…å±± ç¾Žé¦™', 'uchiyama.mika@email.jp', '2025-02-25 20:00:00'),
('cust-080', '090-2000-0080', 'æ—©å· èª ', 'hayakawa.makoto@email.jp', '2025-03-01 16:15:00'),
('cust-081', '090-2000-0081', 'åœŸäº• å½©ä¹ƒ', 'doi.ayano@email.jp', '2025-03-05 12:30:00'),
('cust-082', '090-2000-0082', 'å €ç”° æµ©äºŒ', 'hotta.koji@email.jp', '2025-03-10 18:45:00'),
('cust-083', '090-2000-0083', 'çŸ¢é‡Ž å„ªå­', 'yano.yuko@email.jp', '2025-03-15 15:00:00'),
('cust-084', '090-2000-0084', 'æµœç”° å¤ªéƒŽ', 'hamada.taro@email.jp', '2025-03-20 11:15:00'),
('cust-085', '090-2000-0085', 'æ˜Ÿé‡Ž çœŸç”±', 'hoshino.mayu@email.jp', '2025-03-25 17:30:00'),
('cust-086', '090-2000-0086', 'æ‘ç”° å¥å¤ª', 'murata.kenta@email.jp', '2025-04-01 13:45:00'),
('cust-087', '090-2000-0087', 'å®®å´Ž æ„›', 'miyazaki.ai@email.jp', '2025-04-05 20:15:00'),
('cust-088', '090-2000-0088', 'é–¢å£ ä¸€éƒŽ', 'sekiguchi.ichiro@email.jp', '2025-04-10 16:30:00'),
('cust-089', '090-2000-0089', 'ä¸¸å±± ç¾Žå’²', 'maruyama.misaki@email.jp', '2025-04-15 12:45:00'),
('cust-090', '090-2000-0090', 'å¹³ç”° é”ä¹Ÿ', 'hirata.tatsuya@email.jp', '2025-04-20 19:00:00'),
('cust-091', '090-2000-0091', 'å¥¥æ‘ æµ', 'okumura.megumi@email.jp', '2025-04-25 15:15:00'),
('cust-092', '090-2000-0092', 'å¤å· æ‹“çœŸ', 'furukawa.takuma@email.jp', '2025-05-01 11:30:00'),
('cust-093', '090-2000-0093', 'é£¯ç”° ç”±ç¾Žå­', 'iida.yumiko@email.jp', '2025-05-05 18:00:00'),
('cust-094', '090-2000-0094', 'æ¾äº• å¥å¸', 'matsui.kenji@email.jp', '2025-05-10 14:15:00'),
('cust-095', '090-2000-0095', 'æ°´é‡Ž ç¾Žé¦™', 'mizuno.mika@email.jp', '2025-05-15 10:45:00'),
('cust-096', '090-2000-0096', 'è’æœ¨ èª ä¸€', 'araki.seiichi@email.jp', '2025-05-20 17:00:00'),
('cust-097', '090-2000-0097', 'å¤§ä¹…ä¿ å½©', 'okubo.aya@email.jp', '2025-05-25 13:30:00'),
('cust-098', '090-2000-0098', 'é‡Žç”° å¤§åœ°', 'noda.daichi@email.jp', '2025-06-01 20:00:00'),
('cust-099', '090-2000-0099', 'é ˆè—¤ éº»è¡£', 'sudo.mai@email.jp', '2025-06-05 16:15:00'),
('cust-100', '090-2000-0100', 'å®®ç”° è‰¯å¹³', 'miyata.ryohei@email.jp', '2025-06-10 12:30:00');

-- ============================================
-- 6. BRANCH CUSTOMERS (relationships)
-- ============================================
INSERT INTO branch_customers (id, global_customer_id, branch_code, visit_count, last_visit, is_vip, notes) VALUES
-- JIAN branch (30 customers)
('bc-001', 'cust-001', 'hirama', 15, '2025-12-20 19:30:00', true, 'å¸¸é€£æ§˜ã€‚ã„ã¤ã‚‚ã‚¿ãƒ³å¡©ã‚’æ³¨æ–‡ã•ã‚Œã‚‹'),
('bc-002', 'cust-002', 'hirama', 8, '2025-11-15 18:00:00', false, 'ãŠå­æ§˜é€£ã‚Œã§æ¥åº—ã€‚å€‹å®¤å¸Œæœ›'),
('bc-003', 'cust-003', 'hirama', 3, '2025-10-01 20:00:00', false, 'åˆå›žå‰²å¼•åˆ©ç”¨'),
('bc-004', 'cust-004', 'hirama', 22, '2026-01-10 19:00:00', true, 'VIPã€‚ç‰¹åˆ¥ãªãŠç¥ã„ã§ã‚ˆãåˆ©ç”¨'),
('bc-005', 'cust-005', 'hirama', 1, '2025-08-05 18:30:00', false, 'ä¸€åº¦ãã‚Šã®æ¥åº—'),
('bc-006', 'cust-006', 'hirama', 12, '2025-12-01 20:30:00', true, 'è‚‰ã®ç„¼ãåŠ æ¸›ã«ã“ã ã‚ã‚‹ã€‚ãƒ¬ã‚¢å¸Œæœ›'),
('bc-007', 'cust-007', 'hirama', 5, '2025-09-20 19:00:00', false, 'ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼ï¼ˆç”²æ®»é¡žï¼‰ã‚ã‚Š'),
('bc-008', 'cust-008', 'hirama', 18, '2026-01-25 18:30:00', true, 'ãƒ¯ã‚¤ãƒ³å¥½ãã€‚è¨˜å¿µæ—¥åˆ©ç”¨å¤šã—'),
('bc-009', 'cust-009', 'hirama', 2, '2025-07-10 19:30:00', false, 'ã‚¯ãƒ¼ãƒãƒ³åˆ©ç”¨ã®ã¿'),
('bc-010', 'cust-010', 'hirama', 10, '2025-11-30 20:00:00', true, 'å¤§äººæ•°å®´ä¼šã§ã‚ˆãäºˆç´„'),
('bc-011', 'cust-011', 'hirama', 1, '2025-06-01 18:00:00', false, 'æ–™ç†ã®æä¾›ãŒé…ã„ã¨ã‚¯ãƒ¬ãƒ¼ãƒ '),
('bc-012', 'cust-012', 'hirama', 7, '2025-10-15 19:00:00', false, 'é™ã‹ãªå¸­å¸Œæœ›ã€‚ãƒ‡ãƒ¼ãƒˆåˆ©ç”¨'),
('bc-013', 'cust-013', 'hirama', 4, '2025-09-05 18:30:00', false, 'è¾›ã„ã‚‚ã®å¥½ã'),
('bc-014', 'cust-014', 'hirama', 20, '2026-02-01 19:30:00', true, 'ä¼šç¤¾ã®æŽ¥å¾…ã§ã‚ˆãåˆ©ç”¨ã€‚ä¸Šè³ªãªè‚‰å¸Œæœ›'),
('bc-015', 'cust-015', 'hirama', 3, '2025-08-20 20:00:00', false, 'ãƒ™ã‚¸ã‚¿ãƒªã‚¢ãƒ³å‘ã‘ãƒ¡ãƒ‹ãƒ¥ãƒ¼å¸Œæœ›'),
('bc-016', 'cust-016', 'hirama', 1, '2025-07-15 18:00:00', false, 'äºˆç´„æ™‚é–“ã«é…åˆ»ã€‚30åˆ†å¾…ã¡'),
('bc-017', 'cust-017', 'hirama', 9, '2025-11-10 19:00:00', false, 'å†™çœŸæ’®å½±å¥½ãã€‚ã‚¤ãƒ³ã‚¹ã‚¿æŠ•ç¨¿'),
('bc-018', 'cust-018', 'hirama', 25, '2026-01-20 20:30:00', true, 'å‰µæ¥­æ™‚ã‹ã‚‰ã®å¸¸é€£æ§˜ã€‚æœ€é«˜ç´šã‚³ãƒ¼ã‚¹'),
('bc-019', 'cust-019', 'hirama', 2, '2025-08-01 18:30:00', false, 'ä¾¡æ ¼ã«ã¤ã„ã¦è³ªå•å¤šã„'),
('bc-020', 'cust-020', 'hirama', 6, '2025-10-05 19:00:00', false, 'ç¦ç…™å¸­å¸Œæœ›ã€‚åŒ‚ã„ã«æ•æ„Ÿ'),
('bc-021', 'cust-021', 'hirama', 1, '2025-06-20 18:00:00', false, 'ã‚µãƒ¼ãƒ“ã‚¹ã«ä¸æº€ã€‚äºŒåº¦ã¨æ¥ãªã„ã¨ç™ºè¨€'),
('bc-022', 'cust-022', 'hirama', 11, '2025-12-10 19:30:00', true, 'èª•ç”Ÿæ—¥ã‚±ãƒ¼ã‚­æŒã¡è¾¼ã¿è¨±å¯æ¸ˆ'),
('bc-023', 'cust-023', 'hirama', 4, '2025-09-15 20:00:00', false, 'é£²ã¿æ”¾é¡Œãƒ—ãƒ©ãƒ³å¥½ã'),
('bc-024', 'cust-024', 'hirama', 8, '2025-11-01 18:30:00', false, 'å­ä¾›ç”¨ãƒ¡ãƒ‹ãƒ¥ãƒ¼æ³¨æ–‡'),
('bc-025', 'cust-025', 'hirama', 2, '2025-07-25 19:00:00', false, 'å‰å›žã®ä¼šè¨ˆãƒŸã‚¹ã§è¿”é‡‘å¯¾å¿œæ¸ˆ'),
('bc-026', 'cust-026', 'hirama', 15, '2025-12-25 20:00:00', true, 'ã‚¯ãƒªã‚¹ãƒžã‚¹æ¯Žå¹´äºˆç´„ã€‚ãƒ­ãƒžãƒ³ãƒãƒƒã‚¯ãªå¸­å¸Œæœ›'),
('bc-027', 'cust-027', 'hirama', 1, '2025-06-10 18:00:00', false, 'ãƒ¡ãƒ‹ãƒ¥ãƒ¼ãŒåˆ†ã‹ã‚Šã«ãã„ã¨ãƒ•ã‚£ãƒ¼ãƒ‰ãƒãƒƒã‚¯'),
('bc-028', 'cust-028', 'hirama', 7, '2025-10-20 19:30:00', false, 'ãƒ›ãƒ«ãƒ¢ãƒ³å°‚é–€ã€‚é€šãªæ³¨æ–‡'),
('bc-029', 'cust-029', 'hirama', 3, '2025-08-15 18:30:00', false, 'æ—©ã‚ã®æ™‚é–“å¸¯å¸Œæœ›ã€‚é«˜é½¢è€…åŒä¼´'),
('bc-030', 'cust-030', 'hirama', 19, '2026-01-15 20:00:00', true, 'ãƒ¯ã‚¤ãƒ³ä¼šå¹¹äº‹ã€‚å¤§å£æ³¨æ–‡'),
-- Shinjuku branch (10 customers)
('bc-031', 'cust-002', 'shinjuku', 5, '2025-11-20 19:00:00', false, 'å­ä¾›é€£ã‚Œã§è¨ªå•'),
('bc-032', 'cust-012', 'shinjuku', 8, '2025-12-15 18:30:00', true, 'ã‚«ãƒƒãƒ—ãƒ«åˆ©ç”¨å¤šã„'),
('bc-033', 'cust-017', 'shinjuku', 12, '2026-01-05 20:00:00', true, 'SNSæŠ•ç¨¿æœ‰åäºº'),
('bc-034', 'cust-039', 'shinjuku', 6, '2025-10-30 19:30:00', false, 'å¥³å­ä¼šã‚°ãƒ«ãƒ¼ãƒ—'),
('bc-035', 'cust-044', 'shinjuku', 15, '2026-01-20 18:00:00', true, 'æ³•äººæ§˜åˆ©ç”¨'),
('bc-036', 'cust-050', 'shinjuku', 3, '2025-09-10 19:00:00', false, 'åˆæ¥åº—'),
('bc-037', 'cust-055', 'shinjuku', 7, '2025-11-25 20:30:00', false, 'ãƒ‰ãƒªãƒ³ã‚¯å¤šã‚'),
('bc-038', 'cust-060', 'shinjuku', 10, '2025-12-20 19:00:00', true, 'é‡‘æ›œå¤œå¸¸é€£'),
('bc-039', 'cust-065', 'shinjuku', 2, '2025-08-15 18:30:00', false, 'å¶ç„¶ã®æ¥åº—'),
('bc-040', 'cust-070', 'shinjuku', 18, '2026-01-25 20:00:00', true, 'VIPå€‹å®¤å¸¸é€£'),
-- Yaesu branch (7 customers - business focus)
('bc-041', 'cust-003', 'yaesu', 8, '2025-12-01 12:30:00', true, 'ãƒ©ãƒ³ãƒå¸¸é€£'),
('bc-042', 'cust-007', 'yaesu', 4, '2025-10-20 18:00:00', false, 'ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼å¯¾å¿œå¿…è¦'),
('bc-043', 'cust-014', 'yaesu', 12, '2025-12-15 19:00:00', true, 'æŽ¥å¾…åˆ©ç”¨å¤šã„'),
('bc-044', 'cust-036', 'yaesu', 6, '2025-11-10 19:30:00', false, 'å¤–å›½äººã‚²ã‚¹ãƒˆåŒä¼´'),
('bc-045', 'cust-048', 'yaesu', 3, '2025-09-25 12:00:00', false, 'ãƒ©ãƒ³ãƒåˆåˆ©ç”¨'),
('bc-046', 'cust-062', 'yaesu', 9, '2025-12-20 18:30:00', true, 'ãƒ“ã‚¸ãƒã‚¹å¸¸é€£'),
('bc-047', 'cust-075', 'yaesu', 2, '2025-08-30 12:30:00', false, 'ä¸€å›žé™ã‚Š'),
-- Shinagawa branch (6 customers)
('bc-048', 'cust-032', 'shinagawa', 7, '2025-11-15 18:00:00', false, 'ã‚¹ãƒãƒ¼ãƒ„é¸æ‰‹'),
('bc-049', 'cust-037', 'shinagawa', 5, '2025-10-25 17:30:00', false, 'ãƒ•ã‚¡ãƒŸãƒªãƒ¼'),
('bc-050', 'cust-045', 'shinagawa', 10, '2025-12-10 19:00:00', true, 'è¨˜å¿µæ—¥åˆ©ç”¨'),
('bc-051', 'cust-058', 'shinagawa', 3, '2025-09-05 18:30:00', false, 'åˆæ¥åº—'),
('bc-052', 'cust-072', 'shinagawa', 8, '2025-11-30 20:00:00', true, 'å¸¸é€£æ§˜'),
('bc-053', 'cust-085', 'shinagawa', 2, '2025-08-20 19:00:00', false, 'å¶ç„¶ã®æ¥åº—'),
-- Yokohama branch (8 customers)
('bc-054', 'cust-040', 'yokohama', 12, '2025-12-15 19:00:00', true, 'å¹´æœ«å¹´å§‹å¸¸é€£'),
('bc-055', 'cust-050', 'yokohama', 8, '2025-11-20 18:30:00', true, 'VIPæ§˜'),
('bc-056', 'cust-056', 'yokohama', 5, '2025-10-10 19:30:00', false, 'å¤§å®¶æ—'),
('bc-057', 'cust-066', 'yokohama', 10, '2026-01-05 18:00:00', true, 'æ–°å¹´ä¼šå¹¹äº‹'),
('bc-058', 'cust-074', 'yokohama', 4, '2025-09-20 20:00:00', false, 'ã‚¹ãƒãƒ¼ãƒ„è¦³æˆ¦'),
('bc-059', 'cust-080', 'yokohama', 6, '2025-11-05 19:00:00', false, 'ã‚«ãƒƒãƒ—ãƒ«'),
('bc-060', 'cust-090', 'yokohama', 3, '2025-10-25 18:30:00', false, 'åˆæ¥åº—'),
('bc-061', 'cust-095', 'yokohama', 7, '2025-12-01 20:00:00', false, 'ãƒªãƒ”ãƒ¼ã‚¿ãƒ¼');

-- ============================================
-- 7. CUSTOMER PREFERENCES
-- ============================================
INSERT INTO customer_preferences (id, branch_customer_id, preference, category, note, confidence, source) VALUES
('pref-001', 'bc-001', 'åŽšåˆ‡ã‚Šã‚¿ãƒ³å¡©', 'meat', 'æ¯Žå›žå¿…ãšæ³¨æ–‡', 1.0, 'manual'),
('pref-002', 'bc-001', 'çª“éš›å¸­å¸Œæœ›', 'seating', 'æ™¯è‰²ã‚’æ¥½ã—ã¿ãŸã„', 1.0, 'booking'),
('pref-003', 'bc-002', 'å€‹å®¤å¸Œæœ›', 'seating', 'å­ä¾›ãŒé¨’ããŸã‚', 1.0, 'booking'),
('pref-004', 'bc-002', 'å­ä¾›ç”¨æ¤…å­å¿…è¦', 'facility', '3æ­³ã®ãŠå­æ§˜', 1.0, 'manual'),
('pref-005', 'bc-004', 'æœ€é«˜ç´šå’Œç‰›ã‚³ãƒ¼ã‚¹', 'meat', 'æŽ¥å¾…ãƒ»è¨˜å¿µæ—¥ç”¨', 1.0, 'manual'),
('pref-006', 'bc-004', 'ã‚·ãƒ£ãƒ³ãƒ‘ãƒ³å¥½ã', 'drinks', 'ãŠç¥ã„æ™‚ã«æ³¨æ–‡', 0.9, 'chat'),
('pref-007', 'bc-006', 'ãƒ¬ã‚¢ç„¼ã', 'cooking', 'ç”Ÿã«è¿‘ã„çŠ¶æ…‹ãŒå¥½ã', 1.0, 'manual'),
('pref-008', 'bc-006', 'ãƒãƒ©ãƒŸ', 'meat', 'è„‚èº«å°‘ãªã‚ãŒå¥½ã¿', 1.0, 'chat'),
('pref-009', 'bc-007', 'ç”²æ®»é¡žã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼', 'allergy', 'ã‚¨ãƒ“ãƒ»ã‚«ãƒ‹NG', 1.0, 'manual'),
('pref-010', 'bc-008', 'èµ¤ãƒ¯ã‚¤ãƒ³å¥½ã', 'drinks', 'ãƒœãƒ«ãƒ‰ãƒ¼ç³»å¸Œæœ›', 1.0, 'manual'),
('pref-011', 'bc-008', 'è¨˜å¿µæ—¥åˆ©ç”¨', 'occasion', 'å¹´ã«3å›žç¨‹åº¦', 0.85, 'chat'),
('pref-012', 'bc-010', 'å¤§äººæ•°å®´ä¼š', 'occasion', '10åä»¥ä¸Šã§ã‚ˆãäºˆç´„', 1.0, 'booking'),
('pref-013', 'bc-010', 'é£²ã¿æ”¾é¡Œãƒ—ãƒ©ãƒ³', 'drinks', 'å¿…ãšåˆ©ç”¨', 1.0, 'manual'),
('pref-014', 'bc-012', 'é™ã‹ãªå¸­', 'seating', 'ã‚«ãƒƒãƒ—ãƒ«ã§ãƒ‡ãƒ¼ãƒˆ', 1.0, 'booking'),
('pref-015', 'bc-013', 'ã‚­ãƒ ãƒè¿½åŠ ', 'side', 'è¾›ã„ã‚‚ã®å¥½ã', 0.8, 'chat'),
('pref-016', 'bc-014', 'æŽ¥å¾…åˆ©ç”¨', 'occasion', 'ä¼šç¤¾çµŒè²»', 1.0, 'manual'),
('pref-017', 'bc-014', 'ä¸Šè³ªãªéƒ¨ä½ã®ã¿', 'meat', 'äºˆç®—ã¯æ°—ã«ã—ãªã„', 1.0, 'manual'),
('pref-018', 'bc-017', 'å†™çœŸæ’®å½±OK', 'other', 'ã‚¤ãƒ³ã‚¹ã‚¿æŠ•ç¨¿', 0.9, 'chat'),
('pref-019', 'bc-018', 'å‰µæ¥­æ™‚ã‹ã‚‰å¸¸é€£', 'loyalty', 'ç‰¹åˆ¥å¯¾å¿œå¿…è¦', 1.0, 'manual'),
('pref-020', 'bc-018', 'VIPãƒ«ãƒ¼ãƒ ', 'seating', 'ãƒ—ãƒ©ã‚¤ãƒã‚·ãƒ¼é‡è¦–', 1.0, 'booking'),
('pref-021', 'bc-020', 'ç¦ç…™å¸­', 'seating', 'åŒ‚ã„ã«æ•æ„Ÿ', 1.0, 'booking'),
('pref-022', 'bc-022', 'æŒã¡è¾¼ã¿ã‚±ãƒ¼ã‚­OK', 'other', 'èª•ç”Ÿæ—¥å¯¾å¿œæ¸ˆ', 1.0, 'manual'),
('pref-023', 'bc-024', 'å­ä¾›ãƒ¡ãƒ‹ãƒ¥ãƒ¼', 'kids', 'ãŠå­æ§˜ãƒ©ãƒ³ãƒå¸Œæœ›', 1.0, 'manual'),
('pref-024', 'bc-026', 'ãƒ­ãƒžãƒ³ãƒãƒƒã‚¯ãªå¸­', 'seating', 'ã‚«ãƒƒãƒ—ãƒ«å¸­', 1.0, 'booking'),
('pref-025', 'bc-026', 'ãƒ‡ã‚¶ãƒ¼ãƒˆç››ã‚Šåˆã‚ã›', 'dessert', 'è¨˜å¿µæ—¥ç”¨', 0.9, 'chat'),
('pref-026', 'bc-028', 'ãƒ›ãƒ«ãƒ¢ãƒ³ç³»', 'meat', 'é€šãªã‚ªãƒ¼ãƒ€ãƒ¼', 0.85, 'chat'),
('pref-027', 'bc-030', 'ãƒ¯ã‚¤ãƒ³ä¼š', 'occasion', 'æœˆ1å›žé–‹å‚¬', 1.0, 'manual'),
('pref-028', 'bc-030', 'å€‹å®¤12å', 'seating', 'ãƒ¯ã‚¤ãƒ³æŒã¡è¾¼ã¿å¯', 1.0, 'booking'),
('pref-029', 'bc-048', 'ã‚¿ãƒ³ãƒ‘ã‚¯è³ªé‡è¦–', 'diet', 'ã‚¢ã‚¹ãƒªãƒ¼ãƒˆé£Ÿ', 1.0, 'manual'),
('pref-030', 'bc-048', 'ã‚µãƒ©ãƒ€å¤§ç››ã‚Š', 'side', 'é‡Žèœå¤šã‚', 0.9, 'chat');

-- ============================================
-- 8. BOOKINGS (25 sample bookings)
-- ============================================
INSERT INTO bookings (id, branch_code, branch_customer_id, guest_name, guest_phone, guest_email, date, time, guests, status, note, source) VALUES
('bk-001', 'hirama', 'bc-001', 'ä½ã€…æœ¨ ç¾Žå’²', '090-2000-0001', 'sasaki.misaki@email.jp', '2025-06-20', '19:00', 3, 'confirmed', 'åŽšåˆ‡ã‚Šã‚¿ãƒ³å¡©å¸Œæœ›', 'web'),
('bk-002', 'hirama', 'bc-004', 'äº•ä¸Š å¤§è¼”', '090-2000-0004', 'inoue.daisuke@email.jp', '2025-06-20', '19:30', 6, 'confirmed', 'æŽ¥å¾…åˆ©ç”¨ã€‚VIPå¯¾å¿œãŠé¡˜ã„ã—ã¾ã™ã€‚ã‚·ãƒ£ãƒ³ãƒ‘ãƒ³ç”¨æ„', 'phone'),
('bk-003', 'hirama', 'bc-006', 'æ¸…æ°´ ç¿”å¤ª', '090-2000-0006', 'shimizu.shota@email.jp', '2025-06-20', '18:30', 2, 'confirmed', 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼å¸­å¸Œæœ›', 'web'),
('bk-004', 'hirama', 'bc-008', 'æ£®ç”° ä¸€éƒŽ', '090-2000-0008', 'morita.ichiro@email.jp', '2025-06-21', '19:00', 4, 'confirmed', 'è¨˜å¿µæ—¥ã‚±ãƒ¼ã‚­æŒã¡è¾¼ã¿ã€‚èµ¤ãƒ¯ã‚¤ãƒ³æº–å‚™', 'web'),
('bk-005', 'hirama', 'bc-010', 'è—¤ç”° å¤ªéƒŽ', '090-2000-0010', 'fujita.taro@email.jp', '2025-06-21', '18:00', 10, 'confirmed', 'å®´ä¼šäºˆç´„ã€‚é£²ã¿æ”¾é¡Œãƒ—ãƒ©ãƒ³', 'phone'),
('bk-006', 'hirama', 'bc-014', 'é•·è°·å· èª ', '090-2000-0014', 'hasegawa.makoto@email.jp', '2025-06-22', '19:30', 5, 'confirmed', 'ä¼šç¤¾æŽ¥å¾…ã€‚ä¸Šè³ªãªéƒ¨ä½ã§ã‚³ãƒ¼ã‚¹', 'web'),
('bk-007', 'hirama', 'bc-018', 'æ‘ä¸Š æµ©äºŒ', '090-2000-0018', 'murakami.koji@email.jp', '2025-06-22', '19:00', 2, 'confirmed', 'å¸¸é€£æ§˜ã€‚ã„ã¤ã‚‚ã®ã‚³ãƒ¼ã‚¹', 'phone'),
('bk-008', 'hirama', 'bc-022', 'çŸ³ç”° é™½å­', '090-2000-0022', 'ishida.yoko@email.jp', '2025-06-23', '18:00', 4, 'pending', 'èª•ç”Ÿæ—¥ã‚µãƒ—ãƒ©ã‚¤ã‚ºã€‚ã‚±ãƒ¼ã‚­æŒã¡è¾¼ã¿OKæ¸ˆ', 'web'),
('bk-009', 'hirama', 'bc-026', 'ä¸­å±± æ„›', '090-2000-0026', 'nakayama.ai@email.jp', '2025-06-23', '19:30', 2, 'confirmed', 'ãƒ‡ãƒ¼ãƒˆåˆ©ç”¨ã€‚ãƒ­ãƒžãƒ³ãƒãƒƒã‚¯ãªå¸­ã§', 'chat'),
('bk-010', 'hirama', 'bc-030', 'è¥¿æ‘ å¥', '090-2000-0030', 'nishimura.ken@email.jp', '2025-06-24', '19:00', 12, 'confirmed', 'ãƒ¯ã‚¤ãƒ³ä¼šã€‚ãƒ¯ã‚¤ãƒ³6æœ¬æŒã¡è¾¼ã¿', 'phone'),
('bk-011', 'shinjuku', 'bc-031', 'æœ¨æ‘ å¥å¤ª', '090-2000-0002', 'kimura.kenta@email.jp', '2025-06-20', '18:30', 4, 'confirmed', 'å­ä¾›é€£ã‚Œã€‚å€‹å®¤å¸Œæœ›ã€‚å­ä¾›æ¤…å­å¿…è¦', 'web'),
('bk-012', 'shinjuku', 'bc-032', 'å¾Œè—¤ åº·å¹³', '090-2000-0012', 'goto.kohei@email.jp', '2025-06-20', '19:00', 2, 'confirmed', 'ãƒ‡ãƒ¼ãƒˆã€‚çª“éš›å¸­å¸Œæœ›', 'web'),
('bk-013', 'shinjuku', 'bc-033', 'è—¤äº• ç¾Žç©‚', '090-2000-0017', 'fujii.miho@email.jp', '2025-06-21', '20:00', 4, 'confirmed', 'å†™çœŸæ’®å½±OKç¢ºèªæ¸ˆ', 'web'),
('bk-014', 'shinjuku', 'bc-034', 'å¥³å­ä¼šã‚°ãƒ«ãƒ¼ãƒ—', '090-2000-0039', 'group@email.jp', '2025-06-21', '19:00', 6, 'confirmed', 'å¥³å­ä¼šãƒ—ãƒ©ãƒ³ã€‚ã‚µãƒ©ãƒ€å¤šã‚', 'phone'),
('bk-015', 'shinjuku', 'bc-035', 'æ³•äººæ§˜', '090-2000-0044', 'corp@email.jp', '2025-06-22', '18:30', 14, 'confirmed', 'æ³•äººå®´ä¼šã€‚é ˜åŽæ›¸å¿…è¦', 'phone'),
('bk-016', 'yaesu', 'bc-041', 'å±±æœ¬ çœŸç”±ç¾Ž', '090-2000-0003', 'yamamoto.mayumi@email.jp', '2025-06-20', '12:00', 4, 'confirmed', 'ãƒ©ãƒ³ãƒå•†è«‡', 'web'),
('bk-017', 'yaesu', 'bc-042', 'æ¾æœ¬ æ„›', '090-2000-0007', 'matsumoto.ai@email.jp', '2025-06-20', '19:00', 2, 'confirmed', 'ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼æ³¨æ„ã€‚ç”²æ®»é¡žNG', 'web'),
('bk-018', 'yaesu', 'bc-044', 'å¤–å›½äººã‚²ã‚¹ãƒˆæ§˜', '090-2000-0036', 'foreigner@email.jp', '2025-06-21', '19:30', 6, 'pending', 'è‹±èªžå¯¾å¿œå¿…è¦ã€‚è‹±èªžãƒ¡ãƒ‹ãƒ¥ãƒ¼', 'phone'),
('bk-019', 'shinagawa', 'bc-048', 'ã‚¢ã‚¹ãƒªãƒ¼ãƒˆæ§˜', '090-2000-0032', 'athlete@email.jp', '2025-06-20', '18:00', 3, 'confirmed', 'é«˜ã‚¿ãƒ³ãƒ‘ã‚¯é£Ÿã€‚ã‚µãƒ©ãƒ€å¤§ç››ã‚Š', 'web'),
('bk-020', 'shinagawa', 'bc-049', 'ãƒ•ã‚¡ãƒŸãƒªãƒ¼æ§˜', '090-2000-0037', 'family@email.jp', '2025-06-21', '17:30', 4, 'confirmed', 'èµ¤ã¡ã‚ƒã‚“é€£ã‚Œã€‚ãƒ™ãƒ“ãƒ¼ã‚«ãƒ¼ã‚ã‚Š', 'phone'),
('bk-021', 'yokohama', 'bc-054', 'å¹´æœ«å¸¸é€£æ§˜', '090-2000-0040', 'regular@email.jp', '2025-06-20', '19:00', 4, 'confirmed', 'çª“éš›ã§æµ·ã‚’è¦‹ãªãŒã‚‰', 'web'),
('bk-022', 'yokohama', 'bc-055', 'VIPæ§˜', '090-2000-0050', 'vip@email.jp', '2025-06-21', '19:30', 8, 'confirmed', 'ç‰¹ä¸Šç››ã‚Šåˆã‚ã›å¸Œæœ›ã€‚VIPå¯¾å¿œ', 'phone'),
('bk-023', 'hirama', NULL, 'å±±ç”° å¤ªéƒŽ', '090-9999-0001', NULL, '2025-06-20', '20:00', 4, 'confirmed', 'æ–°è¦ã®ãŠå®¢æ§˜', 'walk_in'),
('bk-024', 'hirama', NULL, 'ç”°ä¸­ èŠ±å­', '090-9999-0002', NULL, '2025-06-21', '18:30', 2, 'cancelled', 'ã‚­ãƒ£ãƒ³ã‚»ãƒ«', 'web'),
('bk-025', 'shinjuku', NULL, 'æ–°è¦æ§˜', '090-9999-0003', NULL, '2025-06-22', '19:00', 3, 'pending', 'ç¢ºèªå¾…ã¡', 'web');

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
