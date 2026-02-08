/**
 * ========================================
 * Yakiniku JIAN (ヅアン) - Main Application Script
 * Mobile-First Booking Experience
 * ========================================
 */

(function() {
    'use strict';

    // ============================================
    // API CONFIGURATION
    // ============================================
    // Auto-detect: Dev → backend :8000 | Prod (Traefik) → same origin
    const _h = window.location.hostname;
    const _p = window.location.port;
    const _d = _p && !['80','443',''].includes(_p);
    const API_BASE = `${_d ? 'http:' : window.location.protocol}//${_h}${_d ? ':8000' : ''}/api`;  // Dev: backend always HTTP
    const BRANCH_CODE = 'hirama';

    // ============================================
    // MOBILE MENU
    // ============================================
    const hamburger = document.querySelector('.hamburger');
    const mobileNav = document.querySelector('.mobile-nav');

    function toggleMenu() {
        hamburger.classList.toggle('active');
        mobileNav.classList.toggle('active');
        document.body.style.overflow = mobileNav.classList.contains('active') ? 'hidden' : '';
    }

    if (hamburger) {
        hamburger.addEventListener('click', toggleMenu);
    }

    // Close menu when clicking nav links
    document.querySelectorAll('.mobile-nav a').forEach(link => {
        link.addEventListener('click', () => {
            if (mobileNav.classList.contains('active')) {
                toggleMenu();
            }
        });
    });

    // ============================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ============================================
    // BOOKING WIDGET
    // ============================================
    const bookingData = {
        date: null,
        time: null,
        guests: null,
        name: '',
        phone: '',
        email: '',
        note: ''
    };

    let currentStep = 1;
    let selectedMonth = new Date();

    // Initialize Calendar
    function initCalendar() {
        renderCalendar();
    }

    function renderCalendar() {
        const grid = document.getElementById('dateGrid');
        const monthLabel = document.getElementById('currentMonth');

        if (!grid || !monthLabel) return;

        // Clear previous dates (keep headers)
        const headers = grid.querySelectorAll('.date-header');
        grid.innerHTML = '';
        headers.forEach(h => grid.appendChild(h));

        // Set month label
        const year = selectedMonth.getFullYear();
        const month = selectedMonth.getMonth();
        monthLabel.textContent = `${year}年 ${month + 1}月`;

        // Get first day of month and total days
        const firstDay = new Date(year, month, 1).getDay();
        const totalDays = new Date(year, month + 1, 0).getDate();
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // Add empty cells for days before first day
        for (let i = 0; i < firstDay; i++) {
            const empty = document.createElement('div');
            empty.className = 'date-cell empty';
            grid.appendChild(empty);
        }

        // Add day cells
        for (let day = 1; day <= totalDays; day++) {
            const cell = document.createElement('div');
            cell.className = 'date-cell';
            cell.textContent = day;

            const cellDate = new Date(year, month, day);
            const dayOfWeek = cellDate.getDay();

            // Tuesday is closed (火曜定休)
            const isTuesday = dayOfWeek === 2;
            const isPast = cellDate < today;

            if (isTuesday || isPast) {
                cell.classList.add('disabled');
            } else {
                if (dayOfWeek === 0) cell.classList.add('sunday');
                if (dayOfWeek === 6) cell.classList.add('saturday');

                cell.addEventListener('click', () => selectDate(year, month, day));

                // Check if this date is selected
                if (bookingData.date) {
                    const selected = new Date(bookingData.date);
                    if (cellDate.getTime() === selected.getTime()) {
                        cell.classList.add('selected');
                    }
                }
            }

            grid.appendChild(cell);
        }
    }

    // Make changeMonth globally accessible
    window.changeMonth = function(delta) {
        selectedMonth.setMonth(selectedMonth.getMonth() + delta);

        // Don't allow going to past months
        const today = new Date();
        if (selectedMonth.getFullYear() < today.getFullYear() ||
            (selectedMonth.getFullYear() === today.getFullYear() &&
             selectedMonth.getMonth() < today.getMonth())) {
            selectedMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        }

        renderCalendar();
    };

    function selectDate(year, month, day) {
        bookingData.date = new Date(year, month, day);
        renderCalendar();

        const btnStep1 = document.getElementById('btnStep1');
        if (btnStep1) btnStep1.disabled = false;

        // Haptic feedback for mobile
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }

        // Fetch available slots for this date from API
        fetchAvailableSlots(year, month, day);
    }

    // Fetch available time slots from API
    async function fetchAvailableSlots(year, month, day) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

        try {
            const response = await fetch(
                `${API_BASE}/bookings/available-slots?booking_date=${dateStr}&branch_code=${BRANCH_CODE}`
            );

            if (!response.ok) {
                console.warn('Failed to fetch slots, using all slots');
                return;
            }

            const data = await response.json();
            const availableSlots = data.available_slots || [];

            // Update time slot UI
            document.querySelectorAll('.time-slot').forEach(slot => {
                const time = slot.dataset.time;
                if (availableSlots.includes(time)) {
                    slot.classList.remove('disabled');
                } else {
                    slot.classList.add('disabled');
                    slot.classList.remove('selected');
                }
            });

            // If currently selected time is no longer available, deselect it
            if (bookingData.time && !availableSlots.includes(bookingData.time)) {
                bookingData.time = null;
                const btnStep2 = document.getElementById('btnStep2');
                if (btnStep2) btnStep2.disabled = true;
            }

            console.log(`📅 Available slots for ${dateStr}:`, availableSlots);

        } catch (error) {
            console.error('Error fetching available slots:', error);
        }
    }

    // Time Selection
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.addEventListener('click', function() {
            if (this.classList.contains('disabled')) return;

            document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
            this.classList.add('selected');
            bookingData.time = this.dataset.time;

            const btnStep2 = document.getElementById('btnStep2');
            if (btnStep2) btnStep2.disabled = false;

            if (navigator.vibrate) navigator.vibrate(10);
        });
    });

    // Guest Selection
    document.querySelectorAll('.guest-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.guest-btn').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            bookingData.guests = this.dataset.guests;

            const btnStep3 = document.getElementById('btnStep3');
            if (btnStep3) btnStep3.disabled = false;

            if (navigator.vibrate) navigator.vibrate(10);
        });
    });

    // Step Navigation
    window.nextStep = function() {
        if (currentStep < 5) {
            goToStep(currentStep + 1);
        }
    };

    window.prevStep = function() {
        if (currentStep > 1) {
            goToStep(currentStep - 1);
        }
    };

    function goToStep(step) {
        // Hide all steps
        document.querySelectorAll('.booking-step').forEach(s => s.classList.remove('active'));

        // Show target step
        const targetStep = document.querySelector(`.booking-step[data-step="${step}"]`);
        if (targetStep) {
            targetStep.classList.add('active');
        }

        // Update progress indicators
        document.querySelectorAll('.progress-step').forEach(p => {
            const pStep = parseInt(p.dataset.step);
            p.classList.remove('active', 'completed');
            if (pStep < step) p.classList.add('completed');
            if (pStep === step) p.classList.add('active');
        });

        currentStep = step;

        // Scroll to booking section on mobile
        const bookingSection = document.getElementById('booking');
        if (bookingSection && window.innerWidth < 768) {
            setTimeout(() => {
                bookingSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }

    // Show Confirmation
    window.showConfirmation = function() {
        // Get form data
        bookingData.name = document.getElementById('guestName')?.value || '';
        bookingData.phone = document.getElementById('guestPhone')?.value || '';
        bookingData.email = document.getElementById('guestEmail')?.value || '';
        bookingData.note = document.getElementById('guestNote')?.value || '';

        // Validate required fields
        if (!bookingData.name || !bookingData.phone) {
            alert('お名前と電話番号は必須です。');
            return;
        }

        // Validate phone format (basic Japanese phone)
        const phoneRegex = /^[\d\-+()]{10,15}$/;
        if (!phoneRegex.test(bookingData.phone.replace(/\s/g, ''))) {
            alert('有効な電話番号を入力してください。');
            return;
        }

        // Format date
        const dateObj = new Date(bookingData.date);
        const dateStr = `${dateObj.getFullYear()}年${dateObj.getMonth() + 1}月${dateObj.getDate()}日`;
        const days = ['日', '月', '火', '水', '木', '金', '土'];
        const dayStr = days[dateObj.getDay()];

        // Update confirmation display
        const confirmDate = document.getElementById('confirmDate');
        const confirmTime = document.getElementById('confirmTime');
        const confirmGuests = document.getElementById('confirmGuests');
        const confirmName = document.getElementById('confirmName');
        const confirmPhone = document.getElementById('confirmPhone');

        if (confirmDate) confirmDate.textContent = `${dateStr} (${dayStr})`;
        if (confirmTime) confirmTime.textContent = bookingData.time;
        if (confirmGuests) confirmGuests.textContent = `${bookingData.guests}名様`;
        if (confirmName) confirmName.textContent = bookingData.name;
        if (confirmPhone) confirmPhone.textContent = bookingData.phone;

        goToStep(5);
    };

    // Submit Booking
    window.submitBooking = async function() {
        // Show loading state
        const submitBtn = document.querySelector('.booking-step[data-step="5"] .btn-booking:not(.btn-back)');
        const originalText = submitBtn?.textContent || '予約を確定';
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '送信中...';
        }

        // Prepare data for API
        const payload = {
            date: bookingData.date.toISOString().split('T')[0],
            time: bookingData.time,
            guests: parseInt(bookingData.guests),
            guest_name: bookingData.name,
            guest_phone: bookingData.phone,
            guest_email: bookingData.email || null,
            note: bookingData.note || null,
            branch_code: BRANCH_CODE
        };

        try {
            const response = await fetch(`${API_BASE}/bookings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '予約に失敗しました');
            }

            const result = await response.json();
            console.log('✅ Booking created:', result);

            // Also identify/create customer for insights
            try {
                await fetch(`${API_BASE}/customers/identify?branch_code=${BRANCH_CODE}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        phone: bookingData.phone,
                        name: bookingData.name,
                        email: bookingData.email || null
                    })
                });
            } catch (e) {
                console.warn('Customer identify failed:', e);
            }

            // Show success state
            document.querySelectorAll('.booking-step').forEach(s => s.classList.remove('active'));
            const successStep = document.querySelector('.booking-step[data-step="success"]');
            if (successStep) successStep.classList.add('active');

            // Mark all steps as completed
            document.querySelectorAll('.progress-step').forEach(p => {
                p.classList.remove('active');
                p.classList.add('completed');
            });

            // Haptic feedback
            if (navigator.vibrate) navigator.vibrate([50, 50, 100]);

        } catch (error) {
            console.error('❌ Booking error:', error);
            alert(`予約エラー: ${error.message}`);

            // Reset button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    };

    // Reset Booking
    window.resetBooking = function() {
        // Reset data
        bookingData.date = null;
        bookingData.time = null;
        bookingData.guests = null;
        bookingData.name = '';
        bookingData.phone = '';
        bookingData.email = '';
        bookingData.note = '';

        // Reset UI
        document.querySelectorAll('.time-slot, .guest-btn').forEach(el => {
            el.classList.remove('selected');
        });

        const bookingForm = document.getElementById('bookingForm');
        if (bookingForm) bookingForm.reset();

        const btnStep1 = document.getElementById('btnStep1');
        const btnStep2 = document.getElementById('btnStep2');
        const btnStep3 = document.getElementById('btnStep3');

        if (btnStep1) btnStep1.disabled = true;
        if (btnStep2) btnStep2.disabled = true;
        if (btnStep3) btnStep3.disabled = true;

        // Reset progress
        document.querySelectorAll('.progress-step').forEach(p => {
            p.classList.remove('active', 'completed');
        });
        const firstStep = document.querySelector('.progress-step[data-step="1"]');
        if (firstStep) firstStep.classList.add('active');

        // Go to step 1
        currentStep = 1;
        selectedMonth = new Date();
        document.querySelectorAll('.booking-step').forEach(s => s.classList.remove('active'));
        const step1 = document.querySelector('.booking-step[data-step="1"]');
        if (step1) step1.classList.add('active');

        renderCalendar();
    };

    // ============================================
    // FLOATING BUTTON VISIBILITY
    // ============================================
    const floatingBtn = document.querySelector('.floating-book-btn');
    const bookingSection = document.getElementById('booking');

    function updateFloatingBtnVisibility() {
        if (!floatingBtn || !bookingSection) return;

        const bookingRect = bookingSection.getBoundingClientRect();
        const isBookingVisible = bookingRect.top < window.innerHeight && bookingRect.bottom > 0;

        floatingBtn.style.opacity = isBookingVisible ? '0' : '1';
        floatingBtn.style.pointerEvents = isBookingVisible ? 'none' : 'auto';
    }

    window.addEventListener('scroll', updateFloatingBtnVisibility, { passive: true });

    // ============================================
    // INITIALIZE AOS
    // ============================================
    function initAOS() {
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 600,
                easing: 'ease-out-cubic',
                once: true,
                offset: 50,
                disable: function() {
                    // Disable on very slow devices or if user prefers reduced motion
                    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
                }
            });
        }
    }

    // ============================================
    // HEADER SCROLL EFFECT
    // ============================================
    const header = document.querySelector('header');
    let lastScroll = 0;

    function handleHeaderScroll() {
        if (!header) return;

        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            header.style.background = 'rgba(26, 26, 26, 0.98)';
        } else {
            header.style.background = 'rgba(26, 26, 26, 0.9)';
        }

        lastScroll = currentScroll;
    }

    window.addEventListener('scroll', handleHeaderScroll, { passive: true });

    // ============================================
    // TOUCH OPTIMIZATION
    // ============================================
    // Prevent double-tap zoom on buttons
    document.querySelectorAll('button, .btn-gold, .btn-booking, .header-book-btn').forEach(el => {
        el.addEventListener('touchend', function(e) {
            e.preventDefault();
            this.click();
        }, { passive: false });
    });

    // ============================================
    // INITIALIZE ON DOM READY
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        initCalendar();
        initAOS();
        updateFloatingBtnVisibility();
        handleHeaderScroll();
        initChatWidget();

        console.log('🍖 Yakiniku JIAN (ヅアン) - App Initialized');
    });

    // ============================================
    // CHAT WIDGET WITH CUSTOMER INSIGHTS
    // ============================================
    function initChatWidget() {
        const chatWidget = document.getElementById('chatWidget');
        const chatToggle = document.getElementById('chatToggle');
        const chatClose = document.getElementById('chatClose');
        const chatWindow = document.getElementById('chatWindow');
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('chatInput');
        const chatSend = document.getElementById('chatSend');
        const chatBadge = document.getElementById('chatBadge');
        const quickActions = document.querySelectorAll('.quick-action-btn');
        const customerNameInput = document.getElementById('customerNameInput');
        const saveNameBtn = document.getElementById('saveNameBtn');
        const chatCustomerName = document.getElementById('chatCustomerName');

        if (!chatWidget) return;

        // Customer Data Store (simulating customer insights)
        const customerInsights = {
            // Example customer preferences (would come from backend in production)
            '渡辺': { preferences: ['レバ刺し', '生肉'], note: 'レバ刺しがお好み。生肉系を好む。' },
            '田中': { preferences: ['上タン塩', '厚切り'], note: 'タン塩が大好き。厚切りを好む。' },
            '佐藤': { preferences: ['和牛ハラミ', '赤身'], note: '赤身肉を好む。脂身は控えめに。' },
            '鈴木': { preferences: ['特選盛り', 'ホルモン'], note: 'ホルモン好き。辛いものもOK。' }
        };

        let currentCustomer = localStorage.getItem('yakiniku_customer') || '';
        let chatHistory = JSON.parse(localStorage.getItem('yakiniku_chat_history') || '[]');

        // Initialize customer name field
        if (currentCustomer) {
            customerNameInput.value = currentCustomer;
            chatCustomerName.classList.add('hidden');
        }

        // Toggle chat window
        function toggleChat() {
            chatWidget.classList.toggle('active');
            if (chatWidget.classList.contains('active')) {
                chatBadge.classList.add('hidden');
                if (chatHistory.length === 0) {
                    showWelcomeMessage();
                } else {
                    // Restore chat history
                    chatMessages.innerHTML = '';
                    chatHistory.forEach(msg => {
                        addMessage(msg.text, msg.type, msg.time, false);
                    });
                }
                setTimeout(() => chatInput.focus(), 300);
            }
        }

        chatToggle.addEventListener('click', toggleChat);
        chatClose.addEventListener('click', toggleChat);

        // Save customer name
        saveNameBtn.addEventListener('click', () => {
            const name = customerNameInput.value.trim();
            if (name) {
                currentCustomer = name;
                localStorage.setItem('yakiniku_customer', name);
                chatCustomerName.classList.add('hidden');

                // Check for known customer insights
                const insight = findCustomerInsight(name);
                if (insight) {
                    setTimeout(() => {
                        addMessage(`${name}様、いつもありがとうございます！ ${insight.note}`, 'incoming');
                    }, 500);
                } else {
                    setTimeout(() => {
                        addMessage(`${name}様、ありがとうございます！本日はどのようなお肉をお探しですか？`, 'incoming');
                    }, 500);
                }
            }
        });

        // Find customer insight by name (partial match)
        function findCustomerInsight(name) {
            for (const [key, value] of Object.entries(customerInsights)) {
                if (name.includes(key) || key.includes(name)) {
                    return value;
                }
            }
            return null;
        }

        // Show welcome message
        function showWelcomeMessage() {
            chatMessages.innerHTML = '';
            const welcomeText = currentCustomer
                ? `${currentCustomer}様、こんにちは！焼肉ヅアンへようこそ。特別なご注文やご質問がございましたらお気軽にどうぞ。`
                : 'こんにちは！焼肉ヅアンへようこそ。🥩\n\n特別なご注文やご質問がございましたらお気軽にどうぞ。\n\nまずはお名前を教えていただけますか？';

            addMessage(welcomeText, 'incoming');

            // Check for returning customer insight
            if (currentCustomer) {
                const insight = findCustomerInsight(currentCustomer);
                if (insight) {
                    setTimeout(() => {
                        addMessage(`前回は${insight.preferences.join('、')}をご注文いただきました。本日もいかがですか？`, 'incoming');
                    }, 1000);
                }
            }
        }

        // Add message to chat
        function addMessage(text, type, timeStr = null, save = true) {
            const now = new Date();
            const time = timeStr || `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;

            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${type}`;
            messageDiv.innerHTML = `
                ${text.replace(/\n/g, '<br>')}
                <span class="time">${time}</span>
            `;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Save to history
            if (save) {
                chatHistory.push({ text, type, time });
                // Keep only last 50 messages
                if (chatHistory.length > 50) {
                    chatHistory = chatHistory.slice(-50);
                }
                localStorage.setItem('yakiniku_chat_history', JSON.stringify(chatHistory));
            }
        }

        // Show typing indicator
        function showTyping() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing-indicator';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = '<span></span><span></span><span></span>';
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function hideTyping() {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        }

        // Process user message and generate response via AI API
        async function processMessage(userMessage) {
            // Build conversation history for context
            const history = chatHistory
                .filter(msg => msg.type === 'outgoing' || msg.type === 'incoming')
                .slice(-10)
                .map(msg => ({
                    role: msg.type === 'outgoing' ? 'user' : 'assistant',
                    content: msg.text
                }));

            try {
                const response = await fetch(`${API_BASE}/chat/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: userMessage,
                        customer_name: currentCustomer || null,
                        customer_phone: localStorage.getItem('yakiniku_phone') || null,
                        conversation_history: history,
                        branch_code: BRANCH_CODE
                    })
                });

                if (!response.ok) {
                    throw new Error('Chat API error');
                }

                const data = await response.json();
                return data.response;

            } catch (error) {
                console.warn('Chat API failed, using fallback:', error);
                return fallbackResponse(userMessage);
            }
        }

        // Fallback keyword-based responses when API is unavailable
        function fallbackResponse(userMessage) {
            const lowerMessage = userMessage.toLowerCase();

            const responses = {
                'おすすめ': `本日のおすすめは：\n\n🥇 特選黒毛和牛カルビ ¥2,800\n🥈 厚切り上タン塩 ¥2,200\n🥉 和牛上ハラミ ¥1,800\n\nどれも新鮮で絶品です！`,
                'レバ刺し': '申し訳ございませんが、現在レバ刺しは法律により提供できません。代わりに低温調理のレバーはいかがですか？',
                'アレルギー': 'アレルギー対応可能です。ご来店時にスタッフにお申し付けください。',
                '記念日': '記念日のご予定ですね！🎉 特別デザートプレート・お花のご用意など承ります。',
                '予約': 'ご予約はこのページの「ご予約」セクションから、またはお電話（044-789-8413）で承っております。',
                '営業': '営業時間: 17:00 - 23:00（L.O. 22:30）\n定休日: 火曜日',
                'ホルモン': 'ホルモンメニュー：\n・上ミノ ¥980\n・シマチョウ ¥880\n・ハツ ¥780',
            };

            for (const [keyword, response] of Object.entries(responses)) {
                if (lowerMessage.includes(keyword)) {
                    return response;
                }
            }

            return `ありがとうございます！\n\nご質問を承りました。詳しくはお電話（044-789-8413）でお問い合わせください。`;
        }

        // Send message (async for AI API)
        async function sendMessage() {
            const text = chatInput.value.trim();
            if (!text) return;

            // Add user message
            addMessage(text, 'outgoing');
            chatInput.value = '';
            chatInput.style.height = 'auto';

            // Show typing indicator
            showTyping();

            // Generate response via AI API
            try {
                const response = await processMessage(text);
                hideTyping();
                addMessage(response, 'incoming');
            } catch (error) {
                hideTyping();
                addMessage('申し訳ございません。接続エラーが発生しました。お電話（044-789-8413）でお問い合わせください。', 'incoming');
            }
        }

        // Event listeners
        chatSend.addEventListener('click', sendMessage);

        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 100) + 'px';
        });

        // Quick action buttons
        quickActions.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.dataset.message;
                chatInput.value = message;
                sendMessage();
            });
        });

        // Save customer insight when they mention preferences
        function saveCustomerInsight(preference) {
            if (!currentCustomer) return;

            let storedInsights = JSON.parse(localStorage.getItem('yakiniku_insights') || '{}');
            if (!storedInsights[currentCustomer]) {
                storedInsights[currentCustomer] = { preferences: [], note: '' };
            }
            if (!storedInsights[currentCustomer].preferences.includes(preference)) {
                storedInsights[currentCustomer].preferences.push(preference);
            }
            localStorage.setItem('yakiniku_insights', JSON.stringify(storedInsights));
        }

        // Log for debugging
        console.log('💬 Chat Widget Initialized');
        console.log('📊 Customer Insights:', customerInsights);
    }

})();
