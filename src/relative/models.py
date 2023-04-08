from django.db import models
from django.conf import settings
from django.utils import timezone



class RelativeList(models.Model):

	users				= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="users")
	relatives 			= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="relatives") 

	def __str__(self):
		return self.users.username

	def add_relative(self, account):
		"""
		Add a new friend.
		"""
		if not account in self.relatives.all():
			self.relatives.add(account)
			#self.save()

	def remove_relative(self, account):
		"""
		Remove a friend.
		"""
		if account in self.relatives.all():
			self.relatives.remove(account)

	def unrelative(self, removee):
		"""
		Initiate the action of unfriending someone.
		"""
		remover_relatives_list = self # person terminating the friendship

		# Remove friend from remover friend list
		remover_relatives_list.remove_relative(removee)

		# Remove friend from removee friend list
		relatives_list = RelativeList.objects.get(users=removee)
		relatives_list.remove_relative(self.users)


	def is_mutual_relative(self, relative):
		"""
		Is this a friend?
		"""
		if relative in self.relatives.all():
			return True
		return False


class RelativeRequest(models.Model):
	"""
	A friend request consists of two main parts:
		1. SENDER
			- Person sending/initiating the friend request
		2. RECIVER
			- Person receiving the friend friend
	"""

	senders 				= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="senders")
	receivers 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receivers")

	is_active			= models.BooleanField(blank=False, null=False, default=True)

	timestamp 			= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.senders.username

	def accept(self):
		"""
		Accept a friend request.
		Update both SENDER and RECEIVER friend lists.
		"""
		receivers_relative_list = RelativeList.objects.get(users=self.receivers)
		if receivers_relative_list:
			receivers_relative_list.add_relative(self.senders)
			senders_relative_list = RelativeList.objects.get(users=self.senders)
			if senders_relative_list:
				senders_relative_list.add_relative(self.receivers)
				self.is_active = False
				self.save()

	def decline(self):
		"""
		Decline a friend request.
		Is it "declined" by setting the `is_active` field to False
		"""
		self.is_active = False
		self.save()


	def cancel(self):
		"""
		Cancel a friend request.
		Is it "cancelled" by setting the `is_active` field to False.
		This is only different with respect to "declining" through the notification that is generated.
		"""
		self.is_active = False
		self.save()