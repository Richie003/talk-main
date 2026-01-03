```bash
sudo chmod -R 775 /home/deploy/app
```
If your Gunicorn service runs under another user (e.g., deploy), replace ubuntu with that username.

3. Restart Gunicorn
```bash
sudo systemctl restart gunicorn
```
## check status/log at the moment
```bash
sudo systemctl status gunicorn
```
## check live log
```bash
sudo journalctl -u gunicorn -f
```

## For nginx and aap.sock error. 
```bash
sudo chown -R deploy:www-data /home/deploy/app
```

55834169