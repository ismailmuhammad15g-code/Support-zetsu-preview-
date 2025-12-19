/**
 * Hamburger Menu - Microsoft Fluent Design Style
 * Responsive navigation menu for mobile devices
 */

document.addEventListener('DOMContentLoaded', function() {
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const navbarNav = document.getElementById('navbarNav');
    
    if (hamburgerBtn && navbarNav) {
        // Toggle menu on hamburger button click
        hamburgerBtn.addEventListener('click', function() {
            // Toggle active class on hamburger button
            hamburgerBtn.classList.toggle('active');
            
            // Toggle active class on navigation menu
            navbarNav.classList.toggle('active');
            
            // Toggle body overflow to prevent scrolling when menu is open
            if (navbarNav.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        // Close menu when clicking on a link
        const navLinks = navbarNav.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                hamburgerBtn.classList.remove('active');
                navbarNav.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInsideMenu = navbarNav.contains(event.target);
            const isClickOnHamburger = hamburgerBtn.contains(event.target);
            
            if (!isClickInsideMenu && !isClickOnHamburger && navbarNav.classList.contains('active')) {
                hamburgerBtn.classList.remove('active');
                navbarNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        // Close menu on window resize to desktop size
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768 && navbarNav.classList.contains('active')) {
                hamburgerBtn.classList.remove('active');
                navbarNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
});
