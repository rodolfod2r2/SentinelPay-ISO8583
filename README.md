# Motor de Autorização de Cartões de Benefícios Flexíveis (ISO 8583)

Aplicação **Python 3.11+** com **FastAPI** para autorização de transações baseada na norma **ISO 8583**, com arquitetura multitenant, padrão Strategy (operadoras Visa, Mastercard, Elo) e Chain of Responsibility para a esteira de validação.

## Stack

- **Framework:** FastAPI (assíncrono)
- **Banco de dados:** PostgreSQL com SQLAlchemy 2.0
- **Cache / antifraude:** Redis (Velocity Check)
- **Containerização:** Docker e Docker Compose

## Estrutura de pastas

```
app/
  api/           # Rotas (v1/authorize)
  models/        # SQLAlchemy (Tenants, Clients, Cards, Balances, TransactionLogs)
  rules/         # Chain of Responsibility (integridade, status cartão, MCC, saldo, antifraude)
  schemas/       # Pydantic (request/response)
  services/      # Authorization, Balance, Redis Velocity
  strategies/    # Strategy por operadora (Visa, Mastercard, Elo)
  config.py
  database.py
  main.py
scripts/
  create_tables.py   # Criação das tabelas
  seed_data.py       # Dados iniciais para teste
```

## Como rodar

### Com Docker Compose (recomendado)

1. Subir API, PostgreSQL e Redis:

```bash
docker-compose up -d
```

A API estará em **http://localhost:8000**. O script `create_tables` roda na subida e cria as tabelas.

2. (Opcional) Popular dados de teste (tenant, cartão, saldos):

```bash
docker-compose exec api python -m scripts.seed_data
```

Anote o **Tenant ID** exibido para usar no `metadata.tenant_id` do request.

### Sem Docker (ambiente local)

1. Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# ou: source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

2. Configure o banco e o Redis (ou use os padrões em `app/config.py`). Crie um `.env` se quiser:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/beneficios_flex
REDIS_URL=redis://localhost:6379/0
```

3. Crie as tabelas:

```bash
python -m scripts.create_tables
```

4. (Opcional) Seed:

```bash
python -m scripts.seed_data
```

5. Inicie a API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoint de autorização

- **POST** `/v1/authorize`

Corpo (JSON):

- **metadata:** `tenant_id` (UUID), `operadora` ("Visa" | "Mastercard" | "Elo")
- **iso_8583:** MTI, DE2 (PAN), DE4 (valor), DE18 (MCC), DE42 (Merchant ID), DE48 (CVV), DE49 (moeda)

A API valida na ordem: integridade da mensagem → status do cartão → MCC permitido → saldo (e transbordo se configurado) → velocity check (Redis). Persiste cada tentativa com DE39 (response code) e, se aprovado, debita o saldo da categoria correspondente ao MCC.

## Exemplo de teste com curl

Use o **tenant_id** retornado pelo `seed_data` (ou um UUID de tenant existente). Exemplo com PAN de teste do seed (`4111111111111111`), MCC **5812** (refeição), valor **25.00**:

```bash
curl -X POST "http://localhost:8000/v1/authorize" \
  -H "Content-Type: application/json" \
  -d "{
    \"metadata\": {
      \"tenant_id\": \"SEU_TENANT_ID_AQUI\",
      \"operadora\": \"Visa\"
    },
    \"iso_8583\": {
      \"mti\": \"0100\",
      \"de2_pan\": \"4111111111111111\",
      \"de4_amount\": \"25.00\",
      \"de18_mcc\": \"5812\",
      \"de42_merchant_id\": \"MERCHANT001\",
      \"de48_cvv\": \"123\",
      \"de49_currency\": \"986\"
    }
  }"
```

Resposta esperada (exemplo aprovado):

```json
{
  "approved": true,
  "response_code": "00",
  "message": "Approved",
  "category_used": "refeicao",
  "transaction_id": "uuid-do-log"
}
```

Se o MCC não for permitido ou o saldo for insuficiente, `approved` será `false` e `response_code` trará o código DE39 (ex.: "51" saldo insuficiente, "58" MCC não permitido).

## Regras de validação implementadas

1. **MessageIntegrityHandler** – Integridade da mensagem: PAN, valor, MCC e moeda válidos.
2. **CardStatusHandler** – Cartão existe e está ativo (não bloqueado/cancelado).
3. **MccValidationHandler** – MCC permitido para o tenant e mapeamento para categoria (bolso).
4. **BalanceValidationHandler** – Saldo da categoria; se insuficiente, uso de saldo reserva (transbordo) se a regra do tenant permitir.
5. **AntifraudHandler** – Velocity check via Redis (múltiplas transações em janela curta).

## Documentação da API

- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

## Licença

Uso interno / conforme política do projeto.
