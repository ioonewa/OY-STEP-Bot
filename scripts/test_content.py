from Bot.utils.get_content import overlay_photo, overlay_text

rules = {
    "2": {
        "post": {
            "font": {
                "name": "TTChocolates-Bold.ttf",
                "size": 40,
                "upper": True
            },
            "photo": {
                "top": 189,
                "left": 182,
                "rect_width": 720,
                "rect_height": 540
            },
            "text": {
                "name": {
                    "text_x": 218,
                    "text_y": 970
                },
                "phone_number": {
                    "text_x": 218,
                    "text_y": 1020
                },
                "email": {
                    "text_x": 218,
                    "text_y": 1070
                },
                "username": {
                    "text_x": 218,
                    "text_y": 1120
                }
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Bold.ttf",
                "size": 56,
                "upper": True
            },
            "photo": {
                "top": 240,
                "left": 180,
                "rect_width": 720,
                "rect_height": 720
            },
            "text": {
                "name": {
                    "text_x": 220,
                    "text_y": 1324
                },
                "phone_number": {
                    "text_x": 220,
                    "text_y": 1384
                },
                "email": {
                    "text_x": 220,
                    "text_y": 1444
                },
                "username": {
                    "text_x": 220,
                    "text_y": 1504
                }
                
            }
        },
        "video": {},
        "text_colors": {
            "Black": (255,255,255,255),
            "Color": (255,255,255,255),
            "Pastel": (0,0,0,255),
            "White": (0,0,0,255)
        }
    },
    "3": {
        "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 42,
                "center": False,
                "offset_x": 20
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
                    "text_x": 309,
                    "text_y": 843
                },
                "phone_number": {
                    "text_x": 309,
                    "text_y": 890
                },
                "email": {
                    "text_x": 309,
                    "text_y": 935
                },
                "username": {
                    "text_x": 309,
                    "text_y": 985
                }
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 44
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
                    "text_x": 320,
                    "text_y": 1232
                },
                "phone_number": {
                    "text_x": 320,
                    "text_y": 1280
                },
                "email": {
                    "text_x": 320,
                    "text_y": 1325
                },
                "username": {
                    "text_x": 320,
                    "text_y": 1370
                }
            },
        },
        "video": {},
        "text_colors": {
            "Black": (235,50,35,255),
            "Color": (235,50,35,255),
            "Pastel": (235,50,35,255),
            "White": (235,50,35,255)
        }
    },
    "4": {
        "post": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 58,
                "center": True
            },
            "photo": {
                "top": 292,
                "left": 110,
                "rect_width": 860,
                "rect_height": 530
            },
            "text": {
                "name": {
                    "text_x": 224,
                    "text_y": 900
                },
                "phone_number": {
                    "text_x": 224,
                    "text_y": 970
                },
                "email": {
                    "text_x": 224,
                    "text_y": 1040
                },
                "username": {
                    "text_x": 224,
                    "text_y": 1110
                },
            }
        },
        "story": {
            "font": {
                "name": "TTChocolates-Regular.ttf",
                "size": 62,
                "center": True
            },
            "photo": {
                "top": 577,
                "left": 109,
                "rect_width": 862,
                "rect_height": 532
            },
            "text": {
                "name": {
                    "text_x": 160,
                    "text_y": 1225
                },
                "phone_number": {
                    "text_x": 160,
                    "text_y": 1315
                },
                "email": {
                    "text_x": 160,
                    "text_y": 1405
                },
                "username": {
                    "text_x": 160,
                    "text_y": 1495
                },
                
            },
        },
        "video": {},
        "text_colors": {
            "Black": (255,255,255,255),
            "Color": (255,255,255,255),
            "Pastel": (255,255,255,255),
            "White": (0,0,0,255)
        }
    }
}

def get_personal_photo(
    user_data: dict,
    style: str,
    post_id: str,
    obj: str
) -> str:
    """
    Функция персонализирует и высылает пользователю контент
    для поста по заданному стилю

    Пока это скорее заглушка
    """
    frame_path = f"content/templates/{post_id}/{style}/{obj}/6.png"
    out_file=f"test/{style}_{obj}_{post_id}.png"
    

    rules_obj = rules[f"{post_id}"][obj]
    font =  rules_obj["font"]
    text_colors = rules[f"{post_id}"]["text_colors"]

    overlay_photo(
        **rules_obj['photo'],
        frame_path=frame_path,
        photo_path=user_data['photo_source'],
        out_file=out_file
    )

    for text, params in rules_obj["text"].items():
        data = user_data.get(text)
        if not data:
            continue
        
        overlay_text(
            text=data,
            file_path=out_file,
            font=font["name"],
            font_size=font["size"],
            offset_x=font.get("offset_x", 0),
            center=font.get("center", False),
            upper=font.get("upper", False),
            color=text_colors[style],
            **params
        )

    return out_file

for post in [4]:
    for obj in ["story", "post"]:
        for style in ["White", "Pastel", "Color", "Black"]:

            get_personal_photo(
                {
                    "username": "@ionewa",
                    "phone_number": "+7 987 109 43 74",
                    "email": "daniil.0iwr@gmail.com",
                    "name": "Даниил Лобанов",
                    "photo_source": "photo.png"
                },
                style,
                post,
                obj
            )