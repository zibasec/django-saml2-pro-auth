from django.shortcuts import redirect
from django.views.generic.list import ListView

from saml2_pro_auth.models import SamlProvider


class IndexView(ListView):

    model = SamlProvider
    template_name = "index.html"


def logout(request):
    request.session.flush()
    return redirect("index")
