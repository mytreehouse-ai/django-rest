from django.urls import path
# from .api.langchain_chat_openai.views import LangchainChatRetrieveAPIView
from .api.apollo_exploration.views import ApolloExplorationAiAPIView

urlpatterns = [
    # path("langchain/chat-openai", LangchainChatRetrieveAPIView.as_view())
    path("lanchain/assistant", ApolloExplorationAiAPIView.as_view())
]
