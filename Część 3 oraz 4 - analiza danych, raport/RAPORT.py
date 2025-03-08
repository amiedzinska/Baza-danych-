import mariadb
import sys
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, Frame

#Próba połączenia z bazą danych
try:
    conn = mariadb.connect(
        user="team07",
        password="te@mzaot",
        host="giniewicz.it",
        port=3306,
        database="team07"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

#Utworzenie kursora do wykonywania zapytań
cur = conn.cursor()

#Funkcja generująca wykres słupkowy i zapisująca go jako obraz
def generate_bar_chart(x, y, title, xlabel, ylabel, filename, colors=None):
    plt.figure(figsize=(10, 6))
    plt.bar(x, y, color=colors, alpha=0.7)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

#Funkcja generująca wykres grupowany słupkowy
def generate_grouped_bar_chart(categories, values_list, labels, colors, title, xlabel, ylabel, filename):
    x = range(len(categories))
    bar_width = 0.25

    plt.figure(figsize=(10, 6))

    for i, values in enumerate(values_list):
        plt.bar([pos + i * bar_width for pos in x], values, bar_width, label=labels[i], color=colors[i], alpha=0.7)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks([pos + bar_width for pos in x], categories, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

#Funkcja generująca wykres liniowy
def generate_line_chart(x, y, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', alpha=0.7)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.grid()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

#Zapytania:
#1
cur.execute("""
    SELECT o.rodzaj_wycieczki, SUM(z.liczba_uczestnikow) AS liczba_klientow
    FROM zrealizowane_wycieczki z
    JOIN oferta o ON z.id_oferty = o.id_oferty
    GROUP BY o.rodzaj_wycieczki
    ORDER BY liczba_klientow DESC;
""")
popular_trips = cur.fetchall()
trip_types = [row[0] for row in popular_trips]
trip_counts = [row[1] for row in popular_trips]

generate_bar_chart(
    trip_types,
    trip_counts,
    "Najpopularniejsze rodzaje wycieczek",
    "Rodzaj wycieczki",
    "Liczba klientów",
    "popular_trips.png",
    colors=["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#FF8C33"]
)


#2
cur.execute("""
    SELECT 
        o.rodzaj_wycieczki, 
        SUM(z.liczba_uczestnikow* o.cena_za_jedna_osobe* (1- IFNULL(p.procent_znizki,0)/100)) AS przychod, 
        SUM(z.liczba_uczestnikow* o.koszt_organizacji_za_jedna_osobe) AS koszt_organizacji,
        SUM(z.liczba_uczestnikow* o.cena_za_jedna_osobe* (1- IFNULL(p.procent_znizki,0) /100))- SUM(z.liczba_uczestnikow * o.koszt_organizacji_za_jedna_osobe) AS zysk
    FROM zrealizowane_wycieczki z
    JOIN oferta o ON z.id_oferty= o.id_oferty
    LEFT JOIN transakcje t ON z.id_zrealizowanej_wycieczki= t.id_zrealizowanej_wycieczki
    LEFT JOIN promocje p ON t.id_promocji= p.id_promocji
    GROUP BY o.rodzaj_wycieczki
    ORDER BY zysk DESC;

""")
financials = cur.fetchall()
financial_trip_types = [row[0] for row in financials]
revenues = [row[1] for row in financials]
expenses = [row[2] for row in financials]
profits = [row[3] for row in financials]
generate_grouped_bar_chart(
    financial_trip_types,
    [revenues, expenses, profits],
    ["Przychód", "Koszt organizacji", "Zysk"],
    ["#87CEEB", "#FFA07A", "#90EE90"],
    "Przychody, Koszty i Zyski według rodzaju wycieczki",
    "Rodzaj wycieczki",
    "Kwota (PLN)",
    "financials.png"
)


#3 POWRACAJACY KLIENCI POPRAWA
cur.execute("""
    SELECT 
        o.rodzaj_wycieczki,
        COUNT(DISTINCT t.id_klienta) AS liczba_powracajacych_klientow
    FROM zrealizowane_wycieczki z
    JOIN oferta o ON z.id_oferty = o.id_oferty
    JOIN transakcje t ON z.id_zrealizowanej_wycieczki = t.id_zrealizowanej_wycieczki
    WHERE t.id_klienta IN (
        SELECT id_klienta
        FROM transakcje
        GROUP BY id_klienta
        HAVING COUNT(DISTINCT id_zrealizowanej_wycieczki) > 1
    )
    GROUP BY o.rodzaj_wycieczki
    ORDER BY liczba_powracajacych_klientow DESC;
""")
ret_clients = cur.fetchall()
trip_types_ret = [row[0] for row in ret_clients]
ret_counts = [row[1] for row in ret_clients]
generate_bar_chart(
    trip_types_ret,
    ret_counts,
    "Powracający klienci według rodzaju wycieczek",
    "Rodzaj wycieczki",
    "Liczba powracających klientów",
    "ret_clients.png",
    colors=["#FFC0CB", "#FF69B4", "#FF1493", "#C71585", "#DB7093", "#BA55D3"]
)


#4
cur.execute("""
    SELECT 
        DATE_FORMAT(data_rozpoczecia, '%Y-%m') AS miesiac, 
        SUM(liczba_uczestnikow) AS liczba_klientow
    FROM zrealizowane_wycieczki
    GROUP BY miesiac
    ORDER BY miesiac;
""")
seasonality = cur.fetchall()
months = [row[0] for row in seasonality]
client_counts = [row[1] for row in seasonality]
generate_line_chart(
    months,
    client_counts,
    "Sezonowość - liczba klientów w miesiącach",
    "Miesiąc",
    "Liczba klientów",
    "seasonality.png"
)


#5
cur.execute("""
    SELECT 
        CONCAT(p.imie, ' ', p.nazwisko) AS pracownik,
        AVG(o.ocena_pracownika) AS srednia_ocena
    FROM opinie o
    JOIN zrealizowane_wycieczki z ON o.id_zrealizowanej_wycieczki = z.id_zrealizowanej_wycieczki
    JOIN pracownicy p ON z.id_pracownika = p.id_pracownika
    GROUP BY pracownik
    ORDER BY srednia_ocena DESC
    LIMIT 3;
""")
employees = cur.fetchall()
employee_names1 = [row[0] for row in employees]
employee_ratings = [row[1] for row in employees]
generate_bar_chart(
    employee_names1,
    employee_ratings,
    "Najlepiej oceniani pracownicy",
    "Pracownik",
    "Średnia ocena",
    "employees.png",
    colors=["#FFC300", "#DAF7A6", "#FF5733"]
)


#6
cur.execute("""
    SELECT 
        o.nazwa_wycieczki AS wycieczka,
        AVG(op.ocena_zrealizowanej_wycieczki) AS srednia_ocena
    FROM opinie op
    JOIN zrealizowane_wycieczki z ON op.id_zrealizowanej_wycieczki = z.id_zrealizowanej_wycieczki
    JOIN oferta o ON z.id_oferty = o.id_oferty
    GROUP BY wycieczka
    ORDER BY srednia_ocena DESC
    LIMIT 3;
""")
best_trips = cur.fetchall()
trip_names = [row[0] for row in best_trips]
trip_ratings = [row[1] for row in best_trips]
generate_bar_chart(
    trip_names,
    trip_ratings,
    "Najlepiej oceniane wycieczki",
    "Wycieczka",
    "Średnia ocena",
    "best_trips.png",
    colors=["#C70039", "#900C3F", "#581845"]
)


#7
cur.execute("""
    SELECT metoda_platnosci, COUNT(id_transakcji) AS liczba_transakcji
    FROM transakcje
    GROUP BY metoda_platnosci
    ORDER BY liczba_transakcji DESC;
""")
payment_methods = cur.fetchall()
methods = [row[0] for row in payment_methods]
transactions = [row[1] for row in payment_methods]
generate_bar_chart(
    methods,
    transactions,
    "Popularność metod płatności",
    "Metoda płatności",
    "Liczba transakcji",
    "payment_methods.png",
    colors=["#2ECC71", "#1ABC9C", "#3498DB", "#9B59B6", "#E74C3C"]
)


#8
cur.execute("""
    SELECT 
        CASE
            WHEN TIMESTAMPDIFF(YEAR, k.data_urodzenia, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
            WHEN TIMESTAMPDIFF(YEAR, k.data_urodzenia, CURDATE()) BETWEEN 26 AND 35 THEN '26-35'
            WHEN TIMESTAMPDIFF(YEAR, k.data_urodzenia, CURDATE()) BETWEEN 36 AND 45 THEN '36-45'
            WHEN TIMESTAMPDIFF(YEAR, k.data_urodzenia, CURDATE()) BETWEEN 46 AND 55 THEN '46-55'
            ELSE '56+'
        END AS przedzial_wiekowy,
        COUNT(k.id_klienta) AS liczba_klientow
    FROM klienci k
    GROUP BY przedzial_wiekowy
    ORDER BY przedzial_wiekowy DESC;
""")
age_groups = cur.fetchall()
age_categories = [row[0] for row in age_groups]
age_counts = [row[1] for row in age_groups]
generate_bar_chart(
    age_categories,
    age_counts,
    "Przedziały wiekowe klientów",
    "Przedział wiekowy",
    "Liczba klientów",
    "age_groups.png",
    colors=["#E67E22", "#F1C40F", "#16A085", "#2980B9", "#8E44AD"]
)


#9
cur.execute("""
    SELECT 
        CONCAT(p.imie, ' ', p.nazwisko) AS pracownik,
        COUNT(z.id_zrealizowanej_wycieczki) AS liczba_wycieczek
    FROM zrealizowane_wycieczki z
    JOIN pracownicy p ON z.id_pracownika = p.id_pracownika
    GROUP BY pracownik
    ORDER BY liczba_wycieczek DESC
    LIMIT 5;
""")
employee_tours = cur.fetchall()
employee_names = [row[0] for row in employee_tours]
tours_count = [row[1] for row in employee_tours]
generate_bar_chart(
    employee_names,
    tours_count,
    "Liczba wycieczek realizowanych przez poszczególnych pracowników",
    "Pracownik",
    "Liczba wycieczek",
    "employee_tours.png",
    colors=["#3498DB", "#E74C3C", "#2ECC71", "#F1C40F", "#9B59B6"]
)


#10
cur.execute("""
    SELECT 
        o.kierunek AS kierunek,
        COUNT(z.id_zrealizowanej_wycieczki) AS liczba_wycieczek
    FROM zrealizowane_wycieczki z
    JOIN oferta o ON z.id_oferty = o.id_oferty
    GROUP BY kierunek
    ORDER BY liczba_wycieczek DESC
    LIMIT 5;
""")
popular_destinations = cur.fetchall()
destinations = [row[0] for row in popular_destinations]
destination_counts = [row[1] for row in popular_destinations]
generate_bar_chart(
    destinations,
    destination_counts,
    "Najczęściej odwiedzane kierunki",
    "Kierunek",
    "Liczba wycieczek",
    "popular_destinations.png",
    colors=["#1ABC9C", "#2ECC71", "#3498DB", "#9B59B6", "#E74C3C"]
)


#11
cur.execute("""
    SELECT 
        rodzaj_wycieczki,
        AVG(liczba_dni) AS srednia_dni
    FROM oferta
    GROUP BY rodzaj_wycieczki
    ORDER BY srednia_dni DESC;
""")
trip_days = cur.fetchall()
trip_types = [row[0] for row in trip_days]
average_days = [row[1] for row in trip_days]
generate_bar_chart(
    trip_types,
    average_days,
    "Średnia liczba dni wycieczek",
    "Rodzaj wycieczki",
    "Średnia liczba dni",
    "average_trip_days.png",
    colors=["#F39C12", "#D35400", "#C0392B", "#2980B9", "#16A085"]
)

#Zamknięcie połączenia z bazą danych
cur.close()
conn.close()


#Przygotowanie pliku PDF z wykresami
#Uzyskujemy absolutną ścieżkę do folderu projektu
project_folder = os.path.dirname(os.path.abspath(__file__))

font_path = "C:/Users/user/PycharmProjects/pythonProject6/DejaVuSans.ttf"
# font_path = os.path.join(project_folder, 'DejaVuSans', 'DejaVuSans.ttf')


#Rejestrujemy czcionkę DejaVu
if not os.path.exists(font_path):
    raise FileNotFoundError(f"Czcionka DejaVuSans.ttf nie została znaleziona w: {font_path}")
pdfmetrics.registerFont(TTFont('DejaVu', font_path))

#Ścieżka do pliku PDF
pdf_file = "raport_wycieczki_pelny.pdf"
c = canvas.Canvas(pdf_file, pagesize=letter)

#Lista sekcji do raportu PDF
sections = [
    ("Najpopularniejsze wycieczki", "popular_trips.png"),
    ("Koszt, przychody i zyski według rodzaju wycieczki", "financials.png"),
    ("Sezonowość", "seasonality.png"),
    ("Powracający klienci","ret_clients.png"),
    ("Najlepiej oceniani pracownicy", "employees.png"),
    ("Najlepiej oceniane wycieczki", "best_trips.png"),
    ("Popularność metod płatności", "payment_methods.png"),
    ("Przedziały wiekowe klientów", "age_groups.png"),
    ("Najbardziej aktywni pracownicy", "employee_tours.png"),
    ("Najczęściej odwiedzane kierunki", "popular_destinations.png"),
    ("Średnia liczba dni wycieczek", "average_trip_days.png")
]
def add_conclusion_to_pdf(canvas, title, conclusion):
    canvas.setFont("DejaVu", 12)
    y_position = 350  #Pozycja początkowa tekstu
    for line in conclusion.split('\n'):
        canvas.drawString(100, y_position, line)
        y_position -= 20

#Wnioski do wszystkich zapytań
conclusions = {
    "Najpopularniejsze wycieczki": (
        '''
        Najczęściej wybierane wycieczki to wycieczki przygodowe i rozrywkowe, co sugeruje, że klienci są zainteresowani aktywnym wypoczynkiem oraz możliwością poznawania nowych miejsc. 
        Wycieczki kulturowe, choć mniej popularne, mogą być bardziej atrakcyjne, jeśli zostaną wzbogacone o np. warsztaty, gry terenowe lub niższe ceny. 
        Warto również przeanalizować, czy istnieje możliwość promocji mniej popularnych wycieczek wśród określonych grup wiekowych, aby lepiej dopasować ofertę do ich preferencji.
        '''
    ),

    "Koszt, przychody i zyski według rodzaju wycieczki": (
        '''
        Firma pomimo barwnej i szerokiej oferty która trafia do dużej ilości klientów odnotowywuje duże straty.
        Wykres jest bardzo alarmujący, zarząd powinien poważnie przemyśleć i rozplanować budżet na ten rok.
        Obecnie jedyną naszą atrakcją jaka się zwraca to "sylwester ze Skolimem", może powinniśmy w tym roku przemyśleć poszerzenie oferty o rozrywkowe i okolicznościowe atrakcje. 
        Choć sytuacja firmy nie jest krytyczna, należy rozważyć takie kroki, jak redukcja zbędnych kosztów, wstrzymanie promocji na pewien czas lub ewentualne skorzystanie z kredytu w celu poprawy płynności finansowej.
        
        '''
    ),

    "Sezonowość": (
        '''
        Na samym początku firma dzięki noworocznemu koncertowi Skolima i dobremu marketingowi odniosła sukces i przyciągneła wiele klientów.
        Później liczba klientów ma tendencje spadkową. 
        Maj, ze względu na kryzys w naszej kadrze pracowniczej okazał się naszym najgorszym miesiącem.
        Firma odnotowuje największą liczbę klientów w miesiącach letnich (lipiec, sierpień), co sugeruje silny wzrost w okresie wakacyjnym. 
        Warto wzmocnić promocję w okresach poza sezonem, aby lepiej zbalansować działalność w ciągu roku.
        '''
    ),
    "Powracający klienci":(
        ''' 
        Powracający klient to taki, który brał udział w więcej niż jednej wycieczce.
        Na podstawie wykresu przedstawiającego liczbę powracających klientów w podziale na rodzaj wycieczek można zauważyć, że po wycieczkach przygodowych oraz rozrywkowych klienci wracają najchętniej. 
        Wycieczki tematyczne, wypoczynkowe i ekspedycjne również mają stabilne grono klientów, jednak ich popularność jest wyraźnie mniejsza. 
        Najsłabszym ogniwem po raz kolejny są wycieczki kulturowe.
        Wnioski te sugerują, że firma powinna skupić się na rozwijaniu różnorodności oferty przygodowej i rozrywkowej.
        '''

    ),

    "Najlepiej oceniani pracownicy": (
        f'''
        Najlepiej oceniany pracownik to {employee_names1[0]}, z najwyższą średnią ocen klientów. 
        Warto przeznaczyć dodatkowe środki z budżetu na premię dla tego pracownika. Koniecznie musimy przeanalizować, co przyczynia się do jego sukcesów.
        '''
    ),

    "Najlepiej oceniane wycieczki": (
       '''
        Najwyższe oceny w tym roku uzyskała wycieczka do Laponii tuż za nią uplasowała się fantastyczna noworoczna zabawa ze Skolimem a trzecie miejsce zajęła egzotyczna podróż wzdłuż Amazonki. 
        Jest to wyraźny sygnał, że nasi klienci lubią dalekie podróże i nasz starannie zaplanowany harmonogram spełnia ich oczekiwania. Wycieczki o niższych ocenach należy przeanalizować pod kątem potencjalnych problemów, takich jak jakość obsługi, brak atrakcji czy wygórowane ceny. 
        Rozwiązanie tych problemów może przyczynić się do poprawy opinii klientów i zwiększenia liczby uczestników.
        '''
    ),

    "Popularność metod płatności": (
        '''
        Obie metody płatności cieszą się niemal identyczną popularnością. 
        Liczba transakcji jest bardzo zbliżona, co sugeruje, że użytkownicy w równym stopniu korzystają z obu form płatności. 
        Może to świadczyć dobrze o ich zbilansowanej dostępności i wygodzie.
        '''
    ),

    "Przedziały wiekowe klientów": (
        '''
        Najliczniejszą grupę stanowią osoby w wieku 50+, co sugeruje, że oferta firmy najbardziej odpowiada starszym klientom.
        Osoby w przedziałach wiekowych 36-50 oraz 26-35 również są liczne, ale w mniejszym stopniu niż grupa 50+.
        Najmniej klientów pochodzi z grupy wiekowej 18-25, co może sugerować, że oferta firmy jest mniej atrakcyjna dla młodszych lub może być związane z ich ograniczonymi możliwościami finansowymi.
        Firma powinna skoncentrować się na dalszym rozwijaniu ofert dla starszych klientów (50+), jednocześnie analizując, dlaczego młodsi klienci są mniej zainteresowani. 
        '''
    ),

    "Najbardziej aktywni pracownicy": (
        f'''
        {employee_names[0]} jest najbardziej aktywnym pracownikiem, realizującym największą liczbę wycieczek. 
        {employee_names[1]} zajmuje drugie miejsce, a {employee_names[2]} jest trzeci najbardziej aktywny z tej grupy. 
        Można rozważyć, czy różnice w liczbie realizowanych wycieczek wynikają z kompetencji, doświadczenia, preferencji klientów, czy obciążenia pracą.
        '''
    ),

    "Najczęściej odwiedzane kierunki": (
        '''
        Polska jest zdecydowanie najpopularniejszym kierunkiem wycieczek. To może wskazywać na większe zainteresowanie lokalnymi podróżami w porównaniu do zagranicznych. Przyczyny mogą być różnorodne: niższe koszty, łatwiejszy dostęp, mniejsze bariery językowe czy popularność rodzimych atrakcji.
        Kierunki zagraniczne, takie jak Brazylia, Kenia, Szkocja i Grecja, mają dużo mniejszą popularność. Może to wynikać m. in. z wyższych kosztów lub ograniczonego budżetu klientów.
        Warto byłoby rozważyć promocję ofert zagranicznych, szczególnie w popularnych kierunkach, takich jak Grecja czy Szkocja, które mogą być bardziej przystępne niż Brazylia czy Kenia. Warto także przeanalizować, czy istnieje potencjał zwiększenia popytu na oferty zagraniczne.
        '''
    ),

    "Średnia liczba dni wycieczek": (
        '''
        Najdłuższe wycieczki to ekspedycje i wyjazdy wypoczynkowe – średnio trwają około 14 dni.
        Wycieczki kulturowe są nieco krótsze (około 10 dni), a wycieczki przygodowe trwają jeszcze mniej (około 6 dni).
        Najkrótsze wyjazdy to tematyczne i rozrywkowe, trwające odpowiednio 3 i 1 dzień, co może wynikać z ich charakteru (np. lokalne atrakcje, krótkie wydarzenia).
        Preferencje klientów wydają się zróżnicowane pod względem czasu trwania, co może być podstawą do segmentacji oferty. 
        Warto byłoby zastanowić się, jak dostosować oferty wycieczek do różnych preferencji czasowych klientów.
        '''
     )
}

#Dodanie wykresów i wniosków do raportu PDF
#Importy
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

#Styl tekstu
styles = getSampleStyleSheet()
justified_style = ParagraphStyle(
    'Justified',
    parent=styles['Normal'],
    alignment=TA_JUSTIFY,
    fontName='DejaVu',
    fontSize=12,
    leading=14
)

#W pętli dodawania wniosków do PDF:
for title, image in sections:
    c.setFont("DejaVu", 16)
    c.drawString(100, 750, title)
    c.drawImage(ImageReader(image), 100, 400, width=400, height=300)
    if title in conclusions:
        conclusion_text = conclusions[title]
        conclusion_para = Paragraph(conclusion_text, justified_style)
        frame_width = 400
        frame_height = 200
        x = 100
        y = 150
        conclusion_frame = Frame(x, y, frame_width, frame_height, showBoundary=0)
        conclusion_frame.addFromList([conclusion_para], c)
    c.showPage()

c.save()

print(f"Raport PDF został wygenerowany pod nazwą: {pdf_file}")


