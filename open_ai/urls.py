from django.urls import path
from .api.langchain_chat_openai.views import LangchainChatRetrieveAPIView

urlpatterns = [
    path('langchain/chat-openai', LangchainChatRetrieveAPIView.as_view())
]