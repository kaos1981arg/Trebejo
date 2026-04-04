Feature: Navegación de Trebejo

  Background:
    Given que abro la aplicación Trebejo
    And activo el modo de accesibilidad

  Scenario: Iniciar la aplicación y ver el menú principal
    Then el título de la página debería ser "Trebejo"
    And la ruta debería ser "/"

  Scenario Outline: Navegar desde la Home a diferentes secciones
    When hago clic en el botón con el texto "<boton_texto>"
    Then la ruta debería ser "<ruta_esperada>"

    Examples:

      | boton_texto                             | ruta_esperada |
      | Duelo de Autómatas IA                   | /duelo        |
      | Red de Correspondencia Global           | /red          |
      | Gabinete de Análisis Táctico            | /analisis     |
      | Ajustes del Motor y Reglas              | /ajustes      |
      | Crónica y Rendimiento ELO               | /estadisticas |
