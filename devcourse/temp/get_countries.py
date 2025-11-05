import requests

response = requests.get("https://restcountries.com/v3.1/all?fields=name,area,population")
countries = response.json()

for i, country in enumerate(countries):
    name = country['name']['common']
    population = country['population']
    area = country['area']
    print(
        f"{i+1}번째 국가: {name} \n인구수: {population}\n크기: {area}" 
    )
    if i == 5:
        break
