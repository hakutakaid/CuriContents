import aiosqlite

class Database:
    def __init__(self, db_path='database.sqlite3'):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    session TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS vars_data (
                    user_id TEXT,
                    query_name TEXT,
                    vars_name TEXT,
                    value TEXT,
                    PRIMARY KEY(user_id, query_name, vars_name)
                )
            """)
            await db.commit()

    # ==== USERS ====

    def new_user(self, id, name):
        return dict(id=id, name=name, session=None)

    async def add_user(self, id, name):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (id, name, session) VALUES (?, ?, ?)",
                (id, name, None)
            )
            await db.commit()

    async def is_user_exist(self, id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT 1 FROM users WHERE id = ?", (int(id),)) as cursor:
                return bool(await cursor.fetchone())

    async def total_users_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id, name, session FROM users") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    yield dict(id=row[0], name=row[1], session=row[2])

    async def delete_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM users WHERE id = ?", (int(user_id),))
            await db.commit()

    async def set_session(self, id, session):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET session = ? WHERE id = ?", (session, int(id))
            )
            await db.commit()

    async def get_session(self, id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT session FROM users WHERE id = ?", (int(id),)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    # ==== VARS DATA ====

    async def set_vars(self, user_id, vars_name, value, query="vars"):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO vars_data (user_id, query_name, vars_name, value)
                VALUES (?, ?, ?, ?)""",
                (str(user_id), query, vars_name, str(value))
            )
            await db.commit()

    async def get_vars(self, user_id, vars_name, query="vars"):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT value FROM vars_data
                WHERE user_id = ? AND query_name = ? AND vars_name = ?""",
                (str(user_id), query, vars_name)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

    async def remove_vars(self, user_id, vars_name, query="vars"):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                DELETE FROM vars_data
                WHERE user_id = ? AND query_name = ? AND vars_name = ?""",
                (str(user_id), query, vars_name)
            )
            await db.commit()

    async def all_vars(self, user_id, query="vars"):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT vars_name, value FROM vars_data
                WHERE user_id = ? AND query_name = ?""",
                (str(user_id), query)
            ) as cursor:
                results = await cursor.fetchall()
                return {name: value for name, value in results} if results else None

    async def remove_all_vars(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                DELETE FROM vars_data
                WHERE user_id = ?""",
                (str(user_id),)
            )
            await db.commit()

    async def get_list_from_vars(self, user_id, vars_name, query="vars"):
        vars_data = await self.get_vars(user_id, vars_name, query)
        return [int(x) for x in str(vars_data).split()] if vars_data else []

    async def add_to_vars(self, user_id, vars_name, value, query="vars"):
        vars_list = await self.get_list_from_vars(user_id, vars_name, query)
        vars_list.append(value)
        await self.set_vars(user_id, vars_name, " ".join(map(str, vars_list)), query)

    async def remove_from_vars(self, user_id, vars_name, value, query="vars"):
        vars_list = await self.get_list_from_vars(user_id, vars_name, query)
        if value in vars_list:
            vars_list.remove(value)
            await self.set_vars(user_id, vars_name, " ".join(map(str, vars_list)), query)

# Inisialisasi
db = Database()