from relative.models import RelativeRequest


def get_relative_request_or_false(senders, receivers):
	try:
		return RelativeRequest.objects.get(senders=senders, receivers=receivers, is_active=True)
	except RelativeRequest.DoesNotExist:
		return False
	