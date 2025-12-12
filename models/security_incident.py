from datetime import datetime


class SecurityIncident :

    def __init__(self, incident_id, incident_type, severity, status, description,reported_by=None, timestamp=None):

        self.__id = incident_id
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by
        self.__timestamp = timestamp
    
    def get_id(self) -> int:
        return self.__id

    def get_incident_type(self) -> str:
        return self.__incident_type

    def get_severity(self) -> str:
        return self.__severity

    def get_status(self) -> str:
        return self.__status

    def get_description(self) -> str:
        return self.__description
    
    def get_reported_by(self) -> str:
        return self.__reported_by
    
    def get_timestamp(self) -> str:
        return self.__timestamp


    @classmethod
    def load_by_id(cls, db, incident_id):

        sql = """
            SELECT * FROM cyber_incidents
            WHERE incident_id = ?

        """
        row = db.fetch_one(sql, (incident_id,))
        if not row:
            return None

        return cls(
            incident_id=row[0],
            incident_type=row[1],
            severity=row[2],
            status=row[3],
            description=row[4],
            reported_by=row[5],
            timestamp=row[6]
        )
    
    '''

    Method to update the status of an incident

    '''

    def update_status(self, db, new_status: str) -> bool:
        self.__status = new_status

        sql = "UPDATE cyber_incidents SET status = ? WHERE incident_id = ?"
        cur = db.execute_query(sql, (new_status, self.__id))

        return cur.rowcount > 0



    def insert(self, db):
        """
        Insert incident into the database.

        """

        sql = """
            INSERT INTO cyber_incidents
            (timestamp, severity, category, status, description, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)

        """

        ts = self.__timestamp if self.__timestamp else datetime.now()

        cur = db.execute_query(sql, (
            ts,
            self.__severity,
            self.__incident_type,
            self.__status,
            self.__description,
            self.__reported_by
        ))

        self.__id = cur.lastrowid
        return self.__id
    

    def delete(self, db) -> bool:
        """
        Delete this incident from the database.
        Returns True if deletion was successful, False otherwise.

        """

        sql = "DELETE FROM cyber_incidents WHERE incident_id = ?"
        cur = db.execute_query(sql, (self.__id,))

        return cur.rowcount > 0