### City simulation. v1.2

Цель проекта: создать программу, которая даст возможности пользователю внести необходимое для него количество городов и просимулирует исход.

Возможности пользователя:
- указать количество городов в мире;
- указать название каждого города;
- указать количество изначальных ресурсов для каждого города;
- указать изначальное количество людей в каждом городе.

## Ресурсы
В данном мире существует 6 ресурсов:
- water (вода);
- food (еда);
- wood (дерево);
- ore (руда);
- stone (камень);
- metal (металл).

Людям необходима вода, еда и дерево чтобы выживать, а также, дерево, руда, камень и металл чтобы строить новые здания.

## Здания
Здания делятся на производственные и жилые. У каждого здания есть определённые уровни. Они влияют на количество рабочих мест и коэффициент добычи ресурса в зависимости от опыта работника (производственные здания), или на удобное максимальное количество проживающих людей (жилые). Если у семьи количество людей больше, чем уровень удобного максимального количества проживающих людей в их доме, то они подают запрос на улучшение дома.

## Запросы
Логика городов построена на реакционной модели базирующейся на запросах. В мире существует словарь запросов. В зависимости от потребностей города и индивидов, через словарь запросов, в главный план города поступают команды по постройке или улучшению зданий.

## Требования

Модули:
- re;
- random;
- json;
- time;
- math;
- prettytable = 2.0.0;
- matplotlib = 3.3.4.

## Планы
- Мировые ивенты (катаклизмы, войны, торговля и т.д.);
- Создание правительств в каждом городе.
