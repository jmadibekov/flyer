from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests, json
import asyncio

API = 'https://tequila-api.kiwi.com/v2/search'
API_KEY = 'A5VqFeOZvXoOfy5zY19vBuWO4b4TJL23'
DATE_STR = '16/04/2021'

def index(request):
    response = requests.get(
        API,
        params={
            'fly_from': 'ALA',
            'fly_to': 'TSE',
            'date_from': DATE_STR,
            'date_to': DATE_STR,
        },
        headers={'apikey': API_KEY},
    )
    json_data = response.json()
    print(f'Status code is {response.status_code}')
    return JsonResponse(json_data)

async def index_async(request):
    await asyncio.sleep(5)
    return HttpResponse('Made a pretty page asynchronously!')