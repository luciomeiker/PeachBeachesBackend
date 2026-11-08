from decimal import Decimal

from django.core.management.base import BaseCommand

from productos.models import Categoria, Producto

# (categoría, descripción, [(nombre, descripción, marca, precio, stock), ...])
DATOS = [
    (
        'Accesorios de playa',
        'Todo para armar tu día de playa.',
        [
            ('Sombrilla playera 2m', 'Sombrilla con protección UV50+ y mástil inclinable.', 'SolMar', '18500.00', 25),
            ('Reposera plegable', 'Reposera de aluminio con respaldo reclinable en 4 posiciones.', 'Costa', '32900.00', 18),
            ('Conservadora 24L', 'Conservadora rígida que mantiene el frío hasta 24 horas.', 'IceBox', '27800.00', 12),
            ('Toalla de microfibra', 'Toalla de secado rápido, liviana y compacta.', 'SolMar', '9900.00', 40),
        ],
    ),
    (
        'Indumentaria',
        'Ropa y calzado para el verano.',
        [
            ('Malla entera Coral', 'Malla entera con secado rápido y filtro UV.', 'Oleaje', '21500.00', 15),
            ('Short de baño', 'Short de baño con bolsillos y cintura elástica.', 'Oleaje', '14500.00', 30),
            ('Gorra con visera', 'Gorra de algodón ajustable.', 'Costa', '7600.00', 50),
            ('Ojotas livianas', 'Ojotas antideslizantes de goma.', 'Costa', '8400.00', 60),
        ],
    ),
    (
        'Cuidado personal',
        'Protección y cuidado para la piel.',
        [
            ('Protector solar FPS 50', 'Protector solar resistente al agua, 200 ml.', 'DermaSol', '12900.00', 35),
            ('Bálsamo labial FPS 30', 'Bálsamo con protección solar para labios.', 'DermaSol', '3200.00', 80),
        ],
    ),
    (
        'Deportes y juegos',
        'Diversión en el mar y en la arena.',
        [
            ('Kit de snorkel', 'Máscara y snorkel con válvula antiingreso de agua.', 'Aqua', '19800.00', 10),
            ('Pelota de playa', 'Pelota inflable de 40 cm.', 'Aqua', '4500.00', 45),
        ],
    ),
]


class Command(BaseCommand):
    help = 'Carga categorías y productos de ejemplo (se puede ejecutar varias veces sin duplicar).'

    def handle(self, *args, **options):
        creados = 0
        actualizados = 0
        for nombre_cat, desc_cat, productos in DATOS:
            categoria, _ = Categoria.objects.get_or_create(
                nombre=nombre_cat, defaults={'descripcion': desc_cat}
            )
            for nombre, descripcion, marca, precio, stock in productos:
                _, creado = Producto.objects.update_or_create(
                    nombre=nombre,
                    defaults={
                        'descripcion': descripcion,
                        'marca': marca,
                        'precio': Decimal(precio),
                        'stock': stock,
                        'categoria': categoria,
                        'imagen': f'https://placehold.co/600x400?text={nombre.replace(" ", "+")}',
                    },
                )
                if creado:
                    creados += 1
                else:
                    actualizados += 1
        self.stdout.write(self.style.SUCCESS(
            f'Productos creados: {creados} | actualizados: {actualizados}'
        ))
