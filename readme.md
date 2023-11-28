## Sumary

Users register on the website and access personal accounts where they can edit personal info and view statistics.
Stats include page transitions by VPN, data sent/received from sites. Users can create multiple sites (URL + name) and access them via a button. Instead of directly visiting the URL, the system acts as a proxy, mediating between the user and the external site.

## Installation

1. Clone this project `git clone https://github.com/Eldamorh/vpn_project.git`
2. Cd into folder `cd vpn_project`
3. Change .env.dev file name to .env with `cat .env.dev > .env`(Unix like) or `copy .env.dev .env`(Windows) and change fields if needed
4. Run docker compose `docker-compose up -d`
5. Migrate db using `docker-compose exec web python manage.py migrate`


Now everything should be running. Go to `localhost:8000/register`. 

Available endpoints:
```
/register
/login
/dashboard
/create_site
/update_user
```
