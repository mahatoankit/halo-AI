// Main JavaScript for Halo AI Website
// Enhanced functionality, responsiveness, and user experience

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== GLOBAL UTILITIES =====
    
    // Smooth scrolling for anchor links
    function initSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    // ===== FORM VALIDATION & ENHANCEMENT =====
    
    function initFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            // Real-time validation
            inputs.forEach(input => {
                input.addEventListener('blur', validateField);
                input.addEventListener('input', clearFieldError);
            });
            
            // Form submission
            form.addEventListener('submit', handleFormSubmit);
        });
    }
    
    function validateField(e) {
        const field = e.target;
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Remove existing error styling
        field.classList.remove('error');
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Validation rules
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        } else if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        } else if (field.type === 'password' && value) {
            if (value.length < 6) {
                isValid = false;
                errorMessage = 'Password must be at least 6 characters long';
            }
        }
        
        // Show error if invalid
        if (!isValid) {
            field.classList.add('error');
            showFieldError(field, errorMessage);
        }
        
        return isValid;
    }
    
    function showFieldError(field, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: #e74c3c;
            font-size: 12px;
            margin-top: 4px;
            display: block;
        `;
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearFieldError(e) {
        const field = e.target;
        field.classList.remove('error');
        const errorMessage = field.parentNode.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }
    
    function handleFormSubmit(e) {
        const form = e.target;
        const inputs = form.querySelectorAll('input, textarea, select');
        let isValid = true;
        
        // Validate all fields
        inputs.forEach(input => {
            if (!validateField({ target: input })) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showNotification('Please fix the errors in the form', 'error');
        } else {
            // Show success message for demo purposes
            e.preventDefault();
            showNotification('Form submitted successfully!', 'success');
            
            // Simulate form processing
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = 'Processing...';
                submitBtn.disabled = true;
                
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 2000);
            }
        }
    }
    
    // ===== NOTIFICATION SYSTEM =====
    
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        // Set background color based on type
        switch(type) {
            case 'success':
                notification.style.backgroundColor = '#27ae60';
                break;
            case 'error':
                notification.style.backgroundColor = '#e74c3c';
                break;
            case 'warning':
                notification.style.backgroundColor = '#f39c12';
                break;
            default:
                notification.style.backgroundColor = '#3498db';
        }
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
    
    // ===== RESPONSIVE ENHANCEMENTS =====
    
    function initResponsiveEnhancements() {
        // Add responsive classes to body
        function updateResponsiveClasses() {
            const width = window.innerWidth;
            document.body.classList.remove('mobile', 'tablet', 'desktop');
            
            if (width < 768) {
                document.body.classList.add('mobile');
            } else if (width < 1024) {
                document.body.classList.add('tablet');
            } else {
                document.body.classList.add('desktop');
            }
        }
        
        updateResponsiveClasses();
        window.addEventListener('resize', updateResponsiveClasses);
        
        // Enhance mobile menu functionality
        enhanceMobileMenu();
    }
    
    function enhanceMobileMenu() {
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        const mobileNavMenu = document.querySelector('.mobile-nav-menu');
        
        if (mobileMenuBtn && mobileNavMenu) {
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!mobileMenuBtn.contains(e.target) && !mobileNavMenu.contains(e.target)) {
                    mobileMenuBtn.classList.remove('active');
                    mobileNavMenu.classList.remove('active');
                }
            });
            
            // Close menu when clicking on a link
            const mobileLinks = mobileNavMenu.querySelectorAll('a');
            mobileLinks.forEach(link => {
                link.addEventListener('click', function() {
                    mobileMenuBtn.classList.remove('active');
                    mobileNavMenu.classList.remove('active');
                });
            });
        }
    }
    
    // ===== ANIMATION & INTERACTIVITY =====
    
    function initAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe elements for animation
        const animateElements = document.querySelectorAll('.depth-4-frame-12, .depth-5-frame-12 > div, .depth-6-frame-04 > div');
        animateElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
        
        // Add animation classes
        document.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const parallaxElements = document.querySelectorAll('.depth-6-frame-02');
            
            parallaxElements.forEach(element => {
                const speed = 0.5;
                element.style.transform = `translateY(${scrolled * speed}px)`;
            });
        });
    }
    
    // Add animation styles
    function addAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .animate-in {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
            
            .error {
                border-color: #e74c3c !important;
                box-shadow: 0 0 0 2px rgba(231, 76, 60, 0.2) !important;
            }
            
            .input-field:focus {
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
            }
            
            .log-in-btn, .get-started {
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .log-in-btn:hover, .get-started:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .log-in-btn:active, .get-started:active {
                transform: translateY(0);
            }
            
            /* Loading animation */
            .loading {
                position: relative;
            }
            
            .loading::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 20px;
                height: 20px;
                margin: -10px 0 0 -10px;
                border: 2px solid transparent;
                border-top: 2px solid currentColor;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Responsive improvements */
            @media (max-width: 768px) {
                .depth-4-frame-12 {
                    padding: 20px 16px;
                }
                
                .depth-5-frame-12 > div {
                    margin-bottom: 30px;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // ===== NAVIGATION ENHANCEMENTS =====
    
    function initNavigationEnhancements() {
        // Active page highlighting
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const navLinks = document.querySelectorAll('a[href]');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage || (currentPage === 'index.html' && href === '#')) {
                link.classList.add('active');
            }
        });
        
        // Smooth page transitions
        const internalLinks = document.querySelectorAll('a[href$=".html"]');
        internalLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                if (this.href && this.href.includes(window.location.origin)) {
                    e.preventDefault();
                    const targetUrl = this.href;
                    
                    // Add fade out effect
                    document.body.style.opacity = '0';
                    document.body.style.transition = 'opacity 0.3s ease';
                    
                    setTimeout(() => {
                        window.location.href = targetUrl;
                    }, 300);
                }
            });
        });
    }
    
    // ===== PERFORMANCE OPTIMIZATIONS =====
    
    function initPerformanceOptimizations() {
        // Lazy loading for images
        const images = document.querySelectorAll('img[src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => {
            if (img.src && !img.classList.contains('lazy')) {
                img.dataset.src = img.src;
                img.classList.add('lazy');
                imageObserver.observe(img);
            }
        });
        
        // Debounce resize events
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                // Handle resize events here
            }, 250);
        });
    }
    
    // ===== ACCESSIBILITY ENHANCEMENTS =====
    
    function initAccessibilityEnhancements() {
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                // Close mobile menu
                const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
                const mobileNavMenu = document.querySelector('.mobile-nav-menu');
                if (mobileMenuBtn && mobileNavMenu) {
                    mobileMenuBtn.classList.remove('active');
                    mobileNavMenu.classList.remove('active');
                }
            }
        });
        
        // Focus management
        const focusableElements = document.querySelectorAll('a, button, input, textarea, select');
        focusableElements.forEach(element => {
            element.addEventListener('focus', function() {
                this.style.outline = '2px solid #3498db';
                this.style.outlineOffset = '2px';
            });
            
            element.addEventListener('blur', function() {
                this.style.outline = '';
                this.style.outlineOffset = '';
            });
        });
    }
    
    // ===== INITIALIZATION =====
    
    // Initialize all functionality
    function init() {
        addAnimationStyles();
        initSmoothScrolling();
        initFormValidation();
        initResponsiveEnhancements();
        initAnimations();
        initNavigationEnhancements();
        initPerformanceOptimizations();
        initAccessibilityEnhancements();
        
        // Show welcome message on homepage
        if (window.location.pathname.includes('index.html') || window.location.pathname.endsWith('/')) {
            setTimeout(() => {
                showNotification('Welcome to Halo AI! 🌾', 'success');
            }, 1000);
        }
    }
    
    // Start initialization
    init();
    
    // ===== GLOBAL FUNCTIONS =====
    
    // Make functions globally available
    window.HaloAI = {
        showNotification,
        validateField,
        initFormValidation
    };
});

// Add CSS for enhanced styling
const enhancedStyles = `
    /* Enhanced button styles */
    .log-in-btn, .get-started, button {
        cursor: pointer;
        transition: all 0.3s ease;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .log-in-btn:hover, .get-started:hover, button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Enhanced input styles */
    .input-field {
        transition: all 0.3s ease;
        border-radius: 8px;
        padding: 12px 16px;
        border: 2px solid #e5e8eb;
    }
    
    .input-field:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    /* Active navigation link */
    a.active {
        color: #3498db !important;
        font-weight: 700;
    }
    
    /* Enhanced card hover effects */
    .depth-6-frame-04 > div {
        transition: all 0.3s ease;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .depth-6-frame-04 > div:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Loading states */
    .loading {
        pointer-events: none;
        opacity: 0.7;
    }
    
    /* Responsive text sizing */
    @media (max-width: 768px) {
        .halo-ai2 {
            font-size: 24px !important;
            line-height: 1.3 !important;
        }
        
        .empowering-farmers-with-ai-driven-insights {
            font-size: 16px !important;
            line-height: 1.5 !important;
        }
    }
`;

// Inject enhanced styles
const styleSheet = document.createElement('style');
styleSheet.textContent = enhancedStyles;
document.head.appendChild(styleSheet); 