from django.urls import path
from .views import (
    RecipientListView, RecipientDetailView, RecipientCreateView, RecipientUpdateView, RecipientDeleteView,
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView,
    MailingListView, MailingCreateView, MailingUpdateView, MailingDeleteView, HomeView,
    send_mailing,
)

app_name = 'mailing'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('recipients/', RecipientListView.as_view(), name='recipient-list'),
    path('recipients/<int:pk>/', RecipientDetailView.as_view(), name='recipient-detail'),
    path('recipients/create/', RecipientCreateView.as_view(), name='recipient-create'),
    path('recipients/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient-update'),
    path('recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient-delete'),

    path('messages/', MessageListView.as_view(), name='message-list'),
    path('messages/create/', MessageCreateView.as_view(), name='message-create'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message-update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message-delete'),

    path('mailings/', MailingListView.as_view(), name='mailing-list'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing-create'),
    path('mailings/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing-update'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing-delete'),
    path('mailings/<int:pk>/send/', send_mailing, name='mailing-send'),
]