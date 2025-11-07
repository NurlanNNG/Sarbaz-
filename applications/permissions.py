from rest_framework import permissions

class IsOwnerAndEditable(permissions.BasePermission):
    """
    Разрешаем владельцу изменять/удалять заявку только если её status == 'new'.
    Staff-пользователь (админ) может всё всегда.
    Чтение (SAFE_METHODS) доступно владельцу (или staff).
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Любые действия админа разрешены
        if user.is_staff:
            return True

        # Анонимы ничего не могут
        if not user.is_authenticated:
            return False

        # Владелец всегда может читать свои заявки
        if request.method in permissions.SAFE_METHODS:
            return obj.user == user

        # Для создания (POST) достаточно IsAuthenticated, этот класс не проверяет create
        if view.action == 'create':
            return True

        # Для обновления (PUT/PATCH) и удаления (DELETE):
        # разрешаем только владельцу и только если статус "new"
        if view.action in ['update', 'partial_update', 'destroy']:
            return obj.user == user and obj.status == 'new'

        # По умолчанию запрещаем
        return False
