// web-menu.js: Hide mobile nav elements on desktop
function hideMobileNavOnDesktop() {
  if (window.innerWidth > 900) {
    var mobileHeader = document.querySelector('.mobile-header');
    var mobileNavMenu = document.querySelector('.mobile-nav-menu');
    if (mobileHeader) mobileHeader.style.display = 'none';
    if (mobileNavMenu) mobileNavMenu.style.display = 'none';
    // Optionally, remove from DOM for extra safety
    // if (mobileHeader && mobileHeader.parentNode) mobileHeader.parentNode.removeChild(mobileHeader);
    // if (mobileNavMenu && mobileNavMenu.parentNode) mobileNavMenu.parentNode.removeChild(mobileNavMenu);
  }
}
window.addEventListener('resize', hideMobileNavOnDesktop);
document.addEventListener('DOMContentLoaded', hideMobileNavOnDesktop); 