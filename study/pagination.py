from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
        Пагинация для стандартного набора результатов.

        Этот класс наследует от PageNumberPagination и предоставляет
        стандартные параметры пагинации для API.

        Атрибуты:
            page_size (int): Количество элементов на странице по умолчанию.
                             Установлено на 10.
            page_size_query_param (str): Параметр запроса, который может быть
                                          использован для указания размера страницы.
                                          Установлено на "page_size".
            max_page_size (int): Максимально допустимый размер страницы.
                                 Установлено на 20.
        """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 20
