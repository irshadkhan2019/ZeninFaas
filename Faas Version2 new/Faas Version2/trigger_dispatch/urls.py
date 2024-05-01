from django.urls import path, include
from . import views

app_name = "trigger_dispatch"

urlpatterns = [
    path('dispatch-test-trigger/<int:trigger_id>', views.dispatch_test_trigger, name='dispatch_test_trigger'),
    path('code-detail/<int:trigger_id>', views.code_detail, name='code_detail'),
    path('send-req-and-plot/<int:trigger_id>', views.send_req_and_plot, name='send_req_and_plot'),
]