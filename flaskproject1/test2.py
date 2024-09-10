from datetime import datetime
import pytz

timezone_sao_paulo = pytz.timezone('America/Sao_Paulo')

# Obtém a data e hora atual no timezone de São Paulo
datetime_sao_paulo = datetime.now(timezone_sao_paulo)

print(f"A data e hora atual em São Paulo é: {datetime_sao_paulo}")