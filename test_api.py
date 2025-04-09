from peopleanalytics.analyzer import EvaluationAnalyzer
from peopleanalytics.data_pipeline import DataPipeline

# Initialize with data dir
analyzer = EvaluationAnalyzer('/home/pimentel/Workspace/data-course/data')
pipeline = DataPipeline('/home/pimentel/Workspace/data-course/data')

# Get years and people - observe que anos e pessoas estão invertidos na estrutura atual
print("NOTA: Na estrutura atual, anos e pessoas estão invertidos no caminho.")
print("A estrutura é: <pessoa>/<ano>/resultado.json em vez de <ano>/<pessoa>/resultado.json")

years = analyzer.get_all_people()  # Na verdade são os anos
people = analyzer.get_all_years()  # Na verdade são as pessoas

print(f"\nAnos disponíveis: {years}")
print(f"Pessoas disponíveis: {people}")

# Print people by year (ajustado)
for year in years:
    year_people = analyzer.get_people_for_year(year)  # Na verdade são os anos disponíveis para a pessoa
    print(f"Anos para {year}: {year_people}")

# Test structure navigation
print("\nExemplo de navegação na estrutura invertida:")
for person in people[:3]:  # Primeiras 3 pessoas (que na verdade são anos)
    print(f"\nDados para o ano {person}:")
    for year in analyzer.get_people_for_year(person):  # Anos são pessoas na estrutura atual
        print(f"  - {year}")

# Ajuste para leitura correta dos conceitos
print("\nTentando ler conceitos considerando a estrutura invertida:")
for ano in years[:2]:  # Primeiros 2 "anos" (que na verdade são pessoas)
    try:
        # Temos que inverter a lógica aqui
        conceito = analyzer.get_conceito_by_year(ano)  # Pessoa sendo tratada como ano
        print(f"Conceito de {ano} (pessoa tratada como ano): {conceito}")
    except Exception as e:
        print(f"Erro ao buscar conceito para {ano}: {e}") 