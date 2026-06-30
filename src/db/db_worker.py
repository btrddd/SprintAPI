import psycopg2
from psycopg2 import sql, extras
from dotenv import dotenv_values


config = dotenv_values()

db_connection_config = {
    'dbname': config['FSTR_DB_NAME'],
    'user': config['FSTR_DB_LOGIN'],
    'password': config['FSTR_DB_PASS'],
    'host': config['FSTR_DB_HOST'],
    'port': config['FSTR_DB_PORT'],
}


class DatabaseWorker:
    def connect(self):
        try:
            self.connection = psycopg2.connect(**db_connection_config)
            self.cursor = self.connection.cursor()
            self.dict_cursor = self.connection.cursor(
                cursor_factory=extras.RealDictCursor
            )
        except Exception as ex:
            raise Exception(f'Database connection error:\n{ex}')
        
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def insert_data(self, table, data: dict) -> int:
        if not self.connection:
            raise Exception(f'No connection to the database.')
        
        columns = data.keys()
        values = list(data.values())
        
        query = sql.SQL('INSERT INTO {} ({}) VALUES ({}) RETURNING id').format(
            sql.Identifier(table),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(values))
        )

        self.cursor.execute(query, values)
        result_id = self.cursor.fetchone()[0]
        return result_id
    
    def update_data(self, table: str, data: dict, id: int):
        if not self.connection:
            raise Exception(f'No connection to the database.')
        
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

        self.cursor.execute(query, values)

    def get_or_create_user(self, user_data: dict) -> int:
        if not self.connection:
            raise Exception(f'No connection to the database.')
        
        self.cursor.execute(
            f'SELECT id FROM users WHERE email = %s',
            (user_data['email'],)
        )
        user_id = self.cursor.fetchone()[0]

        if not user_id:
            user_id = self.insert_data('users', user_data)
        
        return user_id

    def add_pereval(self, data: dict) -> int:
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

            pereval = self.insert_data('pereval_added', pereval_data)

            images_data = data['images']
            for image in images_data:
                image['pereval_id'] = pereval
                self.insert_data('pereval_images', image)

            self.connection.commit()
            return pereval
        
        except Exception as ex:
            self.disconnect()
            raise Exception(f'Something went wrong while inserting data:\n{ex}')

    def update_pereval(self, pereval_id, data: dict):
        try:
            pereval = self.get_pereval_by_id(pereval_id)
            print(pereval)

            coords_data: dict = data.pop('coords', None)
            levels_data: dict = data.pop('levels', None)

            if coords_data:
                coords_id = pereval['coords']['id']
                self.update_data('coords', coords_data, coords_id)

            if levels_data:
                levels_id = pereval['levels']['id']
                self.update_data('levels', levels_data, levels_id)

            self.update_data('pereval_added', data, pereval_id)        
            self.connection.commit()
            return 1, None
        except Exception as ex:
            return 0, ex

    def get_pereval_by_id(self, pereval_id: int) -> dict|None:
        if not self.connection:
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

        self.dict_cursor.execute(
            query,
            (pereval_id,)
        )
        pereval = self.dict_cursor.fetchone()

        if pereval:
            pereval = dict(pereval)
            for key in ['user_id', 'coords_id', 'levels_id']:
                pereval.pop(key, None)
            return pereval
        
        return None

    def get_pereval_list_by_email(self, email: str) -> list:
        if not self.connection:
            raise Exception(f'No connection to the database.')
        
        query = '''
            SELECT pereval_added.id FROM pereval_added
            JOIN users ON pereval_added.user_id = users.id
            WHERE users.email = %s
        '''

        self.cursor.execute(
            query,
            (email,)
        )

        result = []
        for record in self.cursor.fetchall():
            result.append(self.get_pereval_by_id(record[0]))
        return result


if __name__ == '__main__':
    new_data = {
        'id': 11, 
        'title': 'new_title', 
        'other_titles': 'new_other_title', 
        'coords': {
            'height': 20
        }, 
        'levels': {
            'summer': '8А', 
            'spring': '3A'
        }
    }

    worker = DatabaseWorker()
    worker.connect()
    # worker.update_pereval(new_data)
    print(worker.get_pereval_by_id(11))
    # print(worker.get_pereval_list_by_email('qwerty123@mail.ru'))
    worker.disconnect()