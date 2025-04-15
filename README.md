# 📐 Projeto Nova Linguagem – Khwarizmi

Bem-vindo ao repositório do **Projeto Nova Linguagem**, parte da disciplina de Linguagens e Paradigmas.

Aqui desenvolvemos a **Khwarizmi**, uma linguagem de programação simbólica e acessível, criada em homenagem ao matemático Al-Khwarizmi, pai da álgebra.

---

## 💡 Motivação

A **Khwarizmi** nasce da vontade de **tornar a resolução de equações algébricas mais acessível** para iniciantes na programação e na matemática. Muitos estudantes enfrentam dificuldades ao lidar com expressões simbólicas em linguagens tradicionais, que exigem tanto conhecimento técnico quanto domínio matemático.

Com a Khwarizmi, buscamos:

- Aproximar a programação da **linguagem matemática simbólica**.
- Reduzir a barreira de entrada para quem está aprendendo **álgebra elementar**.
- Oferecer uma maneira intuitiva de representar e resolver **equações de primeiro grau com múltiplas variáveis**.

---

## 🧠 Características

- **Foco exclusivo em álgebra simbólica**, especialmente equações lineares.
- Suporte a **múltiplas variáveis** e resolução automática de equações.
- Sintaxe baseada em **estruturas simples e expressivas**.
- Estruturas disponíveis:
  - Declaração de variáveis com tipo (`int`, `bool`, `eq`)
  - Atribuição com `=`
  - Impressão de dados com `print(...)`
  - Condicionais com `if` / `elif` / `else`
  - Laços com `while`
  - Entrada com `input()`
  - Comando `show(...)` para visualizar equações
  - Comando `solve(...)` para resolução simbólica

---

## 🔤 Estrutura da Linguagem (EBNF)

A gramática da Khwarizmi foi especificada segundo o padrão **EBNF** e pode ser consultada no arquivo:

📄 [`gramatica.ebnf`](./gramatica.ebnf)

---

## 📘 Exemplo de Código

```khwarizmi
BEGIN

int x
int y
int z = input()
eq fxy = 3*x + y/4 + z + 3

print(z)

int i = 0
while i<=10
BEGIN
print(i)
solve(fxy == 0, x, y==i)
i = i + 1
END
show(fxy, x==0)

END
```

---

## 🧮 Sobre o Nome

**Khwarizmi** homenageia o matemático persa **Muhammad ibn Musa al-Khwarizmi**, cujo trabalho influenciou profundamente o desenvolvimento da álgebra. A linguagem carrega seu nome como forma de valorizar a história da matemática e sua contribuição para o pensamento lógico e computacional.

---

## 🚀 Futuras Expansões

A **Khwarizmi** está apenas começando. Embora o foco inicial seja a resolução simbólica de equações lineares, existem diversas melhorias que podem ser feitas para torná-la ainda mais poderosa. Algumas delas são:

- ✅ **Suporte a equações não-lineares**  
  Ampliação da lógica simbólica para resolver polinômios de grau superior e outras expressões não-lineares.

- ✅ **Suporte ao tipo `float`**  
  Permitirá lidar com números reais não inteiros, ampliando a expressividade da linguagem para problemas mais variados.

- ✅ **Interface gráfica para visualização**  
  Representação visual dos passos de resolução, ideal para fins didáticos e compreensão intuitiva.

- ✅ **Suporte a números imaginários e complexos**  
  Inclusão de suporte a números da forma `a + bi`, viabilizando equações no campo dos complexos.

- ✅ **Operações matemáticas avançadas**, como:
  - `limit(expr, var → valor)` — Cálculo de limites.
  - `derivative(expr, var)` — Derivadas comuns.
  - `integral(expr, var)` — Integrais definidas e indefinidas.
  - `del expr/del var` — Derivadas parciais.
