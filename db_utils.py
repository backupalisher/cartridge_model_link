import db


def get_all_analog_models():
    return db.i_request("SELECT * FROM cartridge_analog_model WHERE linked IS NULL")


def select_model(brand_id, model_name):
    q = db.i_request(f"SELECT * FROM models WHERE brand_id = {brand_id} AND name SIMILAR TO '%{model_name}%'")
    return q


def get_brand_name(brand_id):
    q = db.i_request(f"SELECT name FROM brands WHERE id = {brand_id}")
    return q[0][0]


def update_model_image(cart_id, model_id):
    db.i_request(f"UPDATE cartridge_analog_model SET linked = {model_id} WHERE id = {cart_id}")


def link_model_cartridge(model_id, cartridge_id):
    db.i_request(f"WITH s as (SELECT 1 FROM link_model_cartridge "
                 f"WHERE model_id = {model_id} AND cartridge_id = {cartridge_id}), i as "
                 f"(INSERT INTO link_model_cartridge (model_id, cartridge_id) "
                 f"SELECT {model_id}, {cartridge_id} "
                 f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING 0) SELECT * FROM i UNION ALL SELECT * FROM s")


def get_link_cartridge_model_analog(cartridge_analog_model_id):
    q = db.i_request(f"SELECT cartridge_id FROM link_cartridge_model_analog "
                     f"WHERE cartrindge_analog_model_id = {cartridge_analog_model_id}")
    return q
