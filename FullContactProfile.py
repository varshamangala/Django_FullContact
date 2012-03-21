#Fetch the online profile of a person given an email
from Django_FullContact.models import FullContactProfile, FullContactLogger
from datetime import timedelta
import datetime, requests, simplejson

max_limit_per_month = 10000

class LimitExceeded(Exception):
	pass

class ServerDown(Exception):
	pass

class ContactNotFound(Exception):
	pass

class RequestQueuedRetryLater(Exception):
	pass

class InvalidEmail(Exception):
	pass

class MissingAPIKey(Exception):
	pass

class NetworkError(Exception):
	pass

def getsocialprofile(email):
	try:
		user_result = FullContactProfile.objects.get(emailid=email)
		return simplejson.loads(user_result.userdata)
	except (FullContactProfile.DoesNotExist,ValueError):
		today_minus_30_days = datetime.datetime.now() - timedelta(days=30)
		num_requests_this_month = FullContactLogger.objects.filter(statuscode=200).filter(createts__gt=today_minus_30_days).count()
		if (num_requests_this_month < max_limit_per_month):
			#'pull profile from full contact'
			url = "https://api.fullcontact.com/v2/person.json?email="+email+"&apiKey=xxxxxxxxxxxxxxxx" 
			try:
				result = requests.get(url)
			except requests.exceptions.ConnectionError,e:
				raise NetworkError
			except requests.exceptions.HTTPError,e:
				raise ServerDown
			#'convert unicode to dict'
			data = simplejson.loads(result.text)
			#'log the call to fullcontact'
			FullContactLogger.objects.create(emailid=email,statuscode=data['status'])
			#'store data only if status from full contact is 200'
			if (data['status'] == 200):
				FullContactProfile.objects.create(emailid=email,userdata=result.text)
				return data
			elif (data['status'] == 404):
				raise ContactNotFound
			elif (data['status'] == 202):
				raise RequestQueuedRetryLater
			elif (data['status'] == 422):
				raise InvalidEmail
			elif (data['status'] == 403):
				raise MissingAPIKey
		else:
			raise LimitExceeded