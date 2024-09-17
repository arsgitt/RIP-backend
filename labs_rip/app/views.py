from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

PLAYERS = [
            {'f_name': 'Marc','l_name': 'TER STEGEN', 'pic': 'http://127.0.0.1:9000/test/TerStegen.png', 'id': 1, 'position': 'GOALKEEPER', 'country': 'Германия', 'date_birthday': '21-05-2000', 'number': '1', 'country_image':'http://127.0.0.1:9000/test/germany.svg','height': '185', 'weight': '75','birth_place': 'Мюнхен'},
            {'f_name': 'Gonzalez','l_name': 'PEDRI', 'pic': 'http://127.0.0.1:9000/test/Pedri.png', 'id': 2, 'position': 'MIDFIELDER', 'number': '8'},
            {'f_name': 'Pablo','l_name': 'GAVI', 'pic': 'http://127.0.0.1:9000/test/Gavi.png', 'id': 3, 'position': 'MIDFIELDER', 'number': '6'},
            {'f_name': 'Lamine','l_name': 'YAMAL', 'pic': 'http://127.0.0.1:9000/test/Yamal.png', 'id': 4, 'position': 'FORWARD', 'number': '19'}
]

REQUESTS = [
    {'id': 1, 'tournaments': ['Лига Чемпионов', 'Лига Европы', 'Лига Конференций'], 'players_id': [1, 2]}
]

def home(request):
    return render(request, 'app/index.html', {'data' : {
        'players': PLAYERS,
    }})

def search(request):
    fname = request.GET['text']
    pl_filtered = PLAYERS
    if fname != "":
        pl_filtered = list(filter(lambda x: fname.lower() in x['l_name'].lower(), PLAYERS))

    return render(request, 'app/search.html', {'data' : {
        'players': pl_filtered,
    }})

def player(request, id):
    plr = list(filter(lambda x: x['id'] == id, PLAYERS))[0]
    f_name = plr['f_name']
    l_name = plr['l_name']
    position = plr['position']
    number = plr['number']
    date_birthday = plr['date_birthday']
    country = plr['country']
    country_image = plr['country_image']
    height = plr['height']
    weight = plr['weight']
    birth_place = plr['birth_place']
    pic = plr['pic']
    return render(request, 'app/players.html', {'data' : {
        'f_name': f_name,
        'l_name': l_name,
        'id': id,
        'position': position,
        'number': number,
        'date_birthday': date_birthday,
        'country': country,
        'country_image': country_image,
        'height': height,
        'weight': weight,
        'birth_place': birth_place,
        'pic': pic,
    }})

def basket(request):
    return render(request, 'app/basket.html', {'data' : {
        'players': PLAYERS,
        'requests': REQUESTS,
    }})