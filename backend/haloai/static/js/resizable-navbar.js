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
    
    // Add scroll event listener
    window.addEventListener('scroll', this.throttle(this.handleScroll.bind(this), 10));
    
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
  }
  
  handleScroll() {
    const currentScrollY = window.scrollY;
    
    if (this.navbar) {
      if (currentScrollY > 100) {
        this.navbar.classList.add('scrolled');
      } else {
        this.navbar.classList.remove('scrolled');
      }
    }
    
    this.lastScrollY = currentScrollY;
  }
  
  handleMobileMenu() {
    // Mobile menu functionality
  }
  
  toggleMobileMenu() {
    if (this.mobileMenu) {
      this.mobileMenu.classList.toggle('active');
      
      // Update toggle icon
      const icon = this.mobileMenuToggle.querySelector('i');
      if (icon) {
        if (this.mobileMenu.classList.contains('active')) {
          icon.className = 'fas fa-times';
        } else {
          icon.className = 'fas fa-bars';
        }
      }
    }
  }
  
  closeMobileMenu() {
    if (this.mobileMenu) {
      this.mobileMenu.classList.remove('active');
      
      // Update toggle icon
      const icon = this.mobileMenuToggle?.querySelector('i');
      if (icon) {
        icon.className = 'fas fa-bars';
      }
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
