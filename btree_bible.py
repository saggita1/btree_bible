import time
import re
from collections import defaultdict

class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf
        self.word_count = defaultdict(int)  # Conta ocorrências de cada palavra
    
    def split(self, parent, payload):
        """Divide o nó quando está cheio"""
        new_node = BTreeNode(self.leaf)
        
        mid_point = len(self.keys) // 2
        mid_key = self.keys[mid_point]
        
        new_node.keys = self.keys[mid_point + 1:]
        self.keys = self.keys[:mid_point]
        
        # Copia contadores de palavras
        for key in new_node.keys:
            new_node.word_count[key] = self.word_count[key]
            del self.word_count[key]
        
        # Move o contador da chave do meio para o pai
        parent_count = self.word_count[mid_key]
        del self.word_count[mid_key]
        
        # Se não for folha, divide os filhos também
        if not self.leaf:
            new_node.children = self.children[mid_point + 1:]
            self.children = self.children[:mid_point + 1]
            
        # Insere a chave do meio no pai
        parent.insert_in_node(mid_key, parent_count, new_node)
        
    def insert_in_node(self, key, count, right_child=None):
        """Insere uma chave diretamente no nó com seu contador"""
        # Encontra a posição correta para inserir
        index = 0
        for i, k in enumerate(self.keys):
            if key < k:
                index = i
                break
            else:
                index = i + 1
        
        # Insere a chave na posição correta
        self.keys.insert(index, key)
        self.word_count[key] = count
        
        # Se há um filho direito, insere-o também
        if right_child:
            self.children.insert(index + 1, right_child)
            
    def insert_key(self, key):
        """Insere ou incrementa uma chave no nó"""
        if key in self.word_count:
            self.word_count[key] += 1
            return False  # Não é uma nova palavra única
        else:
            # Encontra a posição correta e insere
            index = 0
            for i, k in enumerate(self.keys):
                if key < k:
                    index = i
                    break
                else:
                    index = i + 1
            
            self.keys.insert(index, key)
            self.word_count[key] = 1
            return True  # É uma nova palavra única
            
    def remove_key(self, key):
        """Remove uma chave do nó"""
        if key in self.keys:
            if self.word_count[key] > 1:
                self.word_count[key] -= 1
            else:
                self.keys.remove(key)
                del self.word_count[key]
            return True
        return False

class BTree:
    def __init__(self, degree=50):  # Grau maior para melhor performance com muitos dados
        self.root = BTreeNode()
        self.degree = degree
        self.insertion_time = 0
        self.removal_time = 0
        self.total_words = 0
        self.unique_words = 0
    
    def insert(self, key):
        """Insere uma palavra na árvore"""
        start_time = time.time()
        
        # Se a raiz está cheia, divide-a
        if len(self.root.keys) >= 2 * self.degree - 1:
            new_root = BTreeNode(leaf=False)
            old_root = self.root
            self.root = new_root
            new_root.children.append(old_root)
            old_root.split(new_root, key)
            
        # Insere no nó apropriado
        is_new = self._insert_non_full(self.root, key)
        
        self.insertion_time += time.time() - start_time
        self.total_words += 1
        
        if is_new:
            self.unique_words += 1
        
    def _insert_non_full(self, node, key):
        """Insere em um nó que não está cheio. Retorna True se é uma nova palavra."""
        if node.leaf:
            # É uma folha, insere diretamente
            return node.insert_key(key)
        else:
            # Não é folha, encontra o filho correto
            child_index = len(node.keys)
            for i, k in enumerate(node.keys):
                if key < k:
                    child_index = i
                    break
                elif key == k:
                    # A chave já existe neste nó
                    node.word_count[k] += 1
                    return False
                    
            child = node.children[child_index]
            
            # Se o filho está cheio, divide-o
            if len(child.keys) >= 2 * self.degree - 1:
                child.split(node, key)
                
                # Após a divisão, pode ser necessário ir para o próximo filho
                if child_index < len(node.keys) and key > node.keys[child_index]:
                    child_index += 1
                    
            # Recursivamente insere no filho apropriado
            return self._insert_non_full(node.children[child_index], key)
    
    def search(self, key, node=None):
        """Busca uma palavra na árvore"""
        if node is None:
            node = self.root
            
        # Procura a chave no nó atual
        for i, k in enumerate(node.keys):
            if key == k:
                return node, i
            elif key < k:
                if not node.leaf:
                    return self.search(key, node.children[i])
                return None, -1
                
        # Se a chave é maior que todas as chaves do nó
        if not node.leaf and len(node.children) > len(node.keys):
            return self.search(key, node.children[-1])
            
        return None, -1
    
    def remove(self, key):
        """Remove uma palavra da árvore"""
        start_time = time.time()
        result = self._remove_from_node(self.root, key)
        self.removal_time += time.time() - start_time
        
        # Se a raiz ficou vazia
        if result and len(self.root.keys) == 0:
            if not self.root.leaf and len(self.root.children) > 0:
                self.root = self.root.children[0]
                
        return result
    
    def _remove_from_node(self, node, key):
        """Remove uma chave de um nó específico"""
        if key in node.keys:
            if node.leaf:
                return node.remove_key(key)
            else:
                return self._remove_from_non_leaf(node, key)
        elif not node.leaf:
            # Encontra o filho onde a chave pode estar
            child_index = len(node.keys)
            for i, k in enumerate(node.keys):
                if key < k:
                    child_index = i
                    break
                    
            if child_index < len(node.children):
                return self._remove_from_subtree(node, child_index, key)
                
        return False
    
    def _remove_from_non_leaf(self, node, key):
        """Remove de nó não-folha"""
        key_index = node.keys.index(key)
        
        if key_index < len(node.children) - 1:
            if len(node.children[key_index].keys) >= self.degree:
                predecessor = self._get_predecessor(node, key_index)
                node.keys[key_index] = predecessor
                # Copia o contador
                pred_node, _ = self.search(predecessor)
                if pred_node:
                    node.word_count[predecessor] = pred_node.word_count[predecessor]
                return self._remove_from_node(node.children[key_index], predecessor)
            elif len(node.children[key_index + 1].keys) >= self.degree:
                successor = self._get_successor(node, key_index)
                node.keys[key_index] = successor
                # Copia o contador
                succ_node, _ = self.search(successor)
                if succ_node:
                    node.word_count[successor] = succ_node.word_count[successor]
                return self._remove_from_node(node.children[key_index + 1], successor)
            else:
                self._merge(node, key_index)
                return self._remove_from_node(node.children[key_index], key)
        
        return False
    
    def _remove_from_subtree(self, node, child_index, key):
        """Remove de uma subárvore"""
        if child_index < len(node.children) and len(node.children[child_index].keys) < self.degree:
            self._fill(node, child_index)
            
        if child_index < len(node.children):
            return self._remove_from_node(node.children[child_index], key)
            
        return False
    
    def _get_predecessor(self, node, key_index):
        """Obtém o predecessor de uma chave"""
        if key_index < len(node.children):
            current = node.children[key_index]
            while not current.leaf and len(current.children) > 0:
                current = current.children[-1]
            if len(current.keys) > 0:
                return current.keys[-1]
        return None
    
    def _get_successor(self, node, key_index):
        """Obtém o sucessor de uma chave"""
        if key_index + 1 < len(node.children):
            current = node.children[key_index + 1]
            while not current.leaf and len(current.children) > 0:
                current = current.children[0]
            if len(current.keys) > 0:
                return current.keys[0]
        return None
    
    def _fill(self, node, child_index):
        """Preenche um filho que tem menos que degree-1 chaves"""
        # Se o irmão anterior tem pelo menos degree chaves
        if child_index != 0 and child_index - 1 < len(node.children) and len(node.children[child_index - 1].keys) >= self.degree:
            self._borrow_from_prev(node, child_index)
        # Se o próximo irmão tem pelo menos degree chaves
        elif child_index != len(node.children) - 1 and child_index + 1 < len(node.children) and len(node.children[child_index + 1].keys) >= self.degree:
            self._borrow_from_next(node, child_index)
        # Se ambos os irmãos têm degree-1 chaves, faz merge
        else:
            if child_index != len(node.children) - 1:
                self._merge(node, child_index)
            else:
                self._merge(node, child_index - 1)
    
    def _borrow_from_prev(self, node, child_index):
        """Pega emprestado do irmão anterior"""
        if child_index > 0 and child_index < len(node.children) and child_index - 1 < len(node.keys):
            child = node.children[child_index]
            sibling = node.children[child_index - 1]
            
            # Move uma chave do pai para o filho
            child.keys.insert(0, node.keys[child_index - 1])
            child.word_count[node.keys[child_index - 1]] = node.word_count[node.keys[child_index - 1]]
            
            # Move uma chave do irmão para o pai
            if len(sibling.keys) > 0:
                node.keys[child_index - 1] = sibling.keys[-1]
                node.word_count[sibling.keys[-1]] = sibling.word_count[sibling.keys[-1]]
                sibling.keys.pop()
            
            # Move o ponteiro do filho se não for folha
            if not child.leaf and len(sibling.children) > 0:
                child.children.insert(0, sibling.children.pop())
    
    def _borrow_from_next(self, node, child_index):
        """Pega emprestado do próximo irmão"""
        if child_index < len(node.children) - 1 and child_index < len(node.keys):
            child = node.children[child_index]
            sibling = node.children[child_index + 1]
            
            # Move uma chave do pai para o filho
            child.keys.append(node.keys[child_index])
            child.word_count[node.keys[child_index]] = node.word_count[node.keys[child_index]]
            
            # Move uma chave do irmão para o pai
            if len(sibling.keys) > 0:
                node.keys[child_index] = sibling.keys[0]
                node.word_count[sibling.keys[0]] = sibling.word_count[sibling.keys[0]]
                sibling.keys.pop(0)
            
            # Move o ponteiro do filho se não for folha
            if not child.leaf and len(sibling.children) > 0:
                child.children.append(sibling.children.pop(0))
    
    def _merge(self, node, key_index):
        """Faz merge de um filho com seu irmão"""
        if key_index < len(node.keys) and key_index + 1 < len(node.children):
            child = node.children[key_index]
            sibling = node.children[key_index + 1]
            
            # Puxa uma chave do pai e faz merge com o irmão direito
            child.keys.append(node.keys[key_index])
            child.word_count[node.keys[key_index]] = node.word_count[node.keys[key_index]]
            
            # Copia as chaves do irmão
            child.keys.extend(sibling.keys)
            for k in sibling.keys:
                child.word_count[k] = sibling.word_count[k]
            
            # Copia os ponteiros dos filhos se não for folha
            if not child.leaf:
                child.children.extend(sibling.children)
                
            # Remove a chave do pai
            node.keys.pop(key_index)
            
            # Remove o ponteiro para o irmão
            node.children.pop(key_index + 1)
    
    def print_stats(self):
        """Imprime estatísticas da árvore"""
        print(f"\n{'='*50}")
        print(f"ESTATÍSTICAS DA ÁRVORE B")
        print(f"{'='*50}")
        print(f"Total de palavras processadas: {self.total_words:,}")
        print(f"Palavras únicas: {self.unique_words:,}")
        print(f"Tempo total de inserção: {self.insertion_time:.4f} segundos")
        if self.total_words > 0:
            print(f"Tempo médio por inserção: {(self.insertion_time/self.total_words)*1000:.4f} ms")
        print(f"Tempo total de remoção: {self.removal_time:.4f} segundos")
        print(f"{'='*50}")

def process_bible_file(filename):
    """Processa o arquivo da Bíblia"""
    print(f"Processando arquivo: {filename}")
    
    # Cria a árvore B com grau otimizado
    btree = BTree(degree=100)  # Aumentado para melhor performance
    
    try:
        # Lê o arquivo
        start_time = time.time()
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()
        
        print(f"Arquivo lido em {time.time() - start_time:.2f} segundos")
        
        # Extrai palavras (remove pontuação e converte para minúsculas)
        # Para inglês, usamos apenas a-zA-Z
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        print(f"Total de palavras encontradas: {len(words):,}")
        
        # Insere todas as palavras
        print("\nInserindo palavras na árvore B...")
        insertion_start = time.time()
        
        for i, word in enumerate(words):
            try:
                btree.insert(word)
            except Exception as e:
                print(f"Erro ao inserir palavra '{word}' na posição {i}: {e}")
                continue
            
            # Mostra progresso a cada 50000 palavras
            if (i + 1) % 50000 == 0:
                elapsed = time.time() - insertion_start
                rate = (i + 1) / elapsed
                remaining = (len(words) - i - 1) / rate
                print(f"  Processadas {i + 1:,} palavras... ({rate:.0f} palavras/seg, ~{remaining:.0f}s restantes)")
        
        print(f"\nInserção completa em {time.time() - insertion_start:.2f} segundos")
        
        # Testa remoção com algumas palavras
        print("\nTestando remoção de palavras...")
        test_words = ['god', 'jesus', 'lord', 'love', 'faith', 'heaven', 'christ']
        removal_start = time.time()
        
        for word in test_words:
            node, _ = btree.search(word)
            if node and word in node.word_count:
                count = node.word_count[word]
                print(f"  Removendo '{word}' (ocorrências: {count})...")
                btree.remove(word)
            else:
                print(f"  '{word}' não encontrado")
        
        print(f"Remoção completa em {time.time() - removal_start:.4f} segundos")
        
        # Mostra estatísticas
        btree.print_stats()
        
        # Testa busca
        print("\nTestando busca de palavras:")
        search_words = ['abraham', 'moses', 'david', 'paul', 'christ', 'jerusalem', 'israel']
        
        total_search_time = 0
        for word in search_words:
            start = time.time()
            node, _ = btree.search(word)
            search_time = time.time() - start
            total_search_time += search_time
            
            if node and word in node.word_count:
                count = node.word_count[word]
                print(f"  '{word}': {count} ocorrências (tempo de busca: {search_time*1000:.4f} ms)")
            else:
                print(f"  '{word}': não encontrado (tempo de busca: {search_time*1000:.4f} ms)")
        
        print(f"\nTempo médio de busca: {(total_search_time/len(search_words))*1000:.4f} ms")
        
        # Mostra as 10 palavras mais frequentes
        print("\n10 palavras mais frequentes:")
        all_words = []
        
        def collect_words(node):
            for key in node.keys:
                if key in node.word_count:
                    all_words.append((key, node.word_count[key]))
            if not node.leaf:
                for child in node.children:
                    collect_words(child)
        
        collect_words(btree.root)
        all_words.sort(key=lambda x: x[1], reverse=True)
        
        for i, (word, count) in enumerate(all_words[:10]):
            print(f"  {i+1}. '{word}': {count:,} ocorrências")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado!")
        print("Por favor, certifique-se de que o arquivo BIBLE.txt está no mesmo diretório.")
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Processa o arquivo BIBLE.txt
    process_bible_file("BIBLE.txt")