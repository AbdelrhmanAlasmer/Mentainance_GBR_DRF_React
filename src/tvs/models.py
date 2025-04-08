from django.db import models

class TVType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class TVModel(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(TVType, on_delete=models.CASCADE, related_name="models")

    def __str__(self):
        return self.name

class TV(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    type = models.ForeignKey(TVType, on_delete=models.CASCADE)
    model = models.ForeignKey(TVModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.type} - {self.model} ({self.serial_number})"
