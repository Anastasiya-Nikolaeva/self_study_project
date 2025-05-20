from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Получаем стандартный ответ
    response = exception_handler(exc, context)

    # Если это ошибка аутентификации
    if response is not None and response.status_code == 401:
        response.data = {
            "detail": "Authentication credentials were not provided or are invalid."
        }

    return response
