from typing import Dict, Any, Optional, List, Tuple

import psycopg2
from psycopg2 import sql, extras
from dotenv import dotenv_values


class DatabaseWorker:
    '''
    Database worker class for PostgreSQL operations.

    This class manages database connections and provides CRUD
    operations for pereval, user, coordinates, levals and image data.
    '''

    def __init__(self):
        self.config = dotenv_values()
        self._connection = None
        self._cursor = None
        self._dict_cursor = None

    @property
    def db_config(self) -> Dict[str, str]:
        '''
        Get database configuration from .env variables.

        Returns:
            Dict[str, str]: Database connections params. 
        '''
        return {
            'dbname': self.config['FSTR_DB_NAME'],
            'user': self.config['FSTR_DB_LOGIN'],
            'password': self.config['FSTR_DB_PASS'],
            'host': self.config['FSTR_DB_HOST'],
            'port': self.config['FSTR_DB_PORT'],
        }

    def connect(self) -> None:
        '''
        Set database connection and cursors.

        Raises:
            Exception: If database collection fails.
        '''
        try:
            self._connection = psycopg2.connect(**self.db_config)
            self._cursor = self._connection.cursor()
            self._dict_cursor = self._connection.cursor(
                cursor_factory=extras.RealDictCursor
            )
        except Exception as ex:
            raise Exception(f'Database connection error:\n{ex}')

    def disconnect(self) -> None:
        '''
        Close database connection.
        '''
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()

    def insert_data(self, table: str, data: dict[str, Any]) -> int:
        '''
        Insert record into the table.

        Args:
            table: Name of the target table in the database.
            data: Dict of column-value pairs to insert.
        
        Returns:
            int: Id of created record.

        Raises:
            Exception: If no connection exists or insertion fails.
        '''
        if not self._connection:
            raise Exception(f'No connection to the database.')
        
        try:
            columns = data.keys()
            values = list(data.values())
            
            query = sql.SQL('INSERT INTO {} ({}) VALUES ({}) RETURNING id').format(
                sql.Identifier(table),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(values))
            )

            self._cursor.execute(query, values)
            result_id = self._cursor.fetchone()[0]
            return result_id
        
        except Exception as ex:
            raise Exception(f'Something went wrong while inserting data: {ex}')

    def update_data(self, table: str, data: dict[str, Any], id: int) -> None:
        '''
        Update record in the table.

        Args:
            table: Name of the target table in the database.
            data: Dict of column-value pairs to update.

        Raises:
            Exception: If no connection exists or insertion fails.
        '''
        if not self._connection:
            raise Exception(f'No connection to the database.')
        
        try:
            columns = list(data.keys())
            values = list(data.values())
            values.append(id)

            query = sql.SQL('UPDATE {} SET {} WHERE id = %s').format(
                sql.Identifier(table),
                sql.SQL(', ').join(
                    [
                        sql.SQL('{} = %s').format(sql.Identifier(column))
                        for column in columns
                    ]
                )
            )

            self._cursor.execute(query, values)

        except Exception as ex:
            raise Exception(f'Something went wrong while updating data: {ex}')

    def get_or_create_user(self, user_data: dict[str, Any]) -> int:
        '''
        Get id of an existing user or create a new one.

        Args:
            user_data: User`s data contains email, name and phone.

        Returns:
            int: Id of existing or new user. 

        Raises:
            Exception: If no connection exists or operation fails.
        '''
        if not self._connection:
            raise Exception(f'No connection to the database.')
        
        try:
            self._cursor.execute(
                f'SELECT id FROM users WHERE email = %s',
                (user_data['email'],)
            )
            user_id = self._cursor.fetchone()

            if not user_id:
                user_id = self.insert_data('users', user_data)
            
            return user_id
        
        except Exception as ex:
            raise Exception(f'Something went wrong while getting or creating user: {ex}')

    def add_pereval(self, data: dict[str, Any]) -> int:
        '''
        Add new pereval record with related data.

        Method performs transaction that inserts user (or gets an 
        existing one), coordinates, diff levels, images and pereval.

        Args:
            data: Complete pereval data dict.
        
        Returns:
            int: Id of new pereval.

        Raises:
            Exception: If any part of the transaction fails.
        '''
        try:
            user_id = self.get_or_create_user(data['user'])
            coords_id = self.insert_data('coords', data['coords'])
            levels_id = self.insert_data('levels', data['level'])

            pereval_data = {
                'beauty_title': data['beauty_title'],
                'title': data['title'],
                'other_titles': data['other_titles'],
                'connect': data['connect'],
                'add_time': data['add_time'],
                'user_id': user_id,
                'coords_id': coords_id,
                'levels_id': levels_id
            }

            pereval_id = self.insert_data('pereval_added', pereval_data)

            images_data = data['images']
            for image in images_data:
                image['pereval_id'] = pereval_id
                self.insert_data('pereval_images', image)

            self._connection.commit()
            return pereval_id
        
        except Exception as ex:
            raise Exception(f'Something went wrong while adding pereval: {ex}')

    def update_pereval(
        self, 
        pereval: dict[str, Any], 
        data: dict[str, Any]
    ) -> Tuple[int, Optional[str]]:
        '''
        Update pereval record.

        Args:
            pereval: Pereval record for getting foreign keys values.
            data: Dict containing fields to update.

        Returns:
            tuple[int, Optional[str]]: Contains state (1-success, 0-error) 
                and error message. 
        '''
        try:
            pereval_id = pereval['id']

            coords_data: dict = data.pop('coords', None)
            levels_data: dict = data.pop('levels', None)

            if coords_data:
                coords_id = pereval['coords']['id']
                self.update_data('coords', coords_data, coords_id)

            if levels_data:
                levels_id = pereval['levels']['id']
                self.update_data('levels', levels_data, levels_id)

            self.update_data('pereval_added', data, pereval_id)        
            self._connection.commit()
            return 1, None

        except Exception as ex:
            return 0, ex

    def get_pereval_by_id(self, pereval_id: int) -> Optional[dict[str, Any]]:
        '''
        Retrieve pereval record by id.
        
        Args:
            pereval_id: Id of the pereval to retrieve.

        Returns:
            Optional[dict[str, Any]]: The pereval data as a dict or 
                None if not found.

        Raises:
            Exception: If operation fails. 
        '''
        if not self._connection:
            raise Exception(f'No connection to the database.')
        
        query = '''
            WITH pereval_cte AS (
                SELECT * FROM pereval_added WHERE id = %s
            )
            SELECT
                pereval_cte.*,
                row_to_json(users) AS user,
                row_to_json(coords) AS coords,
                row_to_json(levels) AS levels,
                COALESCE(
                    (SELECT json_agg(pereval_images)
                    FROM pereval_images
                    WHERE pereval_cte.id = pereval_images.pereval_id),
                    '[]'::json
                ) AS images
            FROM pereval_cte
            LEFT JOIN users ON pereval_cte.user_id = users.id
            LEFT JOIN coords ON pereval_cte.coords_id = coords.id
            LEFT JOIN levels ON pereval_cte.levels_id = levels.id
        '''

        try: 
            self._dict_cursor.execute(
                query,
                (pereval_id,)
            )
            pereval = self._dict_cursor.fetchone()

            if pereval:
                pereval = dict(pereval)
                for key in ['user_id', 'coords_id', 'levels_id']:
                    pereval.pop(key, None)
                return pereval
            
            return None
        
        except Exception as ex:
            raise Exception(f'Something went wrong while getting pereval: {ex}')

    def get_pereval_list_by_email(self, email: str) -> List[Dict[str, Any]]:
        '''
        Retrieve all perevals created by user.

        Args:
            user_email: User`s Email.

        Returns:
            List[Dict[str, Any]]: List of pereval data dicts.

        Raises:
            Exception: If operation fails.
        '''
        if not self._connection:
            raise Exception(f'No connection to the database.')
        
        query = '''
            SELECT pereval_added.id FROM pereval_added
            JOIN users ON pereval_added.user_id = users.id
            WHERE users.email = %s
        '''

        try:
            self._cursor.execute(
                query,
                (email,)
            )

            result = []
            for record in self._cursor.fetchall():
                result.append(self.get_pereval_by_id(record[0]))
            return result
        except Exception as ex:
            raise Exception(f'Something went wrong while getting pereval list: {ex}')
