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
            const response = await fetch('/api/admin/mvp-status');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateServiceStatus(data.data);
            }
        } catch (error) {
            console.error('Error refreshing services:', error);
            this.showError('Failed to refresh service status');
        }
    }

    async refreshService(serviceName) {
        try {
            const response = await fetch(`/api/admin/service-status/${serviceName}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateSingleService(serviceName, data.data);
            }
        } catch (error) {
            console.error(`Error refreshing ${serviceName}:`, error);
        }
    }

    updateServiceStatus(data) {
        // Update overall health
        this.updateOverallHealth(data.system_health);
        
        // Update individual services
        Object.keys(data.services).forEach(serviceName => {
            this.updateSingleService(serviceName, data.services[serviceName]);
        });

        // Update environment info
        this.updateEnvironmentInfo(data.environment);
        
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

    updateSingleService(serviceName, serviceData) {
        const serviceElement = document.querySelector(`[data-service="${serviceName}"]`);
        if (!serviceElement) return;

        // Update status badge
        const statusBadge = serviceElement.querySelector('.service-status');
        if (statusBadge) {
            statusBadge.textContent = serviceData.status || 'Unknown';
            statusBadge.className = `service-status ${serviceData.status || 'unknown'}`;
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
        if (lastUpdated && serviceData.last_updated) {
            lastUpdated.textContent = this.formatTime(serviceData.last_updated);
        }

        // Update rate limit info
        const rateLimit = serviceElement.querySelector('.rate-limit');
        if (rateLimit && serviceData.rate_limit) {
            rateLimit.textContent = `${serviceData.rate_limit.used || 0}/${serviceData.rate_limit.limit || '∞'}`;
        }

        // Update error count
        const errorCount = serviceElement.querySelector('.error-count');
        if (errorCount && serviceData.error_count !== undefined) {
            errorCount.textContent = serviceData.error_count;
            errorCount.className = `error-count ${serviceData.error_count > 0 ? 'has-errors' : 'no-errors'}`;
        }
    }

    updateEnvironmentInfo(env) {
        const envGrid = document.getElementById('env-grid');
        if (!envGrid) return;

        envGrid.innerHTML = Object.entries(env).map(([key, value]) => `
            <div class="env-item">
                <div class="env-label">${key}</div>
                <div class="env-value ${value ? 'configured' : 'not-configured'}">
                    ${value ? '✅ Configured' : '❌ Not Set'}
                </div>
            </div>
        `).join('');
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
            const response = await fetch('/api/livecoinwatch/collect-prices', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
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
document.addEventListener('DOMContentLoaded', function() {
    window.serviceMonitor = new ServiceMonitor();
});

// Global functions for HTML onclick handlers
function triggerLiveCoinWatchCollection() {
    window.serviceMonitor?.triggerLiveCoinWatchCollection();
}

function triggerNewsRefresh() {
    window.serviceMonitor?.triggerNewsRefresh();
} 