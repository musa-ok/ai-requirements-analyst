from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, Requirement, AnalysisResult
from .forms import RequirementForm
from .services import analyze_requirement


def home(request):
    """Ana sayfa - sistem tanıtımı ve navigasyon."""
    recent = Requirement.objects.select_related('project', 'result').order_by('-created_at')[:5]
    context = {
        'recent_requirements': recent,
        'total_count': Requirement.objects.count(),
    }
    return render(request, 'requirements_app/home.html', context)


def requirement_new(request):
    """Gereksinim giriş formu ve analiz başlatma."""
    if request.method == 'POST':
        form = RequirementForm(request.POST)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            raw_text = form.cleaned_data['raw_text']

            project, _ = Project.objects.get_or_create(
                name=project_name,
                defaults={'description': f'{project_name} projesi'},
            )

            requirement = Requirement.objects.create(
                project=project,
                raw_text=raw_text,
                status='pending',
            )

            analysis = analyze_requirement(raw_text)

            AnalysisResult.objects.create(
                requirement=requirement,
                bdd_output=analysis['bdd_output'],
                gherkin_output=analysis['gherkin_output'],
                qa_result=analysis['qa_result'],
                story_point=analysis['story_point'],
            )

            requirement.status = 'analyzed'
            requirement.save()

            messages.success(request, 'Gereksinim analizi başarıyla tamamlandı.')
            return redirect('requirement_detail', pk=requirement.pk)
    else:
        form = RequirementForm()

    return render(request, 'requirements_app/requirement_form.html', {'form': form})


def requirement_detail(request, pk):
    """Analiz sonuç sayfası."""
    requirement = get_object_or_404(Requirement.objects.select_related('project', 'result'), pk=pk)
    return render(request, 'requirements_app/requirement_detail.html', {
        'requirement': requirement,
    })


def requirement_list(request):
    """Geçmiş gereksinim listesi."""
    requirements = Requirement.objects.select_related('project', 'result').order_by('-created_at')
    return render(request, 'requirements_app/requirement_list.html', {
        'requirements': requirements,
    })
