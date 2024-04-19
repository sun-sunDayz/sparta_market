from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete
from django.dispatch import receiver
# Create your models here.

class User(AbstractUser):

    class Grades(models.TextChoices):
        BRONZE = "B", "Bronze"
        SILVER = "S", "Silver"
        GOLD = "G", "Gold"
        DIAMOND = "D", "Diamond"

    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True)
    point = models.IntegerField(default=10000)
    following = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="followers")
    introduce = models.TextField(blank=True)
    grade = models.CharField(max_length=1, choices=Grades.choices, default=Grades.BRONZE)

    def __str__(self):
        return f"{self.username} 님"
    
    def getpic(self):
        if self.profile_pic:
            return self.profile_pic.url
        return "/static/images/noprofile.png"

    @property
    def display_grade(self):
        if self.grade == self.Grades.BRONZE:
            return "Bronze 🥉"
        elif self.grade == self.Grades.SILVER:
            return "Silver 🥈"
        elif self.grade == self.Grades.GOLD:
            return "Gold 🥇"
        elif self.grade == self.Grades.DIAMOND:
            return "Diamond 💎"
        return self.grade
    
    class Meta:
        pass
