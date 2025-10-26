# Sistema de Avaliação de Conversas com IA

Este documento descreve como usar o sistema de avaliação (rating) para conversas com a IA.

## Visão Geral

O sistema permite que usuários avaliem suas conversas com a IA atribuindo uma nota de **0 a 5** e opcionalmente um comentário.

### Características:
- Nota de 0 a 5 (inteiro)
- Comentário opcional (até 1000 caracteres)
- Permite re-avaliar (atualiza a nota anterior)
- Funciona para usuários autenticados e anônimos
- Estatísticas agregadas para admins e usuários

## Campos adicionados ao modelo Chat

```python
rating: int | None              # Nota de 0 a 5
rating_comment: str | None      # Comentário opcional
rated_at: datetime | None       # Timestamp da avaliação
```

## Endpoints da API

### 1. Avaliar uma conversa

**POST** `/chats/{chat_id}/rating`

Avalia ou re-avalia uma conversa.

**Request Body:**
```json
{
  "rating": 4,
  "comment": "A IA foi muito útil e esclarecedora!"
}
```

**Response:**
```json
{
  "chat_id": 123,
  "rating": 4,
  "rating_comment": "A IA foi muito útil e esclarecedora!",
  "rated_at": "2025-10-26T11:05:40.064437",
  "message": "Avaliação registrada com sucesso"
}
```

**Validações:**
- Rating deve estar entre 0 e 5
- Comentário não pode ter mais de 1000 caracteres
- Apenas o dono do chat pode avaliar (ou sessão anônima correspondente)

---

### 2. Estatísticas gerais de avaliações (Admin)

**GET** `/chats/stats/ratings`

Retorna estatísticas agregadas de todas as conversas avaliadas.

**Autenticação:** Requer admin

**Response:**
```json
{
  "total_ratings": 150,
  "average_rating": 4.2,
  "rating_distribution": {
    "0": 2,
    "1": 5,
    "2": 10,
    "3": 28,
    "4": 55,
    "5": 50
  },
  "total_chats": 300,
  "percentage_rated": 50.0
}
```

**Dados retornados:**
- `total_ratings`: Número de conversas avaliadas
- `average_rating`: Média das notas (0-5)
- `rating_distribution`: Contagem de cada nota (0-5)
- `total_chats`: Total de conversas no sistema
- `percentage_rated`: % de conversas avaliadas

---

### 3. Estatísticas do usuário

**GET** `/chats/user/ratings`

Retorna estatísticas das conversas do usuário autenticado.

**Autenticação:** Requer autenticação

**Response:**
```json
{
  "total_ratings": 10,
  "average_rating": 4.5,
  "rating_distribution": {
    "0": 0,
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4
  },
  "total_chats": 15,
  "percentage_rated": 66.67
}
```

---

## Endpoints de Chat (CRUD completo)

### Criar chat
**POST** `/chats`
```json
{
  "title": "Ajuda com documentos",
  "session_id": "abc123"  // Opcional, para usuários anônimos
}
```

### Listar chats
**GET** `/chats?page=1&page_size=20`

Para usuários anônimos, forneça `session_id`:
**GET** `/chats?session_id=abc123`

### Obter chat com mensagens
**GET** `/chats/{chat_id}`

### Atualizar chat
**PATCH** `/chats/{chat_id}`
```json
{
  "title": "Novo título",
  "summary": "Resumo da conversa",
  "is_active": true
}
```

### Deletar chat
**DELETE** `/chats/{chat_id}`

### Adicionar mensagem
**POST** `/chats/{chat_id}/messages`
```json
{
  "content": "Olá, preciso de ajuda!",
  "role": "user"
}
```

### Listar mensagens
**GET** `/chats/{chat_id}/messages?limit=100`

---

## Exemplos de Uso

### Exemplo 1: Fluxo completo de uma conversa avaliada

```bash
# 1. Criar chat
curl -X POST http://localhost:8000/chats \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Ajuda com CPF"}'

# Response: {"id": 123, ...}

# 2. Adicionar mensagens
curl -X POST http://localhost:8000/chats/123/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Como faço para tirar CPF?", "role": "user"}'

curl -X POST http://localhost:8000/chats/123/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Para tirar o CPF você precisa...", "role": "assistant"}'

# 3. Avaliar a conversa
curl -X POST http://localhost:8000/chats/123/rating \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5, "comment": "Muito útil!"}'
```

### Exemplo 2: Re-avaliar uma conversa

```bash
# Atualizar rating existente
curl -X POST http://localhost:8000/chats/123/rating \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rating": 4, "comment": "Na verdade foi bom, mas não excelente"}'
```

### Exemplo 3: Ver estatísticas (Admin)

```bash
# Ver estatísticas gerais
curl -X GET http://localhost:8000/chats/stats/ratings \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Exemplo 4: Ver suas próprias estatísticas

```bash
# Ver estatísticas do usuário
curl -X GET http://localhost:8000/chats/user/ratings \
  -H "Authorization: Bearer $TOKEN"
```

---

## Migração do Banco de Dados

A migração já foi aplicada automaticamente. Caso precise reverter:

```bash
# Reverter migração
./venv/bin/alembic downgrade -1

# Aplicar novamente
./venv/bin/alembic upgrade head
```

---

## Integração com Frontend

### Exemplo React/Next.js

```typescript
// Avaliar conversa
async function rateChat(chatId: number, rating: number, comment?: string) {
  const response = await fetch(`/api/chats/${chatId}/rating`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ rating, comment }),
  });

  return await response.json();
}

// Componente de rating
function ChatRating({ chatId }: { chatId: number }) {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');

  const handleSubmit = async () => {
    await rateChat(chatId, rating, comment);
    alert('Avaliação enviada!');
  };

  return (
    <div>
      <h3>Como foi sua experiência?</h3>
      <StarRating value={rating} onChange={setRating} max={5} />
      <textarea
        placeholder="Comentário opcional"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        maxLength={1000}
      />
      <button onClick={handleSubmit}>Enviar Avaliação</button>
    </div>
  );
}
```

---

## Casos de Uso

1. **Melhorar a IA**: Usar ratings baixos para identificar conversas problemáticas
2. **Métricas de qualidade**: Acompanhar satisfação dos usuários ao longo do tempo
3. **Feedback qualitativo**: Comentários fornecem insights sobre o que melhorar
4. **Gamificação**: Mostrar ao usuário quantas conversas ele avaliou
5. **A/B Testing**: Comparar ratings entre diferentes versões da IA

---

## Considerações de Segurança

- ✅ Usuários só podem avaliar seus próprios chats
- ✅ Sessões anônimas são isoladas por `session_id`
- ✅ Admins têm acesso apenas a estatísticas agregadas
- ✅ Validação de input (0-5, máx 1000 chars)
- ✅ Timestamps automáticos para auditoria

---

## Próximos Passos (Sugestões)

1. **Webhook/Notificação**: Avisar admins quando houver rating muito baixo (0-2)
2. **Análise de sentimento**: Processar comentários com NLP
3. **Dashboard**: Interface visual para acompanhar métricas
4. **Export**: Endpoint para exportar ratings em CSV/JSON
5. **Rating por mensagem**: Além de avaliar a conversa inteira, avaliar mensagens individuais
