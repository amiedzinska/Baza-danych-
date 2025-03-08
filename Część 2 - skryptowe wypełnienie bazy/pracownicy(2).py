import mysql.connector
from faker import Faker
from unidecode import unidecode 
from datetime import datetime, timedelta

# Ponownie używamy Faker z polskimi danymi
faker = Faker('pl_PL')

# Listy z danymi, żeby łatwiej było je wstawiać skryptem
stanowiska = ['Menedżer ds. Eventów', 'Dyrektor Techniczny', 'Główny Sprzedawca', 'Sprzedawca','Sprzedawca', 'Ppiekun Grupy', 'Opiekun Grupy', 'Opiekun Grupy']
wynagrodzenia = [8000 ,7666, 5400, 5000,5000, 4700, 4700, 4700]
dzialy = ['organizacja', 'organizacja', 'sprzedaż', 'sprzedaż', 'sprzedaż', 'obsługa wycieczek', 'obsługa wycieczek', 'obsługa wycieczek']
statusy_zatrudnienia = ['aktywny', 'na urlopie', 'aktywny', 'aktywny', 'aktywny', 'aktywny','aktywny', 'aktywny']
wyksztalcenie = ['magister', 'inżynier', 'magister', 'magister', 'magister', 'student', 'magister', 'student']

def losuj_date_zatrudnienia():
    dzis = datetime.now()
    max_data = dzis - timedelta(days=365)  # Maksymalna data zatrudnienia (rok temu)
    min_data = dzis - timedelta(days=395)  # Minimalna data zatrudnienia (rok i miesiac temu) - tyle działa nasza firma
    return faker.date_between(start_date=min_data, end_date=max_data).strftime('%Y-%m-%d')

def losuj_date_urodzenia():
    dzis = datetime.now()
    max_data = dzis - timedelta(days=22*365)  # Maksymalna data urodzenia (18 lat temu)
    min_data = dzis - timedelta(days=50*365)  # Minimalna data urodzenia (80 lat temu)
    return faker.date_between(start_date=min_data, end_date=max_data).strftime('%Y-%m-%d')

def losuj_telefon():
    telefon = faker.phone_number()
    telefon = ''.join(filter(str.isdigit, telefon))  # Ponownie przycinamy numer telefonu do 9 znaków
    return telefon[-9:] # Dla pewności pobieramy ostatnie 9 znaków (nr telefonu w faker mają postac +48 XXX XXX XXX)

def uzupelnij_pracownika(indeks):
    plec = faker.random_element(['M', 'K'])
    imie = faker.first_name_male() if plec == 'M' else faker.first_name_female()
    nazwisko = faker.last_name_male() if plec == 'M' else faker.last_name_female()
    telefon = losuj_telefon()
    email = f"{unidecode(imie).lower()}.{unidecode(nazwisko).lower()}@wombat.pl" # Każdy pracownik ma służbowego maila
    
    # Wypełnianie zgodnie z kolejnością list
    stanowisko = stanowiska[indeks]
    wynagrodzenie = wynagrodzenia[indeks]
    dzial = dzialy[indeks]
    status = statusy_zatrudnienia[indeks]
    wykszt = wyksztalcenie[indeks]
    
    data_zatrudnienia = losuj_date_zatrudnienia()
    miasto = faker.city()
    ulica = faker.street_address()
    kod_pocztowy = faker.postcode()
    kraj = "Polska"
    data_urodzenia = losuj_date_urodzenia()
    
    return (imie, nazwisko, telefon, email, stanowisko, data_zatrudnienia, wynagrodzenie, dzial, status, wykszt, miasto, ulica, kod_pocztowy, kraj, data_urodzenia)


db = mysql.connector.connect(
    host='giniewicz.it',
    user='team07',
    password='te@mzaot',
    database='team07'
)

cursor = db.cursor()

def wstaw_do_bazy(cursor, pracownik):
    query = """
        INSERT INTO pracownicy (
            imie, nazwisko, telefon, email, stanowisko, data_zatrudnienia, wynagrodzenie, dzial, 
            status_zatrudnienia, wyksztalcenie, miasto, ulica_i_numer, kod_pocztowy, kraj, data_urodzenia
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, pracownik)
    db.commit()

# Liczba rekordów równa długości list, gdybyśmy chcieli większą ilośc pracowników wystarczy to dopisać wyżej to list
liczba_rekordow = len(stanowiska)

for indeks in range(liczba_rekordow):
    pracownik = uzupelnij_pracownika(indeks)
    wstaw_do_bazy(cursor, pracownik)

cursor.close()
db.close()
