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
        self.fart = max(0, self.fart - reduksjon)

    def oppdater(self, dt):
        self.posisjon += self.fart * dt

    def tegn(self, skjerm):
        # 5 piksler på skjermen tilsvarer 1 meter.
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
    # Tid siden forrige oppdatering, målt i sekunder.
    dt = klokke.tick(60) / 1000

    for hendelse in pygame.event.get():
        if hendelse.type == pygame.QUIT:
            kjorer = False

    taster = pygame.key.get_pressed()

    if taster[pygame.K_RIGHT]:
        tog1.ok_fart(2 * dt)

    if taster[pygame.K_LEFT]:
        tog1.brems(4 * dt)

    tog1.oppdater(dt)

    skjerm.fill((135, 206, 235))

    pygame.draw.line(
        skjerm,
        (70, 70, 70),
        (0, 400),
        (900, 400),
        4
    )

    tog1.tegn(skjerm)

    pygame.display.flip()

pygame.quit()