## Startr Style App TODOs
- [ ] **Build out Startr_Style App**: Enhance app for use in Startr/WEB-Django project
  - [ ] Enable Startr.Style base debug page template (404/403 for debug)
    - [ ] template should include Startr branding
    - [ ] links to working URL patterns
  - [ ] Enable Startr.Style base page(s) template (404, 500, 403, 400)
    - [ ] template should include Startr branding
    - [ ] links to working URL patterns
  - [ ] Enable Startr.Style admin page template
    - [ ] template should include Startr branding
    - [ ] links to working URL patterns
    - [ ] enable htmx or our liter alternative with just gets and posts for the admin page
    - [ ] optionally use swup.js for page transitions instead of htmx
  - [ ] Test/verify all templates match Startr Style guide
  - [ ] Update documentation for Startr Style usage

## Error Handling TODOs
- [ ] **Implement Missing Error Handlers**: Create views and templates for 400 and 500 errors
  - [ ] Create `handler400` view in `django_startr/views.py`
  - [ ] Create `technical_400.html` template based on Startr Style
  - [ ] Create `handler500` view in `django_startr/views.py`
  - [ ] Create `technical_500.html` template based on Startr Style
  - [ ] Register new handlers in `our_site/urls.py`
  - [ ] Test/verify error pages in DEBUG=False (production simulation)
  - [ ] Update documentation with error handling details