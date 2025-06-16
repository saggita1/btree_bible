# Processador de Bíblia com Árvore B 📖🌳

Uma implementação de alta performance de Árvore B em Python, projetada para processar e analisar eficientemente o texto completo da Bíblia, realizando operações de inserção, remoção e busca em aproximadamente 800.000 palavras.

**Desenvolvido por**: Ryan Pimentel  
**Disciplina**: Análise de Algoritmos-UFRR

## 📋 Índice
- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [O que é uma Árvore B?](#o-que-é-uma-árvore-b)
- [Detalhes da Implementação](#detalhes-da-implementação)
- [Estrutura do Código](#estrutura-do-código)
- [Métricas de Performance](#métricas-de-performance)
- [Como Usar](#como-usar)
- [Exemplo de Saída](#exemplo-de-saída)
- [Especificações Técnicas](#especificações-técnicas)

## 🎯 Visão Geral

Este projeto implementa uma estrutura de dados Árvore B otimizada para processar arquivos de texto grandes, especificamente a Bíblia em inglês. A implementação inclui:
- Inserção eficiente de palavras com contagem de ocorrências
- Operações de busca rápidas
- Capacidade de remoção de palavras
- Métricas de performance em tempo real
- Análise estatística de frequência de palavras

## ✨ Funcionalidades

- **Estrutura de Árvore B Otimizada**: Grau 100 para performance ótima com grandes conjuntos de dados
- **Rastreamento de Frequência**: Conta ocorrências de cada palavra sem duplicar entradas
- **Monitoramento de Performance**: Rastreia tempos de inserção e remoção
- **Análise Estatística**: Exibe as palavras mais frequentes e performance de busca
- **Acompanhamento de Progresso**: Mostra progresso em tempo real durante processamento
- **Tratamento de Erros**: Tratamento robusto de erros para operações com arquivos

## 🌳 O que é uma Árvore B?

Uma Árvore B é uma estrutura de dados de árvore balanceada que mantém os dados ordenados e permite buscas, inserções e remoções em tempo logarítmico. Diferente de uma árvore binária:

- **Múltiplas chaves por nó**: Cada nó pode conter várias chaves (palavras)
- **Múltiplos filhos**: Cada nó pode ter vários filhos (não apenas 2)
- **Balanceamento automático**: A árvore se mantém balanceada durante inserções e remoções
- **Otimizada para disco**: Ideal para grandes volumes de dados

### Estrutura Visual de uma Árvore B:
```
                    [M]
                   /   \
            [D,H]        [Q,T,X]
           /  |  \      /  |  |  \
       [A,C][F,G][K,L][N,P][R,S][U,V][Y,Z]
```

## 🔧 Detalhes da Implementação

### O que há em cada Nó (`BTreeNode`)

```python
class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []              # Lista ordenada de palavras
        self.children = []          # Lista de nós filhos
        self.leaf = leaf           # True se for folha, False se for nó interno
        self.word_count = defaultdict(int)  # Dicionário com contagem de cada palavra
```

#### Conteúdo dos Nós:

**Nós Folha (leaf = True):**
- Contêm as palavras reais (`keys`)
- Contêm a contagem de ocorrências (`word_count`)
- NÃO têm filhos (`children` está vazio)
- São onde as palavras são efetivamente armazenadas

**Nós Internos (leaf = False):**
- Contêm chaves que servem como "guias" para navegação
- Contêm ponteiros para nós filhos (`children`)
- Também mantêm contagem das palavras que passam por eles
- Servem como índices para encontrar as folhas corretas

#### Métodos Principais do Nó:

1. **`split(parent, payload)` - Divisão de Nó**
   ```python
   # Quando um nó fica cheio (2*grau-1 chaves):
   # 1. Cria um novo nó
   # 2. Move metade das chaves para o novo nó
   # 3. Sobe a chave do meio para o pai
   # 4. Atualiza os ponteiros de filhos se necessário
   ```

2. **`insert_key(key)` - Inserção de Palavra**
   ```python
   # Se a palavra já existe:
   #   - Incrementa o contador
   # Se é nova:
   #   - Insere na posição correta (mantendo ordem)
   #   - Inicializa contador com 1
   ```

3. **`remove_key(key)` - Remoção de Palavra**
   ```python
   # Se tem múltiplas ocorrências:
   #   - Apenas decrementa o contador
   # Se tem apenas uma ocorrência:
   #   - Remove a chave completamente
   ```

### Estrutura da Árvore B (`BTree`)

```python
class BTree:
    def __init__(self, degree=100):
        self.root = BTreeNode()     # Raiz começa como folha vazia
        self.degree = degree        # Grau da árvore (t)
        # Cada nó pode ter:
        # - Mínimo: t-1 chaves (exceto raiz)
        # - Máximo: 2t-1 chaves
        # - Filhos: entre t e 2t (para nós internos)
```

### Como a Árvore B Funciona

#### 1. **Inserção**
```
Processo de inserção de "LOVE":

1. Começa na raiz
2. Se a raiz está cheia → divide e cria nova raiz
3. Desce pela árvore até encontrar a folha correta
4. Insere na folha:
   - Se a folha está cheia → divide primeiro
   - Senão → insere diretamente

Exemplo visual:
Antes:  [GOD,JESUS]           (folha cheia com grau=2)
        
Depois: [JESUS]                (nova raiz)
        /     \
   [GOD]       [LOVE]          (folhas após divisão)
```

#### 2. **Busca**
```
Buscar "FAITH":

1. Começa na raiz [JESUS,MOSES]
2. "FAITH" < "JESUS" → vai para o primeiro filho
3. Chega em [DAVID,GOD]
4. "FAITH" está entre "DAVID" e "GOD" → vai para o segundo filho
5. Chega na folha [FAITH,GRACE]
6. Encontra "FAITH" → retorna nó e posição
```

#### 3. **Remoção**
```
Três casos principais:

Caso 1 - Chave em folha:
  Remove diretamente

Caso 2 - Chave em nó interno:
  Substitui por predecessor ou sucessor

Caso 3 - Chave não está no nó atual:
  Desce para o filho apropriado
  (pode precisar reorganizar a árvore)
```

## 📁 Estrutura do Código

### Componentes Principais:

1. **Classes de Dados**
   ```python
   BTreeNode  # Representa um nó individual
   BTree      # Gerencia toda a estrutura da árvore
   ```

2. **Operações Principais**
   ```python
   insert()    # Adiciona palavras à árvore
   search()    # Busca palavras na árvore
   remove()    # Remove palavras da árvore
   ```

3. **Métodos Auxiliares**
   ```python
   _insert_non_full()      # Inserção recursiva em nó não cheio
   _get_predecessor()      # Encontra predecessor para remoção
   _get_successor()        # Encontra sucessor para remoção
   _borrow_from_prev()     # Pega chave emprestada do irmão anterior
   _borrow_from_next()     # Pega chave emprestada do próximo irmão
   _merge()                # Une dois nós durante remoção
   ```

4. **Função Principal**
   ```python
   process_bible_file()    # Processa o arquivo BIBLE.txt
   ```

## 📊 Métricas de Performance

O sistema rastreia várias métricas:

- **Performance de Inserção**
  - Tempo total de inserção
  - Tempo médio por inserção
  - Palavras processadas por segundo

- **Performance de Busca**
  - Tempo individual de busca em milissegundos
  - Tempo médio de busca

- **Eficiência de Memória**
  - Armazena contadores ao invés de duplicatas
  - Divisão e fusão otimizadas de nós

## 💻 Como Usar
1. Coloque `BIBLE.txt` no mesmo diretório do script
2. Execute o programa:
```bash
python btree_bible.py
```

### Exemplo de Código
```python
# Criar uma Árvore B com grau personalizado
btree = BTree(degree=100)

# Inserir palavras
palavras = ['faith', 'hope', 'love']
for palavra in palavras:
    btree.insert(palavra)

# Buscar uma palavra
node, index = btree.search('love')
if node:
    count = node.word_count['love']
    print(f"'love' encontrada: {count} ocorrências")

# Obter estatísticas
btree.print_stats()
```

## 📈 Exemplo de Saída

```
Processando arquivo: BIBLE.txt
Arquivo lido em 0.02 segundos
Total de palavras encontradas: 794,807

Inserindo palavras na árvore B...
  Processadas 50,000 palavras... (759,651 palavras/seg, ~1s restantes)
  Processadas 100,000 palavras... (676,936 palavras/seg, ~1s restantes)
  Processadas 150,000 palavras... (637,271 palavras/seg, ~1s restantes)
  Processadas 200,000 palavras... (597,037 palavras/seg, ~1s restantes)
  Processadas 250,000 palavras... (558,350 palavras/seg, ~1s restantes)
  Processadas 300,000 palavras... (528,473 palavras/seg, ~1s restantes)
  Processadas 350,000 palavras... (505,609 palavras/seg, ~1s restantes)
  Processadas 400,000 palavras... (485,403 palavras/seg, ~1s restantes)
  Processadas 450,000 palavras... (466,637 palavras/seg, ~1s restantes)
  Processadas 500,000 palavras... (447,931 palavras/seg, ~1s restantes)
  Processadas 550,000 palavras... (432,618 palavras/seg, ~1s restantes)
  Processadas 600,000 palavras... (420,413 palavras/seg, ~0s restantes)
  Processadas 650,000 palavras... (406,851 palavras/seg, ~0s restantes)
  Processadas 700,000 palavras... (395,497 palavras/seg, ~0s restantes)
  Processadas 750,000 palavras... (383,616 palavras/seg, ~0s restantes)

Inserção completa em 2.14 segundos

Testando remoção de palavras...
  Removendo 'god' (ocorrências: 4,472)...
  Removendo 'jesus' (ocorrências: 983)...
  Removendo 'lord' (ocorrências: 7,964)...
  Removendo 'love' (ocorrências: 311)...
  Removendo 'faith' (ocorrências: 247)...
  Removendo 'heaven' (ocorrências: 583)...
  Removendo 'christ' (ocorrências: 571)...
Remoção completa em 0.0002 segundos

==================================================
ESTATÍSTICAS DA ÁRVORE B
==================================================
Total de palavras processadas: 794,807
Palavras únicas: 12,889
Tempo total de inserção: 1.9390 segundos
Tempo médio por inserção: 0.0024 ms
Tempo total de remoção: 0.0001 segundos
==================================================

Testando busca de palavras:
  'abraham': 250 ocorrências (tempo de busca: 0.0095 ms)
  'moses': 851 ocorrências (tempo de busca: 0.0100 ms)
  'david': 1,064 ocorrências (tempo de busca: 0.0188 ms)
  'paul': 176 ocorrências (tempo de busca: 0.0088 ms)
  'christ': 570 ocorrências (tempo de busca: 0.0050 ms)
  'jerusalem': 814 ocorrências (tempo de busca: 0.0093 ms)
  'israel': 2,575 ocorrências (tempo de busca: 0.0191 ms)

Tempo médio de busca: 0.0115 ms

10 palavras mais frequentes:
  1. 'the': 64,193 ocorrências
  2. 'and': 51,763 ocorrências
  3. 'of': 34,782 ocorrências
  4. 'to': 13,660 ocorrências
  5. 'that': 12,927 ocorrências
  6. 'in': 12,724 ocorrências
  7. 'he': 10,422 ocorrências
  8. 'shall': 9,840 ocorrências
  9. 'unto': 8,997 ocorrências
  10. 'for': 8,996 ocorrências
```
