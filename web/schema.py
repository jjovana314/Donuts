schema_donut = {
	"type": "object",
	"properties": {
		"id": {
			"type": "string", "minLength": 4, "maxLength": 4
		},
		"type": {
			"type": "string", "minLength": 3, "maxLength": 20
		},
		"name": {
			"type": "string", "minLength": 3, "maxLength": 20
		},
		"ppu": {
			"type": "number", "minimum": 0.1
		},
		"batters": {
			"type": "object",
			"properties": {
				"batter": {
					"type": "array",
					"items": {
						"type": "object",
						"properties": {
							"id": {
								"type": "string", "minLength": 4, "maxLength": 4
							},
							"type": {
								"type": "string", "minLength": 3, "maxLength": 50
							}
						},
                        "required": ["id", "type"],
						"uniqueItems": True
					}
				}
			}
		},
		"topping": {
			"type": "array",
			"items": {
				"type": "object",
				"properties": {
					"id": {
						"type": "string", "minLength": 4, "maxLength": 4
					},
					"type": {
						"type": "string", "minLength": 3, "maxLength": 50
					}
				},
                "required": ["id", "type"],
                "uniqueItems": True,
			}
		}
	},
    "required": ["id", "type", "name", "ppu", "batters", "topping"],
	"additionalItems": False
}
