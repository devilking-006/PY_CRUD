SELECT * FROM public."Products";
SELECT p_id AS id, p_name FROM public."Products";
SELECT * FROM public."Products" ORDER BY price DESC;
SELECT * FROM public."Products" ORDER BY inventory DESC, price DESC;
INSERT INTO public."Products" (p_name, price, inventory) VALUES ('Bolts', 0.8, 1000);
INSERT INTO public."Products" (p_name, price, inventory) VALUES ('Monitor', 150, 500), ('Laptop', 20000, 100) RETURNING p_id, p_name, created_at;
UPDATE public."Products" SET price = 200, is_sale = true, inventory = 99 WHERE p_id = 18;
UPDATE public."Products" SET is_sale = true, inventory = 50 WHERE p_id = 1 RETURNING *;
SELECT * FROM public."Products" ORDER BY p_id;