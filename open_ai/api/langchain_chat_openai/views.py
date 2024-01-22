import os
import logging
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from rest_framework.generics import RetrieveAPIView
from ...services.lanchain_openai_services import LangchainOpenAIServices


logger = logging.getLogger(__name__)

def generate_openai_response(question: str, stream: bool = False):
    """
    Generator function that retrieves data from the OpenAI service and yields data chunks for streaming
    if streaming is enabled. Otherwise, it returns the complete response.

    :param question: The question to be processed by the OpenAI service.
    :param stream: A boolean flag indicating whether to stream the response.
    :return: A generator yielding data chunks if streaming, otherwise the complete response.
    """
    open_ai_services = LangchainOpenAIServices(api_key=os.environ.get("OPENAI_API_KEY"), stream=stream)

    if stream:
        for result in open_ai_services.run_chain(question):
            yield result
    else:
        return open_ai_services.run_chain(question)
    
class LangchainChatRetrieveAPIView(RetrieveAPIView):
    """
    API view that retrieves data from OpenAI service and streams it to the client.
    """
    def get(self, request, *args, **kwargs):
      question = self.request.query_params.get("q", "")
      stream = self.request.query_params.get("stream", "1")

      if stream == "1":
        response =  StreamingHttpResponse(
            generate_openai_response(question=question, stream=True),
            status=200, 
            content_type='text/event-stream'
        )
        response['Cache-Control']= 'no-cache',
        return response
      else:
         response_data = generate_openai_response(question=question)
         return Response(response_data, content_type='text/plain')

