// slideshow_progress.js

(function () {
    let slideshowSlug = null;
    let saveTimeout = null;
    let isRestoring = false;

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Save progress to server (Debounced)
    function saveProgress(h, v, progress) {
        if (isRestoring) return; // Don't save while restoring

        if (saveTimeout) clearTimeout(saveTimeout);

        saveTimeout = setTimeout(() => {
            const maxPercentage = Math.round(progress * 100);

            fetch('/slideshows/save_progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    slideshow_slug: slideshowSlug,
                    current_h: h,
                    current_v: v,
                    max_percentage: maxPercentage
                })
            })
                .then(response => {
                    if (!response.ok) console.error('Failed to save progress');
                })
                .catch(error => console.error('Error saving progress:', error));
        }, 1000); // 1 second debounce
    }

    // Restore progress from server
    function restoreProgress() {
        fetch(`/slideshows/get_progress/?slideshow_slug=${slideshowSlug}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Reveal.js might not be ready, so we wait or use the API if available
                    if (window.Reveal) {
                        isRestoring = true;
                        try {
                            // Only navigate if we are not at 0,0
                            if (data.current_h > 0 || data.current_v > 0) {
                                Reveal.slide(data.current_h, data.current_v);
                                console.log(`Restored progress to ${data.current_h}, ${data.current_v}`);
                            }
                        } finally {
                            // Small delay to ensure we don't trigger save immediately
                            setTimeout(() => { isRestoring = false; }, 500);
                        }
                    } else {
                        console.error('Reveal.js not found when restoring progress');
                    }
                }
            })
            .catch(error => console.error('Error restoring progress:', error));
    }

    // Initialize
    window.initSlideshowProgress = function (slug) {
        slideshowSlug = slug;
        if (!slideshowSlug) {
            console.error('No slideshow slug provided for progress tracking');
            return;
        }

        // Wait for Reveal to be ready
        if (window.Reveal) {
            if (Reveal.isReady()) {
                restoreProgress();
                attachListener();
            } else {
                Reveal.on('ready', () => {
                    restoreProgress();
                    attachListener();
                });
            }
        } else {
            // Poll for Reveal
            const checkReveal = setInterval(() => {
                if (window.Reveal) {
                    clearInterval(checkReveal);
                    if (Reveal.isReady()) {
                        restoreProgress();
                        attachListener();
                    } else {
                        Reveal.on('ready', () => {
                            restoreProgress();
                            attachListener();
                        });
                    }
                }
            }, 100);
        }
    };

    function attachListener() {
        Reveal.on('slidechanged', event => {
            saveProgress(event.indexh, event.indexv, event.progress);
        });
    }

})();
