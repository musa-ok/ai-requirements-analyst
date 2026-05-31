from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RequirementForm
from .services import analyze_requirement
from .export_bridge import register_from_analysis_result, fetch_analysis_from_api, _format_analysis_for_display


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
                analysis = analyze_requirement(
                    raw_text,
                    project_name=project_name,
                    api_key=form.cleaned_data['api_key'],
                    model_type=form.cleaned_data.get('model_type') or 'gemini',
                )
            except ValueError as exc:
                messages.error(request, str(exc))
                return render(request, 'requirements_app/requirement_form.html', {'form': form})
            api_session_id, api_analysis_id = register_from_analysis_result(
                request,
                project_name=project_name,
                requirement_text=raw_text,
                analysis=analysis,
            )
            all_items = _get_session_items(request)
            next_id = (all_items[-1]['id'] + 1) if all_items else 1
            all_items.append({
                'id': next_id,
                'project_name': project_name,
                'raw_text': raw_text,
                'status': 'analyzed',
                'status_display': 'Analiz Edildi',
                'created_at': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'fastapi_session_id': api_session_id,
                'fastapi_analysis_id': api_analysis_id,
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


def _hydrate_requirement_result(requirement: dict) -> dict:
    """Session'da sonuc yoksa FastAPI kaydindan doldurur."""
    if requirement.get("result"):
        return requirement
    api_session_id = requirement.get("fastapi_session_id")
    analysis_id = requirement.get("fastapi_analysis_id")
    if not api_session_id or not analysis_id:
        return requirement
    api_payload = fetch_analysis_from_api(api_session_id, analysis_id)
    if not api_payload:
        return requirement
    requirement = dict(requirement)
    requirement["result"] = _format_analysis_for_display(api_payload)
    if not requirement.get("raw_text"):
        requirement["raw_text"] = api_payload.get("requirement_text") or ""
    if not requirement.get("project_name"):
        requirement["project_name"] = api_payload.get("project_name") or "Web Projesi"
    return requirement


def requirement_detail(request, pk):
    """Analiz sonuç sayfası."""
    pk_int = int(pk)
    all_items = _get_session_items(request)
    requirement = next((item for item in all_items if item['id'] == pk_int), None)
    if requirement:
        requirement = _hydrate_requirement_result(requirement)
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


def requirement_clear_history(request):
    """Tüm analiz geçmişini oturumdan siler."""
    if request.method != 'POST':
        return redirect('requirement_list')
    request.session.pop(SESSION_KEY, None)
    request.session.pop('ai_ra_fastapi_session_id', None)
    request.session.modified = True
    messages.success(request, 'Geçmiş analizler temizlendi. Yeni bir analizle başlayabilirsiniz.')
    return redirect('home')
