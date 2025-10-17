import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import psycopg2
from openpyxl import load_workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import PatternFill
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from local_settings import postgresql as settings
import numpy as np
import seaborn as sns


#  Настройки 

def get_engine (user, passwd, host, port, db) :
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    engine = create_engine(url, pool_size=50, echo=False)
    return engine

def get_engine_from_settings():
    keys = ['pguser', 'pgpasswd', 'pghost', 'pgport', 'pgdb']
    if not all(key in keys for key in settings.keys()):
        raise Exception('Bad config file')
    return get_engine (settings['pguser'],
                     settings['pgpasswd'],
                     settings['pghost'],
                     settings['pgport'],
                     settings['pgdb'])

def get_session ():
    engine = get_engine_from_settings()
    session = sessionmaker(bind=engine)()
    return session

session = get_session()
engine = get_engine_from_settings()

# --Графики--

os.makedirs("charts", exist_ok=True)


#  1. Круговая диаграмма 
sql = """
SELECT c.customer_state, COUNT(o.order_id) as num_orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY num_orders DESC
LIMIT 5
"""
df_pie = pd.read_sql_query(sql, engine)

plt.figure(figsize=(7,7))
plt.pie(df_pie["num_orders"], labels=df_pie["customer_state"], autopct="%1.1f%%", colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'], startangle=90)
plt.title("Распределение заказов по ТОП-5 штатам")
plt.savefig("charts/pie_chart.png")
print(f"[Pie] {len(df_pie)} строк → pie_chart.png (ТОП-5 штатов по заказам)")


#  2. Линейная 
sql_line = """
SELECT DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
       SUM(oi.price) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month
"""
df_line = pd.read_sql_query(sql_line, engine, parse_dates=["month"])

plt.figure(figsize=(10,6))
plt.plot(df_line["month"], df_line["revenue"], marker="o", color="blue", linewidth=2)

plt.title("Выручка по месяцам", fontsize=16)
plt.xlabel("Месяц", fontsize=14)
plt.ylabel("Выручка", fontsize=14)
plt.grid(True, alpha=0.3)

plt.savefig("charts/line_chart.png")
print(f"[Line] {len(df_line)} строк → line_chart.png (Выручка по месяцам)")


#  3. Горизонтальная столбчатая 
sql = """
SELECT s.seller_state, AVG(oi.price) as avg_price
FROM order_items oi
JOIN sellers s ON oi.seller_id = s.seller_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY s.seller_state
ORDER BY avg_price DESC
LIMIT 10
"""
df_barh = pd.read_sql_query(sql, engine)

plt.figure(figsize=(8,6))
plt.barh(df_barh["seller_state"], df_barh["avg_price"], color=plt.cm.viridis(np.linspace(0,1,10)))
plt.title("Средняя цена товаров по ТОП-10 штатам продавцов")
plt.xlabel("Средняя цена (BRL)")
plt.ylabel("Штат продавца")
plt.tight_layout()
plt.savefig("charts/horizontal_bar.png")
print(f"[BarH] {len(df_barh)} строк → horizontal_bar.png (Средняя цена по штатам продавцов)")


# Bar chart

sql = """
SELECT p.product_category_name, SUM(oi.price) as total_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_price DESC
limit 7
"""
df_bar = pd.read_sql_query(sql, engine)

plt.figure(figsize=(14,10))
plt.bar(df_bar["product_category_name"], df_bar["total_price"], color=['green', 'blue', 'red', 'yellow', 'orange', 'grey', 'purple', 'pink'])
plt.title("Топ 7 категории товаров по продажам")
plt.xlabel("Названия категорий")
plt.ylabel("Сумма продаж")
plt.tight_layout
plt.savefig("charts/bar.png")

#  4. Столбчатый

sql = """
SELECT DATE_TRUNC('month', o.order_purchase_timestamp) as month,
       c.customer_state,
       COUNT(DISTINCT o.order_id) as num_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY month, c.customer_state
ORDER BY month, num_orders DESC
"""
df_anim = pd.read_sql_query(sql, engine, parse_dates=["month"])

df_anim["month_str"] = df_anim["month"].dt.strftime("%Y-%m")

fig = px.bar(
    df_anim,
    x="customer_state",
    y="num_orders",
    color="customer_state",
    animation_frame="month_str",   
    range_y=[0, df_anim["num_orders"].max() * 1.2],
    title="Динамика количества заказов по месяцам",
    labels={"customer_state": "Штат", "num_orders": "Количество заказов"}
)

fig.show()


#  5. Гистограмма 
sql = """
SELECT EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) as delivery_days
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
    AND EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) <= 80
"""
df_hist = pd.read_sql_query(sql, engine)

plt.figure(figsize=(10,6))
plt.hist(df_hist["delivery_days"].dropna(), bins=30, alpha=0.7, color="purple", edgecolor="black")
plt.title("Распределение времени доставки заказов (в днях)")
plt.xlabel("Дней")
plt.ylabel("Количество заказов")
plt.savefig("charts/histogram.png")
print(f"[Histogram] {len(df_hist)} строк → histogram.png (Распределение времени доставки)")


#  6. Диаграмма рассеяния 
sql = """
SELECT oi.price, pay.payment_value
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN order_payments pay ON o.order_id = pay.order_id
WHERE oi.price > 0 AND pay.payment_value > 0
LIMIT 2000
"""
df_scatter = pd.read_sql_query(sql, engine)

plt.figure(figsize=(10,6))
plt.scatter(df_scatter["price"], df_scatter["payment_value"], alpha=0.5, c="red")
plt.title("Зависимость цены товара от суммы платежа")
plt.xlabel("Цена товара (BRL)")
plt.ylabel("Сумма платежа (BRL)")
plt.savefig("charts/scatter.png")
print(f"[Scatter] {len(df_scatter)} строк → scatter.png (Зависимость цены и платежа)")

