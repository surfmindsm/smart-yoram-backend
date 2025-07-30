# EC2 Deployment Guide for Smart Yoram Backend

## Quick Deployment Steps

1. **SSH into your EC2 instance**
   ```bash
   ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip
   ```

2. **Navigate to the project directory**
   ```bash
   cd /home/ubuntu/smart-yoram-backend
   ```

3. **Pull the latest code**
   ```bash
   git pull origin main
   ```

4. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

5. **Install/update dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Update environment variables if needed**
   ```bash
   # Check if .env needs updates
   nano .env
   ```

7. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

8. **Restart the services**
   ```bash
   # If using systemd
   sudo systemctl restart smart-yoram
   sudo systemctl restart nginx
   
   # Or if using Docker
   docker-compose down
   docker-compose up -d --build
   ```

9. **Check CloudFlare tunnel**
   ```bash
   # Make sure CloudFlare tunnel is running
   ps aux | grep cloudflared
   
   # If not running, start it
   nohup cloudflared tunnel --url http://localhost:8000 > cloudflare.log 2>&1 &
   ```

## Verify Deployment

1. **Check if the service is running**
   ```bash
   sudo systemctl status smart-yoram
   ```

2. **Check application logs**
   ```bash
   sudo journalctl -u smart-yoram -f
   ```

3. **Test the API**
   ```bash
   curl http://localhost:8000/api/v1/
   ```

4. **Test through CloudFlare**
   ```bash
   curl https://packs-holds-marc-extended.trycloudflare.com/api/v1/
   ```

## Important Notes

- The new photo upload endpoints require Supabase Storage buckets to be created
- See `SUPABASE_STORAGE_SETUP.md` for bucket setup instructions
- Make sure the CloudFlare URL in frontend matches the active tunnel URL