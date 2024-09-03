from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa

def render_to_pdf(template_src, report_number, context_dict={}):
    """Принимает шаблон отчета, номер отчета и контекст. Возвращает заполненный отчет в формате PDF."""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf-8')), result)
    if pdf.err:
        return HttpResponse('Произошла ошибка', status_code=400, content_type='text/plain')
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'filename= "{}.pdf"'.format(report_number)
    return response