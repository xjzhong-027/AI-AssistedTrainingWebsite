# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.db import models
# from ELW.models import (
#     Unit, MediaMaterial,
#     MainQuestion, SubQuestion, ChoiceOption,
#     MatchingOption, Correction, PaperPage, TimeManagement
# )
# from Account.models import Students, Class
#
# class StudentPracticeRecord(models.Model):
#     user = models.ForeignKey(Students, on_delete=models.CASCADE)
#     practice = models.ForeignKey(Unit, on_delete=models.CASCADE)  # 练习单元
#     started_at = models.DateTimeField(auto_now_add=True)
#     ended_at = models.DateTimeField(null=True, blank=True)
#     finished_at = models.DateTimeField(null=True, blank=True)
#     submitted = models.BooleanField(default=False)
#     score = models.DecimalField(verbose_name='总分', max_digits=5, decimal_places=1, null=True, blank=True)