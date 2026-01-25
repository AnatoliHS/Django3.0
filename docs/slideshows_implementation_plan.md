# Implementation Plan - Slideshows & Certifications Architecture

The goal is to implement user progress tracking now, while establishing a modular architecture that separates content delivery (`slideshows`) from accreditation (`certifications`).

## User Review Required

> [!IMPORTANT]
> **Architecture Strategy**: We will decouple content from certification.
> 1.  **`slideshows` App** (This changes): Handles slide rendering, Markdown generation (future), and **User Progress Tracking**.
> 2.  **`certifications` App** (Future migration): Will handle Quizzes, Exams, and Certificate generation. It will query `slideshows` to check for content completion.
>
> **Development Standards**:
> - **Docker**: All management commands must be run via `make django cmd="..."`.
> - **Security**: All progress API endpoints must require authentication.
> - **Code Quality**: adhere to DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid) principles.

## Proposed Changes

### New App: `slideshows`

*Action*: Run `make django cmd="startapp slideshows"` to create the app.

#### [NEW] `slideshows/models.py`
Create `SlideshowProgress` model:
- `user`: ForeignKey to `User`
- `slideshow_slug`: CharField (e.g., 'whmis-general')
- `current_h`: IntegerField (Horizontal index)
- `current_v`: IntegerField (Vertical index)
- `max_percentage`: IntegerField (0-100)
- `completed`: BooleanField (Set to True when max_percentage > X%)
- `last_updated`: DateTimeField
- `Meta`: unique_together = ('user', 'slideshow_slug')

*Design Note: By keeping this separate from certification, we can easily add non-certified slideshows (e.g., "What's New in 2026") later without overhead.*

#### [NEW] `slideshows/views.py`
- `save_progress`: API endpoint (POST)
    - **Security**: `@login_required` decorator.
    - **Logic**: Update `SlideshowProgress` for `request.user`.
- `get_progress`: API endpoint (GET)
    - **Security**: `@login_required` decorator.
    - **Logic**: Return JSON with current h/v indices for `request.user`.

#### [NEW] `slideshows/urls.py`
- Define API routes: `save/`, `get/`.

### `our_site/settings.py`

#### [MODIFY] `settings.py`
- Add `'slideshows'` to `INSTALLED_APPS`.

### Frontend Integration

#### [NEW] `static/js/slideshow_progress.js`
- JS client to interface with django API.
- Debounced progress updates to server.
- Auto-resume functionality on load.
- **KISS**: Simple fetch calls, no complex state management libraries unless needed.

#### [MODIFY] `polls/templates/polls/slideshow.html` (and variants)
- **Temporary Integration**: We will inject the new JS into the existing `polls` templates for now.
- Inject `slideshow_slug` context variable (via `polls/views.py`).

### `polls/views.py` (Legacy Support)

#### [MODIFY] `views.py`
- Update existing views (`slideshow`, etc.) to pass the appropriate `slideshow_slug` to the template so the new JS knows which slideshow to track.

## Verification Plan

### Automated Tests
- `slideshows/tests.py`:
    - Model constraints (unique user+slideshow).
    - API endpoint behavior (valid/invalid data).
    - Security check: Ensure unauthenticated requests return 403/302.

### Manual Verification
- **Docker**: Use `make django cmd="..."` for any database migrations/updates.
- **Database**: confirm new table `slideshows_slideshowprogress` is created.
- **User Flow**:
    1. Login.
    2. Open WHMIS General slideshow.
    3. Advance 5 slides.
    4. Reload page -> System should auto-navigate to slide 5.
    5. Check Admin -> `SlideshowProgress` record exists.
    6. Logout & Try API directly (e.g. via curl) -> Should be denied.
