from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class to set a default page size.
    """
    page_size = 10  # Set the default number of items per page
    # Allow client to override the page size using this query parameter
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum limit of items per page
