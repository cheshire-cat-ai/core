#### Why am I getting the error `RateLimitError` in my browser console?
Please check if you have a valid credit card connected or if you have used up all the credits of your OpenAI trial period.

#### Everything works in localhost but not on another server
You should configure ports in the `.env` file. Change according to your preferred host and ports:
```
# Decide host and port for your Cat. Default will be localhost:1865
CORE_HOST=anotherhost.com
CORE_PORT=9000

# Decide host and port for your Cat Admin. Default will be localhost:3000
ADMIN_HOST=myhost.eu
ADMIN_PORT=2222
```

#### Port 1865 or port 3000 are not allowed by my operating system and/or firewall
Change the ports as you wish in the `.env` file.
```
# Decide host and port for your Cat. Default will be localhost:1865
CORE_HOST=localhost
CORE_PORT=9000

# Decide host and port for your Cat Admin. Default will be localhost:3000
ADMIN_HOST=localhost
ADMIN_PORT=2222
```

#### Docker has no permissions to write
This is a matter with your docker installation or the user you run docker from.