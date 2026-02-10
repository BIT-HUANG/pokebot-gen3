from pathlib import Path

from notifypy import Notify
from notifypy.exceptions import UnsupportedPlatform
from modules.context import context
from modules.sprites import choose_random_sprite



def desktop_notification(title: str, message: str, icon: Path = None) -> None:
    if not context.config.logging.desktop_notifications:
        return

    try:
        icon = icon or choose_random_sprite()

        notification = Notify(
            default_notification_application_name=f"{context.profile.path.name} | BD4SLW mGBA"
        )
        notification.title = title
        notification.message = message
        notification.icon = icon

        notification.send()
    except UnsupportedPlatform:
        # The `notifypy` library does not support Windows 11 and will throw that error, so in that case
        # there's nothing the user (or we) could do about it. Just ignore that error silently.
        pass
    except Exception as e:
        print(e)
