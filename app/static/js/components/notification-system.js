class NotificationSystem {
    constructor() {
        this.init();
    }

    init() {
        // Create container for notifications
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                --success-bg: rgba(76, 175, 80, 0.1);
                --success-border: #4CAF50;
                --error-bg: rgba(244, 67, 54, 0.1);
                --error-border: #F44336;
                --info-bg: rgba(0, 90, 113, 0.1);
                --info-border: #005A71;
                --warning-bg: rgba(255, 193, 7, 0.1);
                --warning-border: #FFC107;

                padding: 1rem;
                border-radius: 8px;
                background: var(--bg-color);
                border: 1px solid var(--border-color);
                color: var(--text-color);
                margin-bottom: 0.5rem;
                pointer-events: auto;
                display: flex;
                align-items: flex-start;
                gap: 1rem;
                min-width: 300px;
                max-width: 500px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transform: translateX(120%);
                transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            }

            .notification.show {
                transform: translateX(0);
            }

            .notification-icon {
                font-size: 1.25rem;
                flex-shrink: 0;
            }

            .notification-content {
                flex: 1;
            }

            .notification-title {
                font-weight: 600;
                margin-bottom: 0.25rem;
            }

            .notification-message {
                font-size: 0.875rem;
                opacity: 0.8;
            }

            .notification-close {
                background: none;
                border: none;
                color: inherit;
                cursor: pointer;
                padding: 0.25rem;
                opacity: 0.6;
                transition: opacity 0.2s;
            }

            .notification-close:hover {
                opacity: 1;
            }

            .notification-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: var(--border-color);
                opacity: 0.5;
                transition: width 0.1s linear;
            }

            .notification.success {
                --bg-color: var(--success-bg);
                --border-color: var(--success-border);
                --text-color: var(--success-border);
            }

            .notification.error {
                --bg-color: var(--error-bg);
                --border-color: var(--error-border);
                --text-color: var(--error-border);
            }

            .notification.info {
                --bg-color: var(--info-bg);
                --border-color: var(--info-border);
                --text-color: var(--info-border);
            }

            .notification.warning {
                --bg-color: var(--warning-bg);
                --border-color: var(--warning-border);
                --text-color: var(--warning-border);
            }

            @media (max-width: 768px) {
                #notification-container {
                    left: 1rem;
                    right: 1rem;
                }

                .notification {
                    min-width: 0;
                    max-width: none;
                    width: 100%;
                }
            }
        `;
        document.head.appendChild(style);
    }

    show({ title, message, type = 'info', duration = 5000, icon = null }) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // Set default icons if none provided
        if (!icon) {
            switch (type) {
                case 'success':
                    icon = '<i class="fas fa-check-circle"></i>';
                    break;
                case 'error':
                    icon = '<i class="fas fa-times-circle"></i>';
                    break;
                case 'warning':
                    icon = '<i class="fas fa-exclamation-triangle"></i>';
                    break;
                default:
                    icon = '<i class="fas fa-info-circle"></i>';
            }
        }

        notification.innerHTML = `
            <div class="notification-icon">${icon}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">&times;</button>
            <div class="notification-progress"></div>
        `;

        this.container.appendChild(notification);

        // Trigger reflow to enable animation
        notification.offsetHeight;
        notification.classList.add('show');

        // Progress bar
        const progress = notification.querySelector('.notification-progress');
        let width = 100;
        const interval = 10;
        const step = (interval * 100) / duration;

        const progressTimer = setInterval(() => {
            width -= step;
            progress.style.width = `${width}%`;
            
            if (width <= 0) {
                clearInterval(progressTimer);
            }
        }, interval);

        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            clearInterval(progressTimer);
            this.close(notification);
        });

        // Auto close
        if (duration > 0) {
            setTimeout(() => {
                clearInterval(progressTimer);
                this.close(notification);
            }, duration);
        }

        return notification;
    }

    close(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }

    success(title, message, duration) {
        return this.show({ title, message, type: 'success', duration });
    }

    error(title, message, duration) {
        return this.show({ title, message, type: 'error', duration });
    }

    warning(title, message, duration) {
        return this.show({ title, message, type: 'warning', duration });
    }

    info(title, message, duration) {
        return this.show({ title, message, type: 'info', duration });
    }
}

// Initialize notification system
const notifications = new NotificationSystem();
