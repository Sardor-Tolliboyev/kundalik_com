from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def bosh_sahifa_view(request):
    user = request.user

    if user.rol == 'oqituvchi':
        return render(request, 'oqituvchi/dashboard.html')
    elif user.rol == 'oquvchi':
        # Agar bu fayl templates/oquvchi/profil.html manzilda bo'lmasa, xato beradi
        return render(request, 'oquvchi/profil.html')
    elif user.rol == 'admin':
        return redirect('/admin/')

    return render(request, 'base.html')