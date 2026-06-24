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
        except Exception as ex:
            raise Exception(f'Database connection error:\n{ex}')
        
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def insert_data(self, table, data: dict):
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

    def get_or_create_user(self, user_data):
        self.cursor.execute(
            f'SELECT id FROM users WHERE email = %s',
            (user_data['email'],)
        )
        user_id = self.cursor.fetchone()[0]

        if not user_id:
            user_id = self.insert_data('users', user_data)
        
        return user_id

    def add_pereval(self, data: dict):
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


if __name__ == '__main__':
    data = {
        "beauty_title": "пер. ",
        "title": "Пхия",
        "other_titles": "Триев",
        "connect": "",
        "add_time": "2021-09-22 13:18:13",
        "user": {
            "email": "qwerty123@mail.ru", 		
            "fam": "Пупкин",
            "name": "Василий",
            "otc": "Иванович",
            "phone": "+7 555 55 66"
        }, 
        "coords": {
            "latitude": "45.3842",
            "longitude": "7.1525",
            "height": "1200"
        },
        "level":{
            "winter": "",
            "summer": "1А",
            "autumn": "1А",
            "spring": ""
        },
        "images": [
            {
                "data":"<картинка1>", 
                "title":"Седловина"
            }, 
            {
                "data":"<картинка>", 
                "title":"Подъём"
            }
        ]
    }


    worker = DatabaseWorker()
    worker.connect()
    worker.add_pereval(data)
    worker.disconnect()