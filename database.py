import sqlite3
from contextlib import closing
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_connection()) as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                plant TEXT NOT NULL,
                disease TEXT NOT NULL,
                plant_confidence REAL NOT NULL,
                disease_confidence REAL NOT NULL,
                is_healthy INTEGER NOT NULL,
                mode TEXT NOT NULL,
                width INTEGER,
                height INTEGER,
                file_size_kb REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        conn.commit()


def save_prediction(image_path, plant, disease, plant_confidence, disease_confidence, is_healthy, mode, width, height, file_size_kb):
    with closing(get_connection()) as conn:
        conn.execute(
            '''
            INSERT INTO predictions (
                image_path, plant, disease, plant_confidence, disease_confidence,
                is_healthy, mode, width, height, file_size_kb
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                image_path,
                plant,
                disease,
                plant_confidence,
                disease_confidence,
                int(is_healthy),
                mode,
                width,
                height,
                file_size_kb,
            ),
        )
        conn.commit()


def get_history(limit=100):
    with closing(get_connection()) as conn:
        rows = conn.execute(
            '''
            SELECT id, image_path, plant, disease, plant_confidence, disease_confidence,
                   is_healthy, mode, width, height, file_size_kb, created_at
            FROM predictions
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
    return [dict(row) | {'is_healthy': bool(row['is_healthy']), 'timestamp': row['created_at']} for row in rows]


def get_stats():
    with closing(get_connection()) as conn:
        total = conn.execute('SELECT COUNT(*) AS c FROM predictions').fetchone()['c']
        healthy = conn.execute('SELECT COUNT(*) AS c FROM predictions WHERE is_healthy = 1').fetchone()['c']
        diseased = conn.execute('SELECT COUNT(*) AS c FROM predictions WHERE is_healthy = 0').fetchone()['c']
        plant_counts = [dict(row) for row in conn.execute(
            'SELECT plant, COUNT(*) AS count FROM predictions GROUP BY plant ORDER BY count DESC'
        ).fetchall()]
        top_diseases = [dict(row) for row in conn.execute(
            'SELECT disease, COUNT(*) AS count FROM predictions GROUP BY disease ORDER BY count DESC LIMIT 6'
        ).fetchall()]
    return {
        'total': total,
        'healthy': healthy,
        'diseased': diseased,
        'plant_counts': plant_counts,
        'top_diseases': top_diseases,
    }


def delete_prediction(prediction_id: int) -> bool:
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            'DELETE FROM predictions WHERE id = ?', (prediction_id,)
        )
        conn.commit()
        return cursor.rowcount > 0