# Startr/WEB-Django 🚀

[![Docker Pulls](https://img.shields.io/docker/pulls/startr/web-django.svg)](https://hub.docker.com/r/startr/web-django)
[![Docker Stars](https://img.shields.io/docker/stars/startr/web-django.svg)](https://hub.docker.com/r/startr/web-django)
[![Docker Build Status](https://img.shields.io/docker/cloud/build/startr/web-django.svg)](https://hub.docker.com/r/startr/web-django)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/Startr/WEB-Django.svg)](https://github.com/Startr/WEB-Django/graphs/contributors)
[![Last Commit](https://img.shields.io/github/last-commit/Startr/WEB-Django.svg)](https://github.com/Startr/WEB-Django/commits/main)

## Your Django Project's Perfect Launchpad 🚀

*Startr.Team:* One morning at 9:30 o'clock, our team faced a challenge. We needed a Django solution that worked instantly. No more waiting. No more setup headaches. That day, Startr/WEB-Django was born.

This is not just another template. It is your express ticket to building powerful web applications. We built it for developers who value their time. We built it for teams that move fast.

### Why Startr/WEB-Django? ✨

We believe in speed without compromise. Our solution delivers:

- **Lightning-Fast Setup**: Go from zero to coding in minutes
- **Production-Ready**: Built with security first
- **Developer-Friendly**: Tools that make development a joy
- **Scalable Architecture**: Grows with your project
- **Modern Stack**: Python 3.11 + Django 4.2 + Docker

### The Story Behind Startr/WEB-Django

>When I left Etsy, I saw developers constantly struggle. They spent hours setting up environments. They fought with dependencies. They lost precious time.
>
>I asked myself: "What if we could change this?" The answer came in a Docker image. It spins up instantly. It works seamlessly. It lets you focus on what matters - building great applications.
>
>  - Alex Somma
>  - Sage.is CTO
  

## v0.9.7

 - Backup and restore panel added to admin
 - Enhance person_detail.html layout and improve database initialization in apps.py 
 - db README.md added for clearer comunication of db managment
 - Now with auto setup on first launch
 - Added filesystem caching for improved admin performance
 - Multi-language support with Google Translate integration
 - Enhanced profile sharing and public visibility options
 - Improved badge management system with new badge images
 - Notification email settings for new user signups and admin alerts
 - Easy backup and restoration through Makefile commands
 - Optimized YearSelectorWidget for K-12 educational institutions
 - Enhanced UI with improved templates and user experience

## Major new features and functionality.

 - Performance optimization with filesystem caching for admin interfaces
 - Cache management commands for maintenance and performance tuning
 - Site-wide configuration using django-constance
 - Refactored styles using Startr.Style Utilities
 - Enhanced user-specific views and permissions
 - CSV import functionality for people data
 - Custom YearSelectorWidget for improved date handling
 - Dynamic site title, subtitle, and favicon configuration
 - Improved media handling for profile pictures

Welcome to the foundation of Startr/WEB-Django.

In the early days, we needed a solution that was simple, fast, and effective. One early morning, with great coffee in hand and a spark of creativity, we crafted a Docker image that spins up instantly and works seamlessly.

## Run it with:

```bash
make it_run
# This will launch the container and mount the project directory into the container
# You can now start developing your Django project with the following command
python manage.py makemigrations && python manage.py migrate && python /project/our_site/manage.py runserver 0.0.0.0:8080
```

This mounts your project directory into `/project`, letting you jump straight into coding. It's fast and efficient—just what's needed for smooth development.

We've kept it lean and streamlined—no unnecessary frills, just pure productivity. If you've struggled with environments before, this will feel like a relief.

## Makefile Commands

This project includes a Makefile to make development tasks easier:

```bash
# Run Django management commands
make django cmd='command'  # Example: make django cmd='migrate'

# Access the Docker container shell
make bash

# Set up Django groups
make setup_groups

# Run the development server
make it_run

# Build the Docker image
make it_build

# Generate code with Django Startr
make it_startr
```

## Recent Updates

### Multi-language Support
- Added Google Translate integration for seamless translation of website content
- Implemented smooth transitions and styling for language switching
- Created dedicated translate app for centralized translation functionality
- Enhanced base template with language selection options

### Profile Visibility and Sharing
- Implemented public profile sharing options with customizable visibility settings
- Enhanced profile visibility controls for guardians, students, and activities
- Added temporary access links for sharing profiles with non-registered users
- Improved UI messaging around profile sharing options

### Badge Management System
- Added new badge images for various activities and achievements
- Enhanced badge upload functionality with improved UI
- Added badges field to Group model for group-level achievements
- Updated templates to better display badges in profiles and group pages

### Admin Performance Optimization
- Implemented filesystem-based caching system for admin interfaces
- Added caching for ParticipationInline queryset to improve loading speed
- Cached YearSelectorWidget to reduce redundant calculations
- Created cache management commands (clear_cache, warm_cache)
- Smart cache invalidation to maintain data consistency when records change
- See [CACHING.md](our_site/CACHING.md) for detailed documentation

### Email Notifications
- Implemented notification email settings for new user signups
- Added admin alert system for important site events
- Configured email templates for various notification types

### Backup System
- Added backup and fetch backup commands to Makefile for easy data management
- Created sample.env file for environment configuration
- Improved database consistency with regular updates

### YearSelectorWidget Enhancements
- Adjusted year range in YearSelectorWidget to better support K-12 schools
- Improved user experience for selecting graduation years
- Enhanced Person model representation to include graduating year

### Site Configuration with django-constance
- Added dynamic site configuration (title, subtitle, favicon) using django-constance
- Integrated configuration with admin interface for easy management
- Updated templates to use dynamic configuration values
- Improved favicon handling through media uploads

### Style and UX Improvements
- Refactored inline styles to Startr.Style Utilities for better maintainability
- Enhanced group detail view with permission-based member filtering
- Improved person and participation lists with user-specific messages
- Simplified update/delete options based on user roles
- Enhanced person detail view with profile picture display
- Updated CSV import form layout with clearer instructions

### New Components and Features
- Implemented YearSelectorWidget for intuitive year selection in forms
- Added CSV import functionality for people data
- Enhanced profile picture display in person detail views
- Updated database schema to support new features

### Media Management
- Reorganized media files into a proper `/media` structure
- Updated settings to use the new media structure
- Created a script (`move_media.py`) to migrate existing media files
- Added proper media upload handling for profile pictures

### User Experience Improvements
- Enhanced person listing to show relationships between guardians and students
- Added badges to clearly identify user's own profile and their students
- Created a new accounts app with dashboard and profile management
- Implemented proper permission checks for viewing student information

### Guardian-Student Relationship
- Updated views to filter students based on guardian relationships
- Added visual indicators for student-guardian relationships
- Enhanced account dashboard to show student and guardian information

## Why Use This?

- **Seamless setup**: One Dockerfile gives you a fully configured Python 3.11 environment with Django and `requests`—all ready to go.
- **Efficient multi-stage build**: The Dockerfile's multi-stage build keeps the final image small and production-ready.
- **Consistent development**: No more mismatched dependencies—`pipenv` ensures a clean, reproducible virtual environment every time.
- With `bash <(curl -sL startr.sh) run` and Startr/WEB-Django our
  repository is automatically mounted into your container for rapid
  development
- Simple versioning with our awesome make targets :D

## Django Startr Code Generator

This project uses [Django Startr](our_submodules/STARTR-django-code) as a productivity booster for rapid development. Django Startr automatically generates:

- Views (List, Detail, Create, Update, Delete)
- Forms
- URLs
- Admin interfaces
- Templates

### How We Use Django Startr

1. **Installation**: We've integrated Django Startr as a git submodule at `our_submodules/STARTR-django-code` with a symlink to make it easily accessible:

```bash
# This has already been done for you in this project
git submodule add https://github.com/Startr/STARTR-django-code.git our_submodules/STARTR-django-code
ln -s our_submodules/STARTR-django-code/django_startr django_startr
```

2. **Usage**: After creating a new model, run:

```bash
# Generate code for all models in an app
python manage.py startr your_app_name

# Or generate for specific models
python manage.py startr your_app_name:Model1,Model2
```

3. **Customization**: After generating the code, you can customize the views, templates, and admin interfaces to fit your specific requirements.

For more details on using Django Startr, see the [Django Startr README](our_submodules/STARTR-django-code/README.md).

## How to Get Started

### 1. Build the Docker Image

First, clone the repository and build the Docker image with:

```sh
git clone https://github.com/Startr/WEB-Django/
cd WEB-Django
bash <(curl -sL startr.sh) run
```

### 2. Start Developing

1. Create your Django models
2. Use Django Startr to generate CRUD functionality
3. Customize the generated code as needed
4. Develop your application's unique features

### 3. Push to Production

When you're ready to deploy, push your code to a production server. You can use the same Docker image to run your Django app in production.

## v0.9.4 (May 15, 2025)

### Performance Improvements
- Optimized admin interface performance with enhanced caching strategies
- Improved ParticipationInline loading speed for large groups
- Added case-insensitive facilitator role matching
- Enhanced query optimization with strategic prefetch_related and select_related
- Implemented intelligent cache invalidation for group and participation updates

### Admin Interface Enhancements
- Facilitators now consistently appear at the top of participation lists
- Improved sorting for group members with role-based prioritization
- Enhanced YearSelectorWidget performance
- Optimized JSON handling for participation years

### Developer Experience
- Added debugging tools for facilitator queries
- Improved cache management commands
- Enhanced documentation for performance optimization
- Added cache warmup utilities for production deployment

### Documentation
- Added PERFORMANCE_OPTIMIZATION.md with detailed caching strategies
- Updated deployment guidelines with cache configuration
- Added benchmarking documentation for admin interfaces

