"""
Admin Audit Logging - Track all admin actions.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from ...common.database import get_async_mongodb, MongoCollections
from ...models.mongodb_models import AdminAuditLog

logger = logging.getLogger(__name__)


async def log_admin_action(
    admin_id: str,
    admin_email: Optional[str],
    action_type: str,
    action_category: str,
    entity_type: str,
    entity_id: str,
    changes: List[Dict[str, Any]],
    endpoint: str,
    method: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None
):
    """
    Log an admin action to MongoDB audit log.
    
    Args:
        admin_id: Admin ID performing the action
        admin_email: Admin email
        action_type: Type of action (create, update, delete, etc.)
        action_category: Category (user_mgmt, inventory, financial, system)
        entity_type: Type of entity (user, flight, hotel, car, booking, billing)
        entity_id: ID of the entity being acted upon
        changes: List of changes with old/new values
        endpoint: API endpoint
        method: HTTP method
        ip_address: Admin IP address
        user_agent: Admin user agent
        status: Action status (success, failed, unauthorized)
        error_message: Error message if failed
    """
    try:
        db = get_async_mongodb()
        
        audit_log = AdminAuditLog(
            audit_id=f"AUDIT-{uuid.uuid4().hex[:8].upper()}",
            admin_id=admin_id,
            admin_email=admin_email,
            action_type=action_type,
            action_category=action_category,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status=status,
            error_message=error_message,
            timestamp=datetime.utcnow()
        )
        
        await db[MongoCollections.ADMIN_AUDIT_LOGS].insert_one(audit_log.model_dump())
        logger.info(f"Audit logged: {action_type} {entity_type} {entity_id} by {admin_id}")
    
    except Exception as e:
        logger.error(f"Failed to log admin audit: {e}")


def compare_objects(old_obj: Any, new_obj: Any, fields_to_track: List[str]) -> List[Dict[str, Any]]:
    """
    Compare two objects and return list of changes.
    
    Args:
        old_obj: Old object
        new_obj: New object (or dict of updates)
        fields_to_track: List of field names to compare
    
    Returns:
        List of change dictionaries with field, old_value, new_value
    """
    changes = []
    
    # If new_obj is a dict (updates), only check those fields
    if isinstance(new_obj, dict):
        for field in fields_to_track:
            if field in new_obj:
                old_value = getattr(old_obj, field, None) if hasattr(old_obj, field) else None
                new_value = new_obj[field]
                
                if old_value != new_value:
                    changes.append({
                        "field": field,
                        "old_value": str(old_value) if old_value is not None else None,
                        "new_value": str(new_value) if new_value is not None else None
                    })
    else:
        # Compare all tracked fields
        for field in fields_to_track:
            old_value = getattr(old_obj, field, None) if hasattr(old_obj, field) else None
            new_value = getattr(new_obj, field, None) if hasattr(new_obj, field) else None
            
            if old_value != new_value:
                changes.append({
                    "field": field,
                    "old_value": str(old_value) if old_value is not None else None,
                    "new_value": str(new_value) if new_value is not None else None
                })
    
    return changes

