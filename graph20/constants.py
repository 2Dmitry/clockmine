COLORS = {
    "Новая": "red",
    "В работе": "yellow",
    "На проверке и доработке": "orange",
    "Ожидание": "brown",
    "Ожидание разработки": "brown",
    "Ожидает релиз, проверена": "green",
    "Отменена": "gray",
    "Выполнена": "gray",
}

PRIORITY = {
    1: "Низкий",
    2: "Нормальный",
    3: "Высокий",
    4: "Срочный",
    5: "Немедленный",
}

OPTIONS = """
    const options = {
        "nodes": {
            "borderWidthSelected": null,
            "size": null
        },
        "edges": {
            "arrows": {
            "to": {
                "enabled": true
            }
            },
            "color": {
            "inherit": true
            },
            "selfReferenceSize": null,
            "selfReference": {
            "angle": 0.7853981633974483
            },
            "smooth": false
        },
        "layout": {
            "hierarchical": {
            "enabled": true,
            "levelSeparation": 300,
            "nodeSpacing": 30,
            "treeSpacing": 30,
            "sortMethod": "directed"
            }
        },
        "interaction": {
            "zoomSpeed": 0.5
        },
        "physics": {
            "hierarchicalRepulsion": {
            "centralGravity": 0,
            "springLength": 60,
            "nodeDistance": 200,
            "avoidOverlap": null
            },
            "minVelocity": 0.75,
            "solver": "hierarchicalRepulsion",
            "timestep": 1
        }
    }
"""
