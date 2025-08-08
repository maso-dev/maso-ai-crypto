/**
 * Service Monitor JavaScript
 * Phase 4: Enhanced Admin Dashboard Service Validation
 */

class ServiceMonitor {
    constructor() {
        this.services = {};
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialStatus();
        this.startAutoRefresh();
        console.log('🔧 Service Monitor initialized');
    }

    bindEvents() {
        // Manual refresh button
        document.getElementById('refresh-services')?.addEventListener('click', () => {
            this.refreshAllServices();
        });

        // Individual service refresh buttons
        document.querySelectorAll('.service-refresh-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const serviceName = e.target.dataset.service;
                this.refreshService(serviceName);
            });
        });
    }

    async loadInitialStatus() {
        try {
            await this.refreshAllServices();
        } catch (error) {
            console.error('Error loading initial service status:', error);
        }
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        this.updateInterval = setInterval(() => {
            this.refreshAllServices();
        }, 30000);
    }

    async refreshAllServices() {
        try {
            console.log('🔄 Refreshing all services...');
            console.log('📡 Fetching from: /admin/validate-real-data');
            // Use the correct admin endpoint for real data validation
            const response = await fetch('/admin/validate-real-data');
            console.log('📊 Response status:', response.status);
            console.log('📊 Response ok:', response.ok);
            const data = await response.json();
            console.log('📊 Data received:', Object.keys(data));

            if (data.overall_health) {
                this.updateServiceStatus(data);
            } else {
                console.error('Admin validation failed:', data);
                this.showError('Failed to validate service status');
            }
        } catch (error) {
            console.error('Error refreshing services:', error);
            this.showError('Failed to refresh service status');
        }
    }

    async refreshService(serviceName) {
        try {
            // For now, just refresh all services since individual endpoints might not exist
            await this.refreshAllServices();
        } catch (error) {
            console.error(`Error refreshing ${serviceName}:`, error);
        }
    }

    updateServiceStatus(data) {
        // Update overall health
        const realDataCount = Object.values(data.components).filter(comp => comp.is_real_data).length;
        const totalComponents = Object.keys(data.components).length;

        this.updateOverallHealth({
            score: `${realDataCount}/${totalComponents}`,
            status: realDataCount >= totalComponents * 0.7 ? 'healthy' : 'degraded'
        });

        // Update individual services from components
        this.updateServicesGrid(data.components);
        this.updateBackendServicesGrid(data.components);

        Object.keys(data.components).forEach(serviceName => {
            // Pass both component data and API key status
            const serviceData = {
                ...data.components[serviceName],
                api_key_configured: data.api_keys[serviceName] || false
            };
            this.updateSingleService(serviceName, serviceData);

            // Update specific service elements if they exist
            if (serviceName === 'livecoinwatch') {
                this.updateLiveCoinWatchStatus(serviceData);
            }
        });

        // Update environment info
        this.updateEnvironmentInfo({
            'Real Data Services': `${realDataCount}/${totalComponents}`,
            'Overall Health': data.overall_health || 'Unknown',
            'Data Quality Score': `${data.real_data_percentage || 0}%`,
            'Last Updated': data.last_updated || 'Unknown'
        });

        // Update last refresh time
        this.updateLastRefresh();
    }

    updateOverallHealth(health) {
        const healthScore = document.getElementById('health-score');
        const healthText = document.getElementById('health-text');

        if (healthScore && healthText) {
            healthScore.textContent = health.score || 'N/A';
            healthText.textContent = health.status || 'Unknown';

            // Update color based on health
            healthScore.className = `health-score ${health.status || 'unknown'}`;
        }
    }

    updateServicesGrid(services) {
        const servicesGrid = document.getElementById('services-grid');
        if (!servicesGrid) return;

        servicesGrid.innerHTML = Object.entries(services).map(([serviceName, serviceData]) => `
            <div class="service-card" data-service="${serviceName}">
                <div class="service-header">
                    <span class="service-icon">${this.getServiceIcon(serviceName)}</span>
                    <h4 class="service-name">${this.getServiceDisplayName(serviceName)}</h4>
                    <span class="service-status ${serviceData.status || 'unknown'}">${serviceData.status || 'Unknown'}</span>
                </div>
                <div class="service-details">
                    <div class="detail-item">
                        <span class="detail-label">API Key:</span>
                        <span class="key-status ${serviceData.api_key_configured ? 'configured' : 'not-configured'}">
                            ${serviceData.api_key_configured ? '✅ Configured' : '❌ Not Configured'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Last Updated:</span>
                        <span class="last-updated">Just now</span>
                    </div>
                </div>
                <div class="mt-3">
                    <button class="service-refresh-btn liquid-button secondary" data-service="${serviceName}">
                        <span>🔄</span>
                        Refresh
                    </button>
                </div>
            </div>
        `).join('');

        // Re-bind event listeners for new buttons
        this.bindEvents();
    }

    getServiceIcon(serviceName) {
        const icons = {
            'openai': '🤖',
            'livecoinwatch': '🪙',
            'newsapi': '📰',
            'tavily': '🔍',
            'milvus': '🗄️',
            'neo4j': '🕸️',
            'langsmith': '📊',
            'binance': '💰'
        };
        return icons[serviceName] || '⚙️';
    }

    getServiceDisplayName(serviceName) {
        const names = {
            'openai': 'OpenAI',
            'livecoinwatch': 'LiveCoinWatch',
            'newsapi': 'NewsAPI',
            'tavily': 'Tavily Search',
            'milvus': 'Milvus Vector DB',
            'neo4j': 'Neo4j Graph DB',
            'langsmith': 'LangSmith',
            'binance': 'Binance'
        };
        return names[serviceName] || serviceName.charAt(0).toUpperCase() + serviceName.slice(1);
    }

    updateBackendServicesGrid(services) {
        const backendGrid = document.getElementById('backend-services-grid');
        if (!backendGrid) return;

        // Define which services are backend/brain services
        const backendServices = ['milvus', 'neo4j', 'langsmith', 'openai'];

        const backendServicesData = {};
        backendServices.forEach(service => {
            if (services[service]) {
                backendServicesData[service] = services[service];
            }
        });

        backendGrid.innerHTML = Object.entries(backendServicesData).map(([serviceName, serviceData]) => `
            <div class="service-card" data-service="${serviceName}">
                <div class="service-header">
                    <span class="service-icon">${this.getServiceIcon(serviceName)}</span>
                    <h4 class="service-name">${this.getServiceDisplayName(serviceName)}</h4>
                    <span class="service-status ${serviceData.status || 'unknown'}">${serviceData.status || 'Unknown'}</span>
                </div>
                <div class="service-details">
                    <div class="detail-item">
                        <span class="detail-label">API Key:</span>
                        <span class="key-status ${serviceData.api_key_configured ? 'configured' : 'not-configured'}">
                            ${serviceData.api_key_configured ? '✅ Configured' : '❌ Not Configured'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Last Updated:</span>
                        <span class="last-updated">Just now</span>
                    </div>
                </div>
                <div class="mt-3">
                    <button class="service-refresh-btn liquid-button secondary" data-service="${serviceName}">
                        <span>🔄</span>
                        Refresh
                    </button>
                </div>
            </div>
        `).join('');

        // Re-bind event listeners for new buttons
        this.bindEvents();
    }

    updateSingleService(serviceName, serviceData) {
        const serviceElement = document.querySelector(`[data-service="${serviceName}"]`);
        if (!serviceElement) return;

        // Update status badge with real data indicators
        const statusBadge = serviceElement.querySelector('.service-status');
        if (statusBadge) {
            let statusText, statusClass;

            if (serviceData.is_real_data) {
                statusText = `✅ ${serviceData.text} (Real Data)`;
                statusClass = 'real-data';
            } else if (serviceData.is_operational) {
                statusText = `⚠️ ${serviceData.text} (Mock Data)`;
                statusClass = 'mock-data';
            } else {
                statusText = `❌ ${serviceData.text}`;
                statusClass = 'error';
            }

            // Add data freshness if available
            if (serviceData.data_freshness_minutes > 0) {
                statusText += ` (${serviceData.data_freshness_minutes}m ago)`;
            }

            statusBadge.textContent = statusText;
            statusBadge.className = `service-status ${statusClass}`;

            // Add tooltip with detailed info
            statusBadge.title = `Last Check: ${serviceData.last_check}\nMock Mode: ${serviceData.mock_mode}\nError: ${serviceData.error || 'None'}`;
        }

        // Update API key status
        const keyStatus = serviceElement.querySelector('.key-status');
        if (keyStatus) {
            const hasKey = serviceData.api_key_configured || false;
            keyStatus.textContent = hasKey ? '✅ Configured' : '❌ Not Configured';
            keyStatus.className = `key-status ${hasKey ? 'configured' : 'not-configured'}`;
        }

        // Update last updated time
        const lastUpdated = serviceElement.querySelector('.last-updated');
        if (lastUpdated) {
            lastUpdated.textContent = this.formatTime(new Date(serviceData.last_check));
        }
    }

    updateEnvironmentInfo(env) {
        const envGrid = document.getElementById('env-grid');
        if (!envGrid) return;

        envGrid.innerHTML = Object.entries(env).map(([key, value]) => {
            // Handle different types of values
            let displayValue, isConfigured, valueClass;

            if (key === 'Real Data Services') {
                const [real, total] = value.split('/').map(Number);
                const percentage = Math.round((real / total) * 100);
                displayValue = `${value} (${percentage}%)`;
                valueClass = percentage >= 70 ? 'excellent' : percentage >= 50 ? 'good' : 'poor';
                isConfigured = true;
            } else if (key === 'Overall Health') {
                displayValue = value;
                valueClass = value === 'healthy' ? 'excellent' : value === 'degraded' ? 'good' : 'poor';
                isConfigured = true;
            } else if (key === 'Data Quality Score') {
                const score = parseInt(value);
                displayValue = value;
                valueClass = score >= 80 ? 'excellent' : score >= 60 ? 'good' : 'poor';
                isConfigured = true;
            } else if (key === 'Last Updated') {
                displayValue = this.formatTime(new Date(value));
                valueClass = 'info';
                isConfigured = true;
            } else {
                displayValue = value ? '✅ Configured' : '❌ Not Set';
                valueClass = value ? 'configured' : 'not-configured';
                isConfigured = !!value;
            }

            return `
                <div class="env-item">
                    <div class="env-label">${key}</div>
                    <div class="env-value ${valueClass}">
                        ${displayValue}
                    </div>
                </div>
            `;
        }).join('');
    }

    updateLiveCoinWatchStatus(serviceData) {
        // Update specific LiveCoinWatch elements in admin page
        const statusElement = document.getElementById('livecoinwatch-status');
        const keyElement = document.getElementById('livecoinwatch-key');

        if (statusElement) {
            statusElement.textContent = serviceData.status || 'Unknown';
            statusElement.className = `detail-value ${serviceData.status || 'unknown'}`;
        }

        if (keyElement) {
            keyElement.textContent = serviceData.key_set ? '✅ Configured' : '❌ Not Configured';
            keyElement.className = `detail-value ${serviceData.key_set ? 'configured' : 'not-configured'}`;
        }
    }

    updateLastRefresh() {
        const lastUpdate = document.getElementById('last-update');
        if (lastUpdate) {
            lastUpdate.textContent = this.formatTime(new Date());
        }
    }

    formatTime(timestamp) {
        if (!timestamp) return 'Never';

        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;

        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours}h ago`;

        return date.toLocaleString();
    }

    showError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Service-specific actions
    async triggerLiveCoinWatchCollection() {
        try {
            const response = await fetch('/api/livecoinwatch/trigger-collection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbols: ["BTC", "ETH", "SOL", "XRP", "ADA"],
                    include_historical: true,
                    include_indicators: true
                })
            });
            const data = await response.json();

            if (data.message) {
                this.showSuccess('LiveCoinWatch data collection triggered successfully');
                // Refresh service status after a delay
                setTimeout(() => this.refreshService('livecoinwatch'), 2000);
            } else {
                this.showError('Failed to trigger LiveCoinWatch collection');
            }
        } catch (error) {
            console.error('Error triggering LiveCoinWatch collection:', error);
            this.showError('Error triggering data collection');
        }
    }

    async triggerNewsRefresh() {
        try {
            const response = await fetch('/api/admin/refresh-mvp-data', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.status === 'success') {
                this.showSuccess('News refresh triggered successfully');
                // Refresh service status after a delay
                setTimeout(() => this.refreshService('newsapi'), 2000);
            } else {
                this.showError('Failed to trigger news refresh');
            }
        } catch (error) {
            console.error('Error triggering news refresh:', error);
            this.showError('Error triggering news refresh');
        }
    }

    showSuccess(message) {
        // Create success notification
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize Service Monitor
document.addEventListener('DOMContentLoaded', function () {
    window.serviceMonitor = new ServiceMonitor();
});

// Global functions for HTML onclick handlers
function triggerLiveCoinWatchCollection() {
    window.serviceMonitor?.triggerLiveCoinWatchCollection();
}

function triggerNewsRefresh() {
    window.serviceMonitor?.triggerNewsRefresh();
}

// Global function for admin page refresh
function loadAdminData() {
    window.serviceMonitor?.refreshAllServices();
}

// Global function for technical indicators
function triggerTechnicalIndicators() {
    // This would trigger technical indicator calculation
    console.log('Triggering technical indicators calculation...');
    // For now, just refresh the services
    window.serviceMonitor?.refreshAllServices();
} 
