/**
 * AI Agent Flow Visualizer
 * Shows real-time LangGraph steps and AI agent processing
 */

class AIFlowVisualizer {
    constructor() {
        this.isProcessing = false;
        this.currentStep = 0;
        this.flowSteps = [
            {
                id: 'news-gathering',
                name: 'News Gathering',
                icon: '📰',
                description: 'Fetching latest crypto news from multiple sources',
                substeps: ['NewsAPI', 'Tavily Search'],
                color: '#00d4ff'
            },
            {
                id: 'classification',
                name: 'Classification & Filtering',
                icon: '🔍',
                description: 'Classifying articles and filtering for quality',
                substeps: ['Spam Detection', 'Quality Filter', 'Relevance Check'],
                color: '#a855f7'
            },
            {
                id: 'processing',
                name: 'Processing Pipeline',
                icon: '⚙️',
                description: 'Summarizing and enriching content',
                substeps: ['Summarization', 'Enrichment', 'Embedding'],
                color: '#ec4899'
            },
            {
                id: 'knowledge',
                name: 'Knowledge Retrieval',
                icon: '🧠',
                description: 'Retrieving relevant context and insights',
                substeps: ['Vector Search', 'Context Retrieval', 'RAG Analysis'],
                color: '#06b6d4'
            },
            {
                id: 'analysis',
                name: 'AI Analysis',
                icon: '🤖',
                description: 'Generating market insights and trading signals',
                substeps: ['Market Analysis', 'Signal Generation', 'Confidence Scoring'],
                color: '#10b981'
            }
        ];
        this.init();
    }

    init() {
        console.log('🎓 AI Flow Visualizer initialized');
        this.renderFlowSteps();
        this.bindEvents();
        this.loadInitialData();
        console.log('✅ AI Flow Visualizer setup complete');
    }

    renderFlowSteps() {
        const container = document.getElementById('ai-flow-steps');
        if (!container) return;

        let html = '<div class="flow-steps-container">';
        
        this.flowSteps.forEach((step, index) => {
            html += `
                <div class="flow-step" id="step-${step.id}" data-step="${index}">
                    <div class="step-header">
                        <div class="step-icon" style="background: ${step.color}20; border-color: ${step.color}">
                            ${step.icon}
                        </div>
                        <div class="step-info">
                            <h3 class="step-title">${step.name}</h3>
                            <p class="step-description">${step.description}</p>
                        </div>
                        <div class="step-status">
                            <span class="status-indicator" id="status-${step.id}">⏳</span>
                        </div>
                    </div>
                    <div class="step-substeps" id="substeps-${step.id}">
                        ${this.renderSubsteps(step.substeps)}
                    </div>
                    <div class="step-details" id="details-${step.id}">
                        <div class="step-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" id="progress-${step.id}"></div>
                            </div>
                            <span class="progress-text" id="progress-text-${step.id}">0%</span>
                        </div>
                        <div class="step-metrics" id="metrics-${step.id}">
                            <div class="metric">
                                <span class="metric-label">Time:</span>
                                <span class="metric-value" id="time-${step.id}">--</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Confidence:</span>
                                <span class="metric-value" id="confidence-${step.id}">--</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }

    renderSubsteps(substeps) {
        return substeps.map(substep => 
            `<div class="substep">
                <span class="substep-icon">•</span>
                <span class="substep-name">${substep}</span>
                <span class="substep-status">⏳</span>
            </div>`
        ).join('');
    }

    updateSubstepDetails(stepId, data) {
        console.log(`Updating substep details for ${stepId}:`, data);
        const substepsContainer = document.getElementById(`substeps-${stepId}`);
        if (!substepsContainer) {
            console.error(`Substeps container not found for ${stepId}`);
            return;
        }

        if (stepId === 'news-gathering') {
            // Show news gathering details
            substepsContainer.innerHTML = `
                <div class="substep-detail">
                    <div class="substep">
                        <span class="substep-icon">📰</span>
                        <span class="substep-name">NewsAPI</span>
                        <span class="substep-status">✅ ${data.newsapi_count} articles</span>
                    </div>
                    <div class="substep">
                        <span class="substep-icon">🔍</span>
                        <span class="substep-name">Tavily Search</span>
                        <span class="substep-status">✅ ${data.tavily_count} articles</span>
                    </div>
                    <div class="substep">
                        <span class="substep-icon">🔒</span>
                        <span class="substep-name">Quality Filter</span>
                        <span class="substep-status">✅ ${data.quality_filtered} filtered</span>
                    </div>
                </div>
            `;
        } else if (stepId === 'classification') {
            // Show classification details with sample headlines
            substepsContainer.innerHTML = `
                <div class="substep-detail">
                    <div class="substep">
                        <span class="substep-icon">🚫</span>
                        <span class="substep-name">Spam Detection</span>
                        <span class="substep-status">✅ ${data.spam_detected} removed</span>
                    </div>
                    <div class="substep">
                        <span class="substep-icon">⭐</span>
                        <span class="substep-name">Quality Filter</span>
                        <span class="substep-status">✅ ${data.quality_filtered} filtered</span>
                    </div>
                    <div class="substep">
                        <span class="substep-icon">🎯</span>
                        <span class="substep-name">Relevance Check</span>
                        <span class="substep-status">✅ ${data.approved_articles} approved</span>
                    </div>
                    ${data.sample_headlines ? `
                    <div class="headlines-preview">
                        <h4>Sample Headlines:</h4>
                        <div class="headlines-grid">
                            <div class="approved-headlines">
                                <h5>✅ Approved:</h5>
                                <ul>
                                    ${data.sample_headlines.approved.map(h => `<li>${h}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="rejected-headlines">
                                <h5>❌ Rejected:</h5>
                                <ul>
                                    ${data.sample_headlines.rejected.map(h => `<li>${h}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                </div>
            `;
        } else if (stepId === 'processing') {
            // Show processing details with token optimization
            substepsContainer.innerHTML = `
                <div class="substep-detail">
                    <div class="substep">
                        <span class="substep-icon">📝</span>
                        <span class="substep-name">Summarization</span>
                        <span class="substep-status">✅ ${data.summaries_generated} summaries</span>
                    </div>
                    <div class="substep">
                        <span class="substep-icon">🏷️</span>
                        <span class="substep-name">Enrichment</span>
                        <span class="substep-status">✅ ${data.enrichment_completed} enriched</span>
                    </div>
                    <div class="substep">
                        <span class="substep-icon">🧮</span>
                        <span class="substep-name">Embeddings</span>
                        <span class="substep-status">✅ ${data.embeddings_created} vectors</span>
                    </div>
                    ${data.token_optimization ? `
                    <div class="token-optimization">
                        <h4>Token Optimization:</h4>
                        <div class="token-metrics">
                            <div class="token-metric">
                                <span class="metric-label">Original:</span>
                                <span class="metric-value">${data.token_optimization.original_tokens.toLocaleString()} tokens</span>
                            </div>
                            <div class="token-metric">
                                <span class="metric-label">Summarized:</span>
                                <span class="metric-value">${data.token_optimization.summarized_tokens.toLocaleString()} tokens</span>
                            </div>
                            <div class="token-metric savings">
                                <span class="metric-label">Savings:</span>
                                <span class="metric-value">${data.token_optimization.savings_percentage}</span>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                    ${data.embedding_matrix ? `
                    <div class="embedding-matrix">
                        <h4>Embedding Matrix:</h4>
                        <div class="matrix-preview">
                            <div class="matrix-dimensions">${data.embedding_matrix.dimensions}</div>
                            <div class="matrix-numbers">${data.embedding_matrix.matrix_preview}</div>
                        </div>
                    </div>
                    ` : ''}
                </div>
            `;
        } else if (stepId === 'analysis') {
            // Show analysis details with historical performance
            substepsContainer.innerHTML = `
                <div class="substep-detail">
                    <div class="substep">
                        <span class="substep-icon">📊</span>
                        <span class="substep-name">Market Analysis</span>
                        <span class="substep-status">✅ Completed</span>
                    </div>
                    <div class="substep">
                        <span class="substep-icon">📈</span>
                        <span class="substep-name">Signal Generation</span>
                        <span class="substep-status">✅ ${data.signals_generated} signals</span>
                    </div>
                    <div class="substep">
                        <span class="substep-icon">🎯</span>
                        <span class="substep-name">Confidence Scoring</span>
                        <span class="substep-status">✅ ${(data.overall_confidence * 100).toFixed(1)}%</span>
                    </div>
                    ${data.historical_performance ? `
                    <div class="historical-performance">
                        <h4>Historical Performance:</h4>
                        <div class="performance-grid">
                            ${Object.entries(data.historical_performance).map(([period, perf]) => `
                                <div class="performance-item ${perf.performance_color}">
                                    <div class="period">${period.replace('_', ' ').toUpperCase()}</div>
                                    <div class="accuracy">${(perf.accuracy * 100).toFixed(1)}%</div>
                                    <div class="signals">${perf.signals_correct}/${perf.signals_total}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                </div>
            `;
        }
    }

    bindEvents() {
        // Manual trigger button
        const triggerBtn = document.getElementById('trigger-analysis');
        if (triggerBtn) {
            triggerBtn.addEventListener('click', () => this.triggerAnalysis());
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-flow');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshFlow());
        }
    }

    async loadInitialData() {
        try {
            // Load current AI agent status
            const response = await fetch('/api/agent/status');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateAgentStatus(data.data);
            }
        } catch (error) {
            console.log('No active AI agent session found');
        }
    }

    async triggerAnalysis() {
        if (this.isProcessing) {
            this.showNotification('Analysis already in progress...', 'warning');
            return;
        }

        this.isProcessing = true;
        this.currentStep = 0;
        this.resetFlow();
        this.updateTriggerButton('Processing...', true);

        try {
            this.showNotification('🚀 Starting AI Agent Analysis...', 'info');
            
            // Step 1: News Gathering
            await this.executeStep('news-gathering', async () => {
                const response = await fetch('/api/agent/trigger-news-gathering', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbols: ['BTC', 'ETH', 'SOL'] })
                });
                return await response.json();
            });

            // Step 2: Classification & Filtering
            await this.executeStep('classification', async () => {
                const response = await fetch('/api/agent/trigger-classification', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                return await response.json();
            });

            // Step 3: Processing Pipeline
            await this.executeStep('processing', async () => {
                const response = await fetch('/api/agent/trigger-processing', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                return await response.json();
            });

            // Step 4: Knowledge Retrieval
            await this.executeStep('knowledge', async () => {
                const response = await fetch('/api/agent/trigger-knowledge-retrieval', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                return await response.json();
            });

            // Step 5: AI Analysis
            await this.executeStep('analysis', async () => {
                const response = await fetch('/api/agent/trigger-analysis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                return await response.json();
            });

            this.showNotification('✅ AI Agent Analysis Complete!', 'success');
            this.updateResults();

        } catch (error) {
            console.error('Error during AI analysis:', error);
            this.showNotification('❌ Analysis failed: ' + error.message, 'error');
        } finally {
            this.isProcessing = false;
            this.updateTriggerButton('🧠 Trigger AI Analysis', false);
        }
    }

    async executeStep(stepId, stepFunction) {
        const stepIndex = this.flowSteps.findIndex(s => s.id === stepId);
        if (stepIndex === -1) return;

        const step = this.flowSteps[stepIndex];
        const startTime = Date.now();

        // Update step status to processing
        this.updateStepStatus(stepId, 'processing');
        this.updateStepProgress(stepId, 0);

        try {
            // Execute the step
            const result = await stepFunction();
            
            // Calculate processing time
            const processingTime = Date.now() - startTime;
            
            // Update step with results
            this.updateStepProgress(stepId, 100);
            const confidence = result.data ? result.data.confidence : result.confidence;
            this.updateStepMetrics(stepId, processingTime, confidence || 0.85);
            this.updateStepStatus(stepId, 'completed');
            
            // Update substep details with detailed data
            this.updateSubstepDetails(stepId, result.data || result);
            
            // Update article preview if available
            if (result.data && result.data.article_preview) {
                this.updateArticlePreview(result.data.article_preview);
            } else if (result.article_preview) {
                this.updateArticlePreview(result.article_preview);
            }

            // Show step completion notification
            this.showNotification(`✅ ${step.name} completed`, 'success');

        } catch (error) {
            this.updateStepStatus(stepId, 'error');
            this.updateStepProgress(stepId, 0);
            throw error;
        }
    }

    updateStepStatus(stepId, status) {
        const statusElement = document.getElementById(`status-${stepId}`);
        if (!statusElement) return;

        const statusMap = {
            'waiting': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'error': '❌'
        };

        statusElement.textContent = statusMap[status] || '⏳';
        statusElement.className = `status-indicator status-${status}`;
    }

    updateStepProgress(stepId, percentage) {
        const progressFill = document.getElementById(`progress-${stepId}`);
        const progressText = document.getElementById(`progress-text-${stepId}`);
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        if (progressText) {
            progressText.textContent = `${percentage}%`;
        }
    }

    updateStepMetrics(stepId, time, confidence) {
        const timeElement = document.getElementById(`time-${stepId}`);
        const confidenceElement = document.getElementById(`confidence-${stepId}`);
        
        if (timeElement) {
            timeElement.textContent = `${time}ms`;
        }
        if (confidenceElement) {
            confidenceElement.textContent = `${(confidence * 100).toFixed(1)}%`;
        }
    }

    updateArticlePreview(preview) {
        const container = document.getElementById('article-preview');
        if (!container) return;

        container.innerHTML = `
            <div class="article-preview-content">
                <h4>📄 Article Preview</h4>
                <div class="article-text">${preview}</div>
            </div>
        `;
    }

    updateResults() {
        // Update the results section with final analysis
        const resultsContainer = document.getElementById('analysis-results');
        if (!resultsContainer) return;

        // Fetch final results from the AI agent
        fetch('/api/agent/results')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.renderResults(data.data);
                }
            })
            .catch(error => {
                console.error('Error fetching results:', error);
            });
    }

    renderResults(data) {
        const container = document.getElementById('analysis-results');
        if (!container) return;

        let html = `
            <div class="results-header">
                <h3>🎯 Analysis Results</h3>
                <div class="results-meta">
                    <span class="meta-item">Confidence: ${(data.confidence * 100).toFixed(1)}%</span>
                    <span class="meta-item">Processing Time: ${data.processing_time}ms</span>
                    <span class="meta-item">Articles Processed: ${data.articles_processed}</span>
                </div>
            </div>
        `;

        if (data.signals && data.signals.length > 0) {
            html += '<div class="signals-section"><h4>📈 Trading Signals</h4>';
            data.signals.forEach(signal => {
                html += `
                    <div class="signal-item">
                        <div class="signal-header">
                            <span class="signal-symbol">${signal.symbol}</span>
                            <span class="signal-action ${signal.action.toLowerCase()}">${signal.action}</span>
                            <span class="signal-confidence">${(signal.confidence * 100).toFixed(1)}%</span>
                        </div>
                        <div class="signal-reasoning">${signal.reasoning}</div>
                    </div>
                `;
            });
            html += '</div>';
        }

        if (data.insights && data.insights.length > 0) {
            html += '<div class="insights-section"><h4>💡 Key Insights</h4><ul>';
            data.insights.forEach(insight => {
                html += `<li>${insight}</li>`;
            });
            html += '</ul></div>';
        }

        container.innerHTML = html;
    }

    resetFlow() {
        this.flowSteps.forEach(step => {
            this.updateStepStatus(step.id, 'waiting');
            this.updateStepProgress(step.id, 0);
            this.updateStepMetrics(step.id, '--', 0);
        });
    }

    updateTriggerButton(text, disabled) {
        const button = document.getElementById('trigger-analysis');
        if (button) {
            button.textContent = text;
            button.disabled = disabled;
        }
    }

    updateAgentStatus(data) {
        const statusElement = document.getElementById('agent-status');
        if (statusElement) {
            statusElement.textContent = data.status || 'Ready';
            statusElement.className = `status-badge status-${data.status || 'ready'}`;
        }
    }

    refreshFlow() {
        this.loadInitialData();
        this.showNotification('🔄 Flow data refreshed', 'info');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize the AI Flow Visualizer
document.addEventListener('DOMContentLoaded', function() {
    window.aiFlowVisualizer = new AIFlowVisualizer();
}); 