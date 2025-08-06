/**
 * Enhanced Dashboard JavaScript - Phase 6 MVP UI Polish
 * Real-time data updates and enhanced UI components with Phase 4 & 5 integration
 */

class EnhancedDashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.marketUpdateInterval = 15000; // 15 seconds
        this.newsUpdateInterval = 60000; // 1 minute
        this.adminUpdateInterval = 120000; // 2 minutes
        this.isUpdating = false;
        this.currentPhase = "6";

        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        console.log('🚀 Enhanced Dashboard Phase 6 initializing...');
        this.startRealTimeUpdates();
        this.loadInitialData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add refresh buttons
        this.addRefreshButtons();

        // Add phase indicator
        this.updatePhaseIndicator();
    }

    addRefreshButtons() {
        const cards = document.querySelectorAll('.liquid-card');
        cards.forEach(card => {
            const header = card.querySelector('h3');
            if (header) {
                const refreshBtn = document.createElement('button');
                refreshBtn.className = 'refresh-btn';
                refreshBtn.innerHTML = '🔄';
                refreshBtn.title = 'Refresh data';
                refreshBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.refreshCardData(card.id || card.className);
                };
                header.appendChild(refreshBtn);
            }
        });
    }

    updatePhaseIndicator() {
        const header = document.querySelector('.liquid-header');
        if (header) {
            const phaseBadge = document.createElement('div');
            phaseBadge.className = 'phase-badge';
            phaseBadge.innerHTML = `Phase ${this.currentPhase}`;
            header.appendChild(phaseBadge);
        }
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.updatePortfolioData(),
                this.updateOpportunitiesData(),
                this.updateNewsData(),
                this.updateAdminStatus()
            ]);
            console.log('✅ Phase 6 initial data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
        }
    }

    startRealTimeUpdates() {
        // Portfolio updates
        setInterval(async () => {
            if (!this.isUpdating) {
                await this.updatePortfolioData();
            }
        }, this.updateInterval);

        // Opportunities updates (Phase 4)
        setInterval(async () => {
            if (!this.isUpdating) {
                await this.updateOpportunitiesData();
            }
        }, this.marketUpdateInterval);

        // News updates
        setInterval(async () => {
            if (!this.isUpdating) {
                await this.updateNewsData();
            }
        }, this.newsUpdateInterval);

        // Admin status updates (Phase 5)
        setInterval(async () => {
            if (!this.isUpdating) {
                await this.updateAdminStatus();
            }
        }, this.adminUpdateInterval);

        console.log('🔄 Phase 6 real-time updates started');
    }

    async refreshCardData(cardType) {
        console.log(`🔄 Refreshing ${cardType} data...`);

        switch (cardType) {
            case 'portfolio-summary':
                await this.updatePortfolioData();
                break;
            case 'agent-insights':
                await this.updateOpportunitiesData();
                break;
            case 'market-analysis':
                await this.updateOpportunitiesData();
                break;
            case 'news-insights':
                await this.updateNewsData();
                break;
            default:
                await this.updatePortfolioData();
        }
    }

    async updatePortfolioData() {
        try {
            this.isUpdating = true;
            // Use cache reader endpoint instead of full AI agent
            const response = await fetch('/api/cache/portfolio/livecoinwatch');
            const data = await response.json();

            if (data.status === 'success') {
                this.updatePortfolioUI(data.data);
                // Update technical indicators from cache data
                if (data.data.portfolio && data.data.portfolio.assets) {
                    const indicators = {};
                    data.data.portfolio.assets.forEach(asset => {
                        indicators[asset.symbol] = asset.technical_indicators;
                    });
                    this.updateTechnicalIndicators(indicators);
                }
            } else {
                throw new Error('Cache data not available');
            }

        } catch (error) {
            console.error('❌ Error updating portfolio data:', error);
            this.showError('portfolio-summary-content', 'Portfolio data temporarily unavailable');
        } finally {
            this.isUpdating = false;
        }
    }

    async updateOpportunitiesData() {
        try {
            this.isUpdating = true;
            // Use cache reader endpoint instead of full AI agent
            const response = await fetch('/api/cache/signals/latest');
            const data = await response.json();

            if (data.status === 'success') {
                this.updateOpportunitiesUI(data.data);
                this.updateMarketAnalysis(data.data);
            } else {
                throw new Error('Cache data not available');
            }

        } catch (error) {
            console.error('❌ Error updating opportunities data:', error);
            this.showError('market-summary-content', 'Market analysis temporarily unavailable');
        } finally {
            this.isUpdating = false;
        }
    }

    async updateNewsData() {
        try {
            this.isUpdating = true;
            // Use cache reader endpoint instead of full AI agent
            const response = await fetch('/api/cache/news/latest-summary');
            const data = await response.json();

            if (data.status === 'success') {
                this.updateNewsUI(data.data);
                this.updateSentimentAnalysis(data.data.summary.sentiment);
            } else {
                throw new Error('Cache data not available');
            }

        } catch (error) {
            console.error('❌ Error updating news data:', error);
            this.showError('news-insights-content', 'News data temporarily unavailable');
        } finally {
            this.isUpdating = false;
        }
    }

    async updateAdminStatus() {
        try {
            this.isUpdating = true;
            const response = await fetch('/api/admin/mvp-status');
            const data = await response.json();

            this.updateSystemStatus(data);

        } catch (error) {
            console.error('❌ Error updating admin status:', error);
        } finally {
            this.isUpdating = false;
        }
    }

    updatePortfolioUI(data) {
        const summaryDiv = document.getElementById('portfolio-summary-content');
        if (!summaryDiv) return;

        // Handle cache data structure
        const portfolio = data.portfolio || data;
        const totalValue = portfolio.total_value || data.total_value_usdt || 0;
        const assets = portfolio.assets || data.assets || [];
        const dataSource = 'LIVECOINWATCH';
        const enhancedFeatures = true;

        let html = `
            <div class="portfolio-overview">
                <div class="summary-stats">
                    <div class="stat-item">
                        <div class="stat-value">${this.formatCurrency(totalValue)}</div>
                        <div class="stat-label">Total Value</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${assets.length}</div>
                        <div class="stat-label">Assets</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${dataSource.toUpperCase()}</div>
                        <div class="stat-label">Data Source</div>
                    </div>
                    ${enhancedFeatures ? `
                    <div class="stat-item">
                        <div class="stat-value">🚀</div>
                        <div class="stat-label">Enhanced</div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;

        if (assets.length > 0) {
            html += `
                <div class="table-container">
                    <table class="portfolio-table">
                        <thead>
                            <tr>
                                <th>Asset</th>
                                <th>Price</th>
                                <th>24h Change</th>
                                <th>Volume</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            assets.forEach(asset => {
                const change24h = asset.change_24h || 0;
                const changeClass = change24h > 0 ? 'roi-positive' : change24h < 0 ? 'roi-negative' : 'roi-neutral';

                html += `
                    <tr>
                        <td>
                            <strong>${asset.symbol}</strong><br>
                            <small>${asset.name}</small>
                        </td>
                        <td>$${asset.price?.toLocaleString() || '0'}</td>
                        <td class="${changeClass}">${change24h >= 0 ? '+' : ''}${change24h.toFixed(2)}%</td>
                        <td>$${this.formatVolume(asset.volume_24h)}</td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
        }

        summaryDiv.innerHTML = html;
    }

    updatePriceTickers(livePrices) {
        const tickerContainer = document.querySelector('.price-ticker');
        if (!tickerContainer || !livePrices || livePrices.length === 0) return;

        let html = '';
        livePrices.forEach(price => {
            const change = price.change_24h || 0;
            const changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';

            html += `
                <div class="ticker-item" data-symbol="${price.symbol}">
                    <span class="symbol">${price.symbol}</span>
                    <span class="price">${this.formatCurrency(price.price)}</span>
                    <span class="change ${changeClass}">${this.formatROI(change)}</span>
                </div>
            `;
        });

        tickerContainer.innerHTML = html;
    }

    updateTechnicalIndicators(indicators) {
        const indicatorsContainer = document.querySelector('.technical-indicators');
        if (!indicatorsContainer || !indicators) return;

        let html = '';
        Object.entries(indicators).forEach(([symbol, data]) => {
            const rsi = data.rsi_14 || 50;
            const rsiClass = rsi < 30 ? 'oversold' : rsi > 70 ? 'overbought' : 'neutral';

            html += `
                <div class="indicator" data-symbol="${symbol}">
                    <span class="label">${symbol} RSI</span>
                    <span class="value">${rsi.toFixed(1)}</span>
                    <span class="status ${rsiClass}">${rsiClass}</span>
                </div>
            `;
        });

        indicatorsContainer.innerHTML = html;
    }

    updateAIInsights(aiAnalysis) {
        const insightsContainer = document.querySelector('.ai-insights');
        if (!insightsContainer || !aiAnalysis) return;

        let html = '';
        if (aiAnalysis.error) {
            html = `
                <div class="insight-item error">
                    <span class="icon">⚠️</span>
                    <span class="text">AI analysis temporarily unavailable</span>
                </div>
            `;
        } else {
            html = `
                <div class="insight-item">
                    <span class="icon">🧠</span>
                    <span class="text">AI analysis completed</span>
                    <span class="confidence">85%</span>
                </div>
            `;
        }

        insightsContainer.innerHTML = html;
    }

    updateOpportunitiesUI(data) {
        const opportunitiesDiv = document.getElementById('market-summary-content');
        if (!opportunitiesDiv) return;

        // Handle cache data structure
        const signals = data.signals || data.opportunities || [];
        const marketRegime = data.market_regime || 'neutral';
        const overallConfidence = data.overall_confidence || 0.5;

        let html = `
            <div class="market-overview">
                <div class="market-regime">
                    <span class="regime-badge ${marketRegime}">${marketRegime.toUpperCase()}</span>
                    <span class="regime-label">Market Regime</span>
                </div>
                <div class="opportunities-stats">
                    <div class="stat-item">
                        <div class="stat-value">${signals.length}</div>
                        <div class="stat-label">Active Signals</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${(overallConfidence * 100).toFixed(0)}%</div>
                        <div class="stat-label">Confidence</div>
                    </div>
                </div>
            </div>
        `;

        if (signals.length > 0) {
            html += '<div class="opportunities-list">';
            signals.forEach(signal => {
                const typeClass = signal.action === 'BUY' ? 'type-buy' : signal.action === 'SELL' ? 'type-sell' : 'type-hold';

                html += `
                    <div class="recommendation-item">
                        <div class="recommendation-type ${typeClass}">${signal.action}</div>
                        <div class="recommendation-header">
                            <span class="symbol">${signal.symbol}</span>
                            <span class="confidence">${(signal.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div class="recommendation-reasons">
                            <div class="reason">${signal.reasoning}</div>
                        </div>
                        <div class="recommendation-metrics">
                            <span class="metric">RSI: ${signal.technical_indicators?.rsi || 'N/A'}</span>
                            <span class="metric">MACD: ${signal.technical_indicators?.macd || 'N/A'}</span>
                            <span class="metric">Target: $${signal.target_price?.toLocaleString() || 'N/A'}</span>
                            <span class="metric">Risk: ${signal.risk_level || 'N/A'}</span>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        } else {
            html += '<div class="no-opportunities">No trading signals available at this time.</div>';
        }

        opportunitiesDiv.innerHTML = html;
    }

    updateMarketAnalysis(data) {
        const analysisDiv = document.getElementById('market-analysis-content');
        if (!analysisDiv) return;

        const marketInsights = data.market_insights || [];
        const aiAnalysis = data.ai_analysis || {};

        let html = `
            <div class="market-analysis-header">
                <h4>Market Intelligence</h4>
                <span class="analysis-source">AI Powered</span>
            </div>
        `;

        if (marketInsights.length > 0) {
            html += '<div class="insights-list">';
            marketInsights.forEach(insight => {
                html += `
                    <div class="insight-item">
                        <div class="insight-type">${insight.type}</div>
                        <div class="insight-content">
                            <strong>${insight.symbol}</strong>: ${insight.insight}
                        </div>
                        <div class="insight-confidence">${(insight.confidence * 100).toFixed(0)}% confidence</div>
                    </div>
                `;
            });
            html += '</div>';
        }

        if (aiAnalysis.market_regime) {
            html += `
                <div class="ai-analysis">
                    <div class="ai-header">AI Market Analysis</div>
                    <div class="ai-content">${aiAnalysis.market_regime.current_regime || 'neutral'} market conditions detected</div>
                </div>
            `;
        }

        analysisDiv.innerHTML = html;
    }

    updateAgentIntelligence(data) {
        const intelligenceDiv = document.getElementById('agent-intelligence-content');
        if (!intelligenceDiv) return;

        const opportunities = data.opportunities || [];
        const statistics = data.statistics || {};

        let html = `
            <div class="intelligence-header">
                <h4>Brotherhood Intelligence</h4>
                <span class="intelligence-phase">Phase ${data.phase || '4'}</span>
            </div>
        `;

        if (opportunities.length > 0) {
            html += `
                <div class="intelligence-stats">
                    <div class="stat-item">
                        <div class="stat-value">${statistics.total_analyzed || 0}</div>
                        <div class="stat-label">Symbols Analyzed</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${statistics.total_opportunities || 0}</div>
                        <div class="stat-label">Opportunities Found</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${(statistics.average_confidence * 100).toFixed(0)}%</div>
                        <div class="stat-label">AI Confidence</div>
                    </div>
                </div>
            `;

            html += '<div class="intelligence-insights">';
            opportunities.slice(0, 3).forEach(opp => {
                html += `
                    <div class="insight-item">
                        <div class="insight-type">${opp.type} OPPORTUNITY</div>
                        <div class="insight-content">
                            <strong>${opp.symbol}</strong> shows strong ${opp.type.toLowerCase()} signals with ${(opp.confidence * 100).toFixed(0)}% confidence
                        </div>
                        <div class="insight-reasons">
                            ${opp.reasons ? opp.reasons.slice(0, 1).map(reason => `<div class="reason">• ${reason}</div>`).join('') : ''}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        } else {
            html += '<div class="no-insights">AI analysis in progress...</div>';
        }

        intelligenceDiv.innerHTML = html;
    }

    updateNewsUI(data) {
        const newsDiv = document.getElementById('news-insights-content');
        if (!newsDiv) return;

        // Handle cache data structure
        const summary = data.summary || data;
        const articles = summary.top_stories || data.articles || [];
        const sources = ['NEWSAPI', 'TAVILY'];
        const totalArticles = summary.total_articles || 0;

        let html = `
            <div class="news-header">
                <div class="news-sources">
                    ${sources.map(source => `<span class="source-badge ${source}">${source}</span>`).join('')}
                </div>
                <div class="quality-metrics">
                    <span class="metric">Articles: ${totalArticles}</span>
                    <span class="metric">Cache: Active</span>
                </div>
            </div>
        `;

        if (articles.length > 0) {
            html += '<div class="news-list">';
            articles.forEach(article => {
                const sentiment = article.sentiment || 'neutral';
                const sentimentClass = sentiment === 'positive' ? 'positive' :
                    sentiment === 'negative' ? 'negative' : 'neutral';

                html += `
                    <div class="news-item">
                        <div class="news-title">${article.title}</div>
                        <div class="news-meta">
                            <span class="news-source">${article.source || 'Unknown'}</span>
                            <span class="news-time">${this.formatTime(article.published_at)}</span>
                            <span class="news-sentiment ${sentimentClass}">${sentiment}</span>
                        </div>
                        <div class="news-summary">${article.summary}</div>
                    </div>
                `;
            });
            html += '</div>';
        } else {
            html += '<div class="no-news">No recent news articles available.</div>';
        }

        newsDiv.innerHTML = html;
    }

    updateSentimentAnalysis(sentiment) {
        const sentimentContainer = document.querySelector('.sentiment-analysis');
        if (!sentimentContainer || !sentiment) return;

        // Simple sentiment visualization
        const sentimentValue = sentiment.overall_sentiment || 'neutral';
        const sentimentClass = sentimentValue === 'bullish' ? 'positive' :
            sentimentValue === 'bearish' ? 'negative' : 'neutral';

        const html = `
            <div class="sentiment-display">
                <div class="sentiment-label">Market Sentiment: <span class="${sentimentClass}">${sentimentValue}</span></div>
                <div class="sentiment-bar">
                    <div class="sentiment-${sentimentClass}" style="width: 100%"></div>
                </div>
            </div>
        `;

        sentimentContainer.innerHTML = html;
    }

    updateSystemStatus(data) {
        // Update system status in a subtle way
        const systemHealth = data.system_health || 'unknown';
        const currentPhase = data.current_phase || '5';

        // Add system status to header if not already present
        let statusIndicator = document.querySelector('.system-status');
        if (!statusIndicator) {
            const header = document.querySelector('.liquid-header');
            if (header) {
                statusIndicator = document.createElement('div');
                statusIndicator.className = 'system-status';
                header.appendChild(statusIndicator);
            }
        }

        if (statusIndicator) {
            const healthClass = systemHealth === 'healthy' ? 'healthy' :
                systemHealth === 'degraded' ? 'degraded' : 'unhealthy';

            statusIndicator.innerHTML = `
                <span class="status-badge ${healthClass}">
                    ${systemHealth.toUpperCase()} | Phase ${currentPhase}
                </span>
            `;
        }
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

    formatCurrency(amount) {
        if (!amount || amount === 0) return '$0.00';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    formatROI(roi) {
        if (roi === null || roi === undefined) return '-';
        const val = Number(roi).toFixed(2);
        return (roi > 0 ? '+' : '') + val + '%';
    }

    formatVolume(volume) {
        if (!volume) return '-';
        if (volume >= 1e9) return (volume / 1e9).toFixed(1) + 'B';
        if (volume >= 1e6) return (volume / 1e6).toFixed(1) + 'M';
        if (volume >= 1e3) return (volume / 1e3).toFixed(1) + 'K';
        return volume.toFixed(0);
    }

    formatTime(timestamp) {
        if (!timestamp) return 'Unknown';
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

        if (diffHours < 1) return 'Just now';
        if (diffHours < 24) return `${diffHours}h ago`;
        return date.toLocaleDateString();
    }
}

// Initialize enhanced dashboard
const enhancedDashboard = new EnhancedDashboard(); 
