document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const mobileToggle = document.getElementById('mobile-toggle');
    const closeMenu = document.getElementById('close-menu');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-nav-link');

    function toggleMenu() {
        mobileMenu.classList.toggle('active');
        document.body.classList.toggle('no-scroll');
    }

    if (mobileToggle) {
        mobileToggle.addEventListener('click', toggleMenu);
    }

    if (closeMenu) {
        closeMenu.addEventListener('click', toggleMenu);
    }

    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (mobileMenu.classList.contains('active')) {
                toggleMenu();
            }
        });
    });

    // Sticky Header
    const header = document.getElementById('header');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Smooth Scrolling for Anchor Links
    // Smooth Scrolling for Anchor Links (Multi-page compatible)
    document.querySelectorAll('a[href]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');

            // Should we scroll? 
            // 1. It's a hash link (#id)
            // 2. It's a link to the current page with a hash (page.html#id)

            const currentPath = window.location.pathname.split('/').pop() || 'index.html';
            const targetPath = href.split('#')[0];
            const targetHash = href.split('#')[1];

            // Check if it's a link to an element on this page
            const isSamePage = (targetPath === '' || targetPath === currentPath) && targetHash;

            if (isSamePage) {
                const targetElement = document.getElementById(targetHash);
                if (targetElement) {
                    e.preventDefault();

                    const headerHeight = header.offsetHeight;
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.scrollY - headerHeight;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Active Link State Management based on URL
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');

    navLinks.forEach(link => {
        // Clear active class first (optional, as we hardcoded it in HTML, but good for safety)
        // link.classList.remove('active'); 

        const linkHref = link.getAttribute('href');

        // Simple check: if link matches current page
        // Also handle the case where products is a separate page now, so ignore hash if it's external
        if (linkHref === currentPath || (currentPath === 'index.html' && linkHref === './') || (linkHref.startsWith(currentPath) && linkHref.includes('#') === false)) {
            link.classList.add('active');
        } else if (currentPath === '' && linkHref === 'index.html') {
            link.classList.add('active');
        }
    });

    // Intersection Observer for Scroll Animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.section-title, .section-desc, .solution-card, .product-card, .about-content, .about-image-wrapper');

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.8s ease-out, transform 0.8s ease-out';
        observer.observe(el);
    });

    // Add class for visible state
    const style = document.createElement('style');
    style.innerHTML = `
        .visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
    // Logo Loop Logic
    function initLogoLoop() {
        const track = document.getElementById('logo-loop-track');
        if (!track) return;

        const techLogos = [
            { icon: "fa-brands fa-github", title: "GitHub" },
            { icon: "fa-brands fa-docker", title: "Docker" },
            { icon: "fa-brands fa-react", title: "React" },
            { icon: "fa-brands fa-aws", title: "AWS" },
            { icon: "fa-brands fa-google", title: "Google Cloud" },
            { icon: "fa-brands fa-microsoft", title: "Azure" },
            { icon: "fa-brands fa-python", title: "Python" },
            { icon: "fa-brands fa-node-js", title: "Node.js" },
            { icon: "fa-brands fa-golang", title: "Go" },
            { icon: "fa-brands fa-rust", title: "Rust" }
        ];

        // Create the logo list items
        const createList = () => {
            const ul = document.createElement('ul');
            ul.className = 'logoloop__list';
            techLogos.forEach(logo => {
                const li = document.createElement('li');
                li.className = 'logoloop__item';
                li.innerHTML = `
                    <div class="logo-item-content" title="${logo.title}">
                        <i class="${logo.icon}"></i>
                        <span class="logo-title-text" style="margin-left: 10px; font-size: 0.9rem; color: var(--text-gray); font-weight: 600;">${logo.title}</span>
                    </div>
                `;
                ul.appendChild(li);
            });
            return ul;
        };

        // Add multiple copies for infinite loop
        for (let i = 0; i < 4; i++) {
            track.appendChild(createList());
        }

        // Animation logic
        let offset = 0;
        const speed = 1; // Pixels per frame
        let isPaused = false;

        track.addEventListener('mouseenter', () => isPaused = true);
        track.addEventListener('mouseleave', () => isPaused = false);

        function animate() {
            if (!isPaused) {
                offset -= speed;

                // Reset offset if we've scrolled past one full set
                const firstChild = track.firstElementChild;
                if (firstChild) {
                    const firstWidth = firstChild.offsetWidth;
                    if (Math.abs(offset) >= firstWidth) {
                        offset += firstWidth;
                        // Move first element to end to maintain continuity if needed, 
                        // but simple offset reset works if we have enough clones
                    }
                }

                track.style.transform = `translateX(${offset}px)`;
            }
            requestAnimationFrame(animate);
        }

        animate();
    }

    initLogoLoop();

    // Theme Toggle Logic
    const themeToggleBtn = document.getElementById('theme-toggle');

    if (themeToggleBtn) {
        // Check local storage for theme preference
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'light') {
            document.body.classList.add('light-mode');
            const icon = themeToggleBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        }

        themeToggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('light-mode');
            const icon = themeToggleBtn.querySelector('i');
            let theme = 'dark';

            if (document.body.classList.contains('light-mode')) {
                theme = 'light';
                if (icon) {
                    icon.classList.remove('fa-sun');
                    icon.classList.add('fa-moon');
                }
            } else {
                if (icon) {
                    icon.classList.remove('fa-moon');
                    icon.classList.add('fa-sun');
                }
            }

            // Save preference to local storage
            localStorage.setItem('theme', theme);
        });
    }

    // ── WhatsApp Floating Chat Button ──
    const WHATSAPP_CONFIG = {
        phoneNumber: "919426082865", // Configure your WhatsApp number here (include country code, e.g. 91 for India)
        message: "Hello! I would like to know more about ReviewShield AI." // Default chat template message
    };

    function initWhatsAppButton() {
        // Prevent duplicate buttons if already present
        if (document.querySelector('.whatsapp-float')) return;

        const whatsappUrl = `https://wa.me/${WHATSAPP_CONFIG.phoneNumber}?text=${encodeURIComponent(WHATSAPP_CONFIG.message)}`;

        const btn = document.createElement('a');
        btn.className = 'whatsapp-float';
        btn.href = whatsappUrl;
        btn.target = '_blank';
        btn.rel = 'noopener noreferrer';
        btn.setAttribute('aria-label', 'Chat with us on WhatsApp');
        btn.innerHTML = `
            <i class="fa-brands fa-whatsapp"></i>
            <span class="whatsapp-tooltip">Chat with us on WhatsApp</span>
        `;

        document.body.appendChild(btn);
    }

    initWhatsAppButton();
});
