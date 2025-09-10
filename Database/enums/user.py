class UserStatus():
    INVITED = "invited"
    REGISTRATION = "registration"
    ACTIVE = "active"
    BANNED = "banned"
    SUBSCRIPTION_EXPIRED = "subscription_expired"

    WAITING_LIST = "waiting_list"

    ALL = [
        INVITED,
        REGISTRATION,
        ACTIVE,
        BANNED,
        SUBSCRIPTION_EXPIRED,
        WAITING_LIST
    ]

class UserSubscription():
    # Основные подписки
    BASE = "base"

    # Подарочные подписки
    GIFT_BASE = "gift_base"