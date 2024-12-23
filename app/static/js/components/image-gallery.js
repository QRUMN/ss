class ImageGallery extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.currentIndex = 0;
    }

    connectedCallback() {
        this.images = JSON.parse(this.getAttribute('images') || '[]');
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    position: relative;
                    --gallery-height: 500px;
                    --thumb-size: 80px;
                    --thumb-gap: 0.5rem;
                }

                .gallery-container {
                    position: relative;
                    height: var(--gallery-height);
                    background: var(--bg-secondary, #2A2922);
                    border-radius: 12px;
                    overflow: hidden;
                }

                .main-image {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    transition: opacity 0.3s ease;
                }

                .thumbnails {
                    display: flex;
                    gap: var(--thumb-gap);
                    padding: 1rem;
                    overflow-x: auto;
                    scrollbar-width: thin;
                    scrollbar-color: var(--color-primary) var(--bg-secondary);
                    margin-top: 1rem;
                }

                .thumbnail {
                    flex: 0 0 var(--thumb-size);
                    height: var(--thumb-size);
                    border-radius: 8px;
                    overflow: hidden;
                    cursor: pointer;
                    position: relative;
                    transition: transform 0.2s ease;
                }

                .thumbnail:hover {
                    transform: translateY(-2px);
                }

                .thumbnail.active {
                    box-shadow: 0 0 0 2px var(--color-primary);
                }

                .thumbnail img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }

                .gallery-nav {
                    position: absolute;
                    top: 50%;
                    transform: translateY(-50%);
                    width: 40px;
                    height: 40px;
                    background: rgba(0, 90, 113, 0.8);
                    border: none;
                    border-radius: 50%;
                    color: var(--text-primary);
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.2s ease;
                    z-index: 2;
                }

                .gallery-nav:hover {
                    background: var(--color-primary);
                }

                .gallery-nav.prev {
                    left: 1rem;
                }

                .gallery-nav.next {
                    right: 1rem;
                }

                .gallery-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(30, 29, 22, 0.95);
                    display: none;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                }

                .gallery-overlay.active {
                    display: flex;
                }

                .overlay-content {
                    position: relative;
                    max-width: 90vw;
                    max-height: 90vh;
                }

                .overlay-image {
                    max-width: 100%;
                    max-height: 90vh;
                    object-fit: contain;
                }

                .overlay-close {
                    position: absolute;
                    top: -2rem;
                    right: -2rem;
                    background: none;
                    border: none;
                    color: var(--text-primary);
                    font-size: 1.5rem;
                    cursor: pointer;
                }

                .overlay-caption {
                    position: absolute;
                    bottom: -2rem;
                    left: 0;
                    right: 0;
                    text-align: center;
                    color: var(--text-primary);
                    font-size: 0.875rem;
                }

                @media (max-width: 768px) {
                    :host {
                        --gallery-height: 300px;
                        --thumb-size: 60px;
                    }

                    .gallery-nav {
                        width: 32px;
                        height: 32px;
                    }
                }
            </style>

            <div class="gallery-container">
                <img 
                    src="${this.images[0]?.url}" 
                    alt="${this.images[0]?.caption || ''}"
                    class="main-image"
                >
                <button class="gallery-nav prev">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <button class="gallery-nav next">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>

            <div class="thumbnails">
                ${this.images.map((image, index) => `
                    <div class="thumbnail ${index === 0 ? 'active' : ''}" data-index="${index}">
                        <img 
                            src="${image.url}" 
                            alt="${image.caption || ''}"
                            loading="lazy"
                        >
                    </div>
                `).join('')}
            </div>

            <div class="gallery-overlay">
                <div class="overlay-content">
                    <img class="overlay-image">
                    <button class="overlay-close">&times;</button>
                    <div class="overlay-caption"></div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        const container = this.shadowRoot.querySelector('.gallery-container');
        const mainImage = this.shadowRoot.querySelector('.main-image');
        const prevBtn = this.shadowRoot.querySelector('.gallery-nav.prev');
        const nextBtn = this.shadowRoot.querySelector('.gallery-nav.next');
        const thumbnails = this.shadowRoot.querySelectorAll('.thumbnail');
        const overlay = this.shadowRoot.querySelector('.gallery-overlay');
        const overlayImage = overlay.querySelector('.overlay-image');
        const overlayCaption = overlay.querySelector('.overlay-caption');
        const closeBtn = overlay.querySelector('.overlay-close');

        // Navigation
        prevBtn.addEventListener('click', () => this.navigate(-1));
        nextBtn.addEventListener('click', () => this.navigate(1));

        // Thumbnail clicks
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', () => {
                const index = parseInt(thumb.dataset.index);
                this.setActiveImage(index);
            });
        });

        // Fullscreen view
        mainImage.addEventListener('click', () => {
            overlayImage.src = this.images[this.currentIndex].url;
            overlayCaption.textContent = this.images[this.currentIndex].caption || '';
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });

        closeBtn.addEventListener('click', () => {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (overlay.classList.contains('active')) {
                if (e.key === 'Escape') {
                    overlay.classList.remove('active');
                    document.body.style.overflow = '';
                } else if (e.key === 'ArrowLeft') {
                    this.navigate(-1);
                } else if (e.key === 'ArrowRight') {
                    this.navigate(1);
                }
            }
        });

        // Touch support
        let touchStartX = 0;
        let touchEndX = 0;

        container.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });

        container.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            if (touchStartX - touchEndX > 50) {
                this.navigate(1);
            } else if (touchEndX - touchStartX > 50) {
                this.navigate(-1);
            }
        });
    }

    navigate(direction) {
        const newIndex = this.currentIndex + direction;
        if (newIndex >= 0 && newIndex < this.images.length) {
            this.setActiveImage(newIndex);
        }
    }

    setActiveImage(index) {
        this.currentIndex = index;
        const mainImage = this.shadowRoot.querySelector('.main-image');
        const thumbnails = this.shadowRoot.querySelectorAll('.thumbnail');
        const overlayImage = this.shadowRoot.querySelector('.overlay-image');
        const overlayCaption = this.shadowRoot.querySelector('.overlay-caption');

        // Update main image
        mainImage.style.opacity = '0';
        setTimeout(() => {
            mainImage.src = this.images[index].url;
            mainImage.style.opacity = '1';
        }, 300);

        // Update thumbnails
        thumbnails.forEach(thumb => {
            thumb.classList.toggle('active', parseInt(thumb.dataset.index) === index);
        });

        // Update overlay if active
        if (this.shadowRoot.querySelector('.gallery-overlay').classList.contains('active')) {
            overlayImage.src = this.images[index].url;
            overlayCaption.textContent = this.images[index].caption || '';
        }

        // Scroll thumbnail into view
        thumbnails[index].scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
            inline: 'center'
        });
    }
}

customElements.define('image-gallery', ImageGallery);
