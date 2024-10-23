from starlette import status
from starlette.responses import JSONResponse

from src.domain.schemas import Tokens


async def login(data):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=Tokens(
            access_token="your_test_access_token",
            refresh_token="your_test_refresh_token"
        ).model_dump()
    )

async def refresh(data):
    return JSONResponse(status_code=status.HTTP_200_OK, content={'message': "Test refreshed in."})

async def register(data):
    print(f'Returned data from register!')
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User was registered successfully."})
