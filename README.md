# AI Cars

Este projeto tem como objetivo servir como forma de avaliação para a disciplina de Projeto Machine Learning do Curso de Ciência da Computação da Univerisdade Estadual do Oeste do Paraná.

### Bibliotecas

Para executar o projeto é necessário instalar as seguintes bibliotecas python:

- pygame
- neat-python
- graphviz
- matplotlib

### Utilização

Para iniciar um treinamento basta executar o arquivo main.py. Uma serie de mapas é fornecida e outros ponde ser criados a partir do arquivo GIMP template_map.xcf. Para realizar o treinamento em um mapa desejado basata alterar o nome passado durante a criação do objeto Game:

```python
# Mudar mapName
game = Game(cars, genomes, "mapName")
forcedStop = False
```

Por padrão o treinamento durante 1000 gerações, caso queira salvar o melhor genoma antes desse tempo, basta apertar a tecla **T** durante o treinamento. Isso fará com que o melhor genoma seja salvo no arquivo winner e gráficos sejam gerados nos arquivos fitness.png e species.png

Para testar o genoma criado em outros mapas, execute o arquivo ```run-winner.py```. A mudança de mapa é feita da mesma forma que a anterior, trocando o nome passado para o objeto Game.

### Autor
- Lyncon Baez