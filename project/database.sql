DROP DATABASE IF EXISTS virtual_gallery;
CREATE DATABASE virtual_gallery CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE virtual_gallery;
-- Creats table User
CREATE TABLE user (
  userId       INT NOT NULL AUTO_INCREMENT,
  name         VARCHAR(50) NOT NULL,
  email        VARCHAR(50) NOT NULL,
  passwordHash VARCHAR(255) NOT NULL,
  role         ENUM('admin', 'artist', 'customer') NOT NULL,
  phone        VARCHAR(20),
  createdAt    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE (email),
  PRIMARY KEY (userId)
);
-- Creats table Artist
CREATE TABLE artist (
  artistId            INT NOT NULL AUTO_INCREMENT,
  userId              INT NOT NULL,
  name                VARCHAR(50) NOT NULL,
  bio                 VARCHAR(255),
  contactInfo         VARCHAR(255),
  isIndigenous        BOOLEAN DEFAULT FALSE,
  culturalAffiliation VARCHAR(50),
  UNIQUE (userId),
  FOREIGN KEY (userId) REFERENCES user(userId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  PRIMARY KEY (artistId)
);
-- Creats table Category
CREATE TABLE category (
  categoryId INT NOT NULL AUTO_INCREMENT,
  name       VARCHAR(80) NOT NULL,
  createdAt  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (name),
  PRIMARY KEY (categoryId)
);
-- Creats table Medium
CREATE TABLE medium (
  mediumId  INT NOT NULL AUTO_INCREMENT,
  name      VARCHAR(80) NOT NULL,
  createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (name),
  PRIMARY KEY (mediumId)
);
-- Creats table Artwork
CREATE TABLE artwork (
  artworkId         INT NOT NULL AUTO_INCREMENT,
  artistId          INT NOT NULL,
  mediumId          INT NULL,
  categoryId        INT NOT NULL,
  title             VARCHAR(150) NOT NULL,
  description       TEXT,
  imageUrl          VARCHAR(255),
  dimensions        VARCHAR(120),
  pricePerMonth     DECIMAL(10,2) NULL CHECK (pricePerMonth IS NULL OR pricePerMonth >= 0),
  purchasePrice     DECIMAL(10,2) NULL CHECK (purchasePrice  IS NULL OR purchasePrice  >= 0),
  availabilityStatus ENUM('available','leased','unavailable') NOT NULL DEFAULT 'available',
  region            VARCHAR(120),
  createdAt         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (artistId)   REFERENCES artist(artistId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (mediumId)   REFERENCES medium(mediumId)
    ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (categoryId) REFERENCES category(categoryId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  PRIMARY KEY (artworkId)
);
-- Creats table Cart
CREATE TABLE cart (
  cartId    INT NOT NULL AUTO_INCREMENT,
  userId    INT NOT NULL,
  createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (userId),
  FOREIGN KEY (userId) REFERENCES user(userId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  PRIMARY KEY (cartId)
);
-- Creats table Cartitem
CREATE TABLE cartitem (
  cartItemId    INT NOT NULL AUTO_INCREMENT,
  cartId        INT NOT NULL,
  artworkId     INT NOT NULL,
  quantity      INT NOT NULL CHECK (quantity > 0),
  purchaseType  ENUM('purchase','lease') NOT NULL,
  leaseDuration INT NULL,
  price         DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  createdAt     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (cartId)    REFERENCES cart(cartId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (artworkId) REFERENCES artwork(artworkId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  PRIMARY KEY (cartItemId)
);
-- Creats table Order
CREATE TABLE `order` (
  orderId       INT NOT NULL AUTO_INCREMENT,
  userId        INT NOT NULL,
  totalAmount   DECIMAL(10,2) NOT NULL DEFAULT 0,
  orderDate     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status        ENUM('cart','pending','paid','cancelled','completed') NOT NULL DEFAULT 'cart',
  isEcoDelivery BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (userId) REFERENCES user(userId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  PRIMARY KEY (orderId)
);
-- Creats table Orderitem. This is not in the data model and is newly added.
CREATE TABLE orderitem (
  orderItemId   INT NOT NULL AUTO_INCREMENT,
  orderId       INT NOT NULL,
  artworkId     INT NOT NULL,
  quantity      INT NOT NULL CHECK (quantity > 0),
  unitPrice     DECIMAL(10,2) NOT NULL CHECK (unitPrice >= 0),
  lineTotal     DECIMAL(10,2) NOT NULL CHECK (lineTotal >= 0),
  purchaseType  ENUM('purchase','lease') NOT NULL,
  leaseDuration INT NULL,
  FOREIGN KEY (orderId)   REFERENCES `order`(orderId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (artworkId) REFERENCES artwork(artworkId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  PRIMARY KEY (orderItemId)
);
-- Creats table Payment
CREATE TABLE payment (
  paymentId INT NOT NULL AUTO_INCREMENT,
  orderId   INT NOT NULL,
  amount    DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
  paymentAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  method    ENUM('card', 'cash', 'demo', 'paypal') NOT NULL DEFAULT 'demo',
  FOREIGN KEY (orderId) REFERENCES `order`(orderId)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  PRIMARY KEY (paymentId)
);

-- Add extra artist details for portfolio page
ALTER TABLE artist
  ADD COLUMN imageUrl        VARCHAR(255)  NULL,
  ADD COLUMN specialty       VARCHAR(120)  NULL,
  -- ADD COLUMN bio             TEXT          NULL,
  ADD COLUMN medium          VARCHAR(120)  NULL,
  ADD COLUMN style           VARCHAR(120)  NULL,
  ADD COLUMN experienceYears INT           NULL,
  ADD COLUMN location        VARCHAR(120)  NULL;
 

-- Inserts sample users: 2 admins, 3 artists, and 2 customers
INSERT INTO user (userId, name, email, passwordHash, role, phone, createdAt, updatedAt) VALUES
(1, 'Lauren M', 'lauren@example.com',
 'scrypt:32768:8:1$I1hkAzlpApX5LcPR$2b739bdc7dacae0a1864b628c07729caf13825fd999a046ee87a7c34b7f92f7ca7b735500dcaa9b383cc0ef06a708e8547474df00060e5f51d43c876329d00eb',
 'customer', '0400 111 111', '2025-09-09 09:00:00', '2025-09-09 09:00:00'), -- password: pass1

(2, 'Tanya Baltwyx', 'tanya.painter@example.com',
 'scrypt:32768:8:1$gcEgeSI0W5481bqZ$2fced698036341a3942fabbd756a583efec1ac408e433d09650989f9183f6e47538be61c31addaa028d02d6ce5c011f631a39439328e8ffedbb6b8fcd1ac2531',
 'artist', '0400 222 222', '2025-09-09 09:00:00', '2025-09-09 09:00:00'), -- password: pass2

(3, 'Martha Matthews', 'brunswick.gallery@example.com',
 'scrypt:32768:8:1$9srS05GTaJzgQwgR$9c9169693b8a30b9009ed5e442937db10fcc388f5546b43162090ca7f6d2c3bc7274ac1084ebe9c49ab1d44f2c2370192631712a96bfbccd8dfb725f4a17df5d',
 'artist', '0400 333 333', '2025-09-09 09:00:00', '2025-09-09 09:00:00'), -- password: pass3

(4, 'Bob Buyer', 'bob.buyer@example.com',
 'scrypt:32768:8:1$vgJCGYydYawPYYPn$5d18719292d3be10b269bf2483b0b779c52212c428cb9d51f903aeda57164b107139fe1877ca3a1556f251fb474c33d5f978905a7508e5262ce8734b7695a6eb',
 'customer', '0400 444 444', '2025-09-09 09:00:00', '2025-09-09 09:00:00'), -- password: pass4

(5, 'Site Admin', 'admin@example.com',
 'scrypt:32768:8:1$9E7D9poUwE9YvuFm$80f83f7ee833331e60bdea40c4e2578ede709cb5ecc63aae8cde97b37a2875c07eef414693bbee95f02df54ad31f9670d63adcf5a5485e4fbbbf6867c317fa5a',
 'admin', '0400 555 555', '2025-09-09 09:00:00', '2025-09-09 09:00:00'), -- password: admin1

(6, 'Admin Two', 'admin2@example.com',
 'scrypt:32768:8:1$laUy03f0Uh4YN4sy$dad8574cec45660fef7f8bd147f6999d6f9a7b00be998981b7d8cef817883034efe0e8a0094f6a7bf743d867921748c5e856dbca3104c0c35c91984ea3a857b2',
 'admin', '0400 666 666', NOW(), NOW()), -- password: admin2

(7, 'Ava Alt', 'ava.alt@art.com',
 'scrypt:32768:8:1$sIrGwRYAGDy8k42I$b9fd3e33dee680053f1ff9e298263816ee020ff2c401fdc2bdf1197deba84b562ee56e846301bd73ff25b14fcd9a4489e88685626e4b3771008e2d8b65a94a90',
 'artist', '0400 777 777', NOW(), NOW()); -- password: pass7

-- Reset AUTO_INCREMENT for user table to next available ID
ALTER TABLE user AUTO_INCREMENT = 8;
-- Inserts sample artists linked to their user accounts (1:1 relationship)
INSERT INTO artist (artistId, userId, name, bio, contactInfo, isIndigenous, culturalAffiliation) VALUES
(1, 2, 'Tanya Baltwyx',   'Oil on canvas landscapes',        'tanya@art.com',           FALSE, NULL),
(2, 3, 'Martha Matthews', 'Contemporary Australian artists', 'contact@brunswick.gallery', FALSE, NULL),
(3, 7, 'Petey Bower',     'Studies in light',                'petey.bower@art.com',       FALSE, NULL);
-- Updates AUTO_INCREMENT for artist table. The same applies below
ALTER TABLE artist AUTO_INCREMENT = 4;

-- Insert portfolio info for each artist

UPDATE artist
SET imageUrl='img/artist1.png',
    specialty='Landscape painter',
    bio='Australian landscape painter focusing on urban rain scenes and natural light.',
    medium='Oil on canvas',
    style='Impressionism',
    experienceYears=8,
    location='Brisbane, QLD'
WHERE artistId = 1;

UPDATE artist
SET imageUrl='img/artist2.png',
    specialty='Nature & trail art',
    bio='Works inspired by Australian bushland and hiking trails.',
    medium='Acrylic',
    style='Contemporary',
    experienceYears=6,
    location='Sydney, NSW'
WHERE artistId = 2;

UPDATE artist
SET imageUrl='img/artist3.png',
    specialty='Sculpture & stone forms',
    bio='Creates contemporary sculptures and minimalist stone forms.',
    medium='Stone / Mixed media',
    style='Minimalism',
    experienceYears=5,
    location='Melbourne, VIC'
WHERE artistId = 3;





-- Inserts sample mediums used for artworks
INSERT INTO medium (mediumId, name, createdAt) VALUES
(1, 'Oil on Canvas', '2025-09-09 09:00:00'),
(2, 'Acrylic',       '2025-09-09 09:00:00'),
(3, 'Photograph',    '2025-09-09 09:00:00'),
(4, 'Stone',         '2025-09-09 09:00:00'),
(5, 'Digital Ink',   '2025-09-09 09:00:00');
ALTER TABLE medium AUTO_INCREMENT = 6;


INSERT INTO category (categoryId, name, createdAt) VALUES
(1, 'Landscape',   '2025-09-09 09:00:00'),
(2, 'Abstract',    '2025-09-09 09:00:00'),
(3, 'Photography', '2025-09-09 09:00:00'),
(4, 'Sculpture',   '2025-09-09 09:00:00'),
(5, 'Illustration','2025-09-09 09:00:00');

ALTER TABLE category AUTO_INCREMENT = 6;

-- Inserts sample artwork items (15 total, across multiple categories)
INSERT INTO artwork (artworkId, artistId, mediumId, categoryId, title, description, imageUrl, dimensions, pricePerMonth, purchasePrice, availabilityStatus, region, createdAt)
VALUES
(1, 1, 1, 1, 'Sun Yard',             'Warm twilight scene',          'img/Sun Yard.png',            '90x60',      120,  NULL, 'available', 'QLD', '2025-09-09 09:00:00'),
(2, 2, 2, 2, 'Woven Sky',            'Abstract city geometry',       'img/Woven Sky.png',            '80x80x2',    500, 3000, 'available', 'QLD', '2025-09-09 09:00:00'),
(3, 3, 4, 4, 'Stone Form',           'Minimal sculpture',            'img/Stone Form.png',           '50x40',      120,  800, 'available', 'QLD', '2025-09-09 09:00:00'),
(4, 2, 4, 4, 'Desert Bloom',         'An organic stone sculpture',   'img/Desert Bloom.png',           '25x40x25',   900, 7000, 'available', 'QLD', '2025-09-09 09:00:00'),
(5, 1, 3, 3, 'Night Bridge',         'Long exposure photograph',     'img/Night Bridge.png',            '60x40',       40,  600, 'available', 'QLD', '2025-09-09 09:00:00'),
(6, 1, 1, 1, 'Morning Mist',         'Soft fog over valley',         'img/Morning Mist.png',           '80x60',      140,  NULL, 'available', 'QLD', '2025-09-09 09:00:00'),
(7, 1, 2, 2, 'Chromatic Echoes',     'Bold acrylic color fields',    'img/Chromatic Echoes.png',            '80x80',      420, 2500, 'available', 'QLD', '2025-09-09 09:00:00'),
(8, 2, 1, 1, 'Coastal Dusk',         'Shoreline at dusk',            'img/Coastal Dusk.png',            '100x60',     180,  NULL, 'available', 'QLD', '2025-09-09 09:00:00'),
(9, 2, 2, 2, 'Refraction',           'Geometric abstractions',       'img/Refraction.png',            '60x60',      300, 1800, 'available', 'QLD', '2025-09-09 09:00:00'),
(10, 2, 4, 4, 'Granite Bloom',       'Stone form exploration',       'img/Granite Bloom.png',            '30x30x40',   800, 6200, 'available', 'QLD', '2025-09-09 09:00:00'),
(11, 3, 5, 5, 'Stellar Tale',        'Dreamlike creature in stars',  'img/Stellar Tale.png',            '50x50',      110,  700, 'available', 'QLD', '2025-09-09 09:00:00'),
(12, 3, 3, 3, 'City at Blue Hour',   'Blue hour skyline',            'img/City at Blue Hour.png',             '60x40',       55,  650, 'available', 'QLD', '2025-09-09 09:00:00'),
(13, 1, 3, 3, 'Rainy Street',        'Street reflections',           'img/Rainy Street.png',            '60x40',       50,  620, 'available', 'QLD', '2025-09-09 09:00:00'),
(14, 2, 1, 1, 'Bushland Path',       'Path through bushland',        'img/Bushland Path.png',            '90x60',      160,  NULL, 'available', 'QLD', '2025-09-09 09:00:00'),
(15, 3, 5, 5, 'Wombat Whimsy',       'Playful illustration',         'img/Wombat Whimsy.png',            '45x35',      115,  680, 'available', 'QLD', '2025-09-09 09:00:00');
-- Dynamically updates AUTO_INCREMENT for artwork table to next available ID
SET @next_art_id := (SELECT COALESCE(MAX(artworkId),0)+1 FROM artwork);
SET @sql := CONCAT('ALTER TABLE artwork AUTO_INCREMENT = ', @next_art_id);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Inserts sample carts for 5 users
INSERT INTO cart (cartId, userId, createdAt) VALUES
(1, 1, '2025-09-09 09:00:00'),
(2, 2, '2025-09-09 09:00:00'),
(3, 3, '2025-09-09 09:00:00'),
(4, 4, '2025-09-09 09:00:00'),
(5, 5, '2025-09-09 09:00:00');

ALTER TABLE cart AUTO_INCREMENT = 6;

-- Inserts items into each user's cart to demonstrate purchase/lease options
INSERT INTO cartitem (cartItemId, cartId, artworkId, quantity, purchaseType, leaseDuration, price, createdAt) VALUES
(1, 1, 1, 1, 'lease',     2, 300.00, '2025-09-09 09:00:00'),
(2, 2, 2, 1, 'purchase', NULL, 3000.00, '2025-09-09 09:00:00'),
(3, 3, 3, 1, 'lease',     1, 120.00, '2025-09-09 09:00:00'),
(4, 4, 4, 1, 'lease',     1, 900.00, '2025-09-09 09:00:00'),
(5, 5, 5, 1, 'purchase', NULL, 600.00, '2025-09-09 09:00:00');

ALTER TABLE cartitem AUTO_INCREMENT = 6;

-- Creates first order record for a completed purchase (Customer 1)
INSERT INTO `order` (orderId, userId, totalAmount, orderDate, status, isEcoDelivery)
VALUES (1, 1, 0, '2025-09-09 09:00:00', 'pending', FALSE);
INSERT INTO orderitem (orderItemId, orderId, artworkId, quantity, unitPrice, lineTotal, purchaseType, leaseDuration)
VALUES (1, 1, 5, 1, 600.00, 600.00, 'purchase', NULL);
UPDATE `order` SET totalAmount = (SELECT SUM(lineTotal) FROM orderitem WHERE orderId=1) WHERE orderId=1;
INSERT INTO payment (paymentId, orderId, amount, paymentAt, method) VALUES (1, 1, 600.00, '2025-09-09 09:00:00', 'card');
UPDATE `order` SET status='completed' WHERE orderId=1;


-- Creates second order record: a lease transaction (Customer 4)
INSERT INTO `order` (orderId, userId, totalAmount, orderDate, status, isEcoDelivery)
VALUES (2, 4, 0, '2025-09-09 09:00:00', 'pending', TRUE);
INSERT INTO orderitem (orderItemId, orderId, artworkId, quantity, unitPrice, lineTotal, purchaseType, leaseDuration)
VALUES (2, 2, 4, 1, 900.00, 900.00, 'lease', 1);
UPDATE `order` SET totalAmount = (SELECT SUM(lineTotal) FROM orderitem WHERE orderId=2) WHERE orderId=2;
INSERT INTO payment (paymentId, orderId, amount, paymentAt, method) VALUES (2, 2, 900.00, '2025-09-09 09:00:00', 'card');
UPDATE `order` SET status='completed' WHERE orderId=2;



-- Creates third order: studio session booking using PayPal
INSERT INTO `order` (orderId, userId, totalAmount, orderDate, status, isEcoDelivery)
VALUES (3, 1, 0, '2025-09-09 09:00:00', 'pending', FALSE);
INSERT INTO orderitem (orderItemId, orderId, artworkId, quantity, unitPrice, lineTotal, purchaseType, leaseDuration)
VALUES (3, 3, 1, 1, 200.00, 400.00, 'lease', 2);
UPDATE `order` SET totalAmount = (SELECT SUM(lineTotal) FROM orderitem WHERE orderId=3) WHERE orderId=3;
INSERT INTO payment (paymentId, orderId, amount, paymentAt, method) VALUES (3, 3, 400.00, '2025-09-09 09:00:00', 'paypal');
UPDATE `order` SET status='completed' WHERE orderId=3;

-- Adds additional test orders to show variety in statuses
INSERT INTO `order` (orderId, userId, totalAmount, orderDate, status, isEcoDelivery)
VALUES 
(4, 2, 800.00, '2025-09-09 09:00:00', 'paid', TRUE),
(5, 1, 120.00, '2025-09-09 09:00:00', 'cancelled', FALSE);
INSERT INTO payment (paymentId, orderId, amount, paymentAt, method)
VALUES 
(4, 4, 800.00, '2025-09-09 09:00:00', 'card'),
(5, 5, 120.00, '2025-09-09 09:00:00', 'card');



-- Dynamically resets AUTO_INCREMENT for order, orderitem, and payment tables
SET @next_order_id := (SELECT COALESCE(MAX(orderId),0)+1 FROM `order`);
SET @sql2 := CONCAT('ALTER TABLE `order` AUTO_INCREMENT = ', @next_order_id);
PREPARE s2 FROM @sql2; EXECUTE s2; DEALLOCATE PREPARE s2;

SET @next_orderitem_id := (SELECT COALESCE(MAX(orderItemId),0)+1 FROM orderitem);
SET @sql3 := CONCAT('ALTER TABLE orderitem AUTO_INCREMENT = ', @next_orderitem_id);
PREPARE s3 FROM @sql3; EXECUTE s3; DEALLOCATE PREPARE s3;

SET @next_payment_id := (SELECT COALESCE(MAX(paymentId),0)+1 FROM payment);
SET @sql4 := CONCAT('ALTER TABLE payment AUTO_INCREMENT = ', @next_payment_id);
PREPARE s4 FROM @sql4; EXECUTE s4; DEALLOCATE PREPARE s4;