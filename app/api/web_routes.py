from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Setup templates directory
# In Docker container, the structure is /app/app/templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/system-admin", response_class=HTMLResponse)
async def system_admin_dashboard(request: Request):
    """System admin dashboard (superuser only)"""
    return templates.TemplateResponse(
        "system_admin_dashboard.html", {"request": request}
    )


@router.get("/system-logs", response_class=HTMLResponse)
async def system_logs_page(request: Request):
    """System logs viewer page (for system admins only)"""
    return templates.TemplateResponse("system_logs.html", {"request": request})


@router.get("/first-time-setup", response_class=HTMLResponse)
async def first_time_setup_page(request: Request):
    """First time setup page"""
    # Check if setup is needed
    from app.db.session import SessionLocal
    from app import models

    db = SessionLocal()
    needs_setup = db.query(models.Church).count() == 0
    db.close()

    if not needs_setup:
        # Redirect to login if setup is already done
        return templates.TemplateResponse("login.html", {"request": request})

    # Create a simple setup page if template doesn't exist
    setup_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Yoram - Initial Setup</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }
            .setup-container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                padding: 40px;
                max-width: 500px;
                width: 100%;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #555;
                font-weight: 500;
            }
            input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
            }
            .section-title {
                color: #667eea;
                font-weight: 600;
                margin-top: 30px;
                margin-bottom: 15px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }
            .section-title:first-of-type {
                margin-top: 0;
                padding-top: 0;
                border-top: none;
            }
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                margin-top: 20px;
            }
            button:hover {
                opacity: 0.9;
            }
            .error {
                color: #e74c3c;
                margin-top: 10px;
                display: none;
            }
            .success {
                color: #27ae60;
                margin-top: 10px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="setup-container">
            <h1>Welcome to Smart Yoram</h1>
            <p class="subtitle">Let's set up your church management system</p>
            
            <form id="setupForm">
                <div class="section-title">Church Information</div>
                
                <div class="form-group">
                    <label for="church_name">Church Name *</label>
                    <input type="text" id="church_name" name="church_name" required>
                </div>
                
                <div class="form-group">
                    <label for="church_address">Church Address</label>
                    <input type="text" id="church_address" name="church_address">
                </div>
                
                <div class="form-group">
                    <label for="church_phone">Church Phone</label>
                    <input type="tel" id="church_phone" name="church_phone">
                </div>
                
                <div class="form-group">
                    <label for="pastor_name">Pastor Name</label>
                    <input type="text" id="pastor_name" name="pastor_name">
                </div>
                
                <div class="section-title">Administrator Account</div>
                
                <div class="form-group">
                    <label for="admin_name">Admin Name *</label>
                    <input type="text" id="admin_name" name="admin_name" required>
                </div>
                
                <div class="form-group">
                    <label for="admin_email">Admin Email *</label>
                    <input type="email" id="admin_email" name="admin_email" required>
                </div>
                
                <div class="form-group">
                    <label for="admin_password">Admin Password *</label>
                    <input type="password" id="admin_password" name="admin_password" required minlength="8">
                </div>
                
                <div class="form-group">
                    <label for="admin_phone">Admin Phone</label>
                    <input type="tel" id="admin_phone" name="admin_phone">
                </div>
                
                <button type="submit">Complete Setup</button>
                
                <div class="error" id="errorMsg"></div>
                <div class="success" id="successMsg"></div>
            </form>
        </div>
        
        <script>
            document.getElementById('setupForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                const errorMsg = document.getElementById('errorMsg');
                const successMsg = document.getElementById('successMsg');
                
                errorMsg.style.display = 'none';
                successMsg.style.display = 'none';
                
                try {
                    const response = await fetch('/api/v1/setup/complete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        successMsg.textContent = 'Setup completed successfully! Redirecting to login...';
                        successMsg.style.display = 'block';
                        
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 2000);
                    } else {
                        errorMsg.textContent = result.detail || 'Setup failed. Please try again.';
                        errorMsg.style.display = 'block';
                    }
                } catch (error) {
                    errorMsg.textContent = 'Network error. Please try again.';
                    errorMsg.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """

    from fastapi.responses import HTMLResponse

    return HTMLResponse(content=setup_html)
