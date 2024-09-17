from django.db import models


class Quiz(models.Model):
  name = models.CharField(max_length= 1000)


class Question(models.Model):
  quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
  text = models.CharField(max_length=1300)


class Answer(models.Model):
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  text = models.CharField(max_length=1300)
  is_correct = models.BooleanField(default=False)

