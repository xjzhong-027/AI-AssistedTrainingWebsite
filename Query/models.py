from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
import uuid
import os
from Account.models import Class


""" ---------------------------------------- 考勤管理 --------------------------------------------"""
class ClassroomLayout(models.Model):
    """ 教室布局表 """
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    seat_rows = models.IntegerField(null=True, blank=True)
    seat_cols = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Classroom for {self.class_instance}"