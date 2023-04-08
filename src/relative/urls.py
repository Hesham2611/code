from django.urls import path

from relative.views import(
	send_relative_request,
	relative_requests,
	accept_relative_request,
	remove_relative,
	decline_relative_request,
	cancel_relative_request,
	relatives_list_view,
)

app_name = 'relative'

urlpatterns = [
	path('list/<user_id>', relatives_list_view, name='list'),
	path('relative_remove/', remove_relative, name='remove-relative'),
    path('relative_request/', send_relative_request, name='relative-request'),
    path('relative_request_cancel/', cancel_relative_request, name='relative-request-cancel'),
    path('relative_requests/<user_id>/', relative_requests, name='relative-requests'),
    path('relative_request_accept/<relative_request_id>/', accept_relative_request, name='relative-request-accept'),
    path('relative_request_decline/<relative_request_id>/', decline_relative_request, name='relative-request-decline'),
]