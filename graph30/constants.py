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

PRIORITY = {1: "Низкий", 2: "Нормальный", 3: "Высокий", 4: "Срочный", 5: "Немедленный"}

OPTIONS = """
const options = {
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
      "levelSeparation": 200,
      "nodeSpacing": 32,
      "treeSpacing": 17,
      "sortMethod": "directed"
    }
  },
  "physics": {
    "hierarchicalRepulsion": {
      "centralGravity": 0,
      "nodeDistance": 190,
      "avoidOverlap": null
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  }
}
"""
