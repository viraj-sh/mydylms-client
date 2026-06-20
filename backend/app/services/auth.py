from app.core.http import HTTPClientDep


async def login(username: str, password: str, client: HTTPClientDep):

    data = {
        "uname_static": username,
        "username": username,
        "uname": username,
        "password": password,
    }
    return await client.post(
        url="https://mydy.dypatil.edu/rait/login/index.php",
        data=data,
        follow_redirects=True,
    )
