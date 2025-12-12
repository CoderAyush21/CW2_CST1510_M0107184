from datetime import datetime

class IT_Ticket:

    def __init__(self, ticket_id, priority, description, status, assigned_to=None, resolution_time_hours=None, created_at=None):
        self.__id = ticket_id
        self.__priority = priority
        self.__description = description
        self.__status = status
        self.__assigned_to = assigned_to
        self.__resolution_time_hours = resolution_time_hours
        self.__created_at = created_at

    def get_id(self):
        return self.__id

    def get_priority(self):
        return self.__priority

    def get_description(self):
        return self.__description

    def get_status(self):
        return self.__status

    def get_assigned_to(self):
        return self.__assigned_to

    def get_resolution_time_hours(self):
        return self.__resolution_time_hours

    def get_created_at(self):
        return self.__created_at


    @classmethod
    def load_by_id(cls, db, ticket_id):
        sql = """
            SELECT ticket_id, priority, description, status, assigned_to, resolution_time_hours, created_at
            FROM it_tickets
            WHERE ticket_id = ?
        """
        row = db.fetch_one(sql, (ticket_id,))
        if not row:
            return None
        return cls(
            ticket_id=row[0],
            priority=row[1],
            description=row[2],
            status=row[3],
            assigned_to=row[4],
            resolution_time_hours=row[5],
            created_at=row[6]
        )

    def update_status(self, db, status):
        self.__status = status
        sql = "UPDATE it_tickets SET status = ? WHERE ticket_id = ?"
        cur = db.execute_query(sql, (self.__status, self.__id))
        return cur.rowcount > 0

    def insert_ticket(self, db):
        sql = """
            INSERT INTO it_tickets
            (priority, description, status, assigned_to, created_at, resolution_time_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        ts = self.__created_at if self.__created_at else datetime.now()
        cur = db.execute_query(sql, (
            self.__priority,
            self.__description,
            self.__status,
            self.__assigned_to,
            ts,
            self.__resolution_time_hours
        ))
        self.__id = cur.lastrowid
        return self.__id

    def delete(self, db):
        sql = "DELETE FROM it_tickets WHERE ticket_id = ?"
        cur = db.execute_query(sql, (self.__id,))
        return cur.rowcount > 0
