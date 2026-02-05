Tuyệt vời! Đây là bản **Redesign hoàn chỉnh** dựa trên yêu cầu thiết kế lại trangweb yakinikuJIAN.com.

Tôi đã thay đổi toàn bộ giao diện sang phong cách **Dark Luxury (Sang trọng tối giản)**. Mã nguồn này bao gồm HTML, CSS và một chút JavaScript (cho menu trên điện thoại).

Bạn hãy tạo file mới tên là `yakinikuJIAN_modern.html` và dán đoạn mã sau vào:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>焼肉ヅアン | YAKINIKU JIAN - 平間の上質焼肉</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&family=Shippori+Mincho:wght@400;700&display=swap" rel="stylesheet">

    <style>
        /* --- 1. VARIABLES & RESET --- */
        :root {
            --bg-color: #1a1a1a;       /* Nền đen nhám */
            --bg-secondary: #252525;   /* Nền phụ */
            --text-color: #f0f0f0;     /* Chữ trắng */
            --accent-color: #d4af37;   /* Vàng ánh kim */
            --font-main: 'Noto Sans JP', sans-serif;
            --font-serif: 'Shippori Mincho', serif;
            --transition: all 0.4s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--font-main);
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.8;
            letter-spacing: 0.05em;
        }

        a {
            text-decoration: none;
            color: inherit;
            transition: var(--transition);
        }

        ul {
            list-style: none;
        }

        img {
            width: 100%;
            height: auto;
            object-fit: cover;
            display: block;
        }

        /* Typography Utilities */
        h1, h2, h3 {
            font-family: var(--font-serif);
            font-weight: 700;
        }

        .section-title {
            font-size: 2.5rem;
            color: var(--accent-color);
            text-align: center;
            margin-bottom: 3rem;
            position: relative;
            display: inline-block;
            left: 50%;
            transform: translateX(-50%);
        }

        .section-title::after {
            content: '';
            display: block;
            width: 60px;
            height: 2px;
            background: var(--accent-color);
            margin: 15px auto 0;
        }

        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
        }

        .btn-gold {
            display: inline-block;
            padding: 12px 40px;
            border: 1px solid var(--accent-color);
            color: var(--accent-color);
            font-family: var(--font-serif);
            font-size: 1rem;
            margin-top: 20px;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }

        .btn-gold::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 0%; height: 100%;
            background: var(--accent-color);
            z-index: -1;
            transition: var(--transition);
        }

        .btn-gold:hover {
            color: #000;
        }

        .btn-gold:hover::before {
            width: 100%;
        }

        /* --- 2. HEADER & NAVIGATION --- */
        header {
            position: fixed;
            top: 0;
            width: 100%;
            padding: 20px 0;
            z-index: 1000;
            background: rgba(26, 26, 26, 0.9);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        }

        .header-inner {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo h1 {
            font-size: 1.8rem;
            color: var(--text-color);
            letter-spacing: 0.1em;
        }

        .logo span {
            color: var(--accent-color);
        }

        /* Desktop Nav */
        .desktop-nav {
            display: flex;
            gap: 30px;
        }

        .desktop-nav a {
            font-size: 0.9rem;
            text-transform: uppercase;
            position: relative;
        }

        .desktop-nav a::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0;
            height: 1px;
            background: var(--accent-color);
            transition: var(--transition);
        }

        .desktop-nav a:hover {
            color: var(--accent-color);
        }

        .desktop-nav a:hover::after {
            width: 100%;
        }

        /* Mobile Menu Button (Hamburger) */
        .hamburger {
            display: none;
            cursor: pointer;
            z-index: 2000;
        }

        .bar {
            display: block;
            width: 25px;
            height: 2px;
            margin: 5px auto;
            background-color: var(--accent-color);
            transition: var(--transition);
        }

        /* Mobile Nav Drawer */
        .mobile-nav {
            position: fixed;
            top: 0;
            right: -100%;
            width: 100%;
            height: 100vh;
            background-color: var(--bg-color);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: var(--transition);
            z-index: 1500;
        }

        .mobile-nav.active {
            right: 0;
        }

        .mobile-nav a {
            font-size: 1.5rem;
            margin: 20px 0;
            font-family: var(--font-serif);
        }

        /* Hamburger Animation */
        .hamburger.active .bar:nth-child(2) { opacity: 0; }
        .hamburger.active .bar:nth-child(1) { transform: translateY(7px) rotate(45deg); }
        .hamburger.active .bar:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

        /* --- 3. HERO SECTION --- */
        .hero {
            height: 100vh;
            width: 100%;
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1558030006-450675393462?q=80&w=1920&auto=format&fit=crop'); /* Ảnh thịt nướng chất lượng cao */
            background-size: cover;
            background-position: center;
            background-attachment: fixed; /* Parallax effect */
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 0 20px;
        }

        .hero-content {
            animation: fadeIn Up 1s ease-out;
        }

        .hero h2 {
            font-size: 3rem;
            margin-bottom: 20px;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
        }

        .hero h2 span {
            display: block;
            font-size: 1.2rem;
            font-family: var(--font-main);
            font-weight: 300;
            margin-bottom: 10px;
            color: var(--accent-color);
        }

        .hero p {
            font-size: 1.1rem;
            margin-bottom: 30px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        /* --- 4. SECTIONS & LAYOUT --- */
        section {
            padding: 100px 0;
        }

        /* News Ticker Modern */
        .news-bar {
            background: var(--bg-secondary);
            padding: 20px 0;
            border-bottom: 1px solid #333;
        }
        .news-container {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }
        .news-label {
            color: var(--accent-color);
            font-weight: bold;
            margin-right: 15px;
            border: 1px solid var(--accent-color);
            padding: 2px 8px;
        }

        /* Concept (Grid Layout) */
        .concept-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 50px;
            align-items: center;
        }

        .concept-img {
            position: relative;
        }

        .concept-img::before {
            content: '';
            position: absolute;
            top: -15px; left: -15px;
            width: 100%; height: 100%;
            border: 1px solid var(--accent-color);
            z-index: -1;
        }

        /* Menu (Card Grid) */
        .menu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }

        .menu-card {
            background: var(--bg-secondary);
            transition: var(--transition);
            overflow: hidden;
            position: relative;
        }

        .menu-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }

        .menu-card img {
            height: 250px;
            transition: var(--transition);
        }

        .menu-card:hover img {
            transform: scale(1.1);
        }

        .menu-info {
            padding: 25px;
            text-align: center;
        }

        .menu-info h3 {
            font-size: 1.3rem;
            margin-bottom: 10px;
            color: var(--text-color);
        }

        .menu-info p {
            font-size: 0.9rem;
            color: #aaa;
            margin-bottom: 15px;
        }

        .price {
            color: var(--accent-color);
            font-weight: bold;
            font-size: 1.1rem;
            font-family: var(--font-serif);
        }

        /* Space Section */
        .space-section {
            background-color: var(--bg-secondary);
        }

        /* --- 5. FOOTER --- */
        footer {
            background-color: #000;
            padding: 60px 0 20px;
            border-top: 1px solid #333;
            text-align: center;
        }

        .footer-logo {
            font-family: var(--font-serif);
            font-size: 2rem;
            color: var(--accent-color);
            margin-bottom: 20px;
        }

        .footer-info {
            color: #888;
            margin-bottom: 30px;
        }

        .copyright {
            font-size: 0.8rem;
            color: #555;
            border-top: 1px solid #222;
            padding-top: 20px;
        }

        /* --- 6. RESPONSIVE --- */
        @media (max-width: 768px) {
            .desktop-nav { display: none; }
            .hamburger { display: block; }

            .hero h2 { font-size: 2rem; }

            .concept-grid {
                grid-template-columns: 1fr;
            }

            .concept-content { order: 1; }
            .concept-img { order: 2; }

            section { padding: 60px 0; }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="container header-inner">
            <div class="logo">
                <a href="#"><h1>焼肉<span>ヅアン</span></h1></a>
            </div>

            <!-- Desktop Nav -->
            <nav class="desktop-nav">
                <a href="#">ホーム</a>
                <a href="#concept">こだわり</a>
                <a href="#menu">お品書き</a>
                <a href="#space">空間・個室</a>
                <a href="#access">店舗情報</a>
            </nav>

            <!-- Mobile Hamburger -->
            <div class="hamburger">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </div>
        </div>
    </header>

    <!-- Mobile Nav Overlay -->
    <div class="mobile-nav">
        <a href="#" onclick="toggleMenu()">ホーム</a>
        <a href="#concept" onclick="toggleMenu()">こだわり</a>
        <a href="#menu" onclick="toggleMenu()">お品書き</a>
        <a href="#space" onclick="toggleMenu()">空間・個室</a>
        <a href="#access" onclick="toggleMenu()">店舗情報</a>
    </div>

    <!-- Hero Section -->
    <div class="hero">
        <div class="hero-content">
            <h2><span>平間の隠れ家で味わう</span>極上の焼肉体験</h2>
            <p>厳選された黒毛和牛と、創業以来変わらぬ秘伝のタレ。<br>大切な人と過ごす、特別なひとときを。</p>
            <a href="#menu" class="btn-gold">メニューを見る</a>
        </div>
    </div>

    <!-- News Ticker -->
    <div class="news-bar">
        <div class="container news-container">
            <span class="news-label">NEWS</span>
            <span class="news-text">2026.02.01 【2月のお休み】火曜定休日となります。</span>
        </div>
    </div>

    <!-- Concept Section -->
    <section id="concept" class="container">
        <div class="concept-grid">
            <div class="concept-content">
                <h2 class="section-title" style="text-align:left; left:0; transform:none;">職人のこだわり</h2>
                <p style="margin-bottom: 20px;">普通の焼肉店とは一味違う、新鮮で上質な肉を揃えて皆様のご来店をお待ちしております。</p>
                <p style="margin-bottom: 20px;">店主自らが市場で目利きした黒毛和牛は、口の中でとろけるような食感と濃厚な旨味が特徴です。お肉以外にも旬の地野菜や鮮度抜群の魚介など、素材本来の味を活かしたメニューを豊富にご用意しています。</p>
                <a href="#" class="btn-gold">詳しく見る</a>
            </div>
            <div class="concept-img">
                <!-- Ảnh đầu bếp cắt thịt hoặc đĩa thịt đẹp -->
                <img src="https://images.unsplash.com/photo-1594041680534-e8c8cdebd659?q=80&w=800&auto=format&fit=crop" alt="こだわりのお肉">
            </div>
        </div>
    </section>

    <!-- Menu Section -->
    <section id="menu" style="background-color: var(--bg-secondary);">
        <div class="container">
            <h2 class="section-title">自慢のお品書き</h2>

            <div class="menu-grid">
                <!-- Card 1 -->
                <div class="menu-card">
                    <div style="overflow:hidden;">
                        <img src="https://images.unsplash.com/photo-1615937691194-96dd43c95456?q=80&w=600&auto=format&fit=crop" alt="和牛上ハラミ">
                    </div>
                    <div class="menu-info">
                        <h3>和牛上ハラミ</h3>
                        <p>口の中でほどける柔らかさと濃厚な味わい。</p>
                        <div class="price">¥1,800</div>
                    </div>
                </div>

                <!-- Card 2 -->
                <div class="menu-card">
                    <div style="overflow:hidden;">
                        <img src="https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=600&auto=format&fit=crop" alt="厚切り上タン塩">
                    </div>
                    <div class="menu-info">
                        <h3>厚切り上タン塩</h3>
                        <p>贅沢な厚切り。歯ごたえと肉汁が溢れます。</p>
                        <div class="price">¥2,200</div>
                    </div>
                </div>

                <!-- Card 3 -->
                <div class="menu-card">
                    <div style="overflow:hidden;">
                        <img src="https://images.unsplash.com/photo-1547496502-ffa222d79634?q=80&w=600&auto=format&fit=crop" alt="特選盛り合わせ">
                    </div>
                    <div class="menu-info">
                        <h3>特選盛り合わせ</h3>
                        <p>本日のおすすめ希少部位を贅沢に。</p>
                        <div class="price">¥4,500〜</div>
                    </div>
                </div>
            </div>

            <div style="text-align: center; margin-top: 40px;">
                <a href="#" class="btn-gold">全てのメニューを見る</a>
            </div>
        </div>
    </section>

    <!-- Space Section -->
    <section id="space" class="container">
        <div class="concept-grid">
            <div class="concept-img">
                <!-- Ảnh không gian quán tối, sang trọng -->
                <img src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800&auto=format&fit=crop" alt="店内の様子">
            </div>
            <div class="concept-content">
                <h2 class="section-title" style="text-align:left; left:0; transform:none;">上質な空間</h2>
                <p style="margin-bottom: 20px;">落ち着いた照明とモダンなインテリアが織りなす大人の隠れ家。</p>
                <p>無煙ロースターを完備しておりますので、匂いを気にせずお食事をお楽しみいただけます。掘りごたつ式の個室もご用意しており、接待や記念日、ご家族での団らんに最適です。</p>
                <a href="#" class="btn-gold">店舗情報へ</a>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer id="access">
        <div class="container">
            <div class="footer-logo">焼肉ヅアン</div>
            <div class="footer-info">
                <p>〒211-0013 神奈川県川崎市中原区上平間XXXX</p>
                <p style="font-size: 1.5rem; color: #fff; margin: 10px 0;">044-789-8413</p>
                <p>営業時間: 17:00 - 23:00 (L.O. 22:30)</p>
            </div>
            <div class="copyright">
                &copy; 2024 YAKINIKU JIAN. All Rights Reserved.
            </div>
        </div>
    </footer>

    <!-- JavaScript for Mobile Menu -->
    <script>
        const hamburger = document.querySelector('.hamburger');
        const mobileNav = document.querySelector('.mobile-nav');

        function toggleMenu() {
            hamburger.classList.toggle('active');
            mobileNav.classList.toggle('active');
        }

        hamburger.addEventListener('click', toggleMenu);
    </script>
</body>
</html>
```

### Điểm nổi bật của bản Redesign này:

1.  **Màu sắc & Cảm giác (Look & Feel):**
    *   Sử dụng màu nền đen (`#1a1a1a`) kết hợp với màu phụ (`#252525`) tạo chiều sâu.
    *   Chữ màu vàng Gold (`#d4af37`) tạo điểm nhấn sang trọng cho tiêu đề và các nút bấm.
    *   Hiệu ứng **Glassmorphism** (kính mờ) ở thanh Header giúp menu luôn nổi bật nhưng không che mất nội dung khi cuộn.

2.  **Typography (Phông chữ):**
    *   **Shippori Mincho**: Dùng cho các tiêu đề lớn, tạo cảm giác truyền thống Nhật Bản, cao cấp.
    *   **Noto Sans JP**: Dùng cho nội dung văn bản, dễ đọc, hiện đại.

3.  **Hình ảnh:**
    *   Sử dụng hình ảnh từ Unsplash chất lượng cao để demo (bạn có thể thay thế bằng ảnh thật của quán).
    *   Hiệu ứng **Parallax** (ảnh nền trôi chậm hơn nội dung) ở phần Hero đầu trang tạo cảm giác mượt mà, chuyên nghiệp.
    *   Hiệu ứng **Zoom** nhẹ khi di chuột vào ảnh menu.

4.  **Bố cục (Layout):**
    *   **CSS Grid**: Phần Menu được chia cột tự động co giãn đẹp mắt.
    *   **Whitespace**: Khoảng cách giữa các phần (`padding: 100px 0`) rộng rãi, giúp mắt người xem được nghỉ ngơi và tập trung vào hình ảnh món ăn.

5.  **Mobile First:**
    *   Menu trên điện thoại chuyển thành nút **Hamburger** (3 gạch) với hiệu ứng hoạt hình khi bấm vào.
    *   Menu trượt ra toàn màn hình, dễ thao tác ngón tay.

Bạn hãy thử mở file này trên trình duyệt và trải nghiệm nhé!