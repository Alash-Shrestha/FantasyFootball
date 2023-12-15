from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

class NonDeletedManager(models.Manager):
    def get_queryset(self) :
        return super().get_queryset().filter(deleted_at=None)

class DateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = NonDeletedManager()

    class Meta:
        abstract = True
        ordering = ('-created_at', )

    def delete(self):
        self.deleted_at = timezone.now()
        super().save()