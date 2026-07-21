from app.notifications.enums import NotificationType
from app.notifications.events import NotificationEvent
from app.notifications.repo import NotificationRepo
from app.notifications.service import NotificationService


def make_service(db_session) -> NotificationService:
    return NotificationService(NotificationRepo(db_session))


def create_notification(
    service: NotificationService,
    *,
    project_id: int,
    title: str,
):
    return service.create(
        NotificationEvent(
            project_id=project_id,
            type=NotificationType.ACTIVITY,
            title=title,
            message=f"{title} message",
            data={"source": "test"},
        )
    )


def test_create_get_and_list_project_notifications(db_session):
    service = make_service(db_session)
    first = create_notification(service, project_id=1, title="First")
    second = create_notification(service, project_id=1, title="Second")
    create_notification(service, project_id=2, title="Other project")

    notifications = service.list_project(project_id=1)

    assert [notification.id for notification in notifications] == [second.id, first.id]
    assert service.get(first.id) == first
    assert first.type == NotificationType.ACTIVITY
    assert first.data == {"source": "test"}
    assert first.is_read is False


def test_list_project_supports_pagination_and_unread_filter(db_session):
    service = make_service(db_session)
    first = create_notification(service, project_id=1, title="First")
    second = create_notification(service, project_id=1, title="Second")
    third = create_notification(service, project_id=1, title="Third")
    service.mark_read(third.id)

    assert service.list_project(1, limit=1, offset=1) == [second]
    assert service.list_project(1, unread_only=True) == [second, first]


def test_mark_read_is_idempotent(db_session):
    service = make_service(db_session)
    notification = create_notification(service, project_id=1, title="Read me")

    marked = service.mark_read(notification.id)
    first_read_at = marked.read_at
    marked_again = service.mark_read(notification.id)

    assert marked.is_read is True
    assert first_read_at is not None
    assert marked_again.read_at == first_read_at
    assert service.mark_read(9999) is None


def test_mark_project_read_only_updates_the_requested_project(db_session):
    service = make_service(db_session)
    first = create_notification(service, project_id=1, title="First")
    second = create_notification(service, project_id=1, title="Second")
    other = create_notification(service, project_id=2, title="Other")

    updated_count = service.mark_project_read(1)

    assert updated_count == 2
    assert service.get(first.id).is_read is True
    assert service.get(second.id).is_read is True
    assert service.get(other.id).is_read is False
    assert service.mark_project_read(1) == 0


def test_delete_notification(db_session):
    service = make_service(db_session)
    notification = create_notification(service, project_id=1, title="Delete me")

    assert service.delete(notification.id) is True
    assert service.get(notification.id) is None
    assert service.delete(notification.id) is False
