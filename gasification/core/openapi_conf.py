from drf_yasg.generators import OpenAPISchemaGenerator


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
  def get_schema(self, request=None, public=False):
    """Generate a :class:`.Swagger` object with custom tags"""

    swagger = super().get_schema(request, public)
    swagger.tags = [
        {
            "name": "accounts",
            "description": "Общие методы для работы с учетной записью"
        },
        {
            "name": "clients",
            "description": "Методы для работы с пользователями-клиентами"
        },
        {
            "name": "staff",
            "description": "Методы для работы с пользователями-администраторами"
        },
        {
            "name": "orders",
            "description": "Методы для работы с заявками"
        },
        {
            "name": "config",
            "description": "Методы для конфигурации заявок пользователями-администраторами"
        },
        {
            "name": "erp",
            "description": "Методы для работы с данными из ERP"
        },
    ]

    return swagger