document.addEventListener('DOMContentLoaded', () => {
    // Initialize notifications
    window.notifications = new NotificationSystem();

    // Theme handling
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    const themeToggle = document.getElementById('themeToggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.documentElement.classList.toggle('light-theme');
            const isLight = document.documentElement.classList.contains('light-theme');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            
            notifications.info(
                'Theme Updated',
                `Switched to ${isLight ? 'light' : 'dark'} theme`,
                3000
            );
        });
    }

    // Mobile menu handling
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (mobileMenu.classList.contains('active') &&
                !mobileMenu.contains(e.target) &&
                !mobileMenuButton.contains(e.target)) {
                mobileMenu.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation and enhancement
    document.querySelectorAll('form').forEach(form => {
        const submitButton = form.querySelector('button[type="submit"]');
        
        form.addEventListener('submit', async (e) => {
            if (!form.hasAttribute('data-no-enhance')) {
                e.preventDefault();
                
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.classList.add('loading');
                }

                try {
                    const formData = new FormData(form);
                    const response = await fetch(form.action, {
                        method: form.method,
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    const data = await response.json();

                    if (response.ok) {
                        notifications.success(
                            'Success',
                            data.message || 'Operation completed successfully',
                            5000
                        );

                        // Handle redirect if specified
                        if (data.redirect) {
                            window.location.href = data.redirect;
                            return;
                        }

                        // Handle form reset if specified
                        if (data.reset) {
                            form.reset();
                        }

                        // Trigger success event
                        form.dispatchEvent(new CustomEvent('form:success', { detail: data }));
                    } else {
                        throw new Error(data.message || 'Something went wrong');
                    }
                } catch (error) {
                    notifications.error(
                        'Error',
                        error.message || 'An unexpected error occurred',
                        5000
                    );
                } finally {
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.classList.remove('loading');
                    }
                }
            }
        });
    });

    // Lazy loading images
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = element.dataset.tooltip;
            document.body.appendChild(tooltip);

            const rect = element.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;

            element.addEventListener('mouseleave', () => {
                tooltip.remove();
            }, { once: true });
        });
    });

    // Handle flash messages
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        const closeBtn = message.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 300);
            });
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });

    // Initialize event galleries
    document.querySelectorAll('event-gallery').forEach(gallery => {
        gallery.addEventListener('event-selected', (e) => {
            window.location.href = `/events/${e.detail.eventId}`;
        });
    });

    // Handle infinite scroll for feed pages
    const feedContainer = document.querySelector('.feed-posts');
    if (feedContainer) {
        let loading = false;
        let page = 1;

        const loadMorePosts = async () => {
            if (loading) return;
            
            const scrollPosition = window.innerHeight + window.scrollY;
            const contentHeight = feedContainer.offsetHeight;
            
            if (scrollPosition >= contentHeight - 1000) {
                loading = true;
                page++;

                try {
                    const response = await fetch(`/api/feed?page=${page}`);
                    const data = await response.json();

                    if (data.posts.length > 0) {
                        // Append new posts
                        data.posts.forEach(post => {
                            const postElement = createPostElement(post);
                            feedContainer.appendChild(postElement);
                        });
                    } else {
                        // No more posts to load
                        window.removeEventListener('scroll', loadMorePosts);
                    }
                } catch (error) {
                    notifications.error('Error', 'Failed to load more posts');
                } finally {
                    loading = false;
                }
            }
        };

        window.addEventListener('scroll', loadMorePosts);
    }
});

// Utility function to format dates
window.formatDate = (date) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString(undefined, options);
};

// Utility function to format times
window.formatTime = (time) => {
    const options = { hour: 'numeric', minute: '2-digit' };
    return new Date(`1970-01-01T${time}`).toLocaleTimeString(undefined, options);
};

// Utility function to format currency
window.formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
};
