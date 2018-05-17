Hello, this is highloader

## How to use
```
# Make db migration (python shell)
>>> from highloader.main import db
>>> db.create_all()

# install dependencies
pip3 install requirements.txt

# run app on 5000 port
python3 main.py
```
1) POST /api/register
	takes json {"username":"username", "password":"password"}
	with header Content-Type : application/json

2) POST /api/login
	takes json {"username":"username", "password":"password"}
	return json {"access_token", "token"}
	
Copy that token and paste in headers for upload and download files:
	x-access-token : your_access_token

3) POST /api/upload
	paste file as form-data:
		file: file_to_upload
	with headers Content-Type: multipart/form-data

4) GET /api/download/<filename>
	to download file
	
