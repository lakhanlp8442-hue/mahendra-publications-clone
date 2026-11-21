import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('AUTHOR', 'Author'),
        ('REVIEWER', 'Peer Reviewer'),
        ('EDITOR', 'Editor-in-Chief'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='AUTHOR')
    affiliation = models.CharField(max_length=255, blank=True)
    orcid_id = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class JournalIssue(models.Model):
    volume = models.PositiveIntegerField()
    issue = models.PositiveIntegerField()
    month_year = models.CharField(max_length=50)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-volume', '-issue']
        unique_together = ('volume', 'issue')

    def __str__(self):
        return f"Volume {self.volume}, Issue {self.issue} ({self.month_year})"


class Article(models.Model):
    STATUS_CHOICES = (
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('REVISION', 'Revision Required'),
        ('ACCEPTED', 'Accepted'),
        ('PUBLISHED', 'Published'),
        ('REJECTED', 'Rejected'),
    )

    tracking_id = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=300)
    abstract = models.TextField()
    keywords = models.CharField(max_length=255)
    authors_list = models.CharField(max_length=300)
    submitted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='articles')
    manuscript_pdf = models.FileField(upload_to='manuscripts/%Y/%m/')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    issue = models.ForeignKey(JournalIssue, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    doi = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = f"MS-{uuid.uuid4().hex[:8].upper()}"
        if self.status == 'PUBLISHED' and not self.doi:
            self.doi = f"10.29294/IJASE.{self.id or uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.tracking_id}] {self.title[:50]}"


class ReviewAssignment(models.Model):
    RECOMMENDATION_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPT', 'Accept'),
        ('MINOR_REVISION', 'Minor Revision'),
        ('MAJOR_REVISION', 'Major Revision'),
        ('REJECT', 'Reject'),
    )

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_reviews')
    comments = models.TextField(blank=True)
    recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES, default='PENDING')
    assigned_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.article.tracking_id} -> {self.reviewer.username}"