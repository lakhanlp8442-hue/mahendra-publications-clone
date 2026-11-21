from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404
from django.utils import timezone
from .models import CustomUser, JournalIssue, Article, ReviewAssignment
from .forms import CustomUserRegistrationForm, ArticleSubmissionForm, ReviewForm


def home(request):
    query = request.GET.get('q', '').strip()
    current_issue = JournalIssue.objects.filter(is_current=True).first()
    if not current_issue:
        current_issue = JournalIssue.objects.first()

    if query:
        articles = Article.objects.filter(status='PUBLISHED').filter(
            Q(title__icontains=query) |
            Q(authors_list__icontains=query) |
            Q(keywords__icontains=query) |
            Q(abstract__icontains=query)
        ).order_by('-published_at', '-id')
    elif current_issue:
        articles = Article.objects.filter(status='PUBLISHED', issue=current_issue).order_by('-published_at', '-id')
    else:
        articles = Article.objects.filter(status='PUBLISHED').order_by('-published_at', '-id')

    recent_issues = JournalIssue.objects.all()[:5]
    total_published = Article.objects.filter(status='PUBLISHED').count()

    context = {
        'current_issue': current_issue,
        'articles': articles,
        'recent_issues': recent_issues,
        'total_published': total_published,
        'query': query,
    }
    return render(request, 'publications/home.html', context)


def archives(request):
    issues = JournalIssue.objects.all()
    return render(request, 'publications/archives.html', {'issues': issues})


def issue_detail(request, issue_id):
    issue = get_object_or_404(JournalIssue, id=issue_id)
    articles = Article.objects.filter(issue=issue, status='PUBLISHED').order_by('-published_at', '-id')
    return render(request, 'publications/issue_detail.html', {'issue': issue, 'articles': articles})


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id, status='PUBLISHED')
    article.views_count += 1
    article.save(update_fields=['views_count'])

    keywords_list = [k.strip() for k in article.keywords.split(',') if k.strip()]
    year = article.published_at.year if article.published_at else timezone.now().year
    vol = article.issue.volume if article.issue else 1
    iss = article.issue.issue if article.issue else 1

    apa_citation = f"{article.authors_list} ({year}). {article.title}. International Journal of Advanced Science and Engineering (IJASE), {vol}({iss}). https://doi.org/{article.doi}"
    ieee_citation = f'{article.authors_list}, "{article.title}," Int. J. Adv. Sci. Eng. (IJASE), vol. {vol}, no. {iss}, {year}, doi: {article.doi}.'

    context = {
        'article': article,
        'keywords_list': keywords_list,
        'apa_citation': apa_citation,
        'ieee_citation': ieee_citation,
    }
    return render(request, 'publications/article_detail.html', context)


def download_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, status='PUBLISHED')
    if not article.manuscript_pdf:
        raise Http404("PDF file not found.")
    article.downloads_count += 1
    article.save(update_fields=['downloads_count'])
    return FileResponse(article.manuscript_pdf.open('rb'), as_attachment=True, filename=f"{article.tracking_id}.pdf")


def editorial_board(request):
    editors = CustomUser.objects.filter(role='EDITOR')
    reviewers = CustomUser.objects.filter(role='REVIEWER')
    return render(request, 'publications/editorial_board.html', {
        'editors': editors,
        'reviewers': reviewers,
    })


def about_journal(request):
    return render(request, 'publications/about.html')


def register_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'publications/register.html', {'form': form})


@login_required
def submit_manuscript(request):
    if request.method == 'POST':
        form = ArticleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.submitted_by = request.user
            article.save()
            messages.success(request, f"Manuscript submitted successfully! Tracking ID: {article.tracking_id}")
            return redirect('dashboard')
    else:
        form = ArticleSubmissionForm()
    return render(request, 'publications/submit_manuscript.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    my_articles = Article.objects.filter(submitted_by=user).order_by('-submitted_at')
    assigned_reviews = ReviewAssignment.objects.filter(reviewer=user).order_by('-assigned_at')

    all_articles = Article.objects.all().order_by('-submitted_at') if (user.role == 'EDITOR' or user.is_superuser) else None
    all_reviewers = CustomUser.objects.filter(role='REVIEWER') if (user.role == 'EDITOR' or user.is_superuser) else None
    all_issues = JournalIssue.objects.all() if (user.role == 'EDITOR' or user.is_superuser) else None

    if request.method == 'POST' and (user.role == 'EDITOR' or user.is_superuser):
        action = request.POST.get('action')
        article_id = request.POST.get('article_id')
        article = get_object_or_404(Article, id=article_id)

        if action == 'assign_reviewer':
            reviewer_id = request.POST.get('reviewer_id')
            reviewer = get_object_or_404(CustomUser, id=reviewer_id, role='REVIEWER')
            ReviewAssignment.objects.get_or_create(article=article, reviewer=reviewer)
            article.status = 'UNDER_REVIEW'
            article.save()
            messages.success(request, f"Assigned {reviewer.username} to {article.tracking_id}.")

        elif action == 'update_status':
            new_status = request.POST.get('status')
            issue_id = request.POST.get('issue_id')
            article.status = new_status
            if issue_id:
                article.issue = get_object_or_404(JournalIssue, id=issue_id)
            if new_status == 'PUBLISHED' and not article.published_at:
                article.published_at = timezone.now()
            article.save()
            messages.success(request, f"Updated {article.tracking_id} to {new_status}.")

        return redirect('dashboard')

    context = {
        'my_articles': my_articles,
        'assigned_reviews': assigned_reviews,
        'all_articles': all_articles,
        'all_reviewers': all_reviewers,
        'all_issues': all_issues,
    }
    return render(request, 'publications/dashboard.html', context)


@login_required
def submit_review(request, review_id):
    review = get_object_or_404(ReviewAssignment, id=review_id, reviewer=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.reviewed_at = timezone.now()
            rev.save()
            messages.success(request, f"Peer review submitted for {review.article.tracking_id}.")
            return redirect('dashboard')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'publications/submit_review.html', {'form': form, 'review': review})