from fastapi import FastAPI, WebSocket
import json
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# Database setup
engine = create_engine("sqlite:///wearable.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class WearableData(Base):
    __tablename__ = "wearable_data"

    id = Column(Integer, primary_key=True)
    encrypted_payload = Column(String)

Base.metadata.create_all(engine)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    db = Session()

    while True:

        data = await websocket.receive_text()

        payload = json.loads(data)

        # Encrypt payload
        encrypted = cipher.encrypt(json.dumps(payload).encode())

        record = WearableData(
            encrypted_payload=encrypted.decode()
        )

        db.add(record)
        db.commit()

        await websocket.send_text("Data stored securely")