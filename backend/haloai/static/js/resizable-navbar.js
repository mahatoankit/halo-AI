// Resizable Navbar JavaScript
class ResizableNavbar {
  constructor() {
    this.navbar = document.querySelector('.navbar');
    this.mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    this.mobileMenu = document.querySelector('.mobile-menu');
    this.lastScrollY = window.scrollY;
    
    this.init();
  }
  
  init() {
    this.handleScroll();
    this.handleMobileMenu();
    
    // Add scroll event listener with better performance
    window.addEventListener('scroll', this.throttle(this.handleScroll.bind(this), 16));
    
    // Add mobile menu toggle
    if (this.mobileMenuToggle) {
      this.mobileMenuToggle.addEventListener('click', this.toggleMobileMenu.bind(this));
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.mobile-nav') && this.mobileMenu) {
        this.closeMobileMenu();
      }
    });
    
    // Close mobile menu when pressing Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.mobileMenu) {
        this.closeMobileMenu();
      }
    });
  }
  
  handleScroll() {
    const currentScrollY = window.scrollY;
    
    if (this.navbar) {
      // Apply glassmorphism effect when scrolled down more than 80px
      if (currentScrollY > 80) {
        this.navbar.classList.add('scrolled');
        // Add subtle animation class
        this.navbar.style.setProperty('--scroll-progress', Math.min(currentScrollY / 200, 1));
      } else {
        this.navbar.classList.remove('scrolled');
        this.navbar.style.removeProperty('--scroll-progress');
      }
    }
    
    this.lastScrollY = currentScrollY;
  }
  
  handleMobileMenu() {
    // Mobile menu functionality
  }
  
  toggleMobileMenu() {
    if (this.mobileMenu) {
      const isActive = this.mobileMenu.classList.contains('active');
      
      if (isActive) {
        this.mobileMenu.classList.remove('active');
        this.mobileMenu.classList.add('hidden');
      } else {
        this.mobileMenu.classList.remove('hidden');
        this.mobileMenu.classList.add('active');
      }
      
      // Update hamburger animation
      const hamburger = this.mobileMenuToggle.querySelector('.hamburger');
      if (hamburger) {
        hamburger.classList.toggle('active', !isActive);
      }
      
      // Update ARIA attributes
      this.mobileMenuToggle.setAttribute('aria-expanded', !isActive);
    }
  }
  
  closeMobileMenu() {
    if (this.mobileMenu) {
      this.mobileMenu.classList.remove('active');
      this.mobileMenu.classList.add('hidden');
      
      // Reset hamburger animation
      const hamburger = this.mobileMenuToggle?.querySelector('.hamburger');
      if (hamburger) {
        hamburger.classList.remove('active');
      }
      
      // Update ARIA attributes
      this.mobileMenuToggle?.setAttribute('aria-expanded', 'false');
    }
  }
  
  // Throttle function for better performance
  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new ResizableNavbar();
});
