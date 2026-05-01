import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def create_partitions():
    """
    Creates monthly partitions for StoreAnalytics and UserActivity tables.
    This should be run periodically (e.g., via cron or Airflow).
    """
    try:
        with engine.connect() as conn:
            # Check if partitioning is supported (PostgreSQL)
            if not engine.dialect.name == 'postgresql':
                logger.info("Partitioning is only supported on PostgreSQL. Skipping.")
                return

            now = datetime.utcnow()
            for i in range(-1, 3): # Create partitions for last month, current month, and next two months
                target_date = now + timedelta(days=30 * i)
                year, month = target_date.year, target_date.month

                # Calculate next month
                next_month = month + 1
                next_year = year
                if next_month > 12:
                    next_month = 1
                    next_year += 1

                # Format strings
                start_date = f"'{year}-{month:02d}-01'"
                end_date = f"'{next_year}-{next_month:02d}-01'"

                # Store Analytics Partition
                table_name = f"store_analytics_{year}_{month:02d}"
                sql = text(f"""
                    CREATE TABLE IF NOT EXISTS {table_name}
                    PARTITION OF store_analytics
                    FOR VALUES FROM ({start_date}) TO ({end_date});
                """)
                conn.execute(sql)

                # User Activity Partition
                table_name_ua = f"user_activities_{year}_{month:02d}"
                sql_ua = text(f"""
                    CREATE TABLE IF NOT EXISTS {table_name_ua}
                    PARTITION OF user_activities
                    FOR VALUES FROM ({start_date}) TO ({end_date});
                """)
                conn.execute(sql_ua)

            conn.commit()
            logger.info("Successfully created database partitions.")
    except Exception as e:
        logger.error(f"Failed to create partitions: {e}")

if __name__ == "__main__":
    create_partitions()
