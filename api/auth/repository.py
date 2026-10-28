def getUserByusername(db, username: str):
    return db.query(User).filter(User.username == username).first()

