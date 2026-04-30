class OnboardingTutorial {
    constructor() {
        if (!this.hasSeenTutorial() && !window.location.href.includes('/admin/')) {
            this.init();
        }
    }

    hasSeenTutorial() {
        return localStorage.getItem('aetherstore_onboarding_complete') === 'true';
    }

    markAsSeen() {
        localStorage.setItem('aetherstore_onboarding_complete', 'true');
    }

    init() {
        console.log('Initializing Onboarding Tutorial...');

        this.overlay = document.createElement('div');
        this.overlay.id = 'onboarding-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.85);
            z-index: 10000;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        `;

        this.overlay.innerHTML = `
            <div style="text-align: center; max-width: 600px; padding: 40px; background: rgba(30, 41, 59, 0.9); border: 1px solid #4ecdc4; border-radius: 15px; box-shadow: 0 0 30px rgba(78, 205, 196, 0.3);">
                <h2 style="font-size: 2.5rem; margin-bottom: 20px; color: #4ecdc4;">Welcome to Aetherstore!</h2>
                <p style="font-size: 1.2rem; margin-bottom: 30px; line-height: 1.6;">Navigate the virtual store just like a game.</p>

                <div style="display: flex; justify-content: space-around; margin-bottom: 40px;">
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 10px;">⌨️</div>
                        <h3 style="font-size: 1.2rem; margin-bottom: 10px;">Move</h3>
                        <p style="color: #94a3b8;">Use W, A, S, D keys<br>or the virtual joystick</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 10px;">🖱️</div>
                        <h3 style="font-size: 1.2rem; margin-bottom: 10px;">Look Around</h3>
                        <p style="color: #94a3b8;">Click & Drag mouse<br>or swipe on screen</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 10px;">👆</div>
                        <h3 style="font-size: 1.2rem; margin-bottom: 10px;">Interact</h3>
                        <p style="color: #94a3b8;">Click on clothing<br>to view and try on</p>
                    </div>
                </div>

                <button id="start-exploration" style="background: linear-gradient(135deg, #4ecdc4 0%, #556270 100%); color: white; border: none; padding: 15px 40px; font-size: 1.2rem; border-radius: 30px; cursor: pointer; font-weight: bold; transition: transform 0.2s, box-shadow 0.2s;">
                    Start Exploring
                </button>
            </div>
        `;

        document.body.appendChild(this.overlay);

        // Trigger fade in
        setTimeout(() => {
            this.overlay.style.opacity = '1';
        }, 500);

        // Event listener for close button
        document.getElementById('start-exploration').addEventListener('click', () => {
            this.closeTutorial();
        });
    }

    closeTutorial() {
        this.overlay.style.opacity = '0';
        setTimeout(() => {
            this.overlay.remove();
            this.markAsSeen();
        }, 500);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.onboardingTutorial = new OnboardingTutorial();
});
