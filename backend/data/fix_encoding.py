"""
Fix encoding issues in data files.
Run: cd backend && python -m data.fix_encoding
"""
import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

# Correct Japanese data for staff
STAFF_DATA = [
    # hirama (10 staff)
    ("staff-001", "S001", "hirama", "山田 太郎", "ヤマダ タロウ", "090-1111-0001", "yamada@yakiniku.io", "admin", "111111", "true", "2020-04-01"),
    ("staff-002", "S002", "hirama", "佐藤 花子", "サトウ ハナコ", "090-1111-0002", "sato@yakiniku.io", "admin", "222222", "true", "2020-04-01"),
    ("staff-003", "S003", "hirama", "田中 一郎", "タナカ イチロウ", "090-1111-0003", "tanaka@yakiniku.io", "manager", "333333", "true", "2021-06-15"),
    ("staff-004", "S004", "hirama", "鈴木 美咲", "スズキ ミサキ", "090-1111-0004", "suzuki@yakiniku.io", "cashier", "444444", "true", "2022-01-10"),
    ("staff-005", "S005", "hirama", "高橋 健太", "タカハシ ケンタ", "090-1111-0005", "takahashi@yakiniku.io", "waiter", "555555", "true", "2022-03-20"),
    ("staff-006", "S006", "hirama", "伊藤 さくら", "イトウ サクラ", "090-1111-0006", "ito@yakiniku.io", "waiter", "666666", "true", "2023-04-01"),
    ("staff-007", "S007", "hirama", "渡辺 大輔", "ワタナベ ダイスケ", "090-1111-0007", "watanabe@yakiniku.io", "kitchen", "777777", "true", "2021-08-01"),
    ("staff-008", "S008", "hirama", "中村 真由美", "ナカムラ マユミ", "090-1111-0008", "nakamura@yakiniku.io", "kitchen", "888888", "true", "2022-07-15"),
    ("staff-009", "S009", "hirama", "小林 翔太", "コバヤシ ショウタ", "090-1111-0009", "kobayashi@yakiniku.io", "receptionist", "999999", "true", "2023-09-01"),
    ("staff-010", "S010", "hirama", "加藤 愛", "カトウ アイ", "090-1111-0010", "kato@yakiniku.io", "waiter", "000000", "true", "2024-01-15"),
    # shinjuku (7 staff)
    ("staff-011", "S011", "shinjuku", "松本 大介", "マツモト ダイスケ", "090-2222-0001", "matsumoto@yakiniku.io", "admin", "111112", "true", "2022-03-15"),
    ("staff-012", "S012", "shinjuku", "井上 明美", "イノウエ アケミ", "090-2222-0002", "inoue@yakiniku.io", "manager", "222223", "true", "2022-04-01"),
    ("staff-013", "S013", "shinjuku", "木村 誠", "キムラ マコト", "090-2222-0003", "kimura@yakiniku.io", "cashier", "333334", "true", "2022-06-01"),
    ("staff-014", "S014", "shinjuku", "林 優子", "ハヤシ ユウコ", "090-2222-0004", "hayashi@yakiniku.io", "waiter", "444445", "true", "2022-08-15"),
    ("staff-015", "S015", "shinjuku", "清水 拓也", "シミズ タクヤ", "090-2222-0005", "shimizu@yakiniku.io", "waiter", "555556", "true", "2023-01-10"),
    ("staff-016", "S016", "shinjuku", "山口 彩香", "ヤマグチ アヤカ", "090-2222-0006", "yamaguchi@yakiniku.io", "kitchen", "666667", "true", "2022-05-01"),
    ("staff-017", "S017", "shinjuku", "森 健二", "モリ ケンジ", "090-2222-0007", "mori@yakiniku.io", "kitchen", "777778", "true", "2023-03-01"),
    # yaesu (5 staff)
    ("staff-018", "S018", "yaesu", "池田 直樹", "イケダ ナオキ", "090-3333-0001", "ikeda@yakiniku.io", "admin", "111113", "true", "2023-06-01"),
    ("staff-019", "S019", "yaesu", "橋本 美穂", "ハシモト ミホ", "090-3333-0002", "hashimoto@yakiniku.io", "manager", "222224", "true", "2023-06-15"),
    ("staff-020", "S020", "yaesu", "阿部 翔", "アベ ショウ", "090-3333-0003", "abe@yakiniku.io", "cashier", "333335", "true", "2023-07-01"),
    ("staff-021", "S021", "yaesu", "石川 絵理", "イシカワ エリ", "090-3333-0004", "ishikawa@yakiniku.io", "waiter", "444446", "true", "2023-08-01"),
    ("staff-022", "S022", "yaesu", "前田 龍一", "マエダ リュウイチ", "090-3333-0005", "maeda@yakiniku.io", "kitchen", "555557", "true", "2023-09-01"),
    # shinagawa (5 staff)
    ("staff-023", "S023", "shinagawa", "藤原 剛", "フジワラ ツヨシ", "090-4444-0001", "fujiwara@yakiniku.io", "admin", "111114", "true", "2023-09-01"),
    ("staff-024", "S024", "shinagawa", "岡田 さやか", "オカダ サヤカ", "090-4444-0002", "okada@yakiniku.io", "manager", "222225", "true", "2023-09-15"),
    ("staff-025", "S025", "shinagawa", "後藤 亮太", "ゴトウ リョウタ", "090-4444-0003", "goto@yakiniku.io", "cashier", "333336", "true", "2023-10-01"),
    ("staff-026", "S026", "shinagawa", "遠藤 真理", "エンドウ マリ", "090-4444-0004", "endo@yakiniku.io", "waiter", "444447", "true", "2023-11-01"),
    ("staff-027", "S027", "shinagawa", "青木 大地", "アオキ ダイチ", "090-4444-0005", "aoki@yakiniku.io", "kitchen", "555558", "true", "2023-12-01"),
    # yokohama (7 staff)
    ("staff-028", "S028", "yokohama", "坂本 隼人", "サカモト ハヤト", "090-5555-0001", "sakamoto@yakiniku.io", "admin", "111115", "true", "2024-01-15"),
    ("staff-029", "S029", "yokohama", "吉田 麻衣", "ヨシダ マイ", "090-5555-0002", "yoshida@yakiniku.io", "manager", "222226", "true", "2024-01-20"),
    ("staff-030", "S030", "yokohama", "原田 悠斗", "ハラダ ユウト", "090-5555-0003", "harada@yakiniku.io", "cashier", "333337", "true", "2024-02-01"),
    ("staff-031", "S031", "yokohama", "千葉 紗音", "チバ サオン", "090-5555-0004", "chiba@yakiniku.io", "waiter", "444448", "true", "2024-02-15"),
    ("staff-032", "S032", "yokohama", "野村 蓮", "ノムラ レン", "090-5555-0005", "nomura@yakiniku.io", "waiter", "555559", "true", "2024-03-01"),
    ("staff-033", "S033", "yokohama", "菅原 桃子", "スガワラ モモコ", "090-5555-0006", "sugawara@yakiniku.io", "kitchen", "666668", "true", "2024-03-15"),
    ("staff-034", "S034", "yokohama", "新井 康介", "アライ コウスケ", "090-5555-0007", "arai@yakiniku.io", "kitchen", "777779", "true", "2024-04-01"),
]

STAFF_HEADERS = ["id", "employee_id", "branch_code", "name", "name_kana", "phone", "email", "role", "pin_code", "is_active", "hire_date"]

# Tables data
TABLES_DATA = [
    # hirama (9 tables)
    ("table-hirama-01", "hirama", "A1", "テーブルA1", 4, "table", "floor", "true", "true", "窓際"),
    ("table-hirama-02", "hirama", "A2", "テーブルA2", 4, "table", "floor", "false", "true", ""),
    ("table-hirama-03", "hirama", "A3", "テーブルA3", 4, "table", "floor", "false", "true", ""),
    ("table-hirama-04", "hirama", "A4", "テーブルA4", 6, "table", "floor", "false", "true", "大きめテーブル"),
    ("table-hirama-05", "hirama", "B1", "カウンターB1", 2, "counter", "counter", "false", "true", "カウンター席"),
    ("table-hirama-06", "hirama", "B2", "カウンターB2", 2, "counter", "counter", "false", "true", "カウンター席"),
    ("table-hirama-07", "hirama", "B3", "カウンターB3", 2, "counter", "counter", "false", "true", "カウンター席"),
    ("table-hirama-08", "hirama", "C1", "個室C1", 8, "private", "private", "false", "true", "個室・掘りごたつ"),
    ("table-hirama-09", "hirama", "C2", "VIP個室C2", 10, "private", "private", "false", "true", "VIP個室・カラオケ付"),
    # shinjuku (12 tables)
    ("table-shinjuku-01", "shinjuku", "A1", "テーブルA1", 4, "table", "floor", "true", "true", "窓際"),
    ("table-shinjuku-02", "shinjuku", "A2", "テーブルA2", 4, "table", "floor", "false", "true", ""),
    ("table-shinjuku-03", "shinjuku", "A3", "テーブルA3", 4, "table", "floor", "false", "true", ""),
    ("table-shinjuku-04", "shinjuku", "A4", "テーブルA4", 4, "table", "floor", "false", "true", ""),
    ("table-shinjuku-05", "shinjuku", "A5", "テーブルA5", 6, "table", "floor", "false", "true", "角席"),
    ("table-shinjuku-06", "shinjuku", "A6", "テーブルA6", 6, "table", "floor", "false", "true", ""),
    ("table-shinjuku-07", "shinjuku", "B1", "カウンターB1", 2, "counter", "counter", "false", "true", ""),
    ("table-shinjuku-08", "shinjuku", "B2", "カウンターB2", 2, "counter", "counter", "false", "true", ""),
    ("table-shinjuku-09", "shinjuku", "B3", "カウンターB3", 2, "counter", "counter", "false", "true", ""),
    ("table-shinjuku-10", "shinjuku", "B4", "カウンターB4", 2, "counter", "counter", "false", "true", ""),
    ("table-shinjuku-11", "shinjuku", "C1", "個室C1", 8, "private", "private", "false", "true", "個室"),
    ("table-shinjuku-12", "shinjuku", "C2", "個室C2", 10, "private", "private", "false", "true", "VIP個室"),
]

TABLES_HEADERS = ["id", "branch_code", "table_number", "name", "max_capacity", "table_type", "zone", "has_window", "is_active", "notes"]


def fix_staff_csv():
    """Rewrite staff.csv with correct UTF-8 encoding."""
    csv_path = DATA_DIR / "staff.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(STAFF_HEADERS)
        writer.writerows(STAFF_DATA)
    print(f"✅ Fixed {csv_path.name} - {len(STAFF_DATA)} records")


def fix_tables_csv():
    """Rewrite tables.csv with correct UTF-8 encoding."""
    csv_path = DATA_DIR / "tables.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(TABLES_HEADERS)
        writer.writerows(TABLES_DATA)
    print(f"✅ Fixed {csv_path.name} - {len(TABLES_DATA)} records")


def generate_seed_sql():
    """Generate seed.sql with correct encoding."""
    sql_path = DATA_DIR / "seed.sql"

    lines = [
        "-- ============================================",
        "-- Yakiniku.io Platform - Seed Data (UTF-8)",
        "-- ============================================",
        "",
        "-- Clear existing data",
        "DELETE FROM staff;",
        "DELETE FROM tables;",
        "",
        "-- ============ STAFF ============",
    ]

    for row in STAFF_DATA:
        sql = f"INSERT INTO staff (id, employee_id, branch_code, name, name_kana, phone, email, role, pin_code, is_active, hire_date) VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}', '{row[6]}', '{row[7]}', '{row[8]}', {row[9]}, '{row[10]}');"
        lines.append(sql)

    lines.append("")
    lines.append("-- ============ TABLES ============")

    for row in TABLES_DATA:
        notes = f"'{row[9]}'" if row[9] else "NULL"
        sql = f"INSERT INTO tables (id, branch_code, table_number, name, max_capacity, table_type, zone, has_window, is_active, notes) VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', {row[4]}, '{row[5]}', '{row[6]}', {row[7]}, {row[8]}, {notes});"
        lines.append(sql)

    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Generated {sql_path.name}")


if __name__ == "__main__":
    print("🔧 Fixing encoding issues in data files...")
    fix_staff_csv()
    fix_tables_csv()
    generate_seed_sql()
    print("✅ Done!")
