COLORS = {
    "Новая": "gray",
    "В работе": "orange",
    "На проверке и доработке": "orange",
    "Ожидание": "red",
    "Ожидание разработки": "red",
    "Ожидает релиз, проверена": "green",
    "Отменена": "green",
    "Выполнена": "green",
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
