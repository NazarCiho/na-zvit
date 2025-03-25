async function updateCryptoPrices() {
    try {
        // Отримуємо дані для BTC і ETH
        const [btcResponse, ethResponse] = await Promise.all([
            fetch('https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT'),
            fetch('https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT')
        ]);

        const btcData = await btcResponse.json();
        const ethData = await ethResponse.json();

        // Оновлюємо ціни BTC
        const btcPrice = parseFloat(btcData.lastPrice).toFixed(2);
        const btcChange = parseFloat(btcData.priceChangePercent).toFixed(2);
        const btcPriceElement = document.querySelector('.btc-price');
        const btcChangeElement = document.querySelector('.btc-change');

        if (btcPriceElement) {
            btcPriceElement.textContent = `$${btcPrice}`;
            btcPriceElement.className = `price ${btcChange >= 0 ? 'up' : 'down'}`;
        }
        if (btcChangeElement) {
            btcChangeElement.textContent = `${btcChange}%`;
            btcChangeElement.className = `change ${btcChange >= 0 ? 'up' : 'down'}`;
        }

        // Оновлюємо ціни ETH
        const ethPrice = parseFloat(ethData.lastPrice).toFixed(2);
        const ethChange = parseFloat(ethData.priceChangePercent).toFixed(2);
        const ethPriceElement = document.querySelector('.eth-price');
        const ethChangeElement = document.querySelector('.eth-change');

        if (ethPriceElement) {
            ethPriceElement.textContent = `$${ethPrice}`;
            ethPriceElement.className = `price ${ethChange >= 0 ? 'up' : 'down'}`;
        }
        if (ethChangeElement) {
            ethChangeElement.textContent = `${ethChange}%`;
            ethChangeElement.className = `change ${ethChange >= 0 ? 'up' : 'down'}`;
        }
    } catch (error) {
        console.error('Error fetching crypto prices:', error);
    }
}

// Оновлюємо ціни кожні 5 секунд
updateCryptoPrices();
setInterval(updateCryptoPrices, 5000); 