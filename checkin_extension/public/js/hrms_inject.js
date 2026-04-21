// Inject Project Check In button into HRMS mobile app
(function() {
    // Only run on HRMS pages
    if (!window.location.pathname.startsWith('/hrms')) return;
    
    // Wait for HRMS app to load
    const maxAttempts = 50;
    let attempts = 0;
    
    const injectButton = () => {
        attempts++;
        
        // Find the Check In button in HRMS
        const checkInBtn = document.querySelector('button[class*="check"]') || 
                          document.querySelector('[class*="checkin"]') ||
                          Array.from(document.querySelectorAll('button')).find(b => 
                              b.textContent.toLowerCase().includes('check in')
                          );
        
        // Also try finding by the container structure
        const homeContent = document.querySelector('[class*="home"]') ||
                           document.querySelector('main') ||
                           document.querySelector('#app');
        
        // Check if our button already exists
        if (document.getElementById('project-checkin-btn')) return;
        
        // If we found a check-in button or home content, inject our button
        if (checkInBtn || (homeContent && attempts > 10)) {
            const btn = document.createElement('button');
            btn.id = 'project-checkin-btn';
            btn.innerHTML = '📍 Project Check In';
            btn.style.cssText = `
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                width: 100%;
                max-width: 300px;
                margin: 12px auto;
                padding: 14px 24px;
                font-size: 16px;
                font-weight: 600;
                color: white;
                background: linear-gradient(135deg, #10B981, #059669);
                border: none;
                border-radius: 12px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            `;
            
            btn.onclick = () => {
                window.location.href = '/project-checkin';
            };
            
            // Insert after check-in button or in home content
            if (checkInBtn && checkInBtn.parentElement) {
                checkInBtn.parentElement.insertBefore(btn, checkInBtn.nextSibling);
            } else if (homeContent) {
                // Find a good spot in the home content
                const firstSection = homeContent.querySelector('section') || 
                                    homeContent.querySelector('div > div');
                if (firstSection) {
                    firstSection.appendChild(btn);
                } else {
                    homeContent.appendChild(btn);
                }
            }
            
            console.log('Project Check In button injected');
            return;
        }
        
        // Retry
        if (attempts < maxAttempts) {
            setTimeout(injectButton, 200);
        }
    };
    
    // Start injection after DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectButton);
    } else {
        setTimeout(injectButton, 500);
    }
    
    // Also watch for route changes in SPA
    const observer = new MutationObserver(() => {
        if (!document.getElementById('project-checkin-btn')) {
            setTimeout(injectButton, 300);
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
})();
