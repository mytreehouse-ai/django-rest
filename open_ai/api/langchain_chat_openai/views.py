import os
import time
import logging
from django.http import StreamingHttpResponse
from rest_framework.generics import RetrieveAPIView
from ...services.open_ai_services import OpenAILocalServices


logger = logging.getLogger(__name__)

def retrieve_stream_generator(question: str):
    """
    Generator function that retrieves data from OpenAI service and yields data chunks for streaming.
    Introduces a 100ms delay between each yielded result for rate control.

    :param question: The question to be processed by the OpenAI service.
    """
    open_ai_services = OpenAILocalServices(api_key=os.environ.get("OPENAI_API_KEY"))
    for result in open_ai_services.run_chain(question):
        yield result
        time.sleep(0.001)  # Introduce a 1ms delay before the next iteration

class LangchainChatRetrieveAPIView(RetrieveAPIView):
    """
    API view that retrieves data from OpenAI service and streams it to the client.
    """
    def get(self, request, *args, **kwargs):
      question = self.request.query_params.get("q", "")
      response =  StreamingHttpResponse(
          retrieve_stream_generator(question),
          status=200, 
          content_type='text/event-stream'
      )
      response['Cache-Control']= 'no-cache',
      return response

