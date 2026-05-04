from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RequirementForm
from .services import analyze_requirement


SESSION_KEY = "requirement_analyses"


def _get_session_items(request):
    return request.session.get(SESSION_KEY, [])


def _set_session_items(request, items):
    request.session[SESSION_KEY] = items
    request.session.modified = True


def home(request):
    """Ana sayfa - sistem tanıtımı ve navigasyon."""
    all_items = _get_session_items(request)
    recent = list(reversed(all_items[-5:]))
    context = {
        'recent_requirements': recent,
        'total_count': len(all_items),
    }
    return render(request, 'requirements_app/home.html', context)


def requirement_new(request):
    """Gereksinim giriş formu ve analiz başlatma."""
    if request.method == 'POST':
        form = RequirementForm(request.POST)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            raw_text = form.cleaned_data['raw_text']
            try:
                analysis = analyze_requirement(raw_text, project_name=project_name)
            except ValueError as exc:
                messages.error(request, str(exc))
                return render(request, 'requirements_app/requirement_form.html', {'form': form})
            all_items = _get_session_items(request)
            next_id = (all_items[-1]['id'] + 1) if all_items else 1
            all_items.append({
                'id': next_id,
                'project_name': project_name,
                'raw_text': raw_text,
                'status': 'analyzed',
                'status_display': 'Analiz Edildi',
                'created_at': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'result': {
                    'bdd_output': analysis['bdd_output'],
                    'gherkin_output': analysis['gherkin_output'],
                    'qa_result': analysis['qa_result'],
                    'story_point': analysis['story_point'],
                },
            })
            _set_session_items(request, all_items)

            messages.success(request, 'Gereksinim analizi başarıyla tamamlandı.')
            return redirect('requirement_detail', pk=next_id)
    else:
        form = RequirementForm()

    return render(request, 'requirements_app/requirement_form.html', {'form': form})


def requirement_detail(request, pk):
    """Analiz sonuç sayfası."""
    all_items = _get_session_items(request)
    requirement = next((item for item in all_items if item['id'] == pk), None)
    if not requirement:
        return render(request, 'requirements_app/requirement_detail.html', {'requirement': None}, status=404)
    return render(request, 'requirements_app/requirement_detail.html', {
        'requirement': requirement,
    })


def requirement_list(request):
    """Geçmiş gereksinim listesi."""
    requirements = list(reversed(_get_session_items(request)))
    return render(request, 'requirements_app/requirement_list.html', {
        'requirements': requirements,
    })
