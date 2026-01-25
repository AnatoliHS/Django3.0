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

    // Backfill sidebar completion
    function backfillSidebar(targetH, targetV) {
        console.log(`[SlideshowProgress] backfillSidebar called for targetH=${targetH}, targetV=${targetV}`);

        if (!window.slideMap || !window.childMap) {
            console.warn("[SlideshowProgress] slideMap or childMap not found during restore");
            // Retry once?
            setTimeout(() => {
                if (window.slideMap && window.childMap) {
                    console.log("[SlideshowProgress] slideMap found on retry. Backfilling now.");
                    backfillSidebar(targetH, targetV);
                } else {
                    console.error("[SlideshowProgress] slideMap still missing after retry.");
                }
            }, 500);
            return;
        }

        for (let h = 0; h <= targetH; h++) {
            if (!window.slideMap[h]) {
                // Determine if this is a skip or error
                console.debug(`[SlideshowProgress] no entry in slideMap for h=${h}`);
                continue;
            }

            const vSlides = window.childMap[h] || [];
            const isCurrentH = (h === targetH);

            if (!isCurrentH) {
                // Mark all children completed
                vSlides.forEach(c => c.classList.add("completed"));
                // Mark parent completed
                if (window.slideMap[h].circle) window.slideMap[h].circle.classList.add("completed");
            } else {
                // Mark children up to targetV
                for (let v = 0; v <= targetV; v++) {
                    if (window.slideMap[h][v]) window.slideMap[h][v].classList.add("completed");
                }

                // Check if parent should be completed
                if (vSlides.length > 0) {
                    const allDone = vSlides.every(c => c.classList.contains("completed"));
                    if (allDone && window.slideMap[h].circle) window.slideMap[h].circle.classList.add("completed");
                } else {
                    if (window.slideMap[h].circle) window.slideMap[h].circle.classList.add("completed");
                }
            }
        }
    }

    // Restore progress from server
    function restoreProgress() {
        console.log(`[SlideshowProgress] Restoring progress for ${slideshowSlug}...`);
        fetch(`/slideshows/get_progress/?slideshow_slug=${slideshowSlug}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Reveal.js might not be ready, so we wait or use the API if available
                    if (window.Reveal) {
                        isRestoring = true;
                        try {
                            // Parse integers to be safe
                            const h = parseInt(data.current_h, 10);
                            const v = parseInt(data.current_v, 10) || 0;

                            console.log(`[SlideshowProgress] Restoring to h=${h}, v=${v}`);

                            // Only navigate if we are not at 0,0
                            if (h > 0 || v > 0) {
                                Reveal.slide(h, v);
                            }

                            // Always update sidebar even if at 0,0 (though 0,0 usually empty)
                            // Wait a moment for DOM updates if needed
                            setTimeout(() => {
                                console.log("[SlideshowProgress] Triggering backfillSidebar...");
                                backfillSidebar(h, v);
                            }, 300); // Increased delay slightly to be safe

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
