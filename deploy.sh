#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
sudo apt-get install -y python3 python3-pip python3-venv nginx

# Create project directory
sudo mkdir -p /var/www/flask_app
sudo chown $USER:$USER /var/www/flask_app

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn

# Create WSGI file
cat > wsgi.py << EOL
from src.routes.main import app

if __name__ == "__main__":
    app.run()
EOL

# Create systemd service file
sudo tee /etc/systemd/system/flask_app.service << EOL
[Unit]
Description=Gunicorn instance to serve flask application
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/flask_app
Environment="PATH=/var/www/flask_app/venv/bin"
ExecStart=/var/www/flask_app/venv/bin/gunicorn --workers 3 --bind unix:flask_app.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOL

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/flask_app << EOL
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/flask_app/flask_app.sock;
    }
}
EOL

# Enable the site
sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default

# Start and enable services
sudo systemctl start flask_app
sudo systemctl enable flask_app
sudo systemctl restart nginx

echo "Deployment completed! Please check the status of services:"
echo "sudo systemctl status flask_app"
echo "sudo systemctl status nginx" 