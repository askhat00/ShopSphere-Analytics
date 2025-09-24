-- 1. Количество заказов по статусу
SELECT order_status, COUNT(*) AS total_orders
FROM orders
GROUP BY order_status;

-- 2. Среднее время доставки (от покупки до получения)
SELECT AVG(order_delivered_customer_date - order_purchase_timestamp) AS avg_delivery_time
FROM orders
WHERE order_status = 'delivered';

-- 3. Сумма товаров по заказу
SELECT order_id, SUM(price + freight_value) AS order_total
FROM order_items
GROUP BY order_id
ORDER BY order_total DESC
LIMIT 10;

-- 4. 10 самых популярных категорий товаров
SELECT p.product_category_name, COUNT(*) AS total_items
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_items DESC
LIMIT 10;

-- 5. Средний рейтинг по категориям товаров
SELECT p.product_category_name, AVG(r.review_score) AS avg_rating
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN order_reviews r ON oi.order_id = r.order_id
GROUP BY p.product_category_name
ORDER BY avg_rating DESC;

-- 6. Топ-10 продавцов по объему продаж
SELECT oi.seller_id, SUM(oi.price) AS total_sales
FROM order_items oi
GROUP BY oi.seller_id
ORDER BY total_sales DESC
LIMIT 10;

-- 7. Количество клиентов по городам
SELECT customer_city, COUNT(DISTINCT customer_id) AS total_customers
FROM customers
GROUP BY customer_city
ORDER BY total_customers DESC
LIMIT 10;

-- 8. Средний рейтинг по городам
SELECT c.customer_city, AVG(r.review_score) AS avg_rating
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY c.customer_city
ORDER BY avg_rating DESC
LIMIT 10;

-- 9. Количество заказов по месяцам
SELECT DATE_TRUNC('month', order_purchase_timestamp) AS month, COUNT(*) AS total_orders
FROM orders
GROUP BY month
ORDER BY month;

-- 10. Средняя стоимость доставки (freight_value) по штатам продавцов
SELECT s.seller_state, AVG(oi.freight_value) AS avg_freight
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
GROUP BY s.seller_state
ORDER BY avg_freight DESC;
