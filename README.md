# API
Link API no heroku -> 'https://api-walet-renato.herokuapp.com/cashback'

Criada uma api de cadastro e armazenamento de informações a respeito de cashback.

Para realizar um teste em sua máquina, faça o clone do repositório em sua máquina e instale os requirements.
Após isso, pelo terminal, vá até a pasta em que se encontra o arquivo 'walet.py' e execute o comando 'python walet.py'

Através da rota "/cashback" é possível o envio de informaçõs em formato application/json desde que siga as seguintes regras:

1 - Seja utilizado o token específico para autenticação (authentication: 'sha256$BnV47sednVthpJbS$0321c795cb19b49081d3dac3aaff28eaff74e92c24ab78e8051768dd539105ff')

2 - Tenha os seguintes campos obrigatórios (além do token):

  2.1 - sold_at (formato: YYYY-mm-dd HH:MM:SS)
  
  2.2 - customer
    2.2.1 - document (11 dígitos sem '.' nem '-')
    2.2.2 - name (limitado a 50 caracteres para o banco de dados)
    
  2.3 - total (receberemos como str, mas será tratado como float)
  
  3.4 - products (tipo: lista de dicionarios) e dentro de cada dicionário:
    3.4.1 - type (string de caracter único)
    3.4.2 - value (receberemos como str, mas será tratado como float)
    3.4.3 - qty (receberemos como str, mas será tratado como int)
   
3 - Recebendo estas informações são feitas as seguintes validações:
  3.1 - Ajustes em todas as informações recebidas como string, transformando datetime em datetime
  3.2 - Verificação de CPF (atualmente aceita o CPF 00000000000, mas já está com regra implementada, porem comentada, para permitir os testes)
  3.3 - Verificação da data (se a data recebida for 1 minuto maior ou menor do que a data do processamento, será retornada data inválida)
  3.4 - Verificação de formato do type de produto.
 
4 - Feitas as verificações iniciamos o cálculo de cashback
  4.1 - Primeiramente é analisado se o produto indicado é "A", "B" ou "C", que têm cashbacks respectivos de 10%, 5% e 7%, caso não seja nenhum destes, o cashback é 0
  4.2 - Após os cálculos individuais de cashback, é feito o cálculo total da compra (purchase)

5 - Todo cálculo insere a informação do produto / compra no database e, após as conferências ele é salvo

6 - É feito request para a api da mais todos, informando documento do consumidor e o valor total do cashback
  6.1 - Caso a resposta da api não seja positiva, é retornada informação de erro de comunicação
  6.2 - Caso a comunicação seja bem sucedida, é retornado json informando os valores inseridos, o documento e a mensagem "Cashback successfully created".


Segue modelo de request através da library requests:

r = requests.post(mock_url, data=json.dumps(dicionário de informações), headers=mock_header)

obs: mock_url será a url padrão do flask (quando executado ele mostra o ip e porta) + "\cashback"

obs2: mock_header deve ser {'Content-Type': 'application/json'}

obs3: data deve ser transferido como json, por isso json.dumps(dicionário de informações)

obs4: padrão de corpo de requisição:

    {
        "authentication": "sha256$BnV47sednVthpJbS$0321c795cb19b49081d3dac3aaff28eaff74e92c24ab78e8051768dd539105ff",
        "sold_at": "2026-01-02 00:00:00",
        "customer": {
           "document": "00000000000",
           "name": "JOSE DA SILVA"
        },
        "total": "100.00",
        "products": [
           {
              "type": "A",
              "value": "10.00",
              "qty": 1
           },
           {
              "type": "B",
              "value": "10.00",
              "qty": 9
           }
        ]
    }



Dificuldades encontradas:
Relacionamento de bancos.
Criação em si da API.
Identificação no postman do excesso de "," na requisição padrão.
 
Buscas realizadas:
SQLalchemy
SQLalchemy Many to Many
Flask API
Flask API Authentication

fontes:
https://flask-sqlalchemy.palletsprojects.com/en/2.x/
https://www.sqlalchemy.org/
https://pt.stackoverflow.com/
https://stackoverflow.com/
https://youtu.be/WxGBoY5iNXY
https://youtu.be/J5bIPtEbS0Q
https://youtu.be/RIoC1YOY4yc
https://youtu.be/OvhoYbjtiKc


