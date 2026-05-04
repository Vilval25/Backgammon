# Backgammon en Python

Juego de Backgammon con interfaz gráfica y modo **jugador contra computadora**. La IA controla las fichas del oponente automáticamente.

## Requisito previo

Instalar la librería pygame antes de ejecutar el juego:

	python3 -m pip install -U pygame --user

O usar el gestor de paquetes Anaconda.
Para más información sobre pygame: https://www.pygame.org/wiki/GettingStarted

## Cómo jugar

Ejecuta el archivo **Backgammon.py** para iniciar el juego.

1. Al iniciar, se lanzan los dados automáticamente para determinar qué color comienza.
2. Haz clic en el botón **'DICE ROLL'** para lanzar los dados.
3. Se lanzarán 2 dados y se mostrarán en el lado derecho del tablero.
4. Selecciona una ficha resaltada haciendo clic sobre ella con el **ratón**.
5. Elige el destino resaltado usando:
   - **Flecha ARRIBA**: seleccionar la jugada del dado superior
   - **Flecha ABAJO**: seleccionar la jugada del dado inferior
