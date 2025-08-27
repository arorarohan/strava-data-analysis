#!/usr/bin/env python3

import http.server
import socketserver
import urllib.parse
import webbrowser
import threading
import time
import subprocess
import json
import sys

# Import credentials from keys module
try:
    from keys import CLIENT_ID, CLIENT_SECRET
except ImportError:
    print("Error: keys.py file not found!")
    print("Please create a keys.py file with your Strava app credentials.")
    print("See README.md for setup instructions.")
    exit(1)

REDIRECT_URI = "http://localhost:8000"
AUTH_URL = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=activity:read_all"

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/?'):
            # Parse the authorization code from the callback
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                self.server.auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to your terminal.</p>
                </body>
                </html>
                ''')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Authorization Failed</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress server logs
        pass

def exchange_code_for_token(auth_code):
    """Exchange authorization code for access token using curl"""
    cmd = [
        'curl',
        '-X', 'POST',
        'https://www.strava.com/oauth/token',
        '-F', f'client_id={CLIENT_ID}',
        '-F', f'client_secret={CLIENT_SECRET}',
        '-F', f'code={auth_code}',
        '-F', 'grant_type=authorization_code',
        '-s'  # Silent mode
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        return response
    except subprocess.CalledProcessError as e:
        print(f"Error exchanging code for token: {e}")
        print(f"Response: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing token response: {e}")
        print(f"Raw response: {result.stdout}")
        return None

def main():
    print("Starting Strava OAuth flow...")
    print(f"1. Opening browser to: {AUTH_URL}")
    print("2. Please authorize the application")
    print("3. You'll be redirected back to localhost - don't worry if it looks broken")
    print("4. The script will automatically capture the authorization code\n")
    
    # Start local server to handle callback
    with socketserver.TCPServer(("", 8000), OAuthHandler) as httpd:
        httpd.auth_code = None
        
        # Start server in background thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Open browser
        webbrowser.open(AUTH_URL)
        
        # Wait for authorization code
        print("Waiting for authorization...")
        timeout = 120  # 2 minutes timeout
        start_time = time.time()
        
        while httpd.auth_code is None and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        if httpd.auth_code is None:
            print("Timeout waiting for authorization. Please try again.")
            return
        
        print(f"Got authorization code: {httpd.auth_code[:20]}...")
        
        # Exchange code for tokens
        print("Exchanging code for access token...")
        token_response = exchange_code_for_token(httpd.auth_code)
        
        if token_response and 'access_token' in token_response:
            access_token = token_response['access_token']
            refresh_token = token_response.get('refresh_token', '')
            expires_at = token_response.get('expires_at', 0)
            
            print("\n✅ Success! Your tokens:")
            print(f"Access Token: {access_token}")
            print(f"Refresh Token: {refresh_token}")
            print(f"Expires at: {time.ctime(expires_at) if expires_at else 'Unknown'}")
            
            print(f"\n🔄 To use in your script, replace the STRAVA_API_TOKEN with:")
            print(f'STRAVA_API_TOKEN = "{access_token}"')
            
            # Save tokens to file for convenience
            with open('strava_tokens.json', 'w') as f:
                json.dump(token_response, f, indent=2)
            print(f"\n💾 Tokens saved to: strava_tokens.json")
            
        else:
            print("Failed to get access token")
            if token_response:
                print(f"Response: {token_response}")

if __name__ == "__main__":
    main()