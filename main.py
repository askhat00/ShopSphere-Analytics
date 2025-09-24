import psycopg2
import pandas as pd

try:
    conn = psycopg2.connect(
        dbname="SphereShop",   
        user="postgres",      
        password="your_pass", 
        host="localhost",     
        port=5433           
    )

    cur = conn.cursor()

    queries = {
        "orders_by_status": """
            SELECT order_status, COUNT(*) AS total_orders
            FROM orders
            GROUP BY order_status;
        """,
        "top_sellers": """
            SELECT s.seller_id, AVG(r.review_score) AS avg_review
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            JOIN order_reviews r ON oi.order_id = r.order_id
            GROUP BY s.seller_id
            ORDER BY avg_review DESC
            LIMIT 10;
        """,
        "products_count": """
            SELECT p.product_category_name, COUNT(*) AS total_items
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_category_name
            ORDER BY total_items DESC
            LIMIT 10;
        """
    }

    for name, query in queries.items():
        print(f"\n==== {name} ====")
        df = pd.read_sql(query, conn)   
        print(df)
        df.to_csv(f"{name}.csv", index=False)

except Exception as error:
    print(error)
finally: 
    if cur is not None:
            cur.close()
    if conn is not None:
            conn.close()

