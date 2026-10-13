class Tog:
    def __init__(self, navn, masse):
        self.navn = navn
        self.masse = masse
        self.fart = 0

tog1 = Tog("Lokomotiv 1", 20000)

print(tog1.navn)
print(tog1.masse)
print(tog1.fart)