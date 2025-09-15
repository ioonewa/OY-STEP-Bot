CONTENT_DIR = "content"

LESSONS_DIR = "content/lessons"

TEMPLATES_DIR = "content/templates"

LOGS_DIR = "logs"
PHOTOS_DIR = "photos"
VIDEOS_DIR = "videos"

DIRS = [
    LOGS_DIR,
    PHOTOS_DIR,
    VIDEOS_DIR,

    CONTENT_DIR,
    LESSONS_DIR,
    TEMPLATES_DIR
]

STASH_GROUP = -4831289621
PRIVATE_CHANNEL = -1002907913958

INVITE_LINK = "https://t.me/+Ks5JwTQGofRiOWNi"
PUBLIC_CHANNEL = "https://t.me/oystepmediaburo"
PRIVATE_GROUP_LINK = "https://t.me/+cSLmRvaa6uA3ZmRi"

SUPPORT_LINK = "https://t.me/oybot_support"

# | —


# Lessons

LESSON_1 = "1_WHY_IT_IS_IMPORTANT"
LESSON_2 = "2_HOW_TO_STOP_AFRAID"
LESSON_3 = "3_HOW_TO_FILMING"


#  Fields
FIELDS_TO_EDIT = [
    {"field": "name", "btn": "Имя"},
    {"field": "phone_number", "btn": "Номер телефона"},
    {"field": "email", "btn": "Почта"},
    {"field": "photo", "btn": "Фотография"}
]

# Limits:
NAME_LIMIT = 150
EMAIL_LIMIT = 150


IONEWA = 752021281
VADIM = 421389904
SAMELIYA = 264976221
VITALIY = 133353194
NEGA = 128562688
NIKOLAY = 316341973

ADMINS = [IONEWA, VADIM, SAMELIYA, VITALIY, NEGA, NIKOLAY]


from typing import TypedDict, Tuple, Optional, Dict, Literal

class TextColor(TypedDict):
    Black: Tuple[int,int,int,int]
    Color: Tuple[int,int,int,int]
    Pastel: Tuple[int,int,int,int]
    White: Tuple[int,int,int,int]

class Font(TypedDict):
    name: str
    size: int
    upper: bool
    center: bool
    color: TextColor
    offset_x: Optional[int] = 0
    center: Optional[bool] = False
    upper: Optional[bool] = False

class Position(TypedDict):
    x: Optional[int] = 0
    y: Optional[int] = 0

class Photo(TypedDict):
    top: int
    left: int
    rect_width: int
    rect_height: int
    mask_path: str
    angel: Optional[float] = 0

class ObjParams(TypedDict):
    font: Font  
    photo: Photo
    text: Dict[
        Literal["name", "username", "email", "phone_number"],
        Position
    ]

class Content(TypedDict):
    post: ObjParams
    story: ObjParams

content_rules: Dict[str, Content] = {
    "2": {
        "post": {
            "font": {
                "name": "TTChocolates-Bold.ttf",
                "size": 40,
                "upper": True,
                "color": {
                    "Black": (255,255,255,255),
                    "Color": (255,255,255,255),
                    "Pastel": (0,0,0,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 189,
                "left": 182,
                "rect_width": 720,
                "rect_height": 540
            },
            "text": {
                "name": {
                    "x": 218,
                    "y": 970
                },
                "phone_number": {
                    "x": 218,
                    "y": 1020
                },
                "email": {
                    "x": 218,
                    "y": 1070
                },
                "username": {
                    "x": 218,
                    "y": 1120
                }
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Bold.ttf",
                "size": 56,
                "upper": True,
                "color": {
                    "Black": (255,255,255,255),
                    "Color": (255,255,255,255),
                    "Pastel": (0,0,0,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 240,
                "left": 180,
                "rect_width": 720,
                "rect_height": 720
            },
            "text": {
                "name": {
                    "x": 220,
                    "y": 1324
                },
                "phone_number": {
                    "x": 220,
                    "y": 1384
                },
                "email": {
                    "x": 220,
                    "y": 1444
                },
                "username": {
                    "x": 220,
                    "y": 1504
                }
                
            }
        },
    },
    "3": {
        "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 42,
                "center": False,
                "offset_x": 20,
                "color": {
                    "Black": (235,50,35,255),
                    "Color": (235,50,35,255),
                    "Pastel": (235,50,35,255),
                    "White": (235,50,35,255)
                }
            },
            "photo": {
                "top": 109,
                "left": 196,
                "rect_width": 605,
                "rect_height": 600,
                "angle": 5
            },
            "text": {
                "name": {
                    "x": 309,
                    "y": 843
                },
                "phone_number": {
                    "x": 309,
                    "y": 890
                },
                "email": {
                    "x": 309,
                    "y": 935
                },
                "username": {
                    "x": 309,
                    "y": 985
                }
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 44,
                "color": {
                    "Black": (235,50,35,255),
                    "Color": (235,50,35,255),
                    "Pastel": (235,50,35,255),
                    "White": (235,50,35,255)
                }
            },
            "photo": {
                "top": 236,
                "left": 148,
                "rect_width": 745,
                "rect_height": 736,
                "angle": 5,
            },
            "text": {
                "name": {
                    "x": 320,
                    "y": 1232
                },
                "phone_number": {
                    "x": 320,
                    "y": 1280
                },
                "email": {
                    "x": 320,
                    "y": 1325
                },
                "username": {
                    "x": 320,
                    "y": 1370
                }
            },
        },
    },
    "4": {
        "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 58,
                "center": True,
                "color": {
                    "Black": (255,255,255,255),
                    "Color": (255,255,255,255),
                    "Pastel": (255,255,255,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 292,
                "left": 110,
                "rect_width": 860,
                "rect_height": 530
            },
            "text": {
                "name": {
                    "x": 224,
                    "y": 900
                },
                "phone_number": {
                    "x": 224,
                    "y": 970
                },
                "email": {
                    "x": 224,
                    "y": 1040
                },
                "username": {
                    "x": 224,
                    "y": 1110
                },
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 62,
                "center": True,
                "color": {
                    "Black": (255,255,255,255),
                    "Color": (255,255,255,255),
                    "Pastel": (255,255,255,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 577,
                "left": 109,
                "rect_width": 862,
                "rect_height": 532
            },
            "text": {
                "name": {
                    "x": 160,
                    "y": 1225
                },
                "phone_number": {
                    "x": 160,
                    "y": 1315
                },
                "email": {
                    "x": 160,
                    "y": 1405
                },
                "username": {
                    "x": 160,
                    "y": 1495
                },
                
            },
        },
    },
    "5": {
        "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 58,
                "center": True,
                "color": {
                    "Black": (255,255,255,255),
                    "Color": (0,0,0,255),
                    "Pastel": (0,0,0,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 58,
                "left": 140,
                "rect_width": 800,
                "rect_height": 800,
                "mask_path": "content/templates/5/post_mask.png"
            },
            "text": {
                "name": {
                    "x": 224,
                    "y": 1000
                },
                "phone_number": {
                    "x": 224,
                    "y": 1070
                },
                "email": {
                    "x": 224,
                    "y": 1140
                },
                "username": {
                    "x": 224,
                    "y": 1210
                },
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 62,
                "center": True,
                "color": {
                    "Black": (255,255,255,255),
                    "Color": (0,0,0,255),
                    "Pastel": (0,0,0,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 300,
                "left": 120,
                "rect_width": 840,
                "rect_height": 840,
                "mask_path": "content/templates/5/story_mask.png"
            },
            "text": {
                "name": {
                    "x": 160,
                    "y": 1325
                },
                "phone_number": {
                    "x": 160,
                    "y": 1415
                },
                "email": {
                    "x": 160,
                    "y": 1505
                },
                "username": {
                    "x": 160,
                    "y": 1595
                },
                
            },
        }
    },
    "6": {
        "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 58,
                "center": True,
                "font": {
                    "Black": (0,0,0,255),
                    "Color": (0,0,0,255),
                    "Pastel": (0,0,0,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 334,
                "left": 0,
                "rect_width": 1080,
                "rect_height": 652,
                "mask_path": "content/templates/6/post_mask.png"
            },
            "text": {
                "name": {
                    "x": 224,
                    "y": 1020
                },
                "phone_number": {
                    "x": 224,
                    "y": 1090
                },
                "email": {
                    "x": 224,
                    "y": 1160
                },
                "username": {
                    "x": 224,
                    "y": 1230
                },
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 62,
                "center": True,
                "font": {
                    "Black": (0,0,0,255),
                    "Color": (0,0,0,255),
                    "Pastel": (0,0,0,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 478,
                "left": 0,
                "rect_width": 1080,
                "rect_height": 924,
                "mask_path": "content/templates/6/story_mask.png"
            },
            "text": {
                "name": {
                    "x": 160,
                    "y": 1470
                },
                "phone_number": {
                    "x": 160,
                    "y": 1560
                },
                "email": {
                    "x": 160,
                    "y": 1650
                },
                "username": {
                    "x": 160,
                    "y": 1740
                },
            },
        },
    },
    "8": {
        "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 58,
                "center": True,
                "color": {
                    "Black": (33,81,85,255),
                    "Color": (255,255,255,255),
                    "Pastel": (33,81,85,255),
                    "White": (255,255,255,255)
                }
            },
            "photo": {
                "top": 251,
                "left": 0,
                "rect_width": 1080,
                "rect_height": 639,
                "mask_path": "content/templates/8/post_mask.png"
            },
            "text": {
                "name": {
                    "x": 224,
                    "y": 960
                },
                "phone_number": {
                    "x": 224,
                    "y": 1030
                },
                "email": {
                    "x": 224,
                    "y": 1100
                },
                "username": {
                    "x": 224,
                    "y": 1170
                },
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 62,
                "center": True,
                "color": {
                    "Black": (33,81,85,255),
                    "Color": (255,255,255,255),
                    "Pastel": (33,81,85,255),
                    "White": (255,255,255,255)
                }
            },
            "photo": {
                "top": 399,
                "left": 0,
                "rect_width": 1080,
                "rect_height": 814,
                "mask_path": "content/templates/8/story_mask.png"
            },
            "text": {}
        }
    }
}

content_rules["9"] = {
    "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 54,
                "center": True,
                "upper": True,
                "color": {
                    "Black": (0,0,0,255),
                    "Color": (0,0,0,255),
                    "Pastel": (255,255,255,255),
                    "White": (255,255,255,255)
                }
            },
            "photo": {
                "top": 242,
                "left": 0,
                "rect_width": 1080,
                "rect_height": 628,
            },
            "text": {
                "name": {
                    "x": 224,
                    "y": 980
                },
                "phone_number": {
                    "x": 224,
                    "y": 1050
                },
                "email": {
                    "x": 224,
                    "y": 1120
                },
                "username": {
                    "x": 224,
                    "y": 1190
                },
            }
    },
    "story": {
        "font": {
            "name": "TTChocolates-Regular.ttf",
            "size": 64,
            "center": True,
            "upper": True,
            "color": {
                "Black": (0,0,0,255),
                "Color": (0,0,0,255),
                "Pastel": (255,255,255,255),
                "White": (255,255,255,255)
            }
        },
        "photo": {
            "top": 395,
            "left": 0,
            "rect_width": 1080,
            "rect_height": 800
        },
        "text": {
                "name": {
                    "x": 160,
                    "y": 1300
                },
                "phone_number": {
                    "x": 160,
                    "y": 1370
                },
                "email": {
                    "x": 160,
                    "y": 1440
                },
                "username": {
                    "x": 160,
                    "y": 1510
                },
            }
    }
} 

content_rules["10"] = {
    "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 54,
                "upper": True,
                "color": {
                    "Black": (255,255,255,255),
                    "Color": (255,255,255,255),
                    "Pastel": (0,0,0,255),
                    "White": (0,0,0,255)
                }
            },
            "photo": {
                "top": 151,
                "left": 165,
                "rect_width": 742,
                "rect_height": 568,
            },
            "text": {
                "name": {
                    "x": 141,
                    "y": 960
                },
                "phone_number": {
                    "x": 141,
                    "y": 1030
                },
                "email": {
                    "x": 141,
                    "y": 1100
                },
                "username": {
                    "x": 141,
                    "y": 1170
                },
            }
    },
    "story": {
        "font": {
            "name": "TTChocolates-Regular.ttf",
            "size": 54,
            "upper": True,
            "color": {
                "Black": (255,255,255,255),
                "Color": (255,255,255,255),
                "Pastel": (0,0,0,255),
                "White": (0,0,0,255)
            }
        },
        "photo": {
            "top": 437,
            "left": 165,
            "rect_width": 742,
            "rect_height": 568
        },
        "text": {
                "name": {
                    "x": 141,
                    "y": 1300
                },
                "phone_number": {
                    "x": 141,
                    "y": 1370
                },
                "email": {
                    "x": 141,
                    "y": 1440
                },
                "username": {
                    "x": 141,
                    "y": 1510
                },
            }
    }
} 

INSTRUCTIONS = {
    "video": {
        "tg": """👆🏻 <b>Как выложить историю в Telegram.</b>

1. Откройте видео → нажмите ⋯ → Сохранить.

2. Вверху главного экрана нажмите Моя история (+).

3. Выберите видео из Галереи

4. Нажмите Опубликовать""",
        "ig": """👆🏻 <b>Как выложить историю в Instagram.</b>

1. Откройте видео → нажмите ⋯ → Сохранить.

2. Откройте Instagram → нажмите (+) → История.

3. Выберите видео из Галереи.

4. При необходимости добавьте текст, стикеры, музыку.

5. Нажмите Поделиться""",
        "wa": """👆🏻 <b>Как выложить статус в WhatsApp.</b>

1. Сохраните видео в Галерею.

2. Откройте WhatsApp → вкладка Статус.

3. Нажмите на значок камеры.

4. Выберите видео из Галереи

5. При необходимости добавьте текст, смайлы или подпись.

6. Нажмите Отправить → статус станет доступен всем вашим контактам."""
    },
    "story": {
        "tg": """👆🏻 <b>Как выложить историю в Telegram</b>

1. Откройте фото → нажмите ⋯ → Сохранить

2. Вверху главного экрана нажмите Моя история (+).

3. Выберите фото из Галереи

4. При необходимости отредактируйте.

5. Нажмите Опубликовать""",
        "ig": """👆🏻 <b>Как выложить историю в Instagram</b>

1. Сохраните фото в Галерею.

2. Откройте Instagram → нажмите (+) → История.

3. Выберите фото из Галереи.

4. При необходимости добавьте текст, стикеры, музыку.

5. Нажмите Поделиться → выберите Моя история.""",
        "wa": """👆🏻 <b>Как выложить статус в WhatsApp</b>

1. Сохраните фото в Галерею.

2. Откройте WhatsApp → вкладка Статус.

3. Нажмите на значок камеры.

4. Выберите фото из Галереи.

5. При необходимости добавьте текст, смайлы или подпись.

6. Нажмите Отправить → статус станет доступен всем вашим контактам."""
    },
    "post": {
        "tg": """<b>👆🏻 Как выложить пост в Telegram</b>

1. Перешлите пост в свой телеграм-канал.

2. <b>Не забудьте скрыть имя отправителя.</b>""",
        "ig": """👆🏻 <b>Как выложить пост в Instagram</b>

1. Сохраните фото в Галерею.

2. Откройте Instagram → нажмите (+) → Публикация.

3. Выберите фото из Галереи.

4. При необходимости добавьте фильтр или отредактируйте.

5. Напишите подпись, хэштеги и отметьте людей.

6. Нажмите Поделиться → пост появится в профиле.""",
    }
}
