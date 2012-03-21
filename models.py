from django.db import models

# Create your models here.
class FullContactProfile(models.Model):
	emailid=models.EmailField(primary_key=True)
	userdata=models.TextField()
	modifyts=models.DateField(auto_now=True)

	def _unicode_(self):
		return self.emailid

class FullContactLogger(models.Model):
	emailid=models.EmailField()
	statuscode=models.IntegerField(db_index=True)
	createts=models.DateTimeField(auto_now_add=True,db_index=True)
	
	def _unicode_(self):
		return self.emailid, self.statuscode, self.createts
