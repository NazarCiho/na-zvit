document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded'); // Перевірка завантаження скрипта

    // Функціонал для цін
    async function updatePrices() {
        const priceElements = document.querySelectorAll('.price-value');
        for (let element of priceElements) {
            const symbol = element.dataset.symbol;
            try {
                const response = await fetch(`https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`);
                const data = await response.json();
                const balanceElement = element.closest('.asset-item').querySelector('.asset-balance');
                const balance = parseFloat(balanceElement.textContent);
                const price = parseFloat(data.price);
                const value = (balance * price).toFixed(2);
                element.textContent = value;
            } catch (error) {
                console.error(`Error fetching price for ${symbol}:`, error);
            }
        }
    }

    // Оновлення цін
    updatePrices();
    setInterval(updatePrices, 10000);

    // Перемикання вкладок
    const tabBtns = document.querySelectorAll('.tab-btn');
    console.log('Tab buttons:', tabBtns.length); // Перевірка знайдених кнопок

    tabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            console.log('Tab clicked:', btn.dataset.tab); // Перевірка кліку
            e.preventDefault();

            // Знімаємо активний клас з усіх кнопок і контенту
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Додаємо активний клас вибраній вкладці
            btn.classList.add('active');
            const tabId = btn.dataset.tab;
            const targetTab = document.getElementById(tabId);
            console.log('Target tab:', tabId, targetTab); // Перевірка цільової вкладки
            if (targetTab) {
                targetTab.classList.add('active');
            }
        });
    });

    // Функціонал фільтрів
    const filters = document.querySelectorAll('.filter-select, .date-input');
    console.log('Filters found:', filters.length); // Перевірка знайдених фільтрів

    filters.forEach(filter => {
        filter.addEventListener('change', (e) => {
            console.log('Filter changed:', e.target.id); // Перевірка зміни фільтра
            
            const activeTab = document.querySelector('.tab-content.active');
            if (activeTab.id === 'transactions') {
                filterTransactions();
            } else if (activeTab.id === 'orders') {
                filterOrders();
            }
        });
    });

    // Фільтрація транзакцій
    function filterTransactions() {
        const typeFilter = document.getElementById('type-filter').value;
        const statusFilter = document.getElementById('status-filter').value;
        const dateFrom = document.getElementById('date-from').value;
        const dateTo = document.getElementById('date-to').value;

        console.log('Filtering with:', { typeFilter, statusFilter, dateFrom, dateTo }); // Для дебагу

        const rows = document.querySelectorAll('#transactions tbody tr:not(.empty-table)');
        
        rows.forEach(row => {
            // Змінюємо селектор, щоб отримати саме текст "Купівля" або "Продаж"
            const type = row.querySelector('.type-cell .type-badge').textContent.trim();
            const status = row.querySelector('.status-badge').textContent.trim();
            const date = row.querySelector('td:first-child').textContent;

            console.log('Row data:', { type, status, date }); // Для дебагу

            let showRow = true;

            if (typeFilter !== 'all') {
                // Перевіряємо відповідність українським словам
                if (typeFilter === 'buy' && type !== 'Купівля') {
                    showRow = false;
                }
                if (typeFilter === 'sell' && type !== 'Продаж') {
                    showRow = false;
                }
            }

            if (statusFilter !== 'all' && !status.toLowerCase().includes(statusFilter.toLowerCase())) {
                showRow = false;
            }

            if (dateFrom && new Date(date) < new Date(dateFrom)) {
                showRow = false;
            }

            if (dateTo && new Date(date) > new Date(dateTo)) {
                showRow = false;
            }

            row.style.display = showRow ? '' : 'none';
        });

        // Показуємо повідомлення про відсутність результатів
        const visibleRows = document.querySelectorAll('#transactions tbody tr:not(.empty-table):not([style*="display: none"])');
        const emptyMessage = document.querySelector('#transactions .empty-table');
        if (visibleRows.length === 0 && emptyMessage) {
            emptyMessage.style.display = '';
        } else if (emptyMessage) {
            emptyMessage.style.display = 'none';
        }
    }

    // Фільтрація ордерів
    function filterOrders() {
        const typeFilter = document.getElementById('order-type-filter').value;
        const statusFilter = document.getElementById('order-status-filter').value;

        const rows = document.querySelectorAll('#orders tbody tr:not(.empty-table)');
        
        rows.forEach(row => {
            const type = row.querySelector('.order-type-badge').textContent.trim();
            const status = row.querySelector('.status-badge').textContent.trim();

            let showRow = true;

            if (typeFilter !== 'all' && !type.toLowerCase().includes(typeFilter.toLowerCase())) {
                showRow = false;
            }

            if (statusFilter !== 'all' && !status.toLowerCase().includes(statusFilter.toLowerCase())) {
                showRow = false;
            }

            row.style.display = showRow ? '' : 'none';
        });

        // Показуємо повідомлення про відсутність результатів
        const visibleRows = document.querySelectorAll('#orders tbody tr:not(.empty-table):not([style*="display: none"])');
        const emptyMessage = document.querySelector('#orders .empty-table');
        if (visibleRows.length === 0 && emptyMessage) {
            emptyMessage.style.display = '';
        } else if (emptyMessage) {
            emptyMessage.style.display = 'none';
        }
    }

    // Скасування ордеру
    document.querySelectorAll('.cancel-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const orderId = this.dataset.orderId;
            try {
                const response = await fetch(`/trade/cancel-order/${orderId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                if (response.ok) {
                    // Оновлюємо сторінку після успішного скасування
                    window.location.reload();
                } else {
                    alert('Помилка при скасуванні ордеру');
                }
            } catch (error) {
                console.error('Error cancelling order:', error);
                alert('Помилка при скасуванні ордеру');
            }
        });
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Filter Handlers
    const typeFilter = document.getElementById('type-filter');
    const statusFilter = document.getElementById('status-filter');
    const dateFrom = document.getElementById('date-from');
    const dateTo = document.getElementById('date-to');

    [typeFilter, statusFilter, dateFrom, dateTo].forEach(filter => {
        filter.addEventListener('change', () => {
            // Add logic to filter transactions/orders
            applyFilters();
        });
    });

    function applyFilters() {
        // Add your filter logic here
        console.log('Filters applied');
    }

    const searchInput = document.getElementById('assetSearch');
    const assetRows = document.querySelectorAll('.asset-row');
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        
        assetRows.forEach(row => {
            const assetName = row.querySelector('.asset-name').textContent.toLowerCase();
            if (assetName.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });

    updatePrices();
    // Оновлюємо ціни кожні 10 секунд
    setInterval(updatePrices, 10000);

    // Balance visibility toggle
    const toggleButton = document.querySelector('.toggle-balance');
    if (toggleButton) {
        // Перевіряємо збережений стан
        const isHidden = localStorage.getItem('balanceHidden') === 'true';
        updateBalanceVisibility(isHidden);

        toggleButton.addEventListener('click', () => {
            const isCurrentlyHidden = toggleButton.classList.contains('hidden');
            updateBalanceVisibility(!isCurrentlyHidden);
            // Зберігаємо стан
            localStorage.setItem('balanceHidden', (!isCurrentlyHidden).toString());
        });
    }

    function updateBalanceVisibility(hide) {
        const toggleButton = document.querySelector('.toggle-balance');
        const valueElements = document.querySelectorAll('.balance-value');
        const hiddenElements = document.querySelectorAll('.balance-hidden');
        
        if (hide) {
            toggleButton.classList.add('hidden');
            toggleButton.querySelector('i').classList.remove('fa-eye');
            toggleButton.querySelector('i').classList.add('fa-eye-slash');
            valueElements.forEach(el => el.style.display = 'none');
            hiddenElements.forEach(el => el.style.display = 'inline');
        } else {
            toggleButton.classList.remove('hidden');
            toggleButton.querySelector('i').classList.remove('fa-eye-slash');
            toggleButton.querySelector('i').classList.add('fa-eye');
            valueElements.forEach(el => el.style.display = 'inline');
            hiddenElements.forEach(el => el.style.display = 'none');
        }
    }
}); 