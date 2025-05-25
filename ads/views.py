from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm, ExchangeProposalStatusForm, AdSearchForm, UserRegistrationForm, \
    CustomLoginForm


def login_view(request):
    """Вход в аккаунт пользователя"""
    if request.user.is_authenticated:
        return redirect('ad_list')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                next_url = request.GET.get('next', 'ad_list')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = CustomLoginForm()

    return render(request, 'ads/login.html', {'form': form})

def logout_view(request):
    """Выход из аккаунта пользователя"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт успешно создан! Теперь вы можете войти в систему.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'ads/register.html', {'form': form})


def ad_list(request):
    """Отображение списка объявлений с поиском и фильтрацией"""
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    condition = request.GET.get('condition', '')
    is_mine = bool(request.GET.get('is_mine', ''))

    queryset = Ad.objects.all()
    print(queryset)
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category:
        queryset = queryset.filter(category=category)

    if condition:
        queryset = queryset.filter(condition=condition)

    if is_mine:
        queryset = queryset.filter(user=request.user)
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(page_obj)
    context = {
        'ads': page_obj,
        'search_form': AdSearchForm(request.GET),
    }

    return render(request, 'ads/ad_list.html', context)


def ad_detail(request, pk):
    """Отображение детальной информации об объявлении"""
    ad = get_object_or_404(Ad, pk=pk)
    context = {
        'ad': ad,
        'is_owner': request.user == ad.user,
    }

    if request.user.is_authenticated:
        context['user_ads'] = Ad.objects.filter(user=request.user).exclude(id=ad.id)
        context['proposal_form'] = ExchangeProposalForm()

    return render(request, 'ads/ad_detail.html', context)


@login_required
def ad_create(request):
    """Создание нового объявления"""
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            messages.success(request, 'Объявление успешно создано!')
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm()

    return render(request, 'ads/ad_form.html', {'form': form})


@login_required
def ad_update(request, pk):
    """Редактирование объявления"""
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        return HttpResponseForbidden("У вас нет прав для редактирования этого объявления.")

    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление успешно обновлено!')
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/ad_form.html', {'form': form})


@login_required
def ad_delete(request, pk):
    """Удаление объявления"""
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        return HttpResponseForbidden("У вас нет прав для удаления этого объявления.")

    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Объявление успешно удалено!')
        return redirect('ad_list')

    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})


@login_required
def create_exchange_proposal(request, ad_id):
    """Создание предложения обмена"""
    receiver_ad = get_object_or_404(Ad, id=ad_id)

    if receiver_ad.user == request.user:
        messages.error(request, 'Вы не можете предложить обмен для своего собственного объявления.')
        return redirect('ad_detail', pk=ad_id)

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        sender_ad_id = request.POST.get('sender_ad')
        sender_ad = get_object_or_404(Ad, id=sender_ad_id, user=request.user)

        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_sender = sender_ad
            proposal.ad_receiver = receiver_ad
            proposal.save()

            messages.success(request, 'Предложение обмена успешно отправлено!')
            return redirect('ad_detail', pk=ad_id)

    return redirect('ad_detail', pk=ad_id)


@login_required
def my_proposals(request):
    """Просмотр предложений обмена пользователя"""
    sent_proposals = ExchangeProposal.objects.filter(ad_sender__user=request.user).select_related('ad_sender', 'ad_receiver')
    received_proposals = ExchangeProposal.objects.filter(ad_receiver__user=request.user).select_related('ad_sender', 'ad_receiver')

    return render(request, 'ads/proposal_list.html', {
        'sent_proposals': sent_proposals,
        'received_proposals': received_proposals,
    })


@login_required
def update_proposal_status(request, proposal_id):
    """Обновление статуса предложения обмена (принятие/отклонение)"""
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    if proposal.ad_receiver.user != request.user:
        messages.error(request, 'У вас нет прав для изменения статуса этого предложения.')
        return redirect('my_proposals')

    if request.method == 'POST':
        form = ExchangeProposalStatusForm(request.POST, instance=proposal)
        if form.is_valid():
            form.save()
            status = form.cleaned_data['status']

            if status == 'accepted':
                messages.success(request, 'Предложение обмена принято!')
            else:
                messages.success(request, 'Предложение обмена отклонено.')

            return redirect('my_proposals')

    return redirect('my_proposals')


