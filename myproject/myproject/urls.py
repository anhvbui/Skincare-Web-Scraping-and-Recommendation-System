"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic import RedirectView



from django.urls import include, path, re_path
from app.views import homepage
from app.views import loginPage
from app.views import signup
from app.views import test
from app.views import logoutPage
from app.views import skinQuiz
from app.views import quizResult
from app.views import savedItems


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name = "homepage"),
    path('login/', loginPage, name = "login"),
    path('logout/', logoutPage, name="logout"),
    path('signup/', signup, name = "signup"),
    path('test/', test, name = "test"),
    path('skin-quiz/', skinQuiz, name = "skin-quiz"),
    path('quiz-result/', quizResult, name = "quiz-result"),
    path('saved-items/', savedItems, name = "saved-items"),
    #path('skin-quiz/quiz-result.html', quizResult, name='quiz-result'),
    re_path(r'^favicon\.ico$',RedirectView.as_view(url='/static/images/favicon.ico')),
]
