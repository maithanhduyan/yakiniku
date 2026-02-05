/**
 * YAKINIKU JIAN - Main Application Script
 * Customer website for 焼肉ヅアン
 */

// ============ Configuration ============
const CONFIG = {
    API_BASE: 'http://localhost:8000/api',
    DEFAULT_BRANCH: 'hirama'
};

// ============ State ============
let bookingData = {
    date: null,
    time: null,
    guests: 2,
    name: '',
    phone: '',
    email: '',
    note: ''
};

let currentStep = 1;
const totalSteps = 6;

// ============ Menu Data ============
const menuData = {
    recommend: [
        { name: '特選カルビ', price: 1980, description: '厳選された上質な牛カルビ', image: '🥩' },
        { name: '特選5種盛り', price: 4980, description: 'カルビ、ロース、ハラミ、タン、ホルモン', image: '🍖' },
        { name: '和牛ロース', price: 2480, description: 'A5ランク和牛の上質なロース', image: '🥩' },
        { name: '牛タン塩', price: 1480, description: 'コリコリ食感の牛タン', image: '🥩' }
    ],
    beef: [
        { name: '特選カルビ', price: 1980, description: '厳選された上質な牛カルビ', image: '🥩' },
        { name: '上ハラミ', price: 1680, description: '柔らかく旨味たっぷり', image: '🥩' },
        { name: '牛タン塩', price: 1480, description: 'コリコリ食感の牛タン', image: '🥩' },
        { name: '和牛ロース', price: 2480, description: 'A5ランク和牛', image: '🥩' },
        { name: 'ザブトン', price: 2280, description: '希少部位', image: '🥩' },
        { name: 'イチボ', price: 1880, description: '赤身の旨味', image: '🥩' }
    ],
    set: [
        { name: '特選5種盛り', price: 4980, description: 'カルビ、ロース、ハラミ、タン、ホルモン', image: '🍖' },
        { name: '焼肉盛り合わせ', price: 3980, description: '2〜3名様向け', image: '🍖' },
        { name: '焼肉食べ放題90分', price: 3980, description: '食べ放題コース', image: '🍖' },
        { name: '飲み放題90分', price: 1500, description: 'ビール、サワー、ソフトドリンク', image: '🍺' }
    ],
    side: [
        { name: 'ライス', price: 300, description: '国産コシヒカリ', image: '🍚' },
        { name: '冷麺', price: 880, description: 'さっぱり冷麺', image: '🍜' },
        { name: 'キムチ盛り合わせ', price: 780, description: '3種盛り', image: '🥗' },
        { name: 'ナムル3種', price: 480, description: 'もやし、ほうれん草、大根', image: '🥗' },
        { name: '生ビール', price: 550, description: 'キンキンに冷えた生', image: '🍺' },
        { name: 'チャミスル', price: 680, description: '韓国焼酎', image: '🍶' }
    ]
};

// ============ Initialization ============
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    console.log('🍖 Yakiniku JIAN - App Initialized');

    // Initialize AOS
    AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: true
    });

    // Setup event listeners
    setupNavigation();
    setupMenu();
    setupBooking();
    setupChat();

    // Set min date for booking
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('bookingDate').min = today;
}

// ============ Navigation ============
function setupNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const header = document.getElementById('header');

    // Mobile menu toggle
    navToggle?.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    // Close menu on link click
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active');
        });
    });

    // Header scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ============ Menu ============
function setupMenu() {
    const menuTabs = document.querySelectorAll('.menu-tab');
    const menuGrid = document.getElementById('menuGrid');

    // Initial render
    renderMenu('recommend');

    // Tab click handlers
    menuTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            menuTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderMenu(tab.dataset.category);
        });
    });
}

function renderMenu(category) {
    const menuGrid = document.getElementById('menuGrid');
    const items = menuData[category] || [];

    menuGrid.innerHTML = items.map(item => `
        <div class="menu-card" data-aos="fade-up">
            <div class="menu-image">${item.image}</div>
            <div class="menu-info">
                <h3>${item.name}</h3>
                <p>${item.description}</p>
                <span class="menu-price">¥${item.price.toLocaleString()}</span>
            </div>
        </div>
    `).join('');
}

// ============ Booking ============
function setupBooking() {
    const prevBtn = document.getElementById('prevStep');
    const nextBtn = document.getElementById('nextStep');
    const guestMinus = document.getElementById('guestMinus');
    const guestPlus = document.getElementById('guestPlus');

    // Navigation buttons
    prevBtn?.addEventListener('click', () => goToStep(currentStep - 1));
    nextBtn?.addEventListener('click', handleNextStep);

    // Guest count
    guestMinus?.addEventListener('click', () => updateGuestCount(-1));
    guestPlus?.addEventListener('click', () => updateGuestCount(1));

    // Date change
    document.getElementById('bookingDate')?.addEventListener('change', (e) => {
        bookingData.date = e.target.value;
    });

    // Generate time slots
    generateTimeSlots();
}

function generateTimeSlots() {
    const timeSlots = document.getElementById('timeSlots');
    const slots = [
        '11:30', '12:00', '12:30', '13:00', '13:30',
        '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'
    ];

    timeSlots.innerHTML = slots.map(time => `
        <button class="time-slot" data-time="${time}">${time}</button>
    `).join('');

    // Time slot click handlers
    timeSlots.querySelectorAll('.time-slot').forEach(slot => {
        slot.addEventListener('click', () => {
            timeSlots.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
            slot.classList.add('selected');
            bookingData.time = slot.dataset.time;
        });
    });
}

function updateGuestCount(delta) {
    bookingData.guests = Math.max(1, Math.min(20, bookingData.guests + delta));
    document.getElementById('guestCount').textContent = bookingData.guests;
}

function handleNextStep() {
    if (!validateCurrentStep()) return;

    if (currentStep === totalSteps - 1) {
        // Submit booking
        submitBooking();
    } else {
        goToStep(currentStep + 1);
    }
}

function validateCurrentStep() {
    switch (currentStep) {
        case 1:
            if (!bookingData.date) {
                alert('日付を選択してください');
                return false;
            }
            break;
        case 2:
            if (!bookingData.time) {
                alert('時間を選択してください');
                return false;
            }
            break;
        case 4:
            bookingData.name = document.getElementById('customerName').value;
            bookingData.phone = document.getElementById('customerPhone').value;
            bookingData.email = document.getElementById('customerEmail').value;
            bookingData.note = document.getElementById('customerNote').value;

            if (!bookingData.name || !bookingData.phone) {
                alert('お名前と電話番号は必須です');
                return false;
            }
            break;
    }
    return true;
}

function goToStep(step) {
    if (step < 1 || step > totalSteps) return;

    currentStep = step;

    // Update step visibility
    document.querySelectorAll('.booking-step').forEach((s, i) => {
        s.classList.toggle('active', i + 1 === step);
    });

    // Update navigation buttons
    const prevBtn = document.getElementById('prevStep');
    const nextBtn = document.getElementById('nextStep');

    prevBtn.style.display = step > 1 && step < totalSteps ? 'block' : 'none';

    if (step === totalSteps - 1) {
        nextBtn.textContent = '予約を確定';
        updateBookingSummary();
    } else if (step === totalSteps) {
        nextBtn.style.display = 'none';
        prevBtn.style.display = 'none';
    } else {
        nextBtn.textContent = '次へ';
        nextBtn.style.display = 'block';
    }
}

function updateBookingSummary() {
    const summary = document.getElementById('bookingSummary');
    const date = new Date(bookingData.date);
    const dateStr = date.toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    });

    summary.innerHTML = `
        <div class="summary-item">
            <span class="label">日時</span>
            <span class="value">${dateStr} ${bookingData.time}</span>
        </div>
        <div class="summary-item">
            <span class="label">人数</span>
            <span class="value">${bookingData.guests}名様</span>
        </div>
        <div class="summary-item">
            <span class="label">お名前</span>
            <span class="value">${bookingData.name}</span>
        </div>
        <div class="summary-item">
            <span class="label">電話番号</span>
            <span class="value">${bookingData.phone}</span>
        </div>
        ${bookingData.email ? `
        <div class="summary-item">
            <span class="label">メール</span>
            <span class="value">${bookingData.email}</span>
        </div>
        ` : ''}
        ${bookingData.note ? `
        <div class="summary-item">
            <span class="label">ご要望</span>
            <span class="value">${bookingData.note}</span>
        </div>
        ` : ''}
    `;
}

async function submitBooking() {
    console.log('Submitting booking:', bookingData);

    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Show success step
    goToStep(totalSteps);
}

// ============ Chat Widget ============
function setupChat() {
    const chatToggle = document.getElementById('chatToggle');
    const chatWidget = document.getElementById('chatWidget');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');

    // Toggle chat
    chatToggle?.addEventListener('click', () => {
        chatWidget.classList.toggle('open');
    });

    // Send message
    const sendMessage = () => {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addChatMessage(message, 'user');
        chatInput.value = '';

        // Bot response
        setTimeout(() => {
            const response = getBotResponse(message);
            addChatMessage(response, 'bot');
        }, 500);
    };

    chatSend?.addEventListener('click', sendMessage);
    chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

function addChatMessage(message, type) {
    const chatMessages = document.getElementById('chatMessages');
    const messageEl = document.createElement('div');
    messageEl.className = `chat-message ${type}`;
    messageEl.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getBotResponse(message) {
    const lowerMessage = message.toLowerCase();

    const responses = {
        '予約': 'ご予約は画面上部の「予約する」ボタンから、もしくはお電話(044-XXX-XXXX)でも承っております。',
        '営業時間': 'ランチ 11:30〜14:00、ディナー 17:00〜23:00です。火曜日は定休日です。',
        '場所': 'JR南武線「平間駅」から徒歩1分です。',
        'アクセス': 'JR南武線「平間駅」から徒歩1分、平間駅前ビル2Fにございます。',
        'メニュー': 'おすすめは特選5種盛り(¥4,980)です。A5ランク和牛もご用意しております。',
        'おすすめ': '特選カルビ、和牛ロース、牛タン塩が人気です。',
        '駐車場': '専用駐車場はございませんが、近隣にコインパーキングがございます。',
        'コース': '食べ放題コースは90分¥3,980〜、飲み放題は¥1,500でお付けできます。',
        '個室': '半個室のお席がございます。ご予約時にお申し付けください。'
    };

    for (const [keyword, response] of Object.entries(responses)) {
        if (lowerMessage.includes(keyword)) {
            return response;
        }
    }

    return 'お問い合わせありがとうございます。詳しくはお電話(044-XXX-XXXX)でお気軽にお問い合わせください。';
}
