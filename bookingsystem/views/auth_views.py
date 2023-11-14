from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.urls import reverse
from django.views import View

from bookingsystem.models import UserRestaurantLink, Restaurants


class LogoutView():
    def logout(self, request):
        request.session.flush()
        return render(request, 'login.html')


class CustomLoginView(DefaultLoginView):
    def form_valid(self, form):

        if form.is_valid():
            print('valid')
            response = super().form_valid(form)
            current_user = form.get_user().id
            restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                                flat=True).first()
            self.request.session['restaurant_name'] = Restaurants.objects.get(pk=restaurant_id).name
            self.request.session['restaurant_url'] = Restaurants.objects.get(pk=restaurant_id).website
        user_language = self.request.LANGUAGE_CODE  # Use the name of the language selector field in your form
        redirect_url = reverse('bookingsystem:restaurant_portal')
        # Append the language code as a prefix to the URL path
        if user_language:
            redirect_url = f'/{user_language}{redirect_url}'
        return redirect(redirect_url)


class ChangePasswordView(View):
    template_name = 'change_password.html'
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Logica voor wachtwoordwijziging hier
        # ...

        # Redirect naar een andere pagina na het wijzigen van het wachtwoord
        return redirect('bookingsystem:index')
