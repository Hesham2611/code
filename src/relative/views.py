from django.shortcuts import render,redirect
from django.http import HttpResponse
import json

from account.models import Account
from relative.models import RelativeRequest,RelativeList


def send_relative_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("receivers_user_id")
		if user_id:
			receivers = Account.objects.get(pk=user_id)
			try:
				# Get any friend requests (active and not-active)
				relative_requests = RelativeRequest.objects.filter(senders=user, receivers=receivers)
				# find if any of them are active (pending)
				try:
					for request in relative_requests:
						if request.is_active:
							raise Exception("You already sent them a relative request.")
					# If none are active create a new friend request
					relative_request = RelativeRequest(senders=user, receivers=receivers)
					relative_request.save()
					payload['response'] = "relative request sent."
				except Exception as e:
					payload['response'] = str(e)
			except RelativeRequest.DoesNotExist:
				# There are no friend requests so create one.
				relative_request = RelativeRequest(senders=user, receivers=receivers)
				relative_request.save()
				payload['response'] = "Relative request sent."

			if payload['response'] == None:
				payload['response'] = "Something went wrong."
		else:
			payload['response'] = "Unable to sent a relative request."
	else:
		payload['response'] = "You must be authenticated to send a relative request."
	return HttpResponse(json.dumps(payload), content_type="application/json")

def relatives_list_view(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		user_id = kwargs.get("user_id")
		if user_id:
			try:
				this_user = Account.objects.get(pk=user_id)
				context['this_user'] = this_user
			except Account.DoesNotExist:
				return HttpResponse("That user does not exist.")
			try:
				relative_list = RelativeList.objects.get(users=this_user)
			except RelativeList.DoesNotExist:
				return HttpResponse(f"Could not find a relatives list for {this_user.username}")
			
			# Must be friends to view a friends list
			if user != this_user:
				if not user in relative_list.relatives.all():
					return HttpResponse("You must be friend to view their relatives list.")
			relatives = [] # [(friend1, True), (friend2, False), ...]
			# get the authenticated users friend list
			auth_user_relative_list = RelativeList.objects.get(users=user)
			for relative in relative_list.relatives.all():
				relatives.append((relative, auth_user_relative_list.is_mutual_relative(relative)))
			context['relatives'] = relatives
	else:		
		return HttpResponse("You must be friends to view their relatives list.")
	return render(request, "relative/relative_list.html", context)


def relative_requests(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		user_id = kwargs.get("user_id")
		account = Account.objects.get(pk=user_id)
		if account == user:
			relative_requests = RelativeRequest.objects.filter(receivers=account, is_active=True)
			context['relative_requests'] = relative_requests
		else:
			return HttpResponse("You can't view another users relatives requets.")
	else:
		redirect("login")
	return render(request, "relative/relative_requests.html", context)
def accept_relative_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET" and user.is_authenticated:
		relative_request_id = kwargs.get("relative_request_id")
		if relative_request_id:
			relative_request = RelativeRequest.objects.get(pk=relative_request_id)
			# confirm that is the correct request
			if relative_request.receivers == user:
				if relative_request: 
					# found the request. Now accept it
					updated_notification = relative_request.accept()
					payload['response'] = "Relative request accepted."

				else:
					payload['response'] = "Something went wrong."
			else:
				payload['response'] = "That is not your request to accept."
		else:
			payload['response'] = "Unable to accept that relative request."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to accept a relative request."
	return HttpResponse(json.dumps(payload), content_type="application/json")


def remove_relative(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("receivers_user_id")
		if user_id:
			try:
				removee = Account.objects.get(pk=user_id)
				relative_list = RelativeList.objects.get(users=user)
				relative_list.unrelative(removee)
				payload['response'] = "Successfully removed that relative."
			except Exception as e:
				payload['response'] = f"Something went wrong: {str(e)}"
		else:
			payload['response'] = "There was an error. Unable to remove that relative."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to remove a relative."
	return HttpResponse(json.dumps(payload), content_type="application/json")



def decline_relative_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET" and user.is_authenticated:
		relative_request_id = kwargs.get("relative_request_id")
		if relative_request_id:
			relative_request = RelativeRequest.objects.get(pk=relative_request_id)
			# confirm that is the correct request
			if relative_request.receivers == user:
				if relative_request: 
					# found the request. Now decline it
					updated_notification = relative_request.decline()
					payload['response'] = "Relative request declined."
				else:
					payload['response'] = "Something went wrong."
			else:
				payload['response'] = "That is not your relative request to decline."
		else:
			payload['response'] = "Unable to decline that relative request."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to decline a relative request."
	return HttpResponse(json.dumps(payload), content_type="application/json")




def cancel_relative_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("receivers_user_id")
		if user_id:
			receivers = Account.objects.get(pk=user_id)
			try:
				relative_requests = RelativeRequest.objects.filter(senders=user, receiver=receivers, is_active=True)
			except RelativeRequest.DoesNotExist:
				payload['response'] = "Nothing to cancel. Relative request does not exist."

			# There should only ever be ONE active friend request at any given time. Cancel them all just in case.
			if len(relative_requests) > 1:
				for request in relative_requests:
					request.cance()
				payload['response'] = "Relative request canceled."
			else:
				# found the request. Now cancel it
				relative_requests.first().cancel()
				payload['response'] = "Relative request canceled."
		else:
			payload['response'] = "Unable to cancel that relative request."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to cancel a relative request."
	return HttpResponse(json.dumps(payload), content_type="application/json")
