from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


def _has_user_instance_and_request(user_instance, request):
    """Validate prerequisites for role change validation."""
    if user_instance is None:
        raise ValidationError(
            "User instance required for role validation.", code="missing_user_instance"
        )
    if not request:
        raise ValidationError(
            "Role changes require authenticated user context.",
            code="missing_request",
        )


def _get_role_info(user_instance, new_role, request):
    """Get role information for validation checks."""
    try:
        new_role_index = user_instance.Roles.get_privilege_level(new_role)
        request_user_role = request.user.role
        request_user_role_index = user_instance.Roles.get_privilege_level(request_user_role)
        is_self_update = user_instance.pk == request.user.pk

        if user_instance.pk:
            current_user_role = user_instance.role
            current_user_role_index = user_instance.Roles.get_privilege_level(current_user_role)
            has_role_update = current_user_role != new_role
        else:
            current_user_role = None
            current_user_role_index = None
            has_role_update = True

        return {
            "current_user_role": current_user_role,
            "current_user_role_index": current_user_role_index,
            "new_role": new_role,
            "new_role_index": new_role_index,
            "request_user_role": request_user_role,
            "request_user_role_index": request_user_role_index,
            "is_self_update": is_self_update,
            "has_role_update": has_role_update,
            "request": request,
        }
    except ValueError:
        raise ValidationError(
            "Please select a valid role for user.",
            code="invalid_role",
        )


def _validate_super_admin_self_update(info):
    """Validate super admin cannot change their own role."""
    if info["is_self_update"] and info["has_role_update"]:
        raise ValidationError(
            {
                "role": "Super admin cannot change their own role.",
            }
        )


def _validate_non_super_assigning_super_admin(info):
    """Validate non-super admins cannot assign super admin role."""
    if info["new_role"] == User.Roles.SUPER_ADMIN and info["has_role_update"]:
        raise ValidationError(
            {
                "role": "Only Super Admins can assign Super Admin role.",
            }
        )


def _validate_self_upgrade(info):
    """Validate user cannot self-upgrade to a higher role."""
    if info["is_self_update"] and info["new_role_index"] > info["current_user_role_index"]:
        raise ValidationError(
            {
                "role": (
                    f"Cannot self upgrade from '{info['current_user_role']}' "
                    f"to '{info['new_role']}'."
                ),
            }
        )


def _validate_self_downgrade(info):
    """Validate user cannot self-downgrade to a lower role."""
    if info["is_self_update"] and info["new_role_index"] < info["current_user_role_index"]:
        raise ValidationError(
            {
                "role": (
                    f"Cannot self downgrade from '{info['current_user_role']}' "
                    f"to '{info['new_role']}'."
                ),
            }
        )


def _validate_non_super_assigning_higher_or_equal_role(info):
    """Validate non-super admins cannot assign higher or equal roles."""
    if (
        not info["request"].user.is_superuser
        and not info["is_self_update"]
        and info["has_role_update"]
    ):
        if info["current_user_role_index"] >= info["request_user_role_index"]:
            raise ValidationError(
                {
                    "role": "You don't have permission to downgrade users with higher roles.",
                }
            )

        if info["new_role_index"] >= info["request_user_role_index"]:
            raise ValidationError(
                {
                    "role": f"Role '{info['new_role']}' exceeds your permission level.",
                },
                code="insufficient_privileges",
            )


def validate_user_role_change(user_instance, new_role, request=None):
    """Validate role change based on user privileges and current role."""
    _has_user_instance_and_request(user_instance, request)
    info = _get_role_info(user_instance, new_role, request)

    if request.user.is_superuser:
        # For new users, skip self-update check since there's no existing user
        if user_instance.pk:
            _validate_super_admin_self_update(info)
        return

    _validate_non_super_assigning_super_admin(info)

    if user_instance.pk:
        _validate_self_upgrade(info)
        _validate_self_downgrade(info)
        _validate_non_super_assigning_higher_or_equal_role(info)
    else:
        if info["new_role_index"] >= info["request_user_role_index"]:
            raise ValidationError(
                {
                    "role": f"Role '{info['new_role']}' exceeds your permission level.",
                },
                code="insufficient_privileges",
            )
