
Plansza = {'7': ' ', '8': ' ', '9': ' ',
            '4': ' ', '5': ' ', '6': ' ',
            '1': ' ', '2': ' ', '3': ' '}
Klawisze_Plansza = []
for Klawisz in Plansza:
    Klawisze_Plansza.append(Klawisz)
def printBoard(board):
    print(board['7'] + '|' + board['8'] + '|' + board['9'])
    print('-+-+-')
    print(board['4'] + '|' + board['5'] + '|' + board['6'])
    print('-+-+-')
    print(board['1'] + '|' + board['2'] + '|' + board['3'])
def Gra():
    ruch2 = 'X'
    Ilosc = 0

    for i in range(10):
        printBoard(Plansza)
        print("Twoj ruch," + ruch2 + ".Gdzie chcesz postawic znak?")
        Ruch = input()
        if Plansza[Ruch] == ' ':
            Plansza[Ruch] = ruch2
            Ilosc += 1
        else:
            print("To miejsce jest juz zajete\nGdzie chcesz postawic znak?")
            continue
        if Ilosc >= 5:
            if Plansza['7'] == Plansza['8'] == Plansza['9'] != ' ':
                printBoard(Plansza)
                print("\nKoniec.\n")
                print(" **** " + ruch2 + " Wygral. ****")
                break
            elif Plansza['4'] == Plansza['5'] == Plansza['6'] != ' ':
                printBoard(Plansza)
                print("\Koniec.\n")
                print(" **** " + ruch2 + " Wygral ****")
                break
            elif Plansza['1'] == Plansza['2'] == Plansza['3'] != ' ':
                printBoard(Plansza)
                print("\nKoniec\n")
                print(" **** " + ruch2 + " Wygral ****")
                break
            elif Plansza['1'] == Plansza['4'] == Plansza['7'] != ' ':
                printBoard(Plansza)
                print("\nKoniec.\n")
                print(" **** " + ruch2 + " Wygral ****")
                break
            elif Plansza['2'] == Plansza['5'] == Plansza['8'] != ' ':
                printBoard(Plansza)
                print("\nGame Over.\n")
                print(" **** " + ruch2 + " Wygral ****")
                break
            elif Plansza['3'] == Plansza['6'] == Plansza['9'] != ' ':
                printBoard(Plansza)
                print("\nKoniec.\n")
                print(" **** " + ruch2 + " Wygral ****")
                break
            elif Plansza['7'] == Plansza['5'] == Plansza['3'] != ' ':
                printBoard(Plansza)
                print("\Koniec\n")
                print(" **** " + ruch2 + " Wygral ****")
                break
            elif Plansza['1'] == Plansza['5'] == Plansza['9'] != ' ':
                printBoard(Plansza)
                print("\nKoniec\n")
                print(" **** " + ruch2 + " Wygral ****")
                break
        if Ilosc == 9:
            print("\nKoniec\n")
            print("Remis")
        if ruch2 == 'X':
            ruch2 = 'O'
        else:
            ruch2 = 'X'
    restart = input("Czy chcesz zagrac ponowanie [T/N]")
    if restart == "t" or restart == "T":
        for key in Klawisze_Plansza:
            Plansza[key] = " "

        Gra()
if __name__ == "__main__":
    Gra()