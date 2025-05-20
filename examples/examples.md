
# Exemplos de Programas em Khwarizmi

---

## 📘 1. Declarações Simples

```khwarizmi
BEGIN
int a
bool ativo
eq e
END
```

---

## 📘 2. Declarações com Atribuição

```khwarizmi
BEGIN
int idade = input()
int x = 10
eq e1 = x + 5
END
```

---

## 📘 3. Expressões com Operadores

```khwarizmi
BEGIN
int x = 3
int y = 4
int resultado = (x + 5) * 2 - y / 2
bool cond = x >= 10 && y != 15 || x < 2
END
```

---

## 📘 4. Reatribuições

```khwarizmi
BEGIN
int z = 5
z = z + 1
ativo = true
END
```

---

## 📘 5. Comandos: print, show, solve

```khwarizmi
BEGIN
int x
int y
int z = 3
eq fxy = z + y + x * x

print(z)
show(fxy, x == 2) // mostra gráfico de fxy por y

// solve(fxy == 0, x, y == 1)
// ^ retornaria erro, uma vez que solve é capaz de resolver apenas
// funções de primeiro grau com uma variável livre

solve(fxy == 0, y, x == 1) 
// ^ Neste caso daria certo, uma vez que x está sendo definido
// constante no input da função

END
```

---

## 📘 6. Condicional if/elif/else

```khwarizmi
BEGIN
int x = input()

if x < 5
BEGIN
print(x)
END
elif x == 5
BEGIN
print(x)
END
else
BEGIN
print(x)
END
END
```

---

## 📘 7. Laço while

```khwarizmi
BEGIN
int i = 0

while i < 3
BEGIN
print(i)
i = i + 1
END
END
```

---

## 📘 8. Bloco isolado

```khwarizmi
BEGIN
int a = 1
print(a)
END
```

---

## 📘 9. Equação com múltiplas variáveis livres

```khwarizmi
BEGIN
int x // variável livre
int y // variável livre
int z = 3 // valor inteiro
int resultado = z * z // valor inteiro
eq fxy = z + (y + y) * x

solve(fxy == resultado, x, y == 2) // mostra a solução no terminal
END
```