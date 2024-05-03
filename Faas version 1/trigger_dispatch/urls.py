from django.urls import path, include
from . import views

app_name = "trigger_dispatch"

urlpatterns = [
    path('dispatch-test-trigger/<int:trigger_id>', views.dispatch_test_trigger, name='dispatch_test_trigger'),
    path('install-dependencies/<int:trigger_id>', views.install_dependencies, name='install_dependencies'),
    # path('test-trigger/<int:trigger_id>', views.test_trigger, name='test_trigger'),
    path('code-detail/<int:trigger_id>', views.code_detail, name='code_detail'),
    path('delete-trigger/<int:trigger_id>', views.delete_trigger, name='delete_trigger'),
  
]