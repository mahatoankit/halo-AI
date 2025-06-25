// Forms and Interactive Features for Halo AI
// Enhanced form handling, validation, and user interactions

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== ENHANCED FORM HANDLING =====
    
    function initEnhancedForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Add form enhancement classes
            form.classList.add('enhanced-form');
            
            // Add floating labels
            const inputs = form.querySelectorAll('input, textarea');
            inputs.forEach(input => {
                addFloatingLabel(input);
                addInputEnhancements(input);
            });
            
            // Add form submission feedback
            form.addEventListener('submit', handleEnhancedFormSubmit);
        });
    }
    
    function addFloatingLabel(input) {
        const label = input.parentNode.querySelector('label');
        if (label) {
            label.classList.add('floating-label');
            
            // Check if input has value on load
            if (input.value) {
                label.classList.add('active');
            }
            
            // Handle focus and blur events
            input.addEventListener('focus', function() {
                label.classList.add('active');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    label.classList.remove('active');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.value) {
                    label.classList.add('active');
                } else {
                    label.classList.remove('active');
                }
            });
        }
    }
    
    function addInputEnhancements(input) {
        // Add character counter for textareas
        if (input.tagName === 'TEXTAREA') {
            const counter = document.createElement('div');
            counter.className = 'char-counter';
            counter.style.cssText = `
                font-size: 12px;
                color: #666;
                text-align: right;
                margin-top: 4px;
            `;
            input.parentNode.appendChild(counter);
            
            function updateCounter() {
                const maxLength = input.maxLength || 500;
                const currentLength = input.value.length;
                counter.textContent = `${currentLength}/${maxLength}`;
                
                if (currentLength > maxLength * 0.9) {
                    counter.style.color = '#e74c3c';
                } else {
                    counter.style.color = '#666';
                }
            }
            
            input.addEventListener('input', updateCounter);
            updateCounter();
        }
        
        // Add password strength indicator
        if (input.type === 'password') {
            const strengthIndicator = document.createElement('div');
            strengthIndicator.className = 'password-strength';
            strengthIndicator.style.cssText = `
                height: 4px;
                background: #e5e8eb;
                border-radius: 2px;
                margin-top: 8px;
                overflow: hidden;
            `;
            
            const strengthBar = document.createElement('div');
            strengthBar.style.cssText = `
                height: 100%;
                width: 0%;
                transition: all 0.3s ease;
                border-radius: 2px;
            `;
            strengthIndicator.appendChild(strengthBar);
            input.parentNode.appendChild(strengthIndicator);
            
            function updatePasswordStrength() {
                const password = input.value;
                let strength = 0;
                
                if (password.length >= 6) strength += 25;
                if (password.match(/[a-z]/)) strength += 25;
                if (password.match(/[A-Z]/)) strength += 25;
                if (password.match(/[0-9]/)) strength += 25;
                
                strengthBar.style.width = strength + '%';
                
                if (strength <= 25) {
                    strengthBar.style.backgroundColor = '#e74c3c';
                } else if (strength <= 50) {
                    strengthBar.style.backgroundColor = '#f39c12';
                } else if (strength <= 75) {
                    strengthBar.style.backgroundColor = '#f1c40f';
                } else {
                    strengthBar.style.backgroundColor = '#27ae60';
                }
            }
            
            input.addEventListener('input', updatePasswordStrength);
        }
    }
    
    function handleEnhancedFormSubmit(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            // Add loading state
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            
            // Simulate form processing
            setTimeout(() => {
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
                
                // Show success message
                if (window.HaloAI && window.HaloAI.showNotification) {
                    window.HaloAI.showNotification('Form submitted successfully!', 'success');
                }
            }, 2000);
        }
    }
    
    // ===== INTERACTIVE FEATURES =====
    
    function initInteractiveFeatures() {
        // Add hover effects to cards
        const cards = document.querySelectorAll('.depth-6-frame-04 > div, .depth-7-frame-02');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
                this.style.boxShadow = '0 15px 35px rgba(0,0,0,0.1)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '';
            });
        });
        
        // Add click effects to buttons
        const buttons = document.querySelectorAll('button, .log-in-btn, .get-started');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                // Create ripple effect
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255,255,255,0.3);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    pointer-events: none;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
        
        // Add scroll-triggered animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        const animatedElements = document.querySelectorAll('.depth-4-frame-12, .depth-5-frame-12 > div');
        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(50px)';
            el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            observer.observe(el);
        });
    }
    
    // ===== RESPONSIVE UTILITIES =====
    
    function initResponsiveUtilities() {
        // Add responsive navigation highlighting
        const navLinks = document.querySelectorAll('.depth-4-frame-02 a');
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage || (currentPage === 'index.html' && href === '#')) {
                link.classList.add('current-page');
            }
            
            // Add hover effects
            link.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.color = '#3498db';
            });
            
            link.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                if (!this.classList.contains('current-page')) {
                    this.style.color = '';
                }
            });
        });
        
        // Add mobile-friendly touch targets
        const touchTargets = document.querySelectorAll('a, button, input[type="submit"]');
        touchTargets.forEach(target => {
            if (window.innerWidth <= 768) {
                target.style.minHeight = '44px';
                target.style.minWidth = '44px';
            }
        });
    }
    
    // ===== PERFORMANCE OPTIMIZATIONS =====
    
    function initPerformanceOptimizations() {
        // Lazy load images
        const images = document.querySelectorAll('img[src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                }
            });
        });
        
        images.forEach(img => {
            if (!img.classList.contains('lazy')) {
                img.dataset.src = img.src;
                img.classList.add('lazy');
                imageObserver.observe(img);
            }
        });
        
        // Debounce scroll events
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(function() {
                // Handle scroll-based animations
            }, 16); // ~60fps
        });
    }
    
    // ===== INITIALIZATION =====
    
    function init() {
        initEnhancedForms();
        initInteractiveFeatures();
        initResponsiveUtilities();
        initPerformanceOptimizations();
        
        // Add CSS animations
        addFormStyles();
    }
    
    function addFormStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .enhanced-form {
                position: relative;
            }
            
            .floating-label {
                position: absolute;
                top: 50%;
                left: 16px;
                transform: translateY(-50%);
                transition: all 0.3s ease;
                pointer-events: none;
                color: #666;
            }
            
            .floating-label.active {
                top: 0;
                left: 12px;
                font-size: 12px;
                color: #3498db;
                background: white;
                padding: 0 4px;
            }
            
            .input-field:focus + .floating-label,
            .input-field:not(:placeholder-shown) + .floating-label {
                top: 0;
                left: 12px;
                font-size: 12px;
                color: #3498db;
                background: white;
                padding: 0 4px;
            }
            
            .current-page {
                color: #3498db !important;
                font-weight: 700;
            }
            
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
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
            
            .lazy {
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .lazy.loaded {
                opacity: 1;
            }
            
            /* Enhanced mobile responsiveness */
            @media (max-width: 768px) {
                .depth-4-frame-02 a {
                    padding: 12px 16px;
                    margin: 4px 0;
                    border-radius: 8px;
                    transition: all 0.3s ease;
                }
                
                .depth-4-frame-02 a:hover {
                    background: rgba(52, 152, 219, 0.1);
                }
                
                .input-field {
                    font-size: 16px; /* Prevents zoom on iOS */
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Start initialization
    init();
}); 