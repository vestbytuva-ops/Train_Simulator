class Tog:
    def __init__(self, navn, masse):
        self.navn = navn
        self.masse = masse
        self.fart = 0
        self.posisjon = 0

    def ok_fart(self, endring):
        self.fart += endring

    def brems(self, reduksjon):
        self.fart -= reduksjon

    def oppdater(self, dt):
        self.posisjon += self.fart * dt


tog1 = Tog("Lokomotiv 1", 20000)

tog1.ok_fart(5)
print(tog1.fart)

tog1.ok_fart(3)
print(tog1.fart)

tog1.brems(2)
print(tog1.fart)

tog1.oppdater(2)
print(tog1.posisjon)
