from typing import Optional, List, Dict, Any, Tuple
from flask import current_app
from . import mysql
from werkzeug.security import generate_password_hash, check_password_hash

#  Utility
def _dict_cursor():
    return mysql.connection.cursor()

def _commit():
    mysql.connection.commit()

def _rollback():
    mysql.connection.rollback()

#  Users 
class User:
    """
    Table: `user`
    Columns: userId, name, email, passwordHash, role, phone, createdAt, updatedAt
    """

    @staticmethod
    def create(name: str, email: str, password: str, role: str = "customer", phone: Optional[str] = None) -> int:
        hashed = generate_password_hash(password)
        q = """
        INSERT INTO `user` (name, email, passwordHash, role, phone)
        VALUES (%s, %s, %s, %s, %s)
        """
        cur = _dict_cursor()
        try:
            cur.execute(q, (name, email.lower().strip(), hashed, role, phone))
            _commit()
            return cur.lastrowid
        except Exception as e:
            _rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        cur = _dict_cursor()
        try:
            cur.execute("SELECT * FROM `user` WHERE email=%s", (email.lower().strip(),))
            return cur.fetchone()
        finally:
            cur.close()

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        cur = _dict_cursor()
        try:
            cur.execute("SELECT * FROM `user` WHERE userId=%s", (user_id,))
            return cur.fetchone()
        finally:
            cur.close()

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        return check_password_hash(stored_hash, password)

# Artists 
class Artist:
    @staticmethod
    def create(userId: int, name: str, bio: Optional[str] = None, contactInfo: Optional[str] = None,
               isIndigenous: bool = False, culturalAffiliation: Optional[str] = None) -> int:
        q = """
        INSERT INTO artist (userId, name, bio, contactInfo, isIndigenous, culturalAffiliation)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur = _dict_cursor()
        try:
            cur.execute(q, (userId, name, bio, contactInfo, isIndigenous, culturalAffiliation))
            _commit()
            return cur.lastrowid
        except Exception as e:
            _rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def get_by_user(userId: int) -> Optional[Dict[str, Any]]:
        cur = _dict_cursor()
        try:
            cur.execute("SELECT * FROM artist WHERE userId=%s", (userId,))
            return cur.fetchone()
        finally:
            cur.close()
            
    @staticmethod
    def count_all() -> int:
        cur = _dict_cursor()
        try:
            
            cur.execute("SELECT COUNT(artistId) AS count FROM artist")
            result = cur.fetchone()
            return result['count'] if result else 0
        finally:
            cur.close()

    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        cur = _dict_cursor()
        try:
            cur.execute("SELECT artistId, name FROM artist ORDER BY name")
            return cur.fetchall()
        finally:
            cur.close()

#Category 
class Category:
    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        cur = _dict_cursor()
        try:
            cur.execute("SELECT * FROM category ORDER BY name")
            return cur.fetchall()
        finally:
            cur.close()

# Medium 
class Medium:
    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        cur = _dict_cursor()
        try:
            cur.execute("SELECT * FROM medium ORDER BY name")
            return cur.fetchall()
        finally:
            cur.close()

#Artwork 
class Artwork:
    @staticmethod
    def list_available(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        q = """
        SELECT a.*, ar.name AS artistName, c.name AS categoryName, m.name AS mediumName
        FROM artwork a
        JOIN artist ar ON a.artistId = ar.artistId
        JOIN category c ON a.categoryId = c.categoryId
        LEFT JOIN medium m ON a.mediumId = m.mediumId
        WHERE a.availabilityStatus = 'available'
        ORDER BY a.createdAt DESC
        LIMIT %s OFFSET %s
        """
        cur = _dict_cursor()
        try:
            cur.execute(q, (limit, offset))
            return cur.fetchall()
        finally:
            cur.close()

    @staticmethod
    def get(artworkId: int) -> Optional[Dict[str, Any]]:
        q = """
        SELECT a.*, ar.name AS artistName, c.name AS categoryName, m.name AS mediumName
        FROM artwork a
        JOIN artist ar ON a.artistId = ar.artistId
        JOIN category c ON a.categoryId = c.categoryId
        LEFT JOIN medium m ON a.mediumId = m.mediumId
        WHERE a.artworkId = %s
        """
        cur = _dict_cursor()
        try:
            cur.execute(q, (artworkId,))
            return cur.fetchone()
        finally:
            cur.close()

#Cart & CartItem 
class Cart:
    @staticmethod
    def get_or_create(userId: int) -> int:
        cur = _dict_cursor()
        try:
            cur.execute("SELECT cartId FROM cart WHERE userId=%s", (userId,))
            row = cur.fetchone()
            if row:
                return row["cartId"]
            cur.execute("INSERT INTO cart (userId) VALUES (%s)", (userId,))
            _commit()
            return cur.lastrowid
        except Exception as e:
            _rollback()
            raise e
        finally:
            cur.close()

class CartItem:
    @staticmethod
    def add(cartId: int, artworkId: int, quantity: int, purchaseType: str,
            price: float, leaseDuration: Optional[int] = None) -> int:
        q = """
        INSERT INTO cartitem (cartId, artworkId, quantity, purchaseType, leaseDuration, price)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur = _dict_cursor()
        try:
            cur.execute(q, (cartId, artworkId, quantity, purchaseType, leaseDuration, price))
            _commit()
            return cur.lastrowid
        except Exception as e:
            _rollback()
            raise e
        finally:
            cur.close()

#Orders, OrderItems, Payments 
class Order:
    @staticmethod
    def create(userId: int, status: str = "pending", isEcoDelivery: bool = False) -> int:
        cur = _dict_cursor()
        try:
            cur.execute("INSERT INTO `order` (userId, totalAmount, status, isEcoDelivery) VALUES (%s, 0, %s, %s)",
                        (userId, status, isEcoDelivery))
            _commit()
            return cur.lastrowid
        except Exception as e:
            _rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def update_total(orderId: int):
        cur = _dict_cursor()
        try:
            cur.execute("UPDATE `order` SET totalAmount=(SELECT COALESCE(SUM(lineTotal),0) FROM orderitem WHERE orderId=%s) WHERE orderId=%s",
                        (orderId, orderId))
            _commit()
        except Exception as e:
            _rollback()
            raise e
        finally:
            cur.close()
    
    @staticmethod
    def count_all() -> int:

        q = "SELECT COUNT(orderId) AS count FROM `order` WHERE status != 'cart'"
        cur = _dict_cursor()
        try:
            cur.execute(q)
            result = cur.fetchone()
            return result['count'] if result else 0
        finally:
            cur.close()

    @staticmethod
    def list_submitted() -> List[Dict[str, Any]]:
        
        q = """
        SELECT orderId, userId, totalAmount, status, orderDate, isEcoDelivery
        FROM `order` 
        WHERE status != 'cart' 
        ORDER BY orderDate DESC
        """
        cur = _dict_cursor()
        try:
            cur.execute(q)
            return cur.fetchall()
        finally:
            cur.close()

class OrderItem:
    @staticmethod
    def add(orderId: int, artworkId: int, quantity: int, unitPrice: float,
            purchaseType: str, leaseDuration: Optional[int]) -> int:
        lineTotal = unitPrice * quantity
        q = """
        INSERT INTO orderitem (orderId, artworkId, quantity, unitPrice, lineTotal, purchaseType, leaseDuration)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur = _dict_cursor()
        try:
            cur.execute(q, (orderId, artworkId, quantity, unitPrice, lineTotal, purchaseType, leaseDuration))
            _commit()
            return cur.lastrowid
        except Exception as e:
            _rollback()
            raise e
        finally:
            cur.close()

class Payment:
    @staticmethod
    def record(orderId: int, amount: float, method: str = "card") -> int:
        cur = _dict_cursor()
        try:
            cur.execute("INSERT INTO payment (orderId, amount, method) VALUES (%s, %s, %s)",
                        (orderId, amount, method))
            _commit()
            return cur.lastrowid
        except Exception as e:
            _rollback()
            raise e
        finally:
            cur.close()