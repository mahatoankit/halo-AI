// Mobile Menu Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Create mobile menu button
    const mobileMenuBtn = document.createElement('button');
    mobileMenuBtn.className = 'mobile-menu-btn';
    mobileMenuBtn.innerHTML = `
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
    `;
    
    // Find navigation container and header
    const navContainer = document.querySelector('.depth-4-frame-02');
    const headerContainer = document.querySelector('.depth-2-frame-0');
    
    if (navContainer && headerContainer) {
        // Create a new mobile header layout
        const mobileHeader = document.createElement('div');
        mobileHeader.className = 'mobile-header';
        
        // Find the logo container
        const logoContainer = document.querySelector('.depth-3-frame-0');
        
        if (logoContainer) {
            // Clone the logo container for mobile
            const mobileLogo = logoContainer.cloneNode(true);
            mobileLogo.className = 'mobile-logo';
            
            // Clone the nav menu for mobile
            const mobileNavMenu = navContainer.cloneNode(true);
            mobileNavMenu.classList.add('mobile-nav-menu');
            mobileNavMenu.classList.remove('depth-4-frame-02'); // Remove original class to avoid style conflicts
            
            // Clone the log out button container for mobile (if present)
            const logOutContainer = document.querySelector('.depth-5-frame-03');
            let mobileLogOut = null;
            if (logOutContainer) {
                mobileLogOut = logOutContainer.cloneNode(true);
                mobileLogOut.classList.add('mobile-log-out');
            }
            
            // Create mobile header content
            mobileHeader.innerHTML = `
                <div class="mobile-header-content">
                    <div class="mobile-logo-container"></div>
                    <div class="mobile-menu-container"></div>
                </div>
            `;
            
            // Insert mobile header before the original header
            headerContainer.parentNode.insertBefore(mobileHeader, headerContainer);
            
            // Move logo and menu button to mobile header
            const mobileLogoContainer = mobileHeader.querySelector('.mobile-logo-container');
            const mobileMenuContainer = mobileHeader.querySelector('.mobile-menu-container');
            
            mobileLogoContainer.appendChild(mobileLogo);
            mobileMenuContainer.appendChild(mobileMenuBtn);
            
            // Append the mobile nav menu to the end of body (so it overlays everything)
            document.body.appendChild(mobileNavMenu);
            
            // If log out exists, append it to the mobile nav menu
            if (mobileLogOut) {
                mobileNavMenu.appendChild(mobileLogOut);
            }
            
            // Add mobile menu styles
            const mobileMenuStyles = document.createElement('style');
            mobileMenuStyles.textContent = `
                .mobile-header {
                    display: none;
                    width: 100%;
                    background: #fafafa;
                    border-bottom: 1px solid #e5e8eb;
                    padding: 12px 16px;
                    position: relative;
                    z-index: 1001;
                }
                
                .mobile-header-content {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    width: 100%;
                }
                
                .mobile-logo-container {
                    display: flex;
                    align-items: center;
                }
                
                .mobile-menu-container {
                    display: flex;
                    align-items: center;
                }
                
                .mobile-logo {
                    display: flex;
                    align-items: center;
                    gap: 16px;
                }
                
                .mobile-logo .depth-4-frame-1 {
                    margin: 0;
                }
                
                .mobile-menu-btn {
                    display: flex;
                    flex-direction: column;
                    justify-content: space-around;
                    width: 30px;
                    height: 30px;
                    background: transparent;
                    border: none;
                    cursor: pointer;
                    padding: 0;
                    z-index: 1101;
                }
                
                .hamburger-line {
                    width: 25px;
                    height: 3px;
                    background: #121712;
                    border-radius: 10px;
                    transition: all 0.3s linear;
                    position: relative;
                    transform-origin: 1px;
                }
                
                .mobile-menu-btn.active .hamburger-line:nth-child(1) {
                    transform: rotate(45deg);
                }
                
                .mobile-menu-btn.active .hamburger-line:nth-child(2) {
                    opacity: 0;
                }
                
                .mobile-menu-btn.active .hamburger-line:nth-child(3) {
                    transform: rotate(-45deg);
                }
                
                @media (max-width: 900px) {
                    .mobile-header {
                        display: block;
                    }
                    
                    .depth-2-frame-0 {
                        display: none;
                    }
                    
                    .mobile-nav-menu {
                        display: none;
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        background: #fafafa;
                        flex-direction: column;
                        padding: 70px 8vw 32px 8vw;
                        z-index: 2000;
                        min-height: 100vh;
                        overflow-y: auto;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
                    }
                    
                    .mobile-nav-menu.active {
                        display: flex;
                    }
                    
                    .mobile-nav-menu > div {
                        margin: 0;
                        text-align: center;
                        padding: 0;
                        border-bottom: 1px solid #ececec;
                    }
                    
                    .mobile-nav-menu > div:last-child {
                        border-bottom: none;
                    }
                    
                    .mobile-nav-menu a {
                        display: block;
                        font-size: 20px;
                        color: #222;
                        padding: 20px 0 12px 0;
                        margin: 0;
                        font-weight: 600;
                        letter-spacing: 0.01em;
                        border-radius: 8px;
                        transition: background 0.2s;
                    }
                    
                    .mobile-nav-menu a:active,
                    .mobile-nav-menu a:focus {
                        background: #f0f0f0;
                    }
                    
                    .mobile-nav-menu a.log-out {
                        display: block;
                    }
                    
                    .mobile-log-out {
                        width: 100%;
                        display: block;
                        margin-top: 0;
                        margin-bottom: 0;
                        border-top: 1px solid #ececec;
                        padding-top: 56px;
                    }
                    
                    .mobile-log-out .log-out {
                        display: block !important;
                        background: none;
                        color: #222;
                        font-size: 20px;
                        font-weight: 600;
                        border: none;
                        border-radius: 0;
                        padding: 20px 0 12px 0;
                        margin: 0;
                        box-shadow: none;
                        text-align: center;
                        transition: background 0.2s;
                        cursor: pointer;
                        outline: none;
                    }
                    
                    .mobile-log-out .log-out:active,
                    .mobile-log-out .log-out:focus {
                        background: #f0f0f0;
                        box-shadow: none;
                    }
                    
                    .mobile-log-out .log-out:hover {
                        background: #f0f0f0;
                        box-shadow: none;
                    }
                }
                
                @media (max-width: 600px) {
                    .mobile-header {
                        padding: 10px 12px;
                    }
                    
                    .mobile-logo {
                        gap: 12px;
                    }
                    
                    .mobile-nav-menu {
                        padding: 60px 4vw 24px 4vw;
                    }
                    
                    .mobile-log-out .log-out {
                        max-width: 94vw;
                        font-size: 16px;
                        padding: 10px 0;
                    }
                }
                
                @media (max-width: 480px) {
                    .mobile-header {
                        padding: 8px 8px;
                    }
                    
                    .mobile-logo {
                        gap: 8px;
                    }
                    
                    .mobile-menu-btn {
                        width: 28px;
                        height: 28px;
                    }
                    
                    .hamburger-line {
                        width: 22px;
                        height: 2px;
                    }
                    
                    .mobile-nav-menu {
                        padding: 48px 2vw 16px 2vw;
                    }
                    
                    .mobile-log-out .log-out {
                        font-size: 16px;
                        padding: 10px 0;
                    }
                }
            `;
            document.head.appendChild(mobileMenuStyles);
            
            // Toggle mobile menu
            mobileMenuBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.classList.toggle('active');
                mobileNavMenu.classList.toggle('active');
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!mobileMenuBtn.contains(e.target) && !mobileNavMenu.contains(e.target)) {
                    mobileMenuBtn.classList.remove('active');
                    mobileNavMenu.classList.remove('active');
                }
            });
            
            // Close menu when clicking on a link
            const navLinks = mobileNavMenu.querySelectorAll('a');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    mobileMenuBtn.classList.remove('active');
                    mobileNavMenu.classList.remove('active');
                });
            });
            
            // Add escape key functionality
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    mobileMenuBtn.classList.remove('active');
                    mobileNavMenu.classList.remove('active');
                }
            });
        }
    } else {
        console.log('Navigation elements not found:', {
            navContainer: !!navContainer,
            headerContainer: !!headerContainer
        });
    }
});

// Add smooth scrolling for better mobile experience
document.addEventListener('DOMContentLoaded', function() {
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
});

// Add touch-friendly interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add touch feedback to buttons
    const buttons = document.querySelectorAll('button, .get-started, .log-in-btn, .sign-up-btn, .send-message, .view-profile, .view-details, .book-call');
    
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Prevent zoom on double tap
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
});

// Hide mobile header on desktop, show on mobile
function updateMobileHeaderVisibility() {
  var mobileHeader = document.querySelector('.mobile-header');
  if (mobileHeader) {
    if (window.innerWidth > 900) {
      mobileHeader.style.display = 'none';
    } else {
      mobileHeader.style.display = 'block';
    }
  }
}
window.addEventListener('resize', updateMobileHeaderVisibility);
document.addEventListener('DOMContentLoaded', updateMobileHeaderVisibility); 