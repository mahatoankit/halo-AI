// Resizable Navbar JavaScript
class ResizableNavbar {
  constructor() {
    this.navbar = document.querySelector('.navbar');
    this.mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    this.mobileMenu = document.querySelector('.mobile-menu');
    this.lastScrollY = window.scrollY;
    this.highlightTimeout = null;
    
    this.init();
  }
  
  // Enhanced method to run current page detection after DOM changes
  observePageChanges() {
    // Create a MutationObserver to watch for DOM changes
    const observer = new MutationObserver((mutations) => {
      let shouldUpdateHighlight = false;
      
      mutations.forEach((mutation) => {
        // Check if navigation links were added or modified
        if (mutation.type === 'childList') {
          const addedNodes = Array.from(mutation.addedNodes);
          const hasNavLinks = addedNodes.some(node => 
            node.nodeType === Node.ELEMENT_NODE && 
            (node.classList?.contains('nav-link') || 
             node.classList?.contains('mobile-nav-link') ||
             node.querySelector?.('.nav-link, .mobile-nav-link'))
          );
          
          if (hasNavLinks) {
            shouldUpdateHighlight = true;
          }
        }
        
        // Check if class changes affected navigation
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
          const target = mutation.target;
          if (target.classList?.contains('nav-link') || target.classList?.contains('mobile-nav-link')) {
            shouldUpdateHighlight = true;
          }
        }
      });
      
      if (shouldUpdateHighlight) {
        // Debounce the highlight update
        clearTimeout(this.highlightTimeout);
        this.highlightTimeout = setTimeout(() => {
          this.highlightCurrentPage();
        }, 100);
      }
    });
    
    // Start observing
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'href']
    });
    
    return observer;
  }

  // Method to manually trigger active state update (useful for SPAs)
  updateActiveState() {
    this.highlightCurrentPage();
  }

  // Enhanced initialization with page change observation
  init() {
    this.handleScroll();
    this.highlightCurrentPage();
    this.observePageChanges();
    
    // Add scroll event listener with better performance
    window.addEventListener('scroll', this.throttle(this.handleScroll.bind(this), 16));
    
    // Re-run highlighting on various navigation events
    window.addEventListener('popstate', () => {
      setTimeout(() => this.highlightCurrentPage(), 50);
    });
    
    // Handle hash changes (for anchor links)
    window.addEventListener('hashchange', () => {
      setTimeout(() => this.highlightCurrentPage(), 50);
    });
    
    // Handle focus changes that might indicate navigation
    window.addEventListener('focus', () => {
      setTimeout(() => this.highlightCurrentPage(), 100);
    });
    
    // Close mobile menu when pressing Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
          mobileMenu.classList.remove('active');
          mobileMenu.classList.add('hidden');
          const hamburger = document.querySelector('.hamburger');
          if (hamburger) {
            hamburger.classList.remove('active');
          }
          const mobileMenuButton = document.querySelector('.mobile-menu-toggle');
          if (mobileMenuButton) {
            mobileMenuButton.setAttribute('aria-expanded', 'false');
          }
        }
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

  highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const currentUrl = window.location.href;
    
    // Remove existing active classes from all nav links
    document.querySelectorAll('.nav-link, .mobile-nav-link').forEach(link => {
      link.classList.remove('active-page', 'current-page');
    });
    
    // Enhanced URL patterns with actual Django URLs from server logs
    const urlPatterns = [
      { 
        patterns: ['/dashboard/', '/dashboard/redirect/', '/dashboard/farmer/'], 
        dataPage: 'dashboard',
        keywords: ['dashboard']
      },
      { 
        patterns: ['/crop-prediction/', '/crop-prediction/prediction/'], 
        dataPage: 'crops',
        keywords: ['crop', 'prediction']
      },
      { 
        patterns: ['/grants-and-offers/'], 
        dataPage: 'grants',
        keywords: ['grants', 'offers']
      },
      { 
        patterns: ['/sensors/'], 
        dataPage: 'sensors',
        keywords: ['sensors']
      },
      { 
        patterns: ['/marketplace/'], 
        dataPage: 'marketplace',
        keywords: ['marketplace']
      },
      { 
        patterns: ['/expert/', '/experts/'], 
        dataPage: 'expert',
        keywords: ['expert']
      },
      { 
        patterns: ['/auth/login/'], 
        dataPage: 'login',
        keywords: ['login']
      },
      { 
        patterns: ['/auth/signup/'], 
        dataPage: 'signup',
        keywords: ['sign up', 'signup']
      },
      { 
        patterns: ['/', '/home/'], 
        dataPage: 'home',
        keywords: ['home']
      }
    ];
    
    // Log for debugging
    console.log('🔍 ResizableNavbar: Detecting current page...');
    console.log('Current path:', currentPath);
    console.log('Current URL:', currentUrl);
    console.log('Available patterns:', urlPatterns.map(p => `${p.dataPage}: ${p.patterns.join(', ')}`));
    
    let foundMatch = false;
    
    // First, try data-page attribute matching (most reliable)
    for (const pattern of urlPatterns) {
      console.log(`Checking pattern for ${pattern.dataPage}:`, pattern.patterns);
      
      const pathMatches = pattern.patterns.some(p => {
        if (p === '/') {
          const homeMatch = currentPath === '/' || currentPath === '';
          console.log(`  Home pattern "${p}": ${homeMatch}`);
          return homeMatch;
        }
        const includesMatch = currentPath.includes(p) || currentUrl.includes(p);
        const exactMatch = currentPath === p;
        console.log(`  Pattern "${p}": includes=${includesMatch}, exact=${exactMatch}`);
        return includesMatch || exactMatch;
      });
      
      if (pathMatches) {
        console.log(`✅ Found match for ${pattern.dataPage}`);
        // Find links with matching data-page attribute
        const matchingLinks = document.querySelectorAll(`[data-page="${pattern.dataPage}"]`);
        console.log(`Found ${matchingLinks.length} links with data-page="${pattern.dataPage}"`);
        
        matchingLinks.forEach(link => {
          if ((link.classList.contains('nav-link') || link.classList.contains('mobile-nav-link'))) {
            link.classList.add('active-page');
            foundMatch = true;
            console.log(`Added active-page to:`, link.textContent.trim());
          }
        });
        
        if (foundMatch) break;
      }
    }
    
    // If no data-page match, fall back to href and text content matching
    if (!foundMatch) {
      for (const pattern of urlPatterns) {
        const pathMatches = pattern.patterns.some(p => {
          if (p === '/') {
            return currentPath === '/' || currentPath === '';
          }
          return currentPath.includes(p) || currentUrl.includes(p);
        });
        
        if (pathMatches) {
          // Try href matching
          const allLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
          allLinks.forEach(link => {
            const href = link.getAttribute('href') || '';
            const linkText = link.textContent.trim().toLowerCase();
            
            // Check href patterns
            const hrefMatches = pattern.patterns.some(p => href.includes(p));
            
            // Check text content
            const textMatches = pattern.keywords.some(keyword => 
              linkText.includes(keyword.toLowerCase())
            );
            
            if (hrefMatches || textMatches) {
              link.classList.add('active-page');
              foundMatch = true;
            }
          });
          
          if (foundMatch) break;
        }
      }
    }
    
    // Special handling for homepage when no other matches
    if (!foundMatch && (currentPath === '/' || currentPath === '')) {
      const homeLinks = document.querySelectorAll('[data-page="home"], a[href*="home"], a[href="/"]');
      homeLinks.forEach(link => {
        if (link.classList.contains('nav-link') || link.classList.contains('mobile-nav-link')) {
          link.classList.add('active-page');
        }
      });
    }
    
    // Log for debugging
    console.log('Current path:', currentPath);
    console.log('Active page detection completed, found match:', foundMatch);
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
