import db


def test():
    q = db.i_request(f"SELECT sd.name as detail_name, sd.name_ru as detail_name_ru, p.code as partcode, "
                     f"mu.name as module_name, mo.name as model_name, mo.main_image model_image, "
                     f"p.images partcode_image FROM details d "
                     f"LEFT JOIN partcodes p ON d.partcode_id = p.id "
                     f"LEFT JOIN spr_details sd ON sd.id = d.spr_detail_id "
                     f"LEFT JOIN spr_modules mu ON d.module_id=mu.id LEFT JOIN models mo ON d.model_id=mo.id "
                     f"WHERE sd.name %> 'cover'")
    return q
