-- pracownicy
CREATE TABLE pracownicy (
    id_pracownika INT AUTO_INCREMENT PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    telefon VARCHAR(15) CHECK (telefon REGEXP '^[0-9]{9,15}$'),
    email VARCHAR(100) UNIQUE,
    stanowisko VARCHAR(50),
    data_zatrudnienia DATE NOT NULL,
    wynagrodzenie DECIMAL(10, 2) CHECK (wynagrodzenie >= 0),
    dzial VARCHAR(50),
    status_zatrudnienia VARCHAR(20),
    wyksztalcenie VARCHAR(50),
    miasto VARCHAR(50),
    ulica_i_numer VARCHAR(100),
    kod_pocztowy CHAR(6) CHECK (kod_pocztowy REGEXP '^[0-9]{2}-[0-9]{3}$'),
    kraj VARCHAR(50),
    data_urodzenia DATE
);


-- klienci
CREATE TABLE klienci (
    id_klienta INT AUTO_INCREMENT PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    telefon VARCHAR(15) CHECK (telefon REGEXP '^[0-9]{9,15}$'),
    telefon_alarmowy VARCHAR(15) CHECK (telefon_alarmowy REGEXP '^[0-9]{9,15}$'),
    email VARCHAR(100) UNIQUE,
    miasto VARCHAR(50),
    ulica_i_numer VARCHAR(100),
    kod_pocztowy CHAR(6) CHECK (kod_pocztowy REGEXP '^[0-9]{2}-[0-9]{3}$'),
    kraj VARCHAR(50),
    data_urodzenia DATE
);


-- oferta
CREATE TABLE oferta (
    id_oferty INT AUTO_INCREMENT PRIMARY KEY,
    nazwa_wycieczki VARCHAR(100) NOT NULL,
    rodzaj_wycieczki VARCHAR(50),
    kierunek VARCHAR(100),
    liczba_dni INT,
    cena_za_jedna_osobe DECIMAL(10, 2) NOT NULL CHECK (cena_za_jedna_osobe >= 0),
    atrakcje TEXT,
    miejsce_zameldowania VARCHAR(100),
    wyzywienie VARCHAR(50),
    miasto VARCHAR(50),
    opis TEXT,
    koszt_organizacji_za_jedna_osobe decimal(10,2)
);


-- zrealizowane wycieczki
CREATE TABLE zrealizowane_wycieczki (
    id_zrealizowanej_wycieczki INT AUTO_INCREMENT PRIMARY KEY,
    id_oferty INT,
    id_pracownika INT,
    data_rozpoczecia DATE NOT NULL,
    data_zakonczenia DATE NOT NULL CHECK (data_zakonczenia > data_rozpoczecia),
    liczba_uczestnikow INT CHECK (liczba_uczestnikow >= 0),
    FOREIGN KEY (id_oferty) REFERENCES oferta(id_oferty),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika)
);


-- opinie
CREATE TABLE opinie (
    id_opinia INT AUTO_INCREMENT PRIMARY KEY,
    id_klienta INT,
    id_zrealizowanej_wycieczki INT,
    data_dodania DATE NOT NULL,
    ocena_zrealizowanej_wycieczki INT CHECK (ocena_zrealizowanej_wycieczki BETWEEN 1 AND 5),
    ocena_pracownika INT CHECK (ocena_pracownika BETWEEN 1 AND 5),
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta),
    FOREIGN KEY (id_zrealizowanej_wycieczki) REFERENCES zrealizowane_wycieczki(id_zrealizowanej_wycieczki)
);


-- promocje
CREATE TABLE promocje (
    id_promocji INT AUTO_INCREMENT PRIMARY KEY,
    nazwa_promocji TEXT,
    procent_znizki DECIMAL(5, 2) CHECK (procent_znizki BETWEEN 0 AND 100),
    kod_promocyjny VARCHAR(20) UNIQUE
);


-- transakcje
CREATE TABLE transakcje (
    id_transakcji INT AUTO_INCREMENT PRIMARY KEY,
    id_klienta INT,
    id_zrealizowanej_wycieczki INT,
    metoda_platnosci VARCHAR(50),
    status_transakcji VARCHAR(50),
    id_promocji INT,
    waluta VARCHAR(3),
    id_pracownika INT,
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta),
    FOREIGN KEY (id_zrealizowanej_wycieczki) REFERENCES zrealizowane_wycieczki(id_zrealizowanej_wycieczki),
    FOREIGN KEY (id_promocji) REFERENCES promocje(id_promocji),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika)
);
