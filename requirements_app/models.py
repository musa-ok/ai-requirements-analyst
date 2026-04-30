from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Requirement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('analyzed', 'Analiz Edildi'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='requirements')
    raw_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gereksinim #{self.pk} - {self.project.name}"

    class Meta:
        ordering = ['-created_at']


class AnalysisResult(models.Model):
    requirement = models.OneToOneField(Requirement, on_delete=models.CASCADE, related_name='result')
    bdd_output = models.TextField()
    gherkin_output = models.TextField()
    qa_result = models.TextField()
    story_point = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analiz #{self.pk} - Gereksinim #{self.requirement.pk}"
