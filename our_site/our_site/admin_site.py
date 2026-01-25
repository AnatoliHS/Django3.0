from django.contrib import admin

class CustomAdminSite(admin.AdminSite):
    site_header = "Startr Admin"
    site_title = "Startr Education Admin Portal"
    index_title = "Welcome to your Startr Education admin panel"

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)
        
        # Identify the 'Settings' (constance) app and move it to the end
        settings_app = None
        for i, app in enumerate(app_list):
            if app['app_label'] == 'constance':
                settings_app = app_list.pop(i)
                break
        
        if settings_app:
            app_list.append(settings_app)
            
        return app_list
