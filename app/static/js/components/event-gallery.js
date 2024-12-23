class EventGallery extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
        this.setupIntersectionObserver();
        this.setupEventListeners();
    }

    render() {
        const events = JSON.parse(this.getAttribute('events') || '[]');
        
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    --grid-gap: 1.5rem;
                }

                .gallery {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: var(--grid-gap);
                }

                .event-card {
                    background: var(--bg-secondary, #2A2922);
                    border-radius: 12px;
                    overflow: hidden;
                    transition: transform 0.3s ease;
                    position: relative;
                }

                .event-card:hover {
                    transform: translateY(-4px);
                }

                .event-image {
                    position: relative;
                    padding-top: 56.25%;
                    overflow: hidden;
                }

                .event-image img {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    transition: transform 0.3s ease;
                }

                .event-card:hover .event-image img {
                    transform: scale(1.05);
                }

                .event-content {
                    padding: 1.5rem;
                }

                .event-meta {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 0.5rem;
                    color: var(--text-secondary, rgba(254, 240, 173, 0.7));
                    font-size: 0.875rem;
                }

                .event-title {
                    margin: 0 0 1rem 0;
                    color: var(--text-primary, #FEF0AD);
                    font-size: 1.25rem;
                }

                .event-description {
                    color: var(--text-secondary, rgba(254, 240, 173, 0.7));
                    margin-bottom: 1.5rem;
                    display: -webkit-box;
                    -webkit-line-clamp: 3;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }

                .event-footer {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .event-price {
                    font-weight: 600;
                    color: var(--text-primary, #FEF0AD);
                }

                .event-badge {
                    position: absolute;
                    top: 1rem;
                    right: 1rem;
                    background: var(--color-primary, #005A71);
                    color: var(--text-primary, #FEF0AD);
                    padding: 0.25rem 0.75rem;
                    border-radius: 9999px;
                    font-size: 0.875rem;
                }

                .skeleton {
                    animation: pulse 1.5s infinite;
                    background: linear-gradient(
                        90deg,
                        var(--bg-secondary, #2A2922) 25%,
                        var(--bg-tertiary, #363529) 50%,
                        var(--bg-secondary, #2A2922) 75%
                    );
                    background-size: 200% 100%;
                }

                @keyframes pulse {
                    0% { background-position: 200% 0; }
                    100% { background-position: -200% 0; }
                }

                @media (max-width: 768px) {
                    .gallery {
                        grid-template-columns: 1fr;
                    }
                }
            </style>

            <div class="gallery">
                ${events.map(event => this.renderEventCard(event)).join('')}
            </div>
        `;
    }

    renderEventCard(event) {
        return `
            <div class="event-card" data-event-id="${event.id}">
                ${event.is_featured ? '<span class="event-badge">Featured</span>' : ''}
                <div class="event-image">
                    <img 
                        src="${event.image_url}" 
                        alt="${event.title}"
                        loading="lazy"
                        data-src="${event.image_url}"
                    >
                </div>
                <div class="event-content">
                    <div class="event-meta">
                        <span>${event.date}</span>
                        <span>${event.time}</span>
                    </div>
                    <h3 class="event-title">${event.title}</h3>
                    <p class="event-description">${event.description}</p>
                    <div class="event-footer">
                        <span class="event-price">
                            ${event.price === 0 ? 'Free' : `$${event.price.toFixed(2)}`}
                        </span>
                        <slot name="action-button"></slot>
                    </div>
                </div>
            </div>
        `;
    }

    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    observer.unobserve(img);
                }
            });
        }, options);

        this.shadowRoot.querySelectorAll('img[data-src]').forEach(img => {
            observer.observe(img);
        });
    }

    setupEventListeners() {
        this.shadowRoot.querySelectorAll('.event-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('slot')) {
                    const event = new CustomEvent('event-selected', {
                        detail: { eventId: card.dataset.eventId },
                        bubbles: true,
                        composed: true
                    });
                    this.dispatchEvent(event);
                }
            });
        });
    }
}

customElements.define('event-gallery', EventGallery);
