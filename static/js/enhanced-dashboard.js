/**
 * Enhanced Dashboard JavaScript
 * Real-time data updates and enhanced UI components
 */

class EnhancedDashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.marketUpdateInterval = 15000; // 15 seconds
        this.newsUpdateInterval = 60000; // 1 minute
        this.isUpdating = false;
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        console.log('🚀 Enhanced Dashboard initializing...');
        this.startRealTimeUpdates();
        this.loadInitialData();
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.updatePortfolioData(),
                this.updateMarketData(),
                this.updateNewsData()
            ]);
            console.log('✅ Initial data loaded successfully');
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
        
        // Market data updates
        setInterval(async () => {
            if (!this.isUpdating) {
                await this.updateMarketData();
            }
        }, this.marketUpdateInterval);
        
        // News updates
        setInterval(async () => {
            if (!this.isUpdating) {
                await this.updateNewsData();
            }
        }, this.newsUpdateInterval);
        
        console.log('🔄 Real-time updates started');
    }
    
    async updatePortfolioData() {
        try {
            this.isUpdating = true;
            const response = await fetch('/api/portfolio');
            const data = await response.json();
            
            this.updatePortfolioUI(data);
            this.updatePriceTickers(data.live_prices);
            this.updateTechnicalIndicators(data.technical_indicators);
            this.updateAIInsights(data.ai_analysis);
            
        } catch (error) {
            console.error('❌ Error updating portfolio data:', error);
        } finally {
            this.isUpdating = false;
        }
    }
    
    async updateMarketData() {
        try {
            this.isUpdating = true;
            const response = await fetch('/api/opportunities');
            const data = await response.json();
            
            this.updateOpportunitiesUI(data);
            this.updateTechnicalAnalysis(data.technical_data);
            
        } catch (error) {
            console.error('❌ Error updating market data:', error);
        } finally {
            this.isUpdating = false;
        }
    }
    
    async updateNewsData() {
        try {
            this.isUpdating = true;
            const response = await fetch('/api/news-briefing');
            const data = await response.json();
            
            this.updateNewsUI(data);
            this.updateSentimentAnalysis(data.sentiment_analysis);
            
        } catch (error) {
            console.error('❌ Error updating news data:', error);
        } finally {
            this.isUpdating = false;
        }
    }
    
    updatePortfolioUI(data) {
        const summaryDiv = document.getElementById('portfolio-summary-content');
        if (!summaryDiv) return;
        
        const totalValue = data.total_value_usdt || 0;
        const assets = data.assets || [];
        const dataSource = data.data_source || 'unknown';
        const enhancedFeatures = data.enhanced_features !== false;
        
        let html = `
            <div class="portfolio-overview">
                <div class="total-value">
                    <span class="value">${this.formatCurrency(totalValue)}</span>
                    <span class="label">Total Portfolio Value</span>
                </div>
                <div class="data-source">
                    <span class="source-badge ${dataSource}">${dataSource.toUpperCase()}</span>
                    ${enhancedFeatures ? '<span class="enhanced-badge">Enhanced</span>' : ''}
                </div>
            </div>
        `;
        
        if (assets.length > 0) {
            html += '<div class="assets-list">';
            assets.forEach(asset => {
                const roi = asset.roi_percentage || 0;
                const roiClass = roi > 0 ? 'positive' : roi < 0 ? 'negative' : 'neutral';
                
                html += `
                    <div class="asset-item">
                        <div class="asset-info">
                            <span class="symbol">${asset.asset}</span>
                            <span class="amount">${asset.total}</span>
                        </div>
                        <div class="asset-value">
                            <span class="usdt-value">${this.formatCurrency(asset.usdt_value)}</span>
                            <span class="roi ${roiClass}">${this.formatROI(roi)}</span>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
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
        const opportunitiesDiv = document.getElementById('opportunities-content');
        if (!opportunitiesDiv) return;
        
        const opportunities = data.opportunities || [];
        const technicalData = data.technical_data || {};
        const aiAnalysis = data.ai_analysis || {};
        
        let html = `
            <div class="opportunities-header">
                <span class="total">${data.total_opportunities || 0} opportunities</span>
                <span class="indicators">${data.indicators_available || 0} indicators</span>
                ${data.ai_available ? '<span class="ai-badge">AI Powered</span>' : ''}
            </div>
        `;
        
        if (opportunities.length > 0) {
            html += '<div class="opportunities-list">';
            opportunities.forEach(opp => {
                const actionClass = opp.action === 'buy' ? 'buy' : opp.action === 'sell' ? 'sell' : 'hold';
                
                html += `
                    <div class="opportunity-item ${actionClass}">
                        <div class="opportunity-header">
                            <span class="symbol">${opp.symbol}</span>
                            <span class="action ${actionClass}">${opp.action.toUpperCase()}</span>
                            <span class="confidence">${(opp.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div class="opportunity-reason">${opp.reason}</div>
                        <div class="technical-summary">
                            ${this.formatTechnicalSummary(opp.technical_indicators)}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        } else {
            html += '<div class="no-opportunities">No trading opportunities available at this time.</div>';
        }
        
        opportunitiesDiv.innerHTML = html;
    }
    
    updateTechnicalAnalysis(technicalData) {
        const analysisContainer = document.querySelector('.technical-analysis');
        if (!analysisContainer || !technicalData) return;
        
        let html = '';
        Object.entries(technicalData).forEach(([symbol, data]) => {
            const rsi = data.rsi_14 || 50;
            const macd = data.macd || {};
            const bb = data.bollinger_bands || {};
            
            html += `
                <div class="analysis-item" data-symbol="${symbol}">
                    <span class="symbol">${symbol}</span>
                    <div class="indicators">
                        <span class="indicator rsi">RSI: ${rsi.toFixed(1)}</span>
                        <span class="indicator macd">MACD: ${macd.signal || 'neutral'}</span>
                        <span class="indicator bb">BB: ${bb.position || 'middle'}</span>
                    </div>
                </div>
            `;
        });
        
        analysisContainer.innerHTML = html;
    }
    
    updateNewsUI(data) {
        const newsDiv = document.getElementById('news-insights-content');
        if (!newsDiv) return;
        
        const articles = data.articles || [];
        const sources = data.sources || [];
        const qualityMetrics = data.quality_metrics || {};
        
        let html = `
            <div class="news-header">
                <div class="news-sources">
                    ${sources.map(source => `<span class="source-badge ${source}">${source}</span>`).join('')}
                </div>
                <div class="quality-metrics">
                    <span class="metric">Articles: ${data.total_articles || 0}</span>
                    ${qualityMetrics.rejected_count ? `<span class="metric">Filtered: ${qualityMetrics.rejected_count}</span>` : ''}
                </div>
            </div>
        `;
        
        if (articles.length > 0) {
            html += '<div class="news-list">';
            articles.slice(0, 5).forEach(article => {
                html += `
                    <div class="news-item">
                        <div class="news-title">${article.title}</div>
                        <div class="news-source">${article.source?.name || 'Unknown'}</div>
                        <div class="news-time">${this.formatTime(article.publishedAt)}</div>
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
    
    formatCurrency(amount) {
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
    
    formatTime(timestamp) {
        if (!timestamp) return 'Unknown';
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    formatTechnicalSummary(indicators) {
        if (!indicators) return '';
        
        const parts = [];
        if (indicators.rsi) {
            parts.push(`RSI: ${indicators.rsi.signal}`);
        }
        if (indicators.macd) {
            parts.push(`MACD: ${indicators.macd.signal}`);
        }
        if (indicators.bollinger_bands) {
            parts.push(`BB: ${indicators.bollinger_bands.position}`);
        }
        
        return parts.join(', ');
    }
}

// Initialize enhanced dashboard
const enhancedDashboard = new EnhancedDashboard(); 