"""
Audit logging middleware for admin actions.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.admin_models import AdminAuditLog, AdminUser
import logging

logger = logging.getLogger(__name__)


class AuditLoggerMiddleware(BaseMiddleware):
    """
    Middleware to automatically log admin actions.
    Logs actions after handler execution if audit_action is set in state data.
    """

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Execute handler and log audit action if set.
        """
        # Call the handler first
        result = await handler(event, data)

        # Check if admin action should be logged
        if "admin" in data and data["admin"] is not None:
            admin: AdminUser = data["admin"]

            # Check if state data has audit_action
            state = data.get("state")
            if state:
                state_data = await state.get_data()
                audit_action = state_data.get("audit_action")

                if audit_action:
                    try:
                        # Create audit log entry
                        await AdminAuditLog.create(
                            admin_id=admin.user_id,
                            action=audit_action.get("action", "unknown"),
                            target_type=audit_action.get("target_type"),
                            target_id=audit_action.get("target_id"),
                            details=audit_action.get("details", {})
                        )

                        logger.info(
                            f"Admin action logged: {audit_action.get('action')} "
                            f"by admin {admin.user_id}"
                        )

                        # Clear audit action from state
                        await state.update_data(audit_action=None)

                    except Exception as e:
                        logger.error(f"Failed to log admin action: {e}")

        return result
