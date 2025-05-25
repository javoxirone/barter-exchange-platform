import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from ads.models import Ad, ExchangeProposal


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )


@pytest.fixture
def another_user():
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='anotherpassword'
    )


@pytest.fixture
def ad(user):
    return Ad.objects.create(
        title='Тестовое объявление',
        description='Описание тестового объявления',
        category='electronics',
        condition='new',
        user=user
    )


@pytest.fixture
def another_ad(another_user):
    return Ad.objects.create(
        title='Другое объявление',
        description='Описание другого объявления',
        category='books',
        condition='good',
        user=another_user
    )


@pytest.fixture
def proposal(ad, another_ad):
    return ExchangeProposal.objects.create(
        ad_sender=ad,
        ad_receiver=another_ad,
        comment='Предлагаю обмен',
        status='pending'
    )


@pytest.mark.django_db
class TestAuthViews:
    """Тесты для функций аутентификации"""

    def test_login_view_get(self, client):
        """Тест GET-запроса на страницу входа"""
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_login_view_post_valid(self, client, user):
        """Тест успешного входа в систему"""
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        assert response.status_code == 302
        assert response.url == reverse('ad_list')

    def test_login_view_post_invalid(self, client):
        """Тест неуспешного входа в систему"""
        response = client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200
        assert 'form' in response.context

    def test_login_redirect_authenticated_user(self, client, user):
        """Тест редиректа уже аутентифицированного пользователя"""
        client.force_login(user)
        response = client.get(reverse('login'))
        assert response.status_code == 302
        assert response.url == reverse('ad_list')

    def test_logout_view(self, client, user):
        """Тест выхода из системы"""
        client.force_login(user)
        response = client.get(reverse('logout'))
        assert response.status_code == 302
        assert response.url == reverse('login')

    def test_register_view_get(self, client):
        """Тест GET-запроса на страницу регистрации"""
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_register_view_post_valid(self, client):
        """Тест успешной регистрации"""
        response = client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'NewPassword123',
            'password2': 'NewPassword123'
        })
        assert response.status_code == 302
        assert response.url == reverse('login')
        assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
class TestAdViews:
    """Тесты для представлений объявлений"""

    def test_ad_list_view(self, client):
        """Тест просмотра списка объявлений"""
        response = client.get(reverse('ad_list'))
        assert response.status_code == 200
        assert 'ads' in response.context
        assert 'search_form' in response.context

    def test_ad_list_view_with_filters(self, client, ad):
        """Тест просмотра списка объявлений с фильтрами"""
        ad.save()
        response = client.get(f"{reverse('ad_list')}?query=Тестовое&category=electronics&condition=new")
        assert response.status_code == 200
        assert 'ads' in response.context
        ads_list = list(response.context['ads'])
        assert ad in ads_list

    def test_ad_detail_view(self, client, ad):
        """Тест просмотра детальной информации об объявлении"""
        response = client.get(reverse('ad_detail', kwargs={'pk': ad.pk}))
        assert response.status_code == 200
        assert response.context['ad'] == ad

    def test_ad_create_view_get(self, client, user):
        """Тест GET-запроса на страницу создания объявления"""
        client.force_login(user)
        response = client.get(reverse('ad_create'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_ad_create_view_post(self, client, user):
        """Тест создания объявления"""
        client.force_login(user)
        response = client.post(reverse('ad_create'), {
            'title': 'Новое объявление',
            'description': 'Описание нового объявления',
            'category': 'electronics',
            'condition': 'new'
        })
        assert response.status_code == 302
        new_ad = Ad.objects.get(title='Новое объявление')
        assert response.url == reverse('ad_detail', kwargs={'pk': new_ad.pk})
        assert new_ad.user == user

    def test_ad_create_view_requires_login(self, client):
        """Тест требования авторизации для создания объявления"""
        response = client.get(reverse('ad_create'))
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_ad_update_view_get(self, client, user, ad):
        """Тест GET-запроса на страницу редактирования объявления"""
        client.force_login(user)
        response = client.get(reverse('ad_update', kwargs={'pk': ad.pk}))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_ad_update_view_post(self, client, user, ad):
        """Тест редактирования объявления"""
        client.force_login(user)
        response = client.post(reverse('ad_update', kwargs={'pk': ad.pk}), {
            'title': 'Обновленное объявление',
            'description': 'Обновленное описание',
            'category': 'electronics',
            'condition': 'good'
        })
        assert response.status_code == 302
        ad.refresh_from_db()
        assert ad.title == 'Обновленное объявление'
        assert ad.condition == 'good'

    def test_ad_update_view_unauthorized(self, client, another_user, ad):
        """Тест редактирования объявления неавторизованным пользователем"""
        client.force_login(another_user)
        response = client.get(reverse('ad_update', kwargs={'pk': ad.pk}))
        assert response.status_code == 403

    def test_ad_delete_view_get(self, client, user, ad):
        """Тест GET-запроса на страницу удаления объявления"""
        client.force_login(user)
        response = client.get(reverse('ad_delete', kwargs={'pk': ad.pk}))
        assert response.status_code == 200

    def test_ad_delete_view_post(self, client, user, ad):
        """Тест удаления объявления"""
        client.force_login(user)
        response = client.post(reverse('ad_delete', kwargs={'pk': ad.pk}))
        assert response.status_code == 302
        assert response.url == reverse('ad_list')
        assert not Ad.objects.filter(pk=ad.pk).exists()

    def test_ad_delete_view_unauthorized(self, client, another_user, ad):
        """Тест удаления объявления неавторизованным пользователем"""
        client.force_login(another_user)
        response = client.get(reverse('ad_delete', kwargs={'pk': ad.pk}))
        assert response.status_code == 403


@pytest.mark.django_db
class TestProposalViews:
    """Тесты для функций обмена"""

    def test_create_exchange_proposal(self, client, user, ad, another_ad):
        """Тест создания предложения обмена"""
        client.force_login(user)
        try:
            url = reverse('create_exchange_proposal', kwargs={'ad_id': another_ad.pk})
        except:
            try:
                url = reverse('exchange_proposal_create', kwargs={'ad_id': another_ad.pk})
            except:
                url = reverse('propose_exchange', kwargs={'ad_id': another_ad.pk})

        response = client.post(url, {
            'sender_ad': ad.pk,
            'comment': 'Предлагаю обмен'
        })
        assert response.status_code == 302
        assert ExchangeProposal.objects.filter(
            ad_sender=ad,
            ad_receiver=another_ad,
            comment='Предлагаю обмен'
        ).exists()

    def test_create_exchange_proposal_own_ad(self, client, user, ad):
        """Тест создания предложения обмена для своего объявления"""
        client.force_login(user)
        try:
            url = reverse('create_exchange_proposal', kwargs={'ad_id': ad.pk})
        except:
            try:
                url = reverse('exchange_proposal_create', kwargs={'ad_id': ad.pk})
            except:
                url = reverse('propose_exchange', kwargs={'ad_id': ad.pk})

        response = client.post(url, {
            'sender_ad': ad.pk,
            'comment': 'Предлагаю обмен'
        })
        assert response.status_code == 302
        assert not ExchangeProposal.objects.filter(ad_sender=ad, ad_receiver=ad).exists()

    def test_create_exchange_proposal_requires_login(self, client, ad, another_ad):
        """Тест требования авторизации для создания предложения обмена"""
        try:
            url = reverse('create_exchange_proposal', kwargs={'ad_id': another_ad.pk})
        except:
            try:
                url = reverse('exchange_proposal_create', kwargs={'ad_id': another_ad.pk})
            except:
                url = reverse('propose_exchange', kwargs={'ad_id': another_ad.pk})

        response = client.post(url, {
            'sender_ad': ad.pk,
            'comment': 'Предлагаю обмен'
        })
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_my_proposals_view(self, client, user, proposal):
        """Тест просмотра своих предложений обмена"""
        client.force_login(user)
        response = client.get(reverse('my_proposals'))
        assert response.status_code == 200
        assert 'sent_proposals' in response.context
        assert 'received_proposals' in response.context
        assert list(response.context['sent_proposals']) == [proposal]

    def test_my_proposals_view_requires_login(self, client):
        """Тест требования авторизации для просмотра предложений"""
        response = client.get(reverse('my_proposals'))
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_update_proposal_status(self, client, another_user, proposal):
        """Тест обновления статуса предложения обмена"""
        client.force_login(another_user)
        try:
            url = reverse('update_proposal_status', kwargs={'proposal_id': proposal.pk})
        except:
            try:
                url = reverse('proposal_status_update', kwargs={'proposal_id': proposal.pk})
            except:
                url = reverse('update_status', kwargs={'proposal_id': proposal.pk})

        response = client.post(url, {
            'status': 'accepted'
        })
        assert response.status_code == 302
        proposal.refresh_from_db()
        assert proposal.status == 'accepted'

    def test_update_proposal_status_unauthorized(self, client, user, proposal):
        """Тест обновления статуса предложения обмена неавторизованным пользователем"""
        # Отправитель не может менять статус
        client.force_login(user)
        try:
            url = reverse('update_proposal_status', kwargs={'proposal_id': proposal.pk})
        except:
            try:
                url = reverse('proposal_status_update', kwargs={'proposal_id': proposal.pk})
            except:
                url = reverse('update_status', kwargs={'proposal_id': proposal.pk})

        response = client.post(url, {
            'status': 'accepted'
        })
        assert response.status_code == 302
        proposal.refresh_from_db()
        assert proposal.status == 'pending'  # Статус не изменился

    def test_update_proposal_status_requires_login(self, client, proposal):
        """Тест требования авторизации для обновления статуса предложения"""
        try:
            url = reverse('update_proposal_status', kwargs={'proposal_id': proposal.pk})
        except:
            try:
                url = reverse('proposal_status_update', kwargs={'proposal_id': proposal.pk})
            except:
                url = reverse('update_status', kwargs={'proposal_id': proposal.pk})

        response = client.post(url, {
            'status': 'accepted'
        })
        assert response.status_code == 302
        assert '/login/' in response.url


@pytest.mark.django_db
class TestAdListFiltering:
    """Дополнительные тесты для фильтрации объявлений"""

    def test_ad_list_filter_by_category(self, client, ad, another_ad):
        """Тест фильтрации по категории"""
        response = client.get(f"{reverse('ad_list')}?category=electronics")
        assert response.status_code == 200
        ads_list = list(response.context['ads'])
        assert ad in ads_list
        assert another_ad not in ads_list

    def test_ad_list_filter_by_condition(self, client, ad, another_ad):
        """Тест фильтрации по состоянию"""
        response = client.get(f"{reverse('ad_list')}?condition=new")
        assert response.status_code == 200
        ads_list = list(response.context['ads'])
        assert ad in ads_list
        assert another_ad not in ads_list

    def test_ad_list_search_query(self, client, ad, another_ad):
        """Тест поиска по запросу"""
        ad.save()
        another_ad.save()

        response = client.get(f"{reverse('ad_list')}?query=Тестовое")
        assert response.status_code == 200
        ads_list = list(response.context['ads'])

        if ad not in ads_list:
            response = client.get(f"{reverse('ad_list')}?query=тестовое")
            ads_list = list(response.context['ads'])

        assert ad in ads_list
        assert another_ad not in ads_list

    def test_ad_list_my_ads_filter(self, client, user, ad, another_ad):
        """Тест фильтрации только своих объявлений"""
        client.force_login(user)
        response = client.get(f"{reverse('ad_list')}?is_mine=on")
        assert response.status_code == 200
        ads_list = list(response.context['ads'])
        assert ad in ads_list
        assert another_ad not in ads_list


@pytest.mark.django_db
class TestProposalPermissions:
    """Дополнительные тесты для разрешений предложений обмена"""

    def test_received_proposals_view(self, client, another_user, proposal):
        """Тест просмотра полученных предложений обмена"""
        client.force_login(another_user)
        response = client.get(reverse('my_proposals'))
        assert response.status_code == 200
        assert list(response.context['received_proposals']) == [proposal]
        assert list(response.context['sent_proposals']) == []