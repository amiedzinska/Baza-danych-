import random
import mysql.connector

# Połączenie z bazą danych
db = mysql.connector.connect(
    host='giniewicz.it',
    user='team07',
    password='te@mzaot',
    database='team07'
)

cursor = db.cursor()

liczba_klientow = 183 # Najwyższe id klienta
liczba_transakcji = 569  # Suma liczby osób z każdej wycieczki (zakładamy, że każdy zapłacił za siebie lub po prostu tak ta płatność została zarejestrowana)

# Listy ze stałymi wartościami zgodnymi z innymi tabelami
metoda_platnosci = ["gotówka na miejscu zbiórki", "karta na miejscu zbiórki"]
status_transakcji = "zrealizowano"
promocje = [None, 1, 2, 3, 4, 5]
waluta = "PLN"
id_pracownikow = [3, 4, 5]

# Dane z tabeli id_zrealizowanej_wycieczki i liczba uczestników
zrealizowane_wycieczki = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
]
liczba_uczestnikow = [
    100, 22, 40, 21, 16, 50, 35, 10, 20, 20, 20, 35, 42, 38, 45, 23, 32
]

# Rozszerzenie listy wycieczek na podstawie liczby uczestników
rozszerzone_wycieczki = []
for id_wycieczki, uczestnicy in zip(zrealizowane_wycieczki, liczba_uczestnikow):
    rozszerzone_wycieczki.extend([id_wycieczki] * uczestnicy)

# Lista przycięta do wymaganej liczby transakcji
rozszerzone_wycieczki = rozszerzone_wycieczki[:liczba_transakcji]

try:
    # Pobranie istniejących ID klientów
    cursor.execute("SELECT id_klienta FROM klienci")
    istniejacy_klienci = {row[0] for row in cursor.fetchall()}

    # Generowanie i wstawianie transakcji
    for i in range(liczba_transakcji):
        id_klienta = i % liczba_klientow + 1 # ID klienta od 1 do 183 w cyklu

        # Pomijanie, jeśli klient nie istnieje
        if id_klienta not in istniejacy_klienci:
            print(f"Ostrzeżenie: Klient o ID {id_klienta} nie istnieje w bazie danych. Pomijanie transakcji.") # Tu dostaliśmy błąd dla ID 78
            continue

        id_zrealizowanej_wycieczki = rozszerzone_wycieczki[i]  # ID wycieczki
        platnosc = random.choice(metoda_platnosci)  # Losowa metoda płatności
        id_promocji = random.choice(promocje)  # Losowa promocja lub jej brak
        id_pracownika = random.choice(id_pracownikow)  # Losowy pracownik odpowiedzialny za sprzedaż

        query = """
        INSERT INTO transakcje (
            id_klienta, id_zrealizowanej_wycieczki, metoda_platnosci, 
            status_transakcji, id_promocji, waluta, id_pracownika
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            id_klienta,
            id_zrealizowanej_wycieczki,
            platnosc,
            status_transakcji,
            id_promocji,
            waluta,
            id_pracownika
        )

        cursor.execute(query, values)

    db.commit()

except mysql.connector.Error as err:
    print(f"Błąd: {err}")

finally:
    cursor.close()
    db.close()
