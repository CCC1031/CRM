/**
 * AI Chat Panel - Alpine.js Component
 *
 * Usage: Add x-data="chatPanel()" to the chat container
 * Communicates with POST /api/chat endpoint
 */
function chatPanel() {
    return {
        messages: [],
        input: '',
        loading: false,

        init() {
            // Load history from localStorage
            const saved = localStorage.getItem('crm-chat-history');
            if (saved) {
                try {
                    this.messages = JSON.parse(saved);
                } catch (e) {
                    this.messages = [];
                }
            }

            // Add welcome message if empty
            if (this.messages.length === 0) {
                this.messages.push({
                    role: 'assistant',
                    content: 'Welcome! I\'m your AI assistant. I can help you manage contacts, deals, and more.\n\nTry:\n\u2022 "Add a contact named John Smith, email john@example.com"\n\u2022 "Show me all leads"\n\u2022 "Move the Garcia deal to Proposal"\n\u2022 "How many deals are in the pipeline?"',
                    timestamp: new Date().toISOString()
                });
            }

            this.$nextTick(() => this.scrollToBottom());
        },

        saveHistory() {
            // Keep last 50 messages
            const toSave = this.messages.slice(-50);
            localStorage.setItem('crm-chat-history', JSON.stringify(toSave));
        },

        scrollToBottom() {
            const container = this.$refs.chatMessages;
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        },

        async send() {
            const message = this.input.trim();
            if (!message || this.loading) return;

            // Add user message
            this.messages.push({
                role: 'user',
                content: message,
                timestamp: new Date().toISOString()
            });
            this.input = '';
            this.loading = true;
            this.saveHistory();
            this.$nextTick(() => this.scrollToBottom());

            try {
                // Build history for API (last 10 messages, excluding current)
                const history = this.messages.slice(-11, -1).map(m => ({
                    role: m.role,
                    content: m.content
                }));

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, history })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();

                // Add assistant response
                this.messages.push({
                    role: 'assistant',
                    content: data.response || 'I couldn\'t process that request.',
                    actions: data.actions_taken || [],
                    timestamp: new Date().toISOString()
                });

                // If actions were taken that modified data, show a subtle page refresh hint
                if (data.actions_taken && data.actions_taken.some(a => a.success)) {
                    // Dispatch event so the page can refresh data if needed
                    window.dispatchEvent(new CustomEvent('crm-data-changed', {
                        detail: { actions: data.actions_taken }
                    }));
                }

            } catch (error) {
                this.messages.push({
                    role: 'assistant',
                    content: 'Sorry, I encountered an error. Please check your OpenRouter API key in the environment variables and try again.',
                    timestamp: new Date().toISOString()
                });
            }

            this.loading = false;
            this.saveHistory();
            this.$nextTick(() => this.scrollToBottom());
        },

        clearHistory() {
            this.messages = [{
                role: 'assistant',
                content: 'Chat history cleared. How can I help you?',
                timestamp: new Date().toISOString()
            }];
            this.saveHistory();
        },

        formatMessage(content) {
            if (!content) return '';

            // Convert markdown-style formatting to HTML
            let html = content
                // Bold
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                // Inline code
                .replace(/`([^`]+)`/g, '<code style="background: rgba(199,163,90,0.15); padding: 2px 6px; border-radius: 4px; font-size: 0.85em;">$1</code>')
                // Bullet points
                .replace(/^[\u2022\-]\s+(.+)$/gm, '<div style="padding-left: 16px; position: relative;"><span style="position: absolute; left: 0; color: var(--gold);">\u2022</span>$1</div>')
                // Line breaks
                .replace(/\n/g, '<br>');

            return html;
        },

        formatTime(timestamp) {
            if (!timestamp) return '';
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;

            if (diff < 60000) return 'just now';
            if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
            if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
            return date.toLocaleDateString();
        }
    };
}
