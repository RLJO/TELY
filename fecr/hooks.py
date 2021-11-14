from .models.tool import Tool


def post_init_hook(cr, registry):
    Tool.load_csv(None, "data/res.country.neighborhood.csv", cr)
