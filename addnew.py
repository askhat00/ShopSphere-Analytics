import random
import time
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:dream@localhost:5433/SphereShop")

categories = [
    'cool_stuff','cama_mesa_banho', 'industria_comercio_e_negocios', 'esporte_lazer'
]

product_names = [
    'Gadget', 'Device', 'Tool', 'Book', 'Toy', 'Accessory', 'Appliance', 
    'Equipment', 'Item', 'Material'
]

while True:
    with engine.begin() as conn:  
        product_id = f"PROD_{random.randint(1000000, 9999999)}"
        category = random.choice(categories)
        product_name = random.choice(product_names) + f" {random.randint(1,100)}"
        weight_g = random.randint(10000, 50000)
        length_cm = round(random.uniform(10, 200), 2)
        height_cm = round(random.uniform(5, 100), 2)
        width_cm = round(random.uniform(5, 100), 2)

        conn.execute(text("""
            INSERT INTO products (
                product_id, product_category_name, product_name_length, product_description_length,
                product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm
            )
            VALUES (
                :pid, :cat, :name_len, :desc_len, :photos, :weight, :length, :height, :width
            )
        """), {
            "pid": product_id,
            "cat": category,
            "name_len": len(product_name),
            "desc_len": random.randint(20, 200),
            "photos": random.randint(1, 5),
            "weight": weight_g,
            "length": length_cm,
            "height": height_cm,
            "width": width_cm
        })

        print(f"✅ Added product {product_id} in category '{category}' with weight {weight_g}g")

    time.sleep(30)  
