from datetime import date
from decimal import Decimal
from .models import ValeurLiquidative
import random

def valeur_liquidative(request):
    aujourd_hui = date.today()

    try:
        vl = ValeurLiquidative.objects.get(date=aujourd_hui)
        created = False
    except ValeurLiquidative.DoesNotExist:
        derniere_vl = ValeurLiquidative.objects.order_by('-date').first()
        valeur_precedente = derniere_vl.valeur if derniere_vl else Decimal('100.0')

        variation = Decimal(str(round(random.uniform(-2, 2), 2)))
        valeur_precedente = Decimal(str(valeur_precedente))
        nouvelle_valeur = valeur_precedente + variation

        vl = ValeurLiquidative(
            date=aujourd_hui,
            valeur=nouvelle_valeur,
            variation=variation,
            est_positive=variation > 0
        )
        vl.save()
        created = True

    return {'vl': vl}
