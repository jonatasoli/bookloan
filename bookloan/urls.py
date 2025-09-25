from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
import os

# Admin View that serves Vue.js app
class VueAdminView(TemplateView):
    template_name = 'admin/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

urlpatterns = [
    # Django Admin (renamed for backup access)
    path('django-admin/', admin.site.urls),
    
    # API Routes
    path('api/', include('library.urls')),
    
    # Vue.js Admin Interface (replaces Django admin)
    path('admin/', VueAdminView.as_view(), name='vue_admin'),
    
    # Frontend Vue.js App (catch-all for SPA routing)
    path('', TemplateView.as_view(template_name='frontend/index.html'), name='frontend_home'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Serve Vue.js admin files during development
    admin_static_path = os.path.join(settings.BASE_DIR, 'static', 'admin')
    if os.path.exists(admin_static_path):
        urlpatterns += [
            path('static/admin/<path:path>', serve, {
                'document_root': admin_static_path,
            }),
        ]

# Add debug toolbar if installed
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
