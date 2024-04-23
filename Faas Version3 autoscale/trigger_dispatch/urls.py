from django.urls import path, include
from . import views

app_name = "trigger_dispatch"

urlpatterns = [
    # path('dispatch-test-trigger-test/<int:trigger_id>/<int:thread_id>', views.dispatch_test_trigger_test, name='dispatch_test_trigger_test'),
    path('dispatch-test-trigger/<int:trigger_id>', views.dispatch_test_trigger, name='dispatch_test_trigger'),
    path('send-req-and-plot/<int:trigger_id>', views.send_req_and_plot, name='send_req_and_plot'),
    path('code-detail/<int:trigger_id>', views.code_detail, name='code_detail'),
  
]