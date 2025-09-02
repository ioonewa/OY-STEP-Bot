class UserStatus():
    INVITED = "invited"
    REGISTRATION = "registration"
    ACTIVE = "active"
    BANNED = "banned"
    SUBSCRIPTION_EXPIRED = "subscription_expired"

    ALL = [
        INVITED,
        REGISTRATION,
        ACTIVE,
        BANNED,
        SUBSCRIPTION_EXPIRED
    ]

class UserSubscription():
    # Основные подписки
    BASE = "base"

    # Подарочные подписки
    GIFT_BASE = "gift_base"