from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

# Model to store the messages and usernames
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize the database
with app.app_context():
    db.create_all()

# Route to get messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.timestamp).all()
    return jsonify([{
        'id': msg.id,  # Include ID for deletion
        'username': msg.username,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for msg in messages])

# Route to send a message
@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    username = data.get('username')
    content = data.get('content')

    if not username or not content:
        return jsonify({'error': 'Username and message content are required'}), 400

    new_message = Message(username=username, content=content)
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message': 'Message sent successfully'}), 200

# Route to delete a message
@app.route('/delete/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    # Check if the user is the admin
    admin_username = 'QAQcew'  # Admin username
    username = request.args.get('username')  # Get the username from query parameters

    if username != admin_username:
        return jsonify({'error': 'Unauthorized access'}), 403

    message = Message.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'Message deleted successfully'}), 200

# Home route for testing
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
