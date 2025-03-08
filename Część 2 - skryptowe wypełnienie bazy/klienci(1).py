import random
from datetime import datetime, timedelta
import mysql.connector
from faker import Faker
from unidecode import unidecode  # Usuwanie polskich znaków

# Faker dla polskiej lokalizacji - pakiet który losuje dane
faker = Faker('pl_PL')

def losuj_date_urodzenia():
    dzis = datetime.now()
    max_data = dzis - timedelta(days=18*365)  # Maksymalna data urodzenia (18 lat temu)
    min_data = dzis - timedelta(days=80*365)  # Minimalna data urodzenia (80 lat temu)
    return faker.date_between(start_date=min_data, end_date=max_data).strftime('%Y-%m-%d')

def losuj_telefon():
    # Generowanie numeru telefonu z zakresu 9 cyfr, bo taki limit mamy w bazie
    return "".join([str(random.randint(0, 9)) for _ in range(0,9)])

def losuj_klienta(plec):
    # Losowanie imienia i nazwiska w zależności od płci (nie jest to konieczne)
    imie = faker.first_name_male() if plec == 'M' else faker.first_name_female()
    nazwisko = faker.last_name_male() if plec == 'M' else faker.last_name_female()
    
    # Usuwanie polskich znaków z imienia i nazwiska do e-maila
    imie_email = unidecode(imie).lower()
    nazwisko_email = unidecode(nazwisko).lower()
    email = f"{imie_email}.{nazwisko_email}@gmail.com" # Założenie, że każdy jest użytkownikiem gmaila
    
    # Generowanie losowych danych
    telefon = losuj_telefon()
    telefon_alarmowy = losuj_telefon()
    miasto = faker.city()
    ulica = faker.street_address()
    kod_pocztowy = faker.postcode()
    kraj = "Polska"
    data_urodzenia = losuj_date_urodzenia()
    
    return (imie, nazwisko, telefon, telefon_alarmowy, email, miasto, ulica, kod_pocztowy, kraj, data_urodzenia)

db = mysql.connector.connect(
    host='giniewicz.it',
    user='team07',
    password='te@mzaot',
    database='team07'
)

cursor = db.cursor()

def wstaw_do_bazy(cursor, klient):
    query = """
        INSERT INTO klienci (imie, nazwisko, telefon, telefon_alarmowy, email, miasto, ulica_i_Numer, kod_pocztowy, kraj, data_urodzenia) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, klient)
    db.commit()

# Wybór liczby rekordów do wstawienia
liczba_rekordow = 183 # W bazie danych brakuje indeksu 74 przez fakt, że mail przy generowaniu się powtórzył i wyskoczył error.
# Miała tu być okrągła liczba ale przez ten włańsnie problem stanęło na 183

# Losowanie płci jest wynikiem wcześniejszy prób wypełniania bazych przez dane GUSu
for _ in range(liczba_rekordow):
    plec = random.choice(['M', 'K'])
    klient = losuj_klienta(plec)
    
    wstaw_do_bazy(cursor, klient)
    print(f'Wstawiono klienta: {klient}')

cursor.close()
db.close()

