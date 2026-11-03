-- ==============================================================
-- Sample Initial Data for MySQL Database
-- Database: sales_forecasting_db
-- ==============================================================

USE `sales_forecasting_db`;

-- Insert Initial Products
INSERT INTO `products` (`product_id`, `product_name`, `category`) VALUES
(101, 'Mechanical Keyboard', 'Computer Accessories'),
(102, 'Wireless Mouse', 'Computer Accessories'),
(103, 'USB-C Multiport Hub', 'Computer Accessories'),
(104, '27-inch 4K Monitor', 'Electronics'),
(105, 'HD Pro Webcam', 'Electronics'),
(106, 'Ergonomic Office Chair', 'Furniture'),
(107, 'Adjustable Standing Desk', 'Furniture'),
(108, 'Noise Cancelling Headphones', 'Audio'),
(109, 'Portable Bluetooth Speaker', 'Audio'),
(110, 'Laser Multifunction Printer', 'Office Supplies'),
(111, 'Premium Paper Ream (Pack of 5)', 'Office Supplies'),
(112, 'Laptop Cooling Pad', 'Computer Accessories')
ON DUPLICATE KEY UPDATE `product_name` = VALUES(`product_name`), `category` = VALUES(`category`);

-- Insert Sample Initial Sales
INSERT INTO `sales` (`product_id`, `sale_date`, `quantity`, `unit_price`, `region`) VALUES
(102, '2024-01-01', 6, 25.00, 'South'),
(104, '2024-01-01', 2, 320.00, 'North'),
(111, '2024-01-01', 10, 24.00, 'North'),
(107, '2024-01-02', 1, 340.00, 'North'),
(102, '2024-01-02', 5, 25.00, 'Central'),
(110, '2024-01-02', 1, 195.00, 'Central'),
(112, '2024-01-03', 10, 35.00, 'West'),
(108, '2024-01-04', 5, 175.00, 'East'),
(103, '2024-01-05', 8, 45.00, 'East'),
(106, '2024-01-06', 2, 210.00, 'West'),
(101, '2024-01-07', 4, 85.00, 'North'),
(109, '2024-01-08', 3, 55.00, 'South');
