-- ==============================================================
-- Predictive Sales Forecasting & Business Analytics System
-- Database Schema for MySQL
-- Database: sales_forecasting_db
-- ==============================================================

CREATE DATABASE IF NOT EXISTS `sales_forecasting_db` 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `sales_forecasting_db`;

-- 1. Products Table
CREATE TABLE IF NOT EXISTS `products` (
    `product_id` INT NOT NULL,
    `product_name` VARCHAR(255) NOT NULL,
    `category` VARCHAR(100) NOT NULL DEFAULT 'General',
    PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Sales Records Table
CREATE TABLE IF NOT EXISTS `sales` (
    `sale_id` INT NOT NULL AUTO_INCREMENT,
    `product_id` INT NOT NULL,
    `sale_date` DATE NOT NULL,
    `quantity` INT NOT NULL,
    `unit_price` DECIMAL(10, 2) NOT NULL,
    `region` VARCHAR(100) DEFAULT 'Default',
    PRIMARY KEY (`sale_id`),
    INDEX `idx_sale_date` (`sale_date`),
    INDEX `idx_product_id` (`product_id`),
    CONSTRAINT `fk_sales_product` 
        FOREIGN KEY (`product_id`) 
        REFERENCES `products` (`product_id`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Forecasts History Table
CREATE TABLE IF NOT EXISTS `forecasts` (
    `forecast_id` INT NOT NULL AUTO_INCREMENT,
    `period` VARCHAR(50) NOT NULL,
    `method` VARCHAR(50) NOT NULL,
    `predicted_value` DECIMAL(10, 2) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`forecast_id`),
    INDEX `idx_forecast_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
