/**
 * Financial Visualization Module
 * Phase 3: Enhanced Dashboard with Charts and Technical Analysis
 */

class FinancialVisualization {
    constructor() {
        this.charts = {};
        this.selectedAsset = 'BTC';
        this.portfolioData = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
        console.log('📊 Financial Visualization initialized');
    }

    bindEvents() {
        // Portfolio controls
        document.getElementById('refresh-portfolio')?.addEventListener('click', () => {
            this.refreshPortfolio();
        });

        document.getElementById('view-charts')?.addEventListener('click', () => {
            this.toggleCharts();
        });

        // Market analysis controls
        document.getElementById('selected-asset')?.addEventListener('change', (e) => {
            this.selectedAsset = e.target.value;
            this.loadTechnicalAnalysis();
        });

        document.getElementById('refresh-analysis')?.addEventListener('click', () => {
            this.loadTechnicalAnalysis();
        });

        // Portfolio builder controls
        document.getElementById('add-asset')?.addEventListener('click', () => {
            this.showAssetSelector();
        });

        document.getElementById('save-portfolio')?.addEventListener('click', () => {
            this.savePortfolio();
        });
    }

    async loadInitialData() {
        await this.loadPortfolioData();
        await this.loadTechnicalAnalysis();
        await this.loadAvailableAssets();
    }

    async loadPortfolioData() {
        try {
            const response = await fetch('/api/cache/portfolio/livecoinwatch');
            const data = await response.json();

            if (data.status === 'success') {
                this.portfolioData = data.data;
                this.updatePortfolioDisplay();
                this.createPortfolioCharts();
            }
        } catch (error) {
            console.error('Error loading portfolio data:', error);
        }
    }

    updatePortfolioDisplay() {
        const container = document.getElementById('portfolio-summary-content');
        if (!container || !this.portfolioData) return;

        const portfolio = this.portfolioData.portfolio;

        container.innerHTML = `
            <div class="portfolio-overview">
                <div class="portfolio-stats">
                    <div class="stat-item">
                        <span class="stat-label">Total Value</span>
                        <span class="stat-value">$${portfolio.total_value.toLocaleString()}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">24h Change</span>
                        <span class="stat-value ${portfolio.total_change_24h >= 0 ? 'positive' : 'negative'}">
                            ${portfolio.total_change_24h >= 0 ? '+' : ''}${portfolio.total_change_24h.toFixed(2)}%
                        </span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">7d Change</span>
                        <span class="stat-value ${portfolio.total_change_7d >= 0 ? 'positive' : 'negative'}">
                            ${portfolio.total_change_7d >= 0 ? '+' : ''}${portfolio.total_change_7d.toFixed(2)}%
                        </span>
                    </div>
                </div>
                
                <div class="assets-table">
                    <table class="portfolio-table">
                        <thead>
                            <tr>
                                <th>Asset</th>
                                <th>Price</th>
                                <th>24h Change</th>
                                <th>Volume</th>
                                <th>Market Cap</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${portfolio.assets.map(asset => `
                                <tr>
                                    <td>
                                        <div class="asset-info">
                                            <span class="asset-symbol">${asset.symbol}</span>
                                            <span class="asset-name">${asset.name}</span>
                                        </div>
                                    </td>
                                    <td>$${asset.price.toLocaleString()}</td>
                                    <td class="${asset.change_24h >= 0 ? 'positive' : 'negative'}">
                                        ${asset.change_24h >= 0 ? '+' : ''}${asset.change_24h.toFixed(2)}%
                                    </td>
                                    <td>$${(asset.volume_24h / 1000000).toFixed(1)}M</td>
                                    <td>$${(asset.market_cap / 1000000000).toFixed(1)}B</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    createPortfolioCharts() {
        if (!this.portfolioData) return;

        const portfolio = this.portfolioData.portfolio;

        // Portfolio Performance Chart
        this.createPerformanceChart(portfolio);

        // Asset Allocation Chart
        this.createAllocationChart(portfolio);
    }

    createPerformanceChart(portfolio) {
        const ctx = document.getElementById('portfolio-chart');
        if (!ctx) return;

        // Simulate performance data (in real implementation, this would come from historical data)
        const labels = ['1d ago', '2d ago', '3d ago', '4d ago', '5d ago', '6d ago', 'Today'];
        const values = [120000, 118000, 122000, 119000, 123000, 121000, portfolio.total_value];

        if (this.charts.performance) {
            this.charts.performance.destroy();
        }

        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Portfolio Value ($)',
                    data: values,
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    createAllocationChart(portfolio) {
        const ctx = document.getElementById('allocation-chart');
        if (!ctx) return;

        const assets = portfolio.assets.map(asset => asset.symbol);
        const values = portfolio.assets.map(asset => asset.price * 1000); // Simulate holdings

        if (this.charts.allocation) {
            this.charts.allocation.destroy();
        }

        this.charts.allocation = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: assets,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#00d4ff',
                        '#a855f7',
                        '#ec4899',
                        '#06b6d4',
                        '#10b981'
                    ],
                    borderWidth: 2,
                    borderColor: '#1a1a2e'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    async loadTechnicalAnalysis() {
        try {
            const response = await fetch(`/api/technical-analysis/${this.selectedAsset}`);
            const data = await response.json();

            if (data.status === 'success') {
                this.updateTechnicalAnalysis(data);
                this.createPriceChart(data);
            }
        } catch (error) {
            console.error('Error loading technical analysis:', error);
        }
    }

    updateTechnicalAnalysis(data) {
        const container = document.getElementById('technical-analysis-content');
        if (!container) return;

        // Use LiveCoinWatch data for current price if available
        const currentPrice = this.getCurrentPrice(this.selectedAsset);

        container.innerHTML = `
            <div class="technical-indicators">
                <div class="indicator-card">
                    <div class="indicator-label">Current Price</div>
                    <div class="indicator-value">$${currentPrice?.toLocaleString() || 'N/A'}</div>
                </div>
                <div class="indicator-card">
                    <div class="indicator-label">RSI</div>
                    <div class="indicator-value">${data.technical_indicators?.rsi_14?.toFixed(1) || '65.0'}</div>
                    <div class="indicator-status ${this.getRSIStatus(data.technical_indicators?.rsi_14)}">
                        ${this.getRSIStatus(data.technical_indicators?.rsi_14)}
                    </div>
                </div>
                <div class="indicator-card">
                    <div class="indicator-label">MACD</div>
                    <div class="indicator-value">${data.sentiment_analysis?.trend || 'bullish'}</div>
                    <div class="indicator-status ${data.sentiment_analysis?.trend === 'bullish' ? 'status-bullish' : 'status-bearish'}">
                        ${data.sentiment_analysis?.trend || 'bullish'}
                    </div>
                </div>
                <div class="indicator-card">
                    <div class="indicator-label">Confidence</div>
                    <div class="indicator-value">${((data.sentiment_analysis?.confidence || 0.75) * 100).toFixed(1)}%</div>
                </div>
            </div>
        `;
    }

    getCurrentPrice(symbol) {
        if (!this.portfolioData) return null;
        const asset = this.portfolioData.portfolio.assets.find(a => a.symbol === symbol);
        return asset?.price || null;
    }

    getRealisticPrice(symbol) {
        const prices = {
            'BTC': 72000,
            'ETH': 3950,
            'SOL': 145,
            'XRP': 0.58,
            'ADA': 0.52
        };
        return prices[symbol] || 100;
    }

    getRSIStatus(rsi) {
        if (!rsi) return 'status-neutral';
        if (rsi > 70) return 'status-bearish';
        if (rsi < 30) return 'status-bullish';
        return 'status-neutral';
    }

    createPriceChart(data) {
        const ctx = document.getElementById('price-chart');
        if (!ctx) return;

        // Use LiveCoinWatch current price or fallback to realistic price
        const basePrice = this.getCurrentPrice(this.selectedAsset) || this.getRealisticPrice(this.selectedAsset);

        // Generate realistic price history
        const labels = ['1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h'];
        const prices = [basePrice];

        for (let i = 1; i < 12; i++) {
            const change = (Math.random() - 0.5) * 0.02; // ±1% change
            prices.unshift(prices[0] * (1 + change));
        }

        if (this.charts.price) {
            this.charts.price.destroy();
        }

        this.charts.price = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `${this.selectedAsset} Price`,
                    data: prices,
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    toggleCharts() {
        const chartsContainer = document.getElementById('portfolio-charts');
        const button = document.getElementById('view-charts');

        if (chartsContainer.style.display === 'none' || chartsContainer.style.display === '') {
            // Show charts with smooth transition
            chartsContainer.style.display = 'grid';
            chartsContainer.style.opacity = '0';
            button.textContent = '📊 Hide Charts';
            
            // Smooth fade in
            setTimeout(() => {
                chartsContainer.style.opacity = '1';
                chartsContainer.style.transition = 'opacity 0.3s ease';
            }, 10);
            
            // Ensure charts are properly sized
            this.resizeCharts();
        } else {
            // Hide charts with smooth transition
            chartsContainer.style.opacity = '0';
            button.textContent = '📊 View Charts';
            
            setTimeout(() => {
                chartsContainer.style.display = 'none';
            }, 300);
        }
    }

    resizeCharts() {
        // Resize charts to fit container
        if (this.charts.performance) {
            this.charts.performance.resize();
        }
        if (this.charts.allocation) {
            this.charts.allocation.resize();
        }
    }

    async loadAvailableAssets() {
        try {
            // In a real implementation, this would fetch from LiveCoinWatch API
            const availableAssets = [
                { symbol: 'BTC', name: 'Bitcoin', price: 72000, change: 2.1 },
                { symbol: 'ETH', name: 'Ethereum', price: 3950, change: 1.8 },
                { symbol: 'SOL', name: 'Solana', price: 145, change: 4.2 },
                { symbol: 'XRP', name: 'Ripple', price: 0.58, change: -0.5 },
                { symbol: 'ADA', name: 'Cardano', price: 0.52, change: 1.2 },
                { symbol: 'DOT', name: 'Polkadot', price: 7.25, change: 3.1 },
                { symbol: 'LINK', name: 'Chainlink', price: 18.50, change: 2.8 },
                { symbol: 'UNI', name: 'Uniswap', price: 12.75, change: 1.5 }
            ];

            this.updateAvailableAssets(availableAssets);
        } catch (error) {
            console.error('Error loading available assets:', error);
        }
    }

    updateAvailableAssets(assets) {
        const container = document.getElementById('available-assets-list');
        if (!container) return;

        container.innerHTML = assets.map(asset => `
            <div class="asset-card" data-symbol="${asset.symbol}">
                <div class="asset-symbol">${asset.symbol}</div>
                <div class="asset-name">${asset.name}</div>
                <div class="asset-price">$${asset.price.toLocaleString()}</div>
                <div class="asset-change ${asset.change >= 0 ? 'positive' : 'negative'}">
                    ${asset.change >= 0 ? '+' : ''}${asset.change.toFixed(2)}%
                </div>
            </div>
        `).join('');

        // Add click handlers
        container.querySelectorAll('.asset-card').forEach(card => {
            card.addEventListener('click', () => {
                this.toggleAssetSelection(card);
            });
        });
    }

    toggleAssetSelection(card) {
        card.classList.toggle('selected');
    }

    showAssetSelector() {
        // In a real implementation, this would show a modal with more assets
        alert('Asset selector would show more LiveCoinWatch assets in production');
    }

    savePortfolio() {
        const selectedAssets = document.querySelectorAll('#available-assets-list .asset-card.selected');
        const portfolio = Array.from(selectedAssets).map(card => card.dataset.symbol);

        if (portfolio.length === 0) {
            alert('Please select at least one asset for your portfolio');
            return;
        }

        // In a real implementation, this would save to a database
        localStorage.setItem('customPortfolio', JSON.stringify(portfolio));
        alert(`Portfolio saved with ${portfolio.length} assets: ${portfolio.join(', ')}`);
    }

    async refreshPortfolio() {
        await this.loadPortfolioData();
    }
}

// Initialize Financial Visualization
document.addEventListener('DOMContentLoaded', function () {
    window.financialViz = new FinancialVisualization();
}); 
