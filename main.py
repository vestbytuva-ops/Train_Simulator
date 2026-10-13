import pygame


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

    def tegn(self, skjerm):
        # Gjør posisjonen i meter om til piksler.
        x = round(100 + self.posisjon * 5)

        pygame.draw.rect(
            skjerm,
            (200, 50, 50),
            (x, 355, 120, 45)
        )


pygame.init()

skjerm = pygame.display.set_mode((900, 500))
pygame.display.set_caption("Train Simulator")
klokke = pygame.time.Clock()

tog1 = Tog("Lokomotiv 1", 20000)

kjorer = True

while kjorer:
    dt = klokke.tick(60) / 1000

    for hendelse in pygame.event.get():
        if hendelse.type == pygame.QUIT:
            kjorer = False

    tog1.oppdater(dt)

    skjerm.fill((135, 206, 235))

    # Tegn skinnen.
    pygame.draw.line(
        skjerm, (70, 70, 70),
        (0, 400), (900, 400), 4
    )

    tog1.tegn(skjerm)

    pygame.display.flip()

pygame.quit()