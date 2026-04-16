from . import mysql

def get_all_artworks():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
          a.artworkId, a.title, a.imageUrl, a.pricePerMonth, a.description,
          ar.name AS artistName, c.name AS categoryName, m.name AS mediumName
        FROM artwork a
        LEFT JOIN artist   ar ON a.artistId   = ar.artistId
        LEFT JOIN category c  ON a.categoryId = c.categoryId
        LEFT JOIN medium   m  ON a.mediumId   = m.mediumId
        ORDER BY a.artworkId
    """)
    rows = cur.fetchall()
    cur.close()
    return [_map_row(r) for r in rows]

def get_artwork_by_id(artwork_id: int):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
          a.artworkId, a.title, a.imageUrl, a.pricePerMonth, a.purchasePrice,
          a.description, a.dimensions, a.availabilityStatus, a.region,
          ar.name AS artistName, c.name AS categoryName, m.name AS mediumName
        FROM artwork a
        LEFT JOIN artist   ar ON a.artistId   = ar.artistId
        LEFT JOIN category c  ON a.categoryId = c.categoryId
        LEFT JOIN medium   m  ON a.mediumId   = m.mediumId
        WHERE a.artworkId = %s
        LIMIT 1
    """, (artwork_id,))
    r = cur.fetchone()
    cur.close()
    return _map_row_detail(r) if r else None

def search_artworks(q=None, artist_id=None, category_id=None, max_price=None):
    sql = """
        SELECT
          a.artworkId, a.title, a.imageUrl, a.pricePerMonth, a.description,
          ar.name AS artistName, c.name AS categoryName, m.name AS mediumName
        FROM artwork a
        LEFT JOIN artist   ar ON a.artistId   = ar.artistId
        LEFT JOIN category c  ON a.categoryId = c.categoryId
        LEFT JOIN medium   m  ON a.mediumId   = m.mediumId
        WHERE 1=1
    """
    params = []
    if q:
        q = q.strip().lower()
        sql += " AND (LOWER(a.title) LIKE %s OR LOWER(IFNULL(a.description,'')) LIKE %s)"
        kw = f"%{q}%"
        params += [kw, kw]
    if artist_id:
        sql += " AND a.artistId = %s"
        params.append(artist_id)
    if category_id:
        sql += " AND a.categoryId = %s"
        params.append(category_id)
    if max_price is not None:
        sql += " AND a.pricePerMonth <= %s"
        params.append(max_price)
    sql += " ORDER BY a.artworkId"

    cur = mysql.connection.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return [_map_row(r) for r in rows]

def insert_artwork(title, artist_id, category_id, image_url, desc, price_per_month, medium_id=None):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO artwork
          (artistId, mediumId, categoryId, title, description, imageUrl, pricePerMonth, availabilityStatus)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'available')
    """, (artist_id, medium_id, category_id, title, desc, image_url, price_per_month))
    mysql.connection.commit()
    cur.close()

def delete_artwork(artwork_id: int) -> bool:
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM artwork WHERE artworkId = %s", (artwork_id,))
    mysql.connection.commit()
    ok = cur.rowcount > 0
    cur.close()
    return ok

def list_artists():
    cur = mysql.connection.cursor()
    cur.execute("SELECT artistId, name FROM artist ORDER BY name")
    rows = cur.fetchall()
    cur.close()
    return rows

def list_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT categoryId, name FROM category ORDER BY name")
    rows = cur.fetchall()
    cur.close()
    return rows

# mappers 
def _map_row(r):
    return {
        "id": r["artworkId"],
        "title": r["title"],
        "artist": r["artistName"],
        "category": r["categoryName"],
        "medium": r.get("mediumName"),
        "price_per_month": r["pricePerMonth"],
        "desc": r["description"],
        "img": r["imageUrl"],
    }

def _map_row_detail(r):
    base = _map_row(r)
    base.update({
        "purchase_price": r.get("purchasePrice"),
        "dimensions": r.get("dimensions"),
        "status": r.get("availabilityStatus"),
        "region": r.get("region"),
    })
    return base

def get_artworks_by_artist(artist_id: int):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
          a.artworkId, a.title, a.imageUrl, a.pricePerMonth, a.description,
          ar.name AS artistName, c.name AS categoryName, m.name AS mediumName
        FROM artwork a
        LEFT JOIN artist   ar ON a.artistId   = ar.artistId
        LEFT JOIN category c  ON a.categoryId = c.categoryId
        LEFT JOIN medium   m  ON a.mediumId   = m.mediumId
        WHERE a.artistId = %s
        ORDER BY a.artworkId
    """, (artist_id,))
    rows = cur.fetchall()
    cur.close()
    return [_map_row(r) for r in rows]




