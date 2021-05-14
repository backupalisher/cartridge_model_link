import db


def get_all_analog_models():
    return db.i_request("SELECT id, brand_id, model FROM supplies_analog_model")


def select_model(brand_id, model_name):
    q = db.i_request(f"SELECT * FROM models WHERE brand_id = {brand_id} AND LOWER(name) SIMILAR TO LOWER('%{model_name}%')")
    return q


def get_brand_name(brand_id):
    q = db.i_request(f"SELECT name FROM brands WHERE id = {brand_id}")
    return q[0][0]


def update_supplies_analog_model(cart_id):
    db.i_request(f"UPDATE supplies_analog_model SET linked = TRUE WHERE id = {cart_id}")


def link_model_supplies(model_id, supplies_id):
    db.i_request(f"WITH s as (SELECT 1 FROM link_model_supplies "
                 f"WHERE model_id = {model_id} AND supplies_id = {supplies_id}), i as "
                 f"(INSERT INTO link_model_supplies (model_id, supplies_id) "
                 f"SELECT {model_id}, {supplies_id} "
                 f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING 0) SELECT * FROM i UNION ALL SELECT * FROM s")


# def get_link_supplies_model_analog(supplies_analog_model_id):
#     q = db.i_request(f"SELECT supplies_analog_model_id FROM link_supplies_model_analog "
#                      f"WHERE supplies_analog_model_id = {supplies_analog_model_id}")
#     return q


def get_link_supplies_model_analog(supplies_analog_model_id):
    q = db.i_request(f"SELECT id FROM partcodes "
                     f"WHERE supplies_analog_model_id = {supplies_analog_model_id}")
    return q


def get_all_supplis_id():
    q = db.i_request(f"""SELECT id FROM partcodes WHERE supplies is TRUE""")
    return q


def get_sm_link(s_id):
    q = db.i_request(f"""SELECT * FROM link_supplies_model_analog WHERE partcode_id = {s_id}""")
    return q


def get_all_models():
    q = db.i_request(f"""SELECT id, brand_id, name FROM models""")
    return q
