/**
 * Cache Reader JavaScript - Phase 1 Capstone Implementation
 * Handles data display from cache readers without triggering AI agent flows
 */

class CacheReader {
    constructor() {
        // CAPSTONE: Reduced update frequency from 30 seconds to 6 hours (4 times per day)
        this.updateInterval = 6 * 60 * 60 * 1000; // 6 hours
        this.isUpdating = false;

        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        console.log('📚 Cache Reader initializing...');
        this.loadInitialData();
        this.startRealTimeUpdates();
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.updateBrotherhoodIntelligence(),
                this.updateAlphaSignals(),
                this.updateAlphaPortfolio()
            ]);
            console.log('✅ Cache Reader initial data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading cache data:', error);
        }
    }

    startRealTimeUpdates() {
        // Update cache data every 30 seconds
        setInterval(async () => {
            if (!this.isUpdating) {
                await this.updateAllCacheData();
            }
        }, this.updateInterval);
    }

    async updateAllCacheData() {
        this.isUpdating = true;
        try {
            await Promise.all([
                this.updateBrotherhoodIntelligence(),
                this.updateAlphaSignals(),
                this.updateAlphaPortfolio()
            ]);
        } catch (error) {
            console.error('❌ Error updating cache data:', error);
        } finally {
            this.isUpdating = false;
        }
    }

    async updateBrotherhoodIntelligence() {
        try {
            const response = await fetch('/api/cache/news/latest-summary');
            const data = await response.json();

            if (data.status === 'success') {
                this.updateBrotherhoodIntelligenceUI(data.data);
            } else {
                this.showError('agent-intelligence-content', 'Failed to load intelligence data');
            }
        } catch (error) {
            console.error('❌ Error fetching brotherhood intelligence:', error);
            this.showError('agent-intelligence-content', 'Network error loading intelligence');
        }
    }

    async updateAlphaSignals() {
        try {
            const response = await fetch('/api/cache/signals/latest');
            const data = await response.json();

            if (data.status === 'success') {
                this.updateAlphaSignalsUI(data.data);
            } else {
                this.showError('market-summary-content', 'Failed to load signals data');
            }
        } catch (error) {
            console.error('❌ Error fetching alpha signals:', error);
            this.showError('market-summary-content', 'Network error loading signals');
        }
    }

    async updateAlphaPortfolio() {
        try {
            const response = await fetch('/api/cache/portfolio/livecoinwatch');
            const data = await response.json();

            if (data.status === 'success') {
                this.updateAlphaPortfolioUI(data.data);
            } else {
                this.showError('portfolio-summary-content', 'Failed to load portfolio data');
            }
        } catch (error) {
            console.error('❌ Error fetching alpha portfolio:', error);
            this.showError('portfolio-summary-content', 'Network error loading portfolio');
        }
    }

    updateBrotherhoodIntelligenceUI(data) {
        const container = document.getElementById('agent-intelligence-content');
        if (!container) return;

        const summary = data.summary;
        const topStories = summary.top_stories;

        let html = `
            <div class="intelligence-header">
                <h4>📰 Latest Market Intelligence</h4>
                <span class="intelligence-phase">Cache Reader</span>
            </div>
            
            <div class="intelligence-stats">
                <div class="stat-item">
                    <div class="stat-value">${summary.total_articles}</div>
                    <div class="stat-label">Articles Processed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${summary.sources.newsapi + summary.sources.tavily}</div>
                    <div class="stat-label">Data Sources</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${summary.sentiment.positive}</div>
                    <div class="stat-label">Positive Sentiment</div>
                </div>
            </div>
            
            <div class="intelligence-insights">
                <div class="insight-item">
                    <div class="insight-type">🔑 Key Insights</div>
                    <ul>
                        ${summary.key_insights.map(insight => `<li>${insight}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="insight-item">
                    <div class="insight-type">📰 Top Stories</div>
                    ${topStories.map(story => `
                        <div class="recommendation-item">
                            <div class="recommendation-header">
                                <span class="symbol">${story.source}</span>
                                <span class="news-sentiment ${story.sentiment}">${story.sentiment}</span>
                            </div>
                            <div class="recommendation-reasons">
                                <div class="reason">${story.title}</div>
                                <div class="reason">${story.summary}</div>
                            </div>
                            <div class="news-meta">
                                <span>${this.formatTime(story.published_at)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    updateAlphaSignalsUI(data) {
        const container = document.getElementById('market-summary-content');
        if (!container) return;

        const signals = data.signals;
        const marketRegime = data.market_regime;

        let html = `
            <div class="market-analysis-header">
                <h4>📈 Today's Alpha Signals</h4>
                <span class="analysis-source">Cache Reader</span>
            </div>
            
            <div class="market-regime">
                <span class="regime-badge ${marketRegime}">${marketRegime}</span>
                <span class="regime-label">Market Regime</span>
            </div>
            
            <div class="opportunities-stats">
                <div class="stat-item">
                    <div class="stat-value">${signals.length}</div>
                    <div class="stat-label">Active Signals</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${(data.overall_confidence * 100).toFixed(0)}%</div>
                    <div class="stat-label">Confidence</div>
                </div>
            </div>
            
            <div class="insights-list">
                ${signals.map(signal => `
                    <div class="recommendation-item">
                        <div class="recommendation-header">
                            <span class="symbol">${signal.symbol}</span>
                            <span class="recommendation-type type-${signal.action.toLowerCase()}">${signal.action}</span>
                            <span class="confidence">${(signal.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div class="recommendation-reasons">
                            <div class="reason">${signal.reasoning}</div>
                        </div>
                        <div class="recommendation-metrics">
                            <span class="metric">RSI: ${signal.technical_indicators.rsi}</span>
                            <span class="metric">MACD: ${signal.technical_indicators.macd}</span>
                            <span class="metric">Target: $${signal.target_price?.toLocaleString()}</span>
                            <span class="metric">Risk: ${signal.risk_level}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = html;
    }

    updateAlphaPortfolioUI(data) {
        const container = document.getElementById('portfolio-summary-content');
        if (!container) return;

        const portfolio = data.portfolio;
        const assets = portfolio.assets;

        let html = `
            <div class="summary-stats">
                <div class="stat-item">
                    <div class="stat-value">$${portfolio.total_value.toLocaleString()}</div>
                    <div class="stat-label">Portfolio Value</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value ${portfolio.total_change_24h >= 0 ? 'roi-positive' : 'roi-negative'}">
                        ${portfolio.total_change_24h >= 0 ? '+' : ''}${portfolio.total_change_24h.toFixed(2)}%
                    </div>
                    <div class="stat-label">24h Change</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value ${portfolio.total_change_7d >= 0 ? 'roi-positive' : 'roi-negative'}">
                        ${portfolio.total_change_7d >= 0 ? '+' : ''}${portfolio.total_change_7d.toFixed(2)}%
                    </div>
                    <div class="stat-label">7d Change</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${assets.length}</div>
                    <div class="stat-label">Assets</div>
                </div>
            </div>
            
            <div class="table-container">
                <table class="portfolio-table">
                    <thead>
                        <tr>
                            <th>Asset</th>
                            <th>Price</th>
                            <th>24h Change</th>
                            <th>Volume</th>
                            <th>Market Cap</th>
                            <th>RSI</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${assets.map(asset => `
                            <tr>
                                <td>
                                    <strong>${asset.symbol}</strong><br>
                                    <small>${asset.name}</small>
                                </td>
                                <td>$${asset.price.toLocaleString()}</td>
                                <td class="${asset.change_24h >= 0 ? 'roi-positive' : 'roi-negative'}">
                                    ${asset.change_24h >= 0 ? '+' : ''}${asset.change_24h.toFixed(2)}%
                                </td>
                                <td>$${this.formatVolume(asset.volume_24h)}</td>
                                <td>$${this.formatVolume(asset.market_cap)}</td>
                                <td>${asset.technical_indicators.rsi}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;
    }

    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="error-message">
                    <span class="error-icon">⚠️</span>
                    <span class="error-text">${message}</span>
                </div>
            `;
        }
    }

    formatTime(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString();
        } catch (error) {
            return timestamp;
        }
    }

    formatVolume(volume) {
        if (volume >= 1e12) {
            return (volume / 1e12).toFixed(2) + 'T';
        } else if (volume >= 1e9) {
            return (volume / 1e9).toFixed(2) + 'B';
        } else if (volume >= 1e6) {
            return (volume / 1e6).toFixed(2) + 'M';
        } else if (volume >= 1e3) {
            return (volume / 1e3).toFixed(2) + 'K';
        } else {
            return volume.toLocaleString();
        }
    }
}

// Initialize cache reader
const cacheReader = new CacheReader(); 
